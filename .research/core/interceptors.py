"""Interceptor Hook Blueprint.

Defines how integrated features attach to the runtime loop via the hook engine.
Each interceptor modifies or validates state at specific lifecycle stages.

All interceptors work with the synchronous trigger_sync() interface so any AI
agent can use them without async infrastructure.
"""

import logging
from pathlib import Path

try:
    from pydantic import ValidationError
except ImportError:
    ValidationError = None

from hooks import hook_engine
from core.utils import (
    find_project_root, load_json_safe, save_json_atomic,
    now_iso, get_data_scale_thresholds,
)

logger = logging.getLogger("research.interceptors")


# =============================================================================
# pre_routing: Semantic skill routing + data scale detection
# =============================================================================

@hook_engine.register("pre_routing")
def semantic_skill_router(state: dict, *args, **kwargs) -> dict:
    """Scan query against skill index. Load only relevant skills into memory.

    Prevents loading all 40+ skills at once. Matches task keywords against
    .research/cache/skill_index.json and loads only the 2-4 most relevant.

    Sets state["loaded_skills"] with matching skill paths so the AI agent
    knows exactly which skill files to read.
    """
    task = state.get("task", "")
    if not task:
        return state

    project_root = find_project_root()
    index_path = project_root / ".research" / "cache" / "skill_index.json"

    if not index_path.exists():
        return state

    index_data = load_json_safe(index_path)
    skills = index_data.get("skills", [])

    task_lower = task.lower()
    scored = []
    for skill in skills:
        score = 0
        for kw in skill.get("keywords", []):
            if kw.lower() in task_lower:
                score += 3
        for kw in skill.get("keywords", []):
            if kw.lower() in skill.get("description", "").lower():
                score += 1
        if score > 0:
            scored.append((score, skill))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_skills = [s for _, s in scored[:4]]

    state["loaded_skills"] = top_skills
    state["skill_count"] = len(top_skills)
    logger.debug("Loaded %d skills for task: %s", len(top_skills), task)
    return state


@hook_engine.register("pre_routing")
def detect_data_scale_constraints(state: dict, *args, **kwargs) -> dict:
    """Scan input data files and enforce library constraints based on file size.

    Prevents OOM errors by detecting large files (>1GB) and forcing the agent
    to use polars lazy frames or pyarrow instead of pandas.

    Sets state["data_scale_profile"] with per-file classifications:
      - "small" (<100MB): pandas OK
      - "medium" (100MB-1GB): pandas OK, polars recommended
      - "large" (1GB-10GB): polars lazy frames REQUIRED
      - "massive" (>10GB): polars lazy frames + chunked processing REQUIRED

    Also sets state["data_processing_constraint"] with a hard constraint message
    that must be injected into the system prompt.
    """
    project_root = find_project_root()
    data_raw = project_root / "inputs" / "data" / "raw"

    if not data_raw.exists():
        return state

    thresholds = get_data_scale_thresholds()
    profile = {}
    has_large_files = False
    constraint_parts = []

    for f in data_raw.iterdir():
        if f.is_file() and f.suffix in {".csv", ".parquet", ".tsv", ".json", ".feather", ".arrow"}:
            size_bytes = f.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            size_gb = size_bytes / (1024 * 1024 * 1024)

            if size_gb >= thresholds["massive_gb"]:
                profile[str(f.relative_to(project_root))] = "massive"
                has_large_files = True
                constraint_parts.append(
                    f"FILE {f.name} ({size_gb:.1f}GB): MUST use polars.scan_* (lazy) "
                    f"or pyarrow.dataset with chunked processing. NEVER use pd.read_csv() "
                    f"or pl.read_* (eager). Process in chunks."
                )
            elif size_gb >= thresholds["large_gb"]:
                profile[str(f.relative_to(project_root))] = "large"
                has_large_files = True
                constraint_parts.append(
                    f"FILE {f.name} ({size_gb:.1f}GB): MUST use polars lazy frames "
                    f"(pl.scan_*). Do NOT use pandas. Collect() only after all transformations."
                )
            elif size_mb >= thresholds["medium_mb"]:
                profile[str(f.relative_to(project_root))] = "medium"
                constraint_parts.append(
                    f"FILE {f.name} ({size_mb:.0f}MB): polars recommended for performance. "
                    f"pandas acceptable but monitor memory usage."
                )
            else:
                profile[str(f.relative_to(project_root))] = "small"

    if not profile:
        return state

    state["data_scale_profile"] = profile
    state["has_large_files"] = has_large_files

    if has_large_files:
        state["data_processing_constraint"] = (
            "DATA SCALE CONSTRAINT ACTIVE — The following files exceed memory thresholds:\n"
            + "\n".join(constraint_parts)
            + "\n\nENFORCEMENT: Any script that attempts to load these files with pandas "
            "or eager polars will be flagged. Use polars lazy evaluation (scan_*) or "
            "pyarrow.dataset for files marked 'large' or 'massive'."
        )
        logger.warning(
            "Data scale constraint active: %d large/massive files detected",
            sum(1 for v in profile.values() if v in ("large", "massive")),
        )
    else:
        state["data_processing_constraint"] = None

    return state


