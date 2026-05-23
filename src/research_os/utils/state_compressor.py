"""State compression utilities for Research OS.

Builds a deterministic sliding context window from the persisted ledger and
execution DAG. The compressor keeps the project brief plus the most recent
completed node outputs without invoking an LLM.
"""

import json
from pathlib import Path
from typing import Any, Optional

from research_os.runtime.hooks import hook_engine
from research_os.utils.common import find_project_root


_HEAD_CHARS = 250
_TAIL_CHARS = 250
_TRUNCATION_MARKER = "\n...[DATA TRUNCATED]...\n"


def _project_root() -> Path:
    return find_project_root()


def _state_path(root: Optional[Path] = None) -> Path:
    root = root or _project_root()
    return root / "03_synthesis" / "state_ledger.json"


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with open(path) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return ""


def _resolve_project_brief(state: dict[str, Any], root: Path) -> dict[str, str]:
    brief = state.get("project_brief")
    if isinstance(brief, dict):
        content = brief.get("content") or brief.get("text") or ""
        path_value = brief.get("path") or brief.get("file") or ""
        if path_value:
            brief_path = Path(path_value)
            if not brief_path.is_absolute():
                brief_path = root / brief_path
            if brief_path.exists() and not content:
                content = _read_text(brief_path)
            return {"path": str(brief_path), "content": content}
        if content:
            return {"path": "", "content": str(content)}
    elif isinstance(brief, str) and brief.strip():
        brief_path = Path(brief)
        if not brief_path.is_absolute():
            brief_path = root / brief_path
        if brief_path.exists():
            return {"path": str(brief_path), "content": _read_text(brief_path)}
        return {"path": "", "content": brief}

    for candidate in (
        root / "project_brief.md",
        root / "03_synthesis" / "project_brief.md",
        root / "inputs" / "project_brief.md",
        root / "docs" / "project_brief.md",
        root / "context" / "project_brief.md",
    ):
        if candidate.exists():
            return {"path": str(candidate), "content": _read_text(candidate)}

    project_name = state.get("project", "")
    return {"path": "", "content": str(project_name) if project_name else ""}


def _node_output(node: dict[str, Any], root: Path) -> str:
    for key in ("output", "stdout", "raw_output", "result", "summary", "last_output"):
        value = node.get(key)
        if isinstance(value, str) and value.strip():
            return value
        if isinstance(value, (dict, list)) and value:
            return json.dumps(value, indent=2, default=str)

    outputs: list[str] = []
    for file_name in node.get("output_files", []) or []:
        file_path = Path(file_name)
        if not file_path.is_absolute():
            file_path = root / file_path
        if file_path.exists() and file_path.is_file():
            outputs.append(f"FILE: {file_name}\n{_read_text(file_path)}")

    return "\n\n".join(outputs)


def _completed_nodes(
    state: dict[str, Any], root: Path, limit: int = 5
) -> list[dict[str, Any]]:
    dag_path = state.get("execution_dag_path")
    if dag_path:
        candidate = Path(dag_path)
        if not candidate.is_absolute():
            candidate = root / candidate
    else:
        candidate = root / ".os_state" / "cache" / "execution_dag.json"

    dag = _load_json(candidate)
    nodes = dag.get("nodes", {}) if isinstance(dag, dict) else {}
    if not isinstance(nodes, dict):
        return []

    completed = [
        node
        for node in nodes.values()
        if str(node.get("status", "")).lower() in {"complete", "completed"}
    ]
    completed.sort(key=lambda node: node.get("timestamp", ""))

    recent: list[dict[str, Any]] = []
    for node in completed[-limit:]:
        recent.append(
            {
                "node_id": str(node.get("node_id", "")),
                "timestamp": node.get("timestamp", ""),
                "output": compress_output_heuristic(_node_output(node, root)),
            }
        )
    return recent


def build_sliding_context_window(
    root: Optional[Path] = None, limit: int = 5
) -> dict[str, Any]:
    root = root or _project_root()
    state = _load_json(_state_path(root))
    return {
        "project_brief": _resolve_project_brief(state, root),
        "completed_nodes": _completed_nodes(state, root, limit=limit),
    }


def compress_output_heuristic(text: str, max_chars: int = 500) -> str:
    """Deterministic head/tail compressor for node output text.

    Preserves the first *head* characters (command invocation, shapes, early
    diagnostics) and the last *tail* characters (final metric, result, or
    traceback), separated by a truncation marker.  No LLM required.

    Args:
        text:      Raw output string from a DAG node.
        max_chars: Total character budget.  Defaults to 500 (250 head + 250
                   tail).  Must be >= 10.

    Returns:
        Compressed string ≤ max_chars + len(marker) characters, or the
        original string unchanged if it already fits.
    """
    if len(text) <= max_chars:
        return text

    head = max_chars // 2
    tail = max_chars - head

    head_part = text[:head].rstrip()
    tail_part = text[-tail:].lstrip()

    return head_part + _TRUNCATION_MARKER + tail_part


# ---------------------------------------------------------------------------
# Legacy alias kept for any callers that used compress_output() directly.
# ---------------------------------------------------------------------------
def compress_output(output_text: str) -> str:
    """Backwards-compatible wrapper around compress_output_heuristic."""
    return compress_output_heuristic(output_text)


@hook_engine.register("post_execution")
def compress_state_hook(state: dict, **kwargs) -> dict:
    """Post-execution hook: cache the deterministic sliding context window."""
    root = _project_root()
    window = build_sliding_context_window(root=root, limit=5)
    state["sliding_context_window"] = window
    state["project_brief"] = window.get("project_brief", {})
    state["recent_completed_nodes"] = window.get("completed_nodes", [])

    return state
