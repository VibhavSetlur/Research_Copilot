#!/usr/bin/env python3
"""Session Restorer — generates context restoration prompts for new conversations.

CLI usage:
    rcp restore
    python session_restorer.py

Programmatic usage:
    from research_os.utils.session_restorer import get_restoration_prompt
    prompt = get_restoration_prompt(root)
    print(prompt)
"""

import sys
from pathlib import Path
from typing import Optional

from research_os.utils.common import (
    find_project_root,
    load_json_safe,
    now_iso,
)


def _read_text(path: Path) -> str:
    """Read text file, return content or empty string."""
    try:
        return path.read_text().strip()
    except (OSError, FileNotFoundError):
        return ""


def _truncate(text: str, max_words: int = 50) -> str:
    """Truncate text to max_words at sentence boundary."""
    words = text.split()
    if len(words) <= max_words:
        return text
    truncated = " ".join(words[:max_words])
    for sep in (". ", "! ", "? "):
        idx = truncated.rfind(sep)
        if idx > 0:
            return truncated[: idx + 1] + "..."
    return truncated + "..."


def _format_checkpoints(checkpoints: dict) -> str:
    """Format phase checkpoints as a compact list."""
    if not checkpoints:
        return "  (no phases completed)"
    lines = []
    for phase, status in checkpoints.items():
        marker = "[x]" if status == "complete" else "[ ]"
        lines.append(f"  {marker} {phase}: {status}")
    return "\n".join(lines)


def _format_decisions(state: dict, n: int = 3) -> str:
    """Extract last N decisions from state."""
    decisions = state.get("decisions", [])
    if not decisions:
        return "  (no decisions recorded)"
    last = decisions[-n:]
    lines = []
    for i, d in enumerate(last, 1):
        if isinstance(d, dict):
            desc = d.get("decision", d.get("description", str(d)))
            lines.append(f"  {i}. {desc}")
        else:
            lines.append(f"  {i}. {d}")
    return "\n".join(lines)


def _format_dead_ends(dead_ends: list, n: int = 5) -> str:
    """Format dead ends to avoid."""
    if not dead_ends:
        return "  (none — all clear)"
    last = dead_ends[-n:]
    return "\n".join(f"  - {e}" for e in last)


def _format_findings(state: dict) -> str:
    """Extract key findings from state."""
    findings = state.get("key_findings", [])
    if not findings:
        return "  (no findings yet)"
    if isinstance(findings, list):
        last = findings[-3:]
        return "\n".join(f"  - {f}" for f in last)
    if isinstance(findings, str):
        return f"  {_truncate(findings, 30)}"
    return "  (findings in unexpected format)"


def _format_ctm_summary(root: Path) -> str:
    """Summarize the latest CTM if one exists."""
    ctm_dir = root / ".os_state" / "cache" / "context_transfer_memos"
    if not ctm_dir.exists():
        return "  (no CTMs)"

    ctms = sorted(ctm_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not ctms:
        return "  (no CTMs)"

    latest = load_json_safe(ctms[-1])
    goals = latest.get("immediate_goals", [])
    questions = latest.get("open_questions", [])

    lines = ["  Latest CTM:"]
    if goals:
        lines.append(f"    Immediate goals: {'; '.join(goals[:3])}")
    if questions:
        lines.append(f"    Open questions: {'; '.join(questions[:3])}")
    if not goals and not questions:
        lines.append(f"    Phase: {latest.get('phase', 'unknown')}")

    return "\n".join(lines)


def _determine_next_agent(state: dict) -> str:
    """Determine which agent should run next based on current phase."""
    state.get("phase", "research_init")
    checkpoints = state.get("checkpoints", {})

    pipeline = [
        "research_init",
        "literature_deep",
        "method_route",
        "generate_preregistration",
        "data_scaffold",
        "execute_analysis",
        "replication_validator",
        "compile_outputs",
        "reviewer2_critic",
        "audit_validate",
    ]

    completed = {p for p, s in checkpoints.items() if s == "complete"}
    for agent in pipeline:
        if agent not in completed:
            return agent

    return "research_iterate"


def get_restoration_prompt(root: Optional[Path] = None, max_tokens: int = 800) -> str:
    """Generate a context restoration prompt pre-filled with current project state.

    Args:
        root: Project root path (auto-detected if None)
        max_tokens: Approximate token limit for the output

    Returns:
        Formatted restoration prompt string
    """
    if root is None:
        root = find_project_root()
        if root is None:
            return "ERROR: Not in a Research OS workspace. Run `rcp init` first."

    state_path = root / "03_synthesis" / "state_ledger.json"
    cache_path = root / ".os_state" / "cache" / "state.json"

    state = load_json_safe(state_path)
    if not state:
        state = load_json_safe(cache_path)
    if not state:
        return "ERROR: No state found. Project has not been initialized. Run `rcp init` first."

    budget = state.get("token_budget", {})
    paths = state.get("paths", {})
    active_path = state.get("current_path", "main")
    path_info = paths.get(active_path, {})
    experiment_dir = path_info.get(
        "experiment_dir", "workspace"
    )

    prompt_parts = [
        "# Context Restoration — Research OS",
        "",
        "You are resuming a Research OS project. Here is the current state:",
        "",
        "### Project Overview",
        f"- **Project**: {state.get('project', 'unnamed')}",
        f"- **Current Phase**: {state.get('phase', 'unknown')} (step {state.get('step', 0)})",
        f"- **Active Path**: {active_path}",
        f"- **Last Updated**: {state.get('updated_at', 'unknown')}",
        "",
        "### Phase Progress",
        _format_checkpoints(state.get("checkpoints", {})),
        "",
        "### Last 3 Decisions",
        _format_decisions(state),
        "",
        "### Key Findings So Far",
        _format_findings(state),
        "",
        "### Dead Ends to Avoid",
        _format_dead_ends(state.get("dead_ends", [])),
        "",
        "### CTM Summary",
        _format_ctm_summary(root),
        "",
        "---",
        "",
        "## Instructions",
        "",
        "1. Read `.os_state/cache/state.json` for the full structured state",
        "2. Read the latest CTM from `.os_state/cache/context_transfer_memos/` if one exists",
        "3. Read `03_synthesis/state_ledger.json` for the global ledger",
        "4. Load only the skill needed for the next action — do NOT load all skills",
        "5. Continue from the phase indicated above",
        "6. If a CTM exists, read its `immediate_goals` and `open_questions` first",
        "7. Do NOT repeat completed phases unless explicitly asked",
        "",
        "## Quick Reference",
        "",
        f"- **Next agent to run**: {_determine_next_agent(state)}",
        f"- **Current experiment directory**: {experiment_dir}",
        f"- **Token budget**: {budget.get('used', 0):,} / {budget.get('limit', 200000):,} used",
        f"- **Resumable from**: {state.get('resumable_from', 'none')}",
        "",
        "---",
        f"Generated: {now_iso()}",
    ]

    prompt = "\n".join(prompt_parts)

    rough_tokens = len(prompt.split())
    if rough_tokens > max_tokens:
        prompt = _truncate(prompt, max_tokens * 0.75)

    return prompt


def main():
    """CLI entry point for `rcp restore`."""
    root = find_project_root()
    if root is None:
        print("ERROR: Not in a Research OS workspace.")
        print("Run `rcp init` first, or navigate to a project directory.")
        sys.exit(1)

    prompt = get_restoration_prompt(root)
    print(prompt)
    print()
    print("---")
    print("Copy the text above and paste it at the start of a new conversation.")


if __name__ == "__main__":
    main()