# =============================================================================
# pre_execution: Token budget throttling + cache lookup
# =============================================================================

@hook_engine.register("pre_execution")
def apply_token_budget_throttle(state: dict, *args, **kwargs) -> dict:
    """Intercept prompt before LLM delivery. Truncate context if near overflow.

    Sets state["context_action"] to one of:
      - "emergency_split" (>90%): must checkpoint, generate CTM, and split conversation
      - "flush_non_essential" (>80%): remove non-essential skill docs
      - "summarize_phases" (>60%): summarize completed phases
      - "none" (<60%): full context available

    At 90%, generates a Context Transfer Memorandum (CTM) to preserve latent
    context that cannot be transferred via structured state alone.
    """
    budget = state.get("token_budget", {})
    limit = budget.get("limit", 200000)
    used = budget.get("used", 0)
    pct = used / limit if limit > 0 else 0

    if pct >= 0.9:
        state["context_action"] = "emergency_split"
        state["context_message"] = (
            f"Context at {pct:.0%}. Force checkpoint, generate CTM, and split conversation."
        )
        logger.warning("Token budget at %.0f%% — emergency split + CTM required", pct * 100)

        ctms_generated = state.get("ctms_generated", 0)
        if ctms_generated == 0:
            ctm = _generate_context_transfer_memo(state, pct)
            if ctm:
                state["ctm_generated"] = ctm
                state["ctms_generated"] = ctms_generated + 1
                logger.info("Context Transfer Memorandum generated: %s", ctm.get("ctm_id"))

        elif pct >= 0.8:
            state["context_action"] = "flush_non_essential"
            state["context_message"] = (
                f"Context at {pct:.0%}. Flushing non-essential skill docs."
            )
            logger.warning("Token budget at %.0f%% — flushing non-essential context", pct * 100)
        elif pct >= 0.6:
            state["context_action"] = "summarize_phases"
            state["context_message"] = (
                f"Context at {pct:.0%}. Summarizing completed phases."
            )
            logger.info("Token budget at %.0f%% — summarizing completed phases", pct * 100)
        else:
            state["context_action"] = "none"

    return state


def _generate_context_transfer_memo(state: dict, token_pct: float) -> dict:
    """Generate a Context Transfer Memorandum at 90% token budget.

    Captures abandoned paths, micro-decisions, and immediate tactical goals
    so a new conversation can resume with full situational awareness.

    Returns a CTM dict ready for serialization.
    """
    project_root = find_project_root()
    ctm_id = f"ctm_{now_timestamp()}"

    ctm_dir = project_root / ".research" / "cache" / "context_transfer_memos"
    ctm_dir.mkdir(parents=True, exist_ok=True)

    ctm = {
        "ctm_id": ctm_id,
        "phase": state.get("phase", "unknown"),
        "token_usage_pct": round(token_pct, 4),
        "generated_at": now_iso(),
        "abandoned_paths": state.get("dead_ends", []),
        "micro_decisions": [],
        "immediate_goals": [],
        "partial_results": [],
        "open_questions": [],
        "state_file_refs": [],
        "handoff_notes": (
            f"EMERGENCY SPLIT: Token budget reached {token_pct:.0%}. "
            f"Phase: {state.get('phase', 'unknown')}, Step: {state.get('step', 0)}. "
            f"Review the state ledger (.research/cache/state.json) and latest checkpoint "
            f"for structured state. This CTM captures the latent context.\n\n"
            f"INSTRUCTIONS FOR NEXT CONVERSATION:\n"
            f"1. Read this CTM first to understand what was in progress\n"
            f"2. Read .research/cache/state.json for structured state\n"
            f"3. Load the latest checkpoint from .research/cache/checkpoints/\n"
            f"4. Continue from the immediate_goals listed below\n"
            f"5. Check open_questions for unresolved items\n"
            f"6. Review abandoned_paths to avoid repeating failed approaches"
        ),
    }

    state_file_refs = [
        ".research/cache/state.json",
        "docs/manifest.json",
        "docs/research_log.md",
    ]
    checkpoint_dir = project_root / ".research" / "cache" / "checkpoints"
    if checkpoint_dir.exists():
        checkpoints = list(checkpoint_dir.glob("*.json"))
        if checkpoints:
            latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
            state_file_refs.append(str(latest.relative_to(project_root)))

    ctm["state_file_refs"] = state_file_refs

    ctm_path = ctm_dir / f"{ctm_id}.json"
    save_json_atomic(ctm_path, ctm)

    logger.info("CTM saved to: %s", ctm_path)
    return ctm


