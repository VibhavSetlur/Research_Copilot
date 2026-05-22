#!/usr/bin/env python3
"""Project Snapshot — compact restore payload for new conversations.

CLI usage:
    rcp snapshot
    python project_snapshot.py

Programmatic usage:
    from research_copilot.utils.project_snapshot import get_snapshot
    payload = get_snapshot(root, max_tokens=800)
"""

import json
from pathlib import Path
from typing import Optional

from research_copilot.utils.common import (
    find_project_root,
    load_json_safe,
    load_text_safe,
)


def compress_to_tokens(text: str, max_tokens: int = 400) -> str:
    """Truncate text at sentence boundary to fit within max_tokens.

    Args:
        text: Input text to compress
        max_tokens: Approximate token limit (1 token ≈ 1 word for English)

    Returns:
        Truncated text ending at sentence boundary
    """
    words = text.split()
    if len(words) <= max_tokens:
        return text

    truncated = " ".join(words[:max_tokens])
    for sep in (". ", "! ", "? ", "\n"):
        idx = truncated.rfind(sep)
        if idx > 0:
            return truncated[: idx + 1]
    return truncated + "..."


def get_snapshot(root: Optional[Path] = None, max_tokens: int = 800) -> str:
    """Generate a compact project snapshot for conversation restoration.

    Reads state + manifest + last 3 iteration files + key_findings and returns
    a compact JSON string. Used by session_restorer.py and new_chat_handoff.

    Args:
        root: Project root path (auto-detected if None)
        max_tokens: Approximate token limit for the output

    Returns:
        Compact JSON string with project state
    """
    if root is None:
        root = find_project_root()
        if root is None:
            return json.dumps({"error": "Not in a Research Copilot workspace"})

    # Read state ledger
    state = load_json_safe(root / "03_synthesis" / "state_ledger.json")
    if not state:
        state = load_json_safe(root / ".research" / "cache" / "state.json")

    # Read manifest
    manifest = load_json_safe(root / "03_synthesis" / "manifest.json")

    # Read last 3 iteration files
    iterations_dir = root / "docs" / "iterations"
    iteration_summaries = []
    if iterations_dir.exists():
        registry = load_json_safe(iterations_dir / "registry.json")
        iters = registry.get("iterations", [])[-3:]
        for it in iters:
            iteration_summaries.append({
                "id": it.get("id"),
                "type": it.get("type"),
                "summary": compress_to_tokens(it.get("summary", ""), 50),
                "decision": it.get("decision"),
            })

    # Read key findings
    key_findings = load_text_safe(root / "03_synthesis" / "key_findings.md")
    key_findings = compress_to_tokens(key_findings, 200)

    # Build snapshot
    snapshot = {
        "project": state.get("project", "unnamed"),
        "phase": state.get("phase", "unknown"),
        "step": state.get("step", 0),
        "branch": state.get("current_branch", state.get("active_branch", "main")),
        "checkpoints": state.get("checkpoints", {}),
        "dead_ends": state.get("dead_ends", [])[-5:],
        "resumable_from": state.get("resumable_from"),
        "token_budget": state.get("token_budget", {}),
        "iterations": iteration_summaries,
        "key_findings": key_findings,
        "manifest_structure": manifest.get("structure", []) if manifest else [],
    }

    result = json.dumps(snapshot, indent=2, default=str)
    # Compress if over limit
    words = result.split()
    if len(words) > max_tokens:
        result = compress_to_tokens(result, max_tokens)

    return result


def main():
    """CLI entry point for `rcp snapshot`."""
    root = find_project_root()
    if root is None:
        print("ERROR: Not in a Research Copilot workspace.")
        return

    snapshot = get_snapshot(root)
    print(snapshot)


if __name__ == "__main__":
    main()
