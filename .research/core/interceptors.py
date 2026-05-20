"""Interceptor Hook Blueprint.

Defines how integrated features attach to the runtime loop via the hook engine.
Each interceptor modifies or validates state at specific lifecycle stages.

All interceptors work with the synchronous trigger_sync() interface so any AI
agent can use them without async infrastructure.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone

try:
    from pydantic import ValidationError
except ImportError:
    ValidationError = None

from hooks import hook_engine

logger = logging.getLogger("research.interceptors")


def find_project_root() -> Path:
    """Find project root by looking for .research/ directory."""
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return Path.cwd()


def load_json_safe(path: Path) -> dict:
    """Load JSON file safely, returning empty dict on failure."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json_atomic(path: Path, data: dict):
    """Write JSON atomically (write to temp, then rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)


# =============================================================================
# pre_routing: Semantic skill routing
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


# =============================================================================
# pre_execution: Token budget throttling + cache lookup
# =============================================================================

@hook_engine.register("pre_execution")
def apply_token_budget_throttle(state: dict, *args, **kwargs) -> dict:
    """Intercept prompt before LLM delivery. Truncate context if near overflow.

    Sets state["context_action"] to one of:
      - "emergency_split" (>90%): must checkpoint and split conversation
      - "flush_non_essential" (>80%): remove non-essential skill docs
      - "summarize_phases" (>60%): summarize completed phases
      - "none" (<60%): full context available

    The AI agent checks state["context_action"] and follows the protocol.
    """
    budget = state.get("token_budget", {})
    limit = budget.get("limit", 200000)
    used = budget.get("used", 0)
    pct = used / limit if limit > 0 else 0

    if pct >= 0.9:
        state["context_action"] = "emergency_split"
        state["context_message"] = (
            f"Context at {pct:.0%}. Force checkpoint and split conversation."
        )
        logger.warning("Token budget at %.0f%% — emergency split required", pct * 100)
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
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

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "recovery_point": f"{phase}:step_{state.get('step', 0)}",
    }

    save_json_atomic(error_log, error_data)
    state["failure_logged"] = True
    state["error_log_path"] = str(error_log)
    state["recovery_point"] = error_data["recovery_point"]

    logger.error("Failure logged for phase %s: %s", phase, error)
    return state