@hook_engine.register("pre_execution")
def check_cache_before_execution(state: dict, *args, **kwargs) -> dict:
    """Check research cache before executing. Return cached result on hit.

    If a cached result exists for the operation+params, sets:
      state["cache_hit"] = True
      state["cached_result"] = <cached data>
      state["skip_execution"] = True

    The AI agent checks these flags and skips redundant computation.
    """
    project_root = find_project_root()
    cache_db = project_root / ".research" / "cache" / "research_cache.db"

    if not cache_db.exists():
        return state

    operation = state.get("operation", "")
    data_hash = state.get("data_hash", "")

    if not operation:
        return state

    try:
        import sys
        sys.path.insert(0, str(project_root / ".research" / "scripts" / "utils"))
        from cache_manager import ResearchCache

        cache = ResearchCache(cache_db)
        cached = cache.get_computed_stats(data_hash, operation)

        if cached:
            state["cache_hit"] = True
            state["cached_result"] = cached
            state["skip_execution"] = True
            logger.info("Cache hit for operation: %s", operation)
        else:
            state["cache_hit"] = False
            logger.debug("Cache miss for operation: %s", operation)
    except ImportError:
        state["cache_hit"] = False
    except Exception as e:
        logger.debug("Cache check failed: %s", e)
        state["cache_hit"] = False

    return state


# =============================================================================
# post_execution: Code sandbox + critic review
# =============================================================================

@hook_engine.register("post_execution")
def evaluate_code_sandbox(state: dict, *args, **kwargs) -> dict:
    """Intercept generated Python scripts. Validate syntax before execution.

    If generated_code exists in state:
      - Validates Python syntax via ast.parse
      - On failure: sets execution_failure=True, includes error
      - The AI agent uses this to auto-fix before running
    """
    generated_code = state.get("generated_code", "")
    if not generated_code:
        return state

    try:
        import ast
        ast.parse(generated_code)
        state["syntax_valid"] = True
        state["syntax_error"] = None
    except SyntaxError as e:
        state["syntax_valid"] = False
        state["syntax_error"] = str(e)
        state["execution_failure"] = True
        state["traceback_log"] = f"SyntaxError: {e}"
        logger.error("Generated code has syntax error: %s", e)

    return state


@hook_engine.register("post_execution")
def check_dependencies(state: dict, *args, **kwargs) -> dict:
    """Detect uninstalled imports in generated code and auto-resolve.

    If generated_code or generated_script exists in state:
      - Extracts imports via AST parsing
      - Checks against installed packages
      - If missing and auto_dependency_resolution enabled: installs via uv/pip
      - Updates requirements.txt with new packages
    """
    project_root = find_project_root()
    config_path = project_root / ".research" / "config.yaml"

    # Check if auto-dependency resolution is enabled
    auto_resolve = False
    try:
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
        auto_resolve = config.get("dependency_management", {}).get("auto_detect", False)
    except Exception:
        pass

    if not auto_resolve:
        return state

    generated_code = state.get("generated_code", "")
    generated_script = state.get("generated_script", "")

    code_to_check = generated_code or generated_script
    if not code_to_check:
        return state

    try:
        import ast
        import sys
        import subprocess

        # Parse imports
        tree = ast.parse(code_to_check)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        # Get installed packages
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        installed = set()
        if result.returncode == 0:
            packages = json.loads(result.stdout)
            installed = {p["name"].lower().replace("-", "_") for p in packages}

        # Find missing
        missing = []
        for imp in imports:
            if imp in sys.stdlib_module_names:
                continue
            if imp.lower().replace("-", "_") not in installed:
                missing.append(imp)

        if missing:
            state["missing_dependencies"] = missing
            state["dependency_resolution_needed"] = True
            logger.warning("Missing dependencies detected: %s", missing)

            # Auto-install if enabled
            if auto_resolve:
                try:
                    # Try uv first
                    subprocess.run(
                        ["uv", "pip", "install"] + missing,
                        capture_output=True,
                        timeout=120,
                    )
                except FileNotFoundError:
                    # Fall back to pip
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install"] + missing,
                        capture_output=True,
                        timeout=120,
                    )

                state["dependencies_installed"] = missing
                logger.info("Installed missing dependencies: %s", missing)
    except Exception as e:
        logger.debug("Dependency check failed: %s", e)

    return state


