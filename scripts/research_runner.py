#!/usr/bin/env python3
"""State and Command Orchestrator for the Research Co-Pilot.

This script provides a platform-agnostic CLI runner to manage the lifecycle of
the research project, track phase completions, generate fully-hydrated prompts
for any LLM/agentic interface, and keep tool-specific configurations (OpenCode,
Cursor, Copilot, etc.) in sync with a single source of truth.

Notes
-----
This script adheres to standard agentic-control patterns by managing state
externally in `.research_state.json`, separating prompt templating from runtime
execution, and providing a clean CLI interface for both terminal-capable agents
and human operators using chat interfaces.
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

# Setup basic logging to stderr so stdout remains clean for prompt printing
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr
)

# ---------------------------------------------------------------------------
# Path Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
STATE_FILE = PROJECT_ROOT / ".research_state.json"
GUARDRAILS_FILE = PROJECT_ROOT / "agents/00_core_guardrails.md"
BRIEF_FILE = PROJECT_ROOT / "docs_input/research_brief.md"

# Output directories for auto-generation
OPENCODE_DIR = PROJECT_ROOT / ".opencode/commands"
CURSOR_DIR = PROJECT_ROOT / ".cursor"
CURSORRULES_FILE = PROJECT_ROOT / ".cursorrules"
COPILOT_FILE = PROJECT_ROOT / ".github/copilot-instructions.md"
SYSTEM_PROMPT_FILE = PROJECT_ROOT / "docs/system_prompt.txt"

# ---------------------------------------------------------------------------
# Prompt Templates and Command Metadata
# ---------------------------------------------------------------------------
COMMANDS: Dict[str, Dict[str, Any]] = {
    "init": {
        "phase": 1,
        "description": "Profile raw data, classify domain/type, and map causal variables.",
        "template": (
            "Execute agents/01_initialize.md against all files in data_raw/ and docs_input/research_brief.md.\n"
            "Perform deep structural profiling of every file (MIME detection, missingness mechanism hypothesis "
            "using Little's MCAR test or pattern correlation matrices, outlier detection, relational integrity, "
            "temporal/spatial irregularity checks).\n"
            "Classify the data into a primary type code and secondary codes (TABULAR-CROSS, TABULAR-PANEL, "
            "TABULAR-SURVEY, TEXT-CORPUS, TIME-SERIES, SPATIAL, NETWORK, BIOMEDICAL, MIXED).\n"
            "Parse all research questions into a causal variable taxonomy (Y, T, W, M, E, Z).\n"
            "Produce a power analysis per RQ citing domain-specific effect size literature.\n"
            "Write docs_input/initial_epistemic_baseline.md with all sections complete.\n"
            "Halt and log ERROR if any required input is missing or malformed."
        ),
        "required_files": [BRIEF_FILE],
        "produced_files": [PROJECT_ROOT / "docs_input/initial_epistemic_baseline.md"]
    },
    "route": {
        "phase": 2,
        "description": "Select analytical methods and discover literature/packages.",
        "template": (
            "Execute agents/02_route_and_discover.md using docs_input/initial_epistemic_baseline.md as context.\n"
            "Consult the full extended internal routing table (covering causal inference, Bayesian, ML, NLP, "
            "survival, spatial, network, and biomedical analysis goals).\n"
            "Flag any RQ not matched by the registry. For flagged gaps, perform live web searches on Google Scholar, "
            "PubMed, arXiv, and PyPI to identify state-of-the-art methods (post-2018, peer-reviewed, DOI required, "
            "package with >=1,000 GitHub stars).\n"
            "For ALL RQs, search for 3–5 highly-cited comparable studies using similar methods on similar data.\n"
            "Write docs/papers_and_tools_cited.md with full selection rationale, DOIs, and dependency manifest."
        ),
        "required_files": [PROJECT_ROOT / "docs_input/initial_epistemic_baseline.md"],
        "produced_files": [PROJECT_ROOT / "docs/papers_and_tools_cited.md"]
    },
    "scaffold": {
        "phase": 3,
        "description": "Build directories, write validation script, and generate data dictionary.",
        "template": (
            "Execute agents/03_ingest_and_scaffold.md using docs_input/initial_epistemic_baseline.md and "
            "docs/papers_and_tools_cited.md as context.\n"
            "Build only the directories required for the classified data type (including subdirectories for text embeddings, "
            "spatial files, rasters, graph files, or normalized genomics data as applicable).\n"
            "Write scripts/01_validation.py implementing strict pandera schema validation; use polars or dask if file > 1 GB.\n"
            "Execute scripts/01_validation.py. Verify SHA-256 hashes of all ingested files.\n"
            "Write docs/data_dictionary.md with full causal role metadata and Table 1 (sample characteristics).\n"
            "Generate reports/figures/missingness_heatmap.png.\n"
            "Write environment/requirements.txt, environment/setup_env.sh, and per-directory READMEs."
        ),
        "required_files": [
            PROJECT_ROOT / "docs_input/initial_epistemic_baseline.md",
            PROJECT_ROOT / "docs/papers_and_tools_cited.md"
        ],
        "produced_files": [
            PROJECT_ROOT / "scripts/01_validation.py",
            PROJECT_ROOT / "docs/data_dictionary.md",
            PROJECT_ROOT / "environment/requirements.txt"
        ]
    },
    "analyze": {
        "phase": 4,
        "description": "Run transformations, assumption tests, modeling, and generate figures.",
        "template": (
            "Execute agents/04_execute_analysis.md for Phase {rq}.\n"
            "For each research question in scope:\n"
            "  1. Load and hash-verify data from data/02_processed/.\n"
            "  2. Apply domain-specific transformations (MICE imputation, embeddings, projections, features, normalization).\n"
            "  3. Run all required assumption and causal diagnostic checks per the estimator-specific table.\n"
            "  4. Log every result to docs/methods_log.md; pivot to robust alternatives if assumptions fail, citing DOIs.\n"
            "  5. Apply Benjamini-Hochberg FDR correction if >3 hypotheses are tested.\n"
            "  6. Compute effect sizes and CIs for all tests.\n"
            "  7. Generate domain-specific additional outputs (KM curves, LISA maps, topic coherence, factor loadings).\n"
            "  8. Generate publication-quality multi-panel figures (.pdf, .png, .html) with annotations and captions.\n"
            "  9. Save all raw results, markdown tables, and LaTeX tables to data/03_analytical/."
        ),
        "required_files": [
            PROJECT_ROOT / "docs/data_dictionary.md",
            PROJECT_ROOT / "docs/papers_and_tools_cited.md"
        ],
        "produced_files": [
            PROJECT_ROOT / "scripts/02_transformation.py",
            PROJECT_ROOT / "scripts/03_modeling.py",
            PROJECT_ROOT / "docs/methods_log.md"
        ]
    },
    "compile": {
        "phase": 5,
        "description": "Generate IMRAD paper findings, LaTeX/MD tables, and 5-tab interactive dashboard.",
        "template": (
            "Execute agents/05_compile_outputs.md using data/03_analytical/, reports/figures/, docs/methods_log.md, "
            "and docs/papers_and_tools_cited.md as context.\n"
            "Write reports/research_findings.md as a complete IMRAD academic paper (structured abstract, Introduction, "
            "Data and Measures, Analytical Strategy with pivot narrative, Results with p-FDR, CIs, effect sizes, "
            "Discussion, references).\n"
            "Generate domain-appropriate publication-grade tables in reports/tables/ as .md and booktabs .tex.\n"
            "Build the self-contained 5-tab interactive publication dashboard in reports/dashboards/analysis_app.py "
            "(Tab 1: Overview with badges, Tab 2: Explorer with correlation heatmap, Tab 3: Methodology with Mermaid flowchart "
            "and audit table, Tab 4: Results with diagnostics and effect size cards, Tab 5: Literature & APA citations).\n"
            "Ensure custom Plotly hover templates, download buttons, token-based styling, and single-command executable."
        ),
        "required_files": [
            PROJECT_ROOT / "docs/methods_log.md",
            PROJECT_ROOT / "docs/papers_and_tools_cited.md"
        ],
        "produced_files": [
            PROJECT_ROOT / "reports/research_findings.md",
            PROJECT_ROOT / "reports/dashboards/analysis_app.py"
        ]
    },
    "audit": {
        "phase": 6,
        "description": "Perform full cold-start reproducibility, causal leakage, and reporting compliance sweep.",
        "template": (
            "Execute agents/06_audit_and_validate.md.\n"
            "  1. Reset environment: delete __pycache__ and intermediate outputs.\n"
            "  2. Re-run setup_env.sh and verify package hashes against requirements.txt.\n"
            "  3. Execute full pipeline cold: scripts/01_validation.py -> 02_transformation.py -> 03_modeling.py.\n"
            "  4. Recompute and verify all SHA-256 hashes against docs/data_dictionary.md.\n"
            "  5. Check every methods_log.md PIVOT has code, outputs, and literature citations.\n"
            "  6. Scan scripts for target leakage (Outcome Y or Mediator M in feature matrices).\n"
            "  7. Scan report for causal claims without causal estimators.\n"
            "  8. Scan markdown for unformatted p-values, missing effect sizes, missing CIs, and colloquial phrases.\n"
            "  9. Verify all figures (.png, .html) and captions (_caption.txt) exist per RQ.\n"
            "  10. Verify docstring and type-hint coverage. Test dashboard startup.\n"
            "Write docs/validation_audit_report.md with all results and a Final Verdict of PASS or FAIL."
        ),
        "required_files": [
            PROJECT_ROOT / "reports/research_findings.md",
            PROJECT_ROOT / "reports/dashboards/analysis_app.py"
        ],
        "produced_files": [PROJECT_ROOT / "docs/validation_audit_report.md"]
    }
}

# ---------------------------------------------------------------------------
# State Management Helpers
# ---------------------------------------------------------------------------

def load_state() -> Dict[str, Any]:
    """Load current project state from the state file.

    Returns
    -------
    Dict[str, Any]
        Decoded state dictionary. If file is missing or corrupted, returns default template.
    """
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.warning("Could not read state file: %s. Re-initializing.", e)
    
    # Return default template
    return {
        "project_name": PROJECT_ROOT.name,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "phases": {cmd: "PENDING" for cmd in COMMANDS},
        "file_hashes": {},
        "active_rq_verdicts": {},
        "remediation_items": []
    }


def save_state(state: Dict[str, Any]) -> None:
    """Save the project state to the state file.

    Parameters
    ----------
    state : Dict[str, Any]
        The state dictionary to write.
    """
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logging.error("Failed to write state file: %s", e)


def sha256_file(path: Path) -> Optional[str]:
    """Compute SHA-256 hash of a file.

    Parameters
    ----------
    path : Path
        Absolute path to the target file.

    Returns
    -------
    Optional[str]
        SHA-256 hex digest, or None if the file does not exist.
    """
    if not path.exists():
        return None
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        logging.error("Failed to compute hash for %s: %s", path, e)
        return None

# ---------------------------------------------------------------------------
# CLI Command Implementations
# ---------------------------------------------------------------------------

def cmd_status() -> None:
    """Read project files and print a detailed status report to stdout."""
    state = load_state()
    
    # Scan filesystem to dynamically check completions
    completed_count = 0
    phase_status = {}
    
    for cmd, meta in COMMANDS.items():
        all_required_present = all(p.exists() for p in meta["required_files"])
        all_produced_present = all(p.exists() for p in meta["produced_files"])
        
        if all_produced_present:
            status = "COMPLETE"
            completed_count += 1
        elif all_required_present:
            status = "READY"
        else:
            status = "PENDING"
            
        phase_status[cmd] = status
        state["phases"][cmd] = status
        
    save_state(state)
    
    # Print status report
    print("=====================================================================")
    print("               RESEARCH CO-PILOT PIPELINE STATUS                     ")
    print("=====================================================================")
    print(f"Project Workspace: {PROJECT_ROOT.name}")
    print(f"Last Evaluation:   {state['last_updated']}")
    print("---------------------------------------------------------------------")
    print(f"{'Phase / Command':<22} | {'Phase #':<8} | {'Status':<10} | {'Description'}")
    print("---------------------------------------------------------------------")
    
    for cmd, meta in COMMANDS.items():
        p_num = f"Phase {meta['phase']}"
        status = phase_status[cmd]
        desc = meta["description"]
        print(f"/{cmd:<21} | {p_num:<8} | {status:<10} | {desc}")
        
    print("---------------------------------------------------------------------")
    
    # Check next recommended action
    next_action = None
    for cmd in ["init", "route", "scaffold", "analyze", "compile", "audit"]:
        if phase_status[cmd] in ["READY", "PENDING"]:
            next_action = f"/{cmd}"
            break
            
    if completed_count == len(COMMANDS):
        print("Pipeline Status: ALL PHASES COMPLETE. Run /audit to re-verify at any time.")
    elif next_action:
        print(f"Recommended Next Step: {next_action}")
    else:
        print("Pipeline Status: Check configuration. Some phases are in a blocked state.")
    print("=====================================================================")


def cmd_prompt(command_name: str, rq_arg: str = "all") -> None:
    """Hydrate and output the full system instructions and prompt for a command.

    Parameters
    ----------
    command_name : str
        The name of the target command (e.g. 'init', 'route').
    rq_arg : str, optional
        Research Question selector passed to the analyze command, by default "all".

    Raises
    ------
    ValueError
        If the specified command_name is invalid.
    """
    if command_name not in COMMANDS:
        print(f"Error: Unknown command '{command_name}'.", file=sys.stderr)
        sys.exit(1)
        
    meta = COMMANDS[command_name]
    
    # Read Guardrails
    guardrails_content = ""
    if GUARDRAILS_FILE.exists():
        try:
            with open(GUARDRAILS_FILE, "r") as f:
                guardrails_content = f.read()
        except Exception as e:
            logging.warning("Could not read guardrails file: %s", e)
            
    # Hydrate prompt template
    prompt_template = meta["template"]
    if command_name == "analyze":
        prompt_template = prompt_template.format(rq=rq_arg)
        
    # Append relevant baseline/dictionary context if files exist
    context_str = ""
    baseline_file = PROJECT_ROOT / "docs_input/initial_epistemic_baseline.md"
    dict_file = PROJECT_ROOT / "docs/data_dictionary.md"
    papers_file = PROJECT_ROOT / "docs/papers_and_tools_cited.md"
    methods_log_file = PROJECT_ROOT / "docs/methods_log.md"
    
    if command_name != "init":
        context_str += "\n\n--- CURRENT ENVIRONMENT CONTEXT ---\n"
        if baseline_file.exists():
            context_str += f"\n[Epistemic Baseline loaded from {baseline_file.name}]\n"
        if dict_file.exists():
            context_str += f"\n[Data Dictionary loaded from {dict_file.name}]\n"
        if papers_file.exists():
            context_str += f"\n[Supporting Literature & Tools loaded from {papers_file.name}]\n"
        if methods_log_file.exists():
            context_str += f"\n[Methods Log loaded from {methods_log_file.name}]\n"
            
    # Output unified hydrated prompt
    print("# SYSTEM COMPLIANCE LAYER")
    print(guardrails_content)
    print("\n# EXECUTION TASK INSTRUCTION")
    print(prompt_template)
    print(context_str)


def cmd_sync() -> None:
    """Sync all client configurations (OpenCode, Cursor, Copilot) from this runner."""
    logging.info("Starting synchronization of all client-specific configs...")
    
    # 1. OpenCode / Antigravity Custom Commands
    OPENCODE_DIR.mkdir(parents=True, exist_ok=True)
    for cmd, meta in COMMANDS.items():
        cmd_file = OPENCODE_DIR / f"research-{cmd}.md"
        rq_placeholder = " $ARGUMENTS" if cmd == "analyze" else ""
        content = (
            "---\n"
            f"description: {meta['description']}\n"
            "---\n\n"
            f"Load agents/00_core_guardrails.md. Execute agents/{meta['phase']:02d}_"
            f"{'initialize' if cmd=='init' else 'route_and_discover' if cmd=='route' else 'ingest_and_scaffold' if cmd=='scaffold' else 'execute_analysis' if cmd=='analyze' else 'compile_outputs' if cmd=='compile' else 'audit_and_validate'}.md"
            f" using python scripts/research_runner.py prompt {cmd}{rq_placeholder} as instruction reference.\n"
        )
        with open(cmd_file, "w") as f:
            f.write(content)
        logging.info("  Synced: %s", cmd_file.relative_to(PROJECT_ROOT))
        
    # Sync status and pivot commands to OpenCode
    status_content = (
        "---\ndescription: Show current project pipeline completion and recommendations\n---\n\n"
        "Run terminal command: python scripts/research_runner.py status\n"
    )
    with open(OPENCODE_DIR / "research-status.md", "w") as f:
        f.write(status_content)
        
    pivot_content = (
        "---\ndescription: Manually record an assumption failure and re-execute affected RQ\n---\n\n"
        "Run terminal command: python scripts/research_runner.py pivot $ARGUMENTS\n"
    )
    with open(OPENCODE_DIR / "research-pivot.md", "w") as f:
        f.write(pivot_content)
        
    # 2. Cursor Rules (`.cursorrules` & `.cursor/rules/`)
    CURSOR_DIR.mkdir(parents=True, exist_ok=True)
    cursor_rules_content = (
        "# Cursor Research Co-Pilot Custom Instructions\n\n"
        "This project is governed by a strict, multi-phase agentic architecture. "
        "Before editing or writing any code, follow these principles:\n\n"
        "1. Load `agents/00_core_guardrails.md` into your execution context.\n"
        "2. To run any phase, generate the prompt by running `python scripts/research_runner.py prompt <cmd>`.\n\n"
        "Available Phases:\n"
    )
    for cmd, meta in COMMANDS.items():
        cursor_rules_content += f"- Phase {meta['phase']} (/{cmd}): {meta['description']}\n"
        
    # Write to root .cursorrules and cursor folder instruction
    with open(CURSORRULES_FILE, "w") as f:
        f.write(cursor_rules_content)
    logging.info("  Synced: .cursorrules")
    
    with open(CURSOR_DIR / "CURSOR_INSTRUCTIONS.md", "w") as f:
        f.write(cursor_rules_content)
    logging.info("  Synced: .cursor/CURSOR_INSTRUCTIONS.md")
    
    # 3. GitHub Copilot Instructions
    COPILOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    copilot_content = (
        "# GitHub Copilot Work Space Instructions\n\n"
        "This workspace implements a formal statistical research pipeline. All agents must follow the "
        "Universal compliance layer in `agents/00_core_guardrails.md`.\n\n"
        "Use `@workspace` with the runner CLI tool to generate prompts and inspect state:\n"
        "- Show status: `python scripts/research_runner.py status`\n"
        "- Generate Prompt: `python scripts/research_runner.py prompt <init|route|scaffold|analyze|compile|audit>`\n"
    )
    with open(COPILOT_FILE, "w") as f:
        f.write(copilot_content)
    logging.info("  Synced: %s", COPILOT_FILE.relative_to(PROJECT_ROOT))
    
    # 4. System Prompt Document
    SYSTEM_PROMPT_FILE.parent.mkdir(parents=True, exist_ok=True)
    system_prompt = (
        "# UNIVERSAL AGENTIC SYSTEM PROMPT\n\n"
        "You are operating within an automated, publication-ready research pipeline.\n"
        "Before performing any actions, always execute: python scripts/research_runner.py status\n\n"
        "To obtain instructions for any phase, run: python scripts/research_runner.py prompt <phase>\n"
    )
    with open(SYSTEM_PROMPT_FILE, "w") as f:
        f.write(system_prompt)
    logging.info("  Synced: %s", SYSTEM_PROMPT_FILE.relative_to(PROJECT_ROOT))
    
    print("Synchronization complete. All client tools are aligned with research_runner.py.")


def cmd_install() -> None:
    """Install global CLI wrapper and Antigravity skills."""
    logging.info("Installing global 'research' CLI wrapper...")
    
    # 1. Install global wrapper script to ~/.local/bin/research
    bin_dir = Path.home() / ".local/bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper_path = bin_dir / "research"
    
    wrapper_content = (
        "#!/usr/bin/env bash\n"
        "# Global wrapper for the Research Co-Pilot\n\n"
        "DIR=\"$(pwd)\"\n"
        "while [ \"$DIR\" != \"\" ] && [ \"$DIR\" != \"/\" ]; do\n"
        "    if [ -f \"$DIR/scripts/research_runner.py\" ]; then\n"
        "        python3 \"$DIR/scripts/research_runner.py\" \"$@\"\n"
        "        exit $?\n"
        "    fi\n"
        "    DIR=\"$(dirname \"$DIR\")\"\n"
        "done\n\n"
        "echo \"Error: Not inside a Research Co-Pilot project workspace (scripts/research_runner.py not found in parent directories).\" >&2\n"
        "exit 1\n"
    )
    
    try:
        with open(wrapper_path, "w") as f:
            f.write(wrapper_content)
        wrapper_path.chmod(0o755)
        logging.info("  Installed CLI wrapper at: %s", wrapper_path)
    except Exception as e:
        logging.error("Failed to install CLI wrapper: %s", e)
        
    # 2. Install Antigravity Skills
    skills_dir = Path.home() / ".gemini/antigravity/skills"
    if skills_dir.exists():
        logging.info("Installing Antigravity global skills under %s...", skills_dir)
        
        # We install research-init, research-route, research-scaffold, research-analyze, research-compile, research-audit, research-status, research-pivot
        all_skill_commands = list(COMMANDS.keys()) + ["status", "pivot"]
        
        for cmd in all_skill_commands:
            skill_folder = skills_dir / f"research-{cmd}"
            skill_folder.mkdir(parents=True, exist_ok=True)
            skill_file = skill_folder / "SKILL.md"
            
            # Formulate the YAML metadata and XML tags
            if cmd in COMMANDS:
                meta = COMMANDS[cmd]
                description = meta["description"]
                objective = f"Execute Phase {meta['phase']} ({cmd}) of the Research Co-Pilot pipeline."
                process = (
                    f"Run the terminal command: python3 scripts/research_runner.py prompt {cmd}\n"
                    f"This prints the fully hydrated system guardrails and phase instructions.\n"
                    f"Read that output in full, then execute the task as specified."
                )
            elif cmd == "status":
                description = "Check project pipeline completion status and recommended next steps."
                objective = "Print current status of research co-pilot pipeline steps."
                process = "Run the terminal command: python3 scripts/research_runner.py status"
            else:  # pivot
                description = "Log a statistical assumption pivot to the methods log."
                objective = "Log statistical pivot for failed assumptions."
                process = "Run the terminal command: python3 scripts/research_runner.py pivot $ARGUMENTS"
                
            skill_content = (
                f"---\n"
                f"name: research-{cmd}\n"
                f"description: {description}\n"
                f"---\n\n"
                f"<objective>\n{objective}\n</objective>\n\n"
                f"<process>\n{process}\n</process>\n"
            )
            
            try:
                with open(skill_file, "w") as f:
                    f.write(skill_content)
                logging.info("  Registered Antigravity Skill: research-%s", cmd)
            except Exception as e:
                logging.error("Failed to write skill file for research-%s: %s", cmd, e)
                
        print("Global installation complete! Run 'research status' or use '/research-*' slash commands in Antigravity.")
    else:
        logging.warning("Antigravity app directory not found. Standard global CLI wrapper was installed successfully.")


def cmd_pivot(rq: int, assumption: str, alternative: str) -> None:
    """Manually log a statistical assumption pivot to the methods log.

    Parameters
    ----------
    rq : int
        Research Question number.
    assumption : str
        The statistical assumption that failed (e.g. 'normality').
    alternative : str
        The selected robust alternative (e.g. 'mannwhitneyu').
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = (
        f"---\n"
        f"Timestamp: {timestamp}\n"
        f"Agent: research_runner.py\n"
        f"Research Question: RQ{rq}\n"
        f"Phase: pivot\n"
        f"Test Conducted: Assumption Check\n"
        f"Statistic: N/A\n"
        f"Decision: PIVOT\n"
        f"If PIVOT:\n"
        f"  Failed assumption: {assumption}\n"
        f"  Failure statistic: N/A\n"
        f"  Alternative selected: {alternative}\n"
        f"  Rationale: Manually logged pivot via runner CLI.\n"
        f"  Causal validity maintained: YES\n"
        f"---\n"
    )
    log_methods_log(entry)
    print(f"Pivot successfully logged for RQ{rq} ({assumption} -> {alternative}).")