@hook_engine.register("post_execution")
def run_critic_review(state: dict, *args, **kwargs) -> dict:
    """Trigger critic agent review on output before advancing pipeline.

    For critical phases (execute_analysis, compile_outputs, literature_deep),
    this sets state["critic_triggered"] = True and writes a critic brief
    to reports/audit/critic_report_<phase>.json so the AI agent knows
    to run the critic agent before proceeding.
    """
    phase = state.get("phase", "")
    critic_phases = {"execute_analysis", "compile_outputs", "literature_deep"}

    if phase not in critic_phases:
        return state

    output = state.get("output", "")
    if not output:
        return state

    state["critic_triggered"] = True

    # Write critic brief so the AI agent picks it up
    project_root = find_project_root()
    audit_dir = project_root / "reports" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    critic_brief = {
        "phase": phase,
        "timestamp": now_iso(),
        "status": "pending_review",
        "checks": [
            "logical_consistency",
            "data_grounding",
            "scope_creep",
            "internal_contradiction",
            "missing_uncertainty",
        ],
        "output_preview": output[:500] if isinstance(output, str) else str(output)[:500],
    }

    critic_path = audit_dir / f"critic_report_{phase}.json"
    save_json_atomic(critic_path, critic_brief)

    logger.info("Critic review triggered for phase: %s", phase)
    return state


@hook_engine.register("post_execution")
def run_reviewer2(state: dict, *args, **kwargs) -> dict:
    """Trigger adversarial Reviewer 2 critique after compile_outputs.

    This is a more aggressive review than the standard critic — it actively
    tries to destroy the findings by finding unaddressed confounders,
    alternative explanations, and methodological flaws.
    """
    phase = state.get("phase", "")

    if phase != "compile_outputs":
        return state

    output = state.get("output", "")
    if not output:
        return state

    state["reviewer2_triggered"] = True

    # Write reviewer2 brief so the AI agent picks it up
    project_root = find_project_root()
    audit_dir = project_root / "reports" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    reviewer2_brief = {
        "phase": "compile_outputs",
        "timestamp": now_iso(),
        "status": "pending_adversarial_review",
        "review_type": "reviewer2_critic",
        "checks": [
            "unaddressed_confounders",
            "alternative_explanations",
            "methodological_flaws",
            "overclaiming",
            "missing_robustness_checks",
            "statistical_concerns",
            "limitations",
        ],
        "output_preview": output[:500] if isinstance(output, str) else str(output)[:500],
    }

    reviewer2_path = audit_dir / "reviewer2_brief.json"
    save_json_atomic(reviewer2_path, reviewer2_brief)

    logger.info("Reviewer 2 adversarial review triggered")
    return state


# =============================================================================
# pre_ledger_commit: Pydantic gatekeeper + approval gate
# =============================================================================

@hook_engine.register("pre_ledger_commit")
def enforce_pydantic_gatekeeper(state: dict, *args, **kwargs) -> dict:
    """Strict evaluation of data payloads prior to permanent state serialization.

    Validates state["current_output"] against the Pydantic schema for
    state["active_task"]. On failure:
      - state["schema_valid"] = False
      - state["rollback_triggered"] = True
      - state["validation_error"] = error message
    """
    if ValidationError is None:
        return state

    output = state.get("current_output")
    active_task = state.get("active_task", "")

    if not output or not active_task:
        return state

    try:
        import sys
        sys.path.insert(0, str(find_project_root() / ".research"))
        from schemas.validator import get_schema_for_task, validate_payload

        schema_cls = get_schema_for_task(active_task)
        validate_payload(output, schema_cls)
        state["schema_valid"] = True
        state["rollback_triggered"] = False
    except (ImportError, ValueError) as e:
        state["schema_valid"] = False
        state["rollback_triggered"] = True
        state["validation_error"] = str(e)
        logger.error("Schema validation failed for %s: %s", active_task, e)
    except ValidationError as e:
        state["schema_valid"] = False
        state["rollback_triggered"] = True
        state["validation_error"] = str(e)
        logger.error("Pydantic validation failed for %s: %s", active_task, e)

    return state


@hook_engine.register("pre_ledger_commit")
def check_approval_gate(state: dict, *args, **kwargs) -> dict:
    """Check if a pending approval exists and process the response.

    This is the NON-BLOCKING version. It checks for an existing response
    file rather than waiting. The AI agent calls this repeatedly or the
    CLI handles the blocking wait.

    Sets state["approval_status"] to:
      - "approved" — pipeline can continue
      - "rejected" — pipeline must stop, state["rejection_reason"] set
      - "pending" — approval gate is active, no response yet
      - "none" — no approval gate for this phase
    """
    action = kwargs.get("action")
    phase = kwargs.get("phase") or state.get("phase")

    if action != "complete_phase":
        state["approval_status"] = "none"
        return state

    TARGET_PHASES = {"method_route", "execute_analysis", "compile_outputs", "audit_validate"}
    if phase not in TARGET_PHASES:
        state["approval_status"] = "none"
        return state

    project_root = find_project_root()
    cache_dir = project_root / ".research" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    pending_path = cache_dir / "pending_approval.json"
    response_path = cache_dir / "approval_response.json"

    # Check if there's already a response
    if response_path.exists():
        try:
            with open(response_path) as f:
                response = json.load(f)

            if response.get("phase") == phase:
                status = response.get("status")
                reason = response.get("reason", "No reason provided.")

                # Clean up
                for path in [pending_path, response_path]:
                    try:
                        if path.exists():
                            path.unlink()
                    except Exception:
                        pass

                if status == "approved":
                    state["approval_status"] = "approved"
                    logger.info("Phase '%s' approved", phase)
                else:
                    state["approval_status"] = "rejected"
                    state["rejection_reason"] = reason
                    logger.warning("Phase '%s' rejected: %s", phase, reason)

                return state
        except Exception:
            pass

    # Check if there's a pending request (from a previous call)
    if pending_path.exists():
        state["approval_status"] = "pending"
        return state

    # No pending request yet — create one
    pending_data = {
        "phase": phase,
        "message": f"Please approve the completion of phase '{phase}'.",
        "timestamp": now_iso(),
    }
    save_json_atomic(pending_path, pending_data)

    state["approval_status"] = "pending"
    state["approval_gate_active"] = True
    logger.info("Approval gate created for phase: %s", phase)
    return state


# =============================================================================
# on_failure: State freeze + error logging
# =============================================================================

@hook_engine.register("on_failure")
def freeze_state_on_failure(state: dict, *args, **kwargs) -> dict:
    """Freeze current state on failure. Serialize to snapshot, log to dead_ends.

    Creates a failure log in docs/dead_ends/ with:
      - Phase and step at failure
      - Error message
      - State snapshot (run_id, checkpoints, loaded_data)
      - Recovery point for resume

    Sets state["recovery_point"] so the AI agent knows where to resume.
    """
    error = kwargs.get("error", "Unknown error")
    phase = state.get("phase", "unknown")

    project_root = find_project_root()
    dead_ends_dir = project_root / "docs" / "dead_ends"
    dead_ends_dir.mkdir(parents=True, exist_ok=True)

    timestamp = now_timestamp()
    error_log = dead_ends_dir / f"failure_{phase}_{timestamp}.json"

    error_data = {
        "phase": phase,
        "step": state.get("step", 0),
        "error": str(error),
        "state_snapshot": {
            "run_id": state.get("run_id"),
            "phase": phase,
            "checkpoints": state.get("checkpoints", {}),
            "loaded_data": state.get("loaded_data", []),
        },
        "timestamp": now_iso(),
        "recovery_point": f"{phase}:step_{state.get('step', 0)}",
    }

    save_json_atomic(error_log, error_data)
    state["failure_logged"] = True
    state["error_log_path"] = str(error_log)
    state["recovery_point"] = error_data["recovery_point"]

    logger.error("Failure logged for phase %s: %s", phase, error)
    return state