# ---------------------------------------------------------------------------
# Main CLI Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse arguments and route execution to the appropriate command handler."""
    parser = argparse.ArgumentParser(
        description="Unified State and Command Runner for the Research Co-Pilot."
    )
    subparsers = parser.add_subparsers(dest="command", help="Orchestrator commands")
    
    # status command
    subparsers.add_parser("status", help="Print pipeline status and recommendations")
    
    # prompt command
    prompt_parser = subparsers.add_parser("prompt", help="Get hydrated prompt for any phase")
    prompt_parser.add_argument(
        "phase",
        choices=["init", "route", "scaffold", "analyze", "compile", "audit"],
        help="Target phase name"
    )
    prompt_parser.add_argument(
        "--rq",
        default="all",
        help="Research Question selector (for analyze phase, default: all)"
    )
    
    # sync command
    subparsers.add_parser("sync", help="Synchronize all client configurations (Cursor, OpenCode, Copilot)")
    
    # install command
    subparsers.add_parser("install", help="Install global CLI wrapper and Antigravity skills")
    
    # pivot command
    pivot_parser = subparsers.add_parser("pivot", help="Manually log an assumption check pivot")
    pivot_parser.add_argument("--rq", type=int, required=True, help="Research question number")
    pivot_parser.add_argument("--assumption", required=True, help="Failed assumption name")
    pivot_parser.add_argument("--alternative", required=True, help="Alternative method selected")
    
    args = parser.parse_args()
    
    if args.command == "status":
        cmd_status()
    elif args.command == "prompt":
        cmd_prompt(args.phase, args.rq)
    elif args.command == "sync":
        cmd_sync()
    elif args.command == "install":
        cmd_install()
    elif args.command == "pivot":
        cmd_pivot(args.rq, args.assumption, args.alternative)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
