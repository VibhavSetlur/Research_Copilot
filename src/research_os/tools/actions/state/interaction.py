"""Researcher-facing notifications and session handoff."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from research_os.project_ops import load_state, now_iso

logger = logging.getLogger("research_os.tools.interaction")


def notify_researcher(message: str, level: str, root: Path) -> dict[str, Any]:
    """Log a notification under ``workspace/logs/notifications.log``."""
    try:
        log_path = root / "workspace" / "logs" / "notifications.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{now_iso()}] [{level.upper()}] {message}\n")
        return {"status": "success", "message": "Notification logged."}
    except Exception as e:
        logger.error(f"Notify failed: {e}")
        return {"status": "error", "message": str(e)}


def session_handoff(root: Path) -> dict[str, Any]:
    """Generate a structured markdown handoff and a resume prompt."""
    try:
        from research_os.tools.actions.state.path import list_paths

        state = load_state(root)
        paths_data = list_paths(root)
        paths = paths_data.get("paths", []) or []
        active_path = next((p for p in paths if p["status"] == "active"), None)

        analysis_tail = ""
        analysis_md = root / "workspace" / "analysis.md"
        if analysis_md.exists():
            lines = analysis_md.read_text().splitlines()
            analysis_tail = "\n".join(lines[-20:])

        pending: list[str] = []
        if active_path:
            scripts_dir = root / "workspace" / active_path["path_id"] / "scripts"
            if scripts_dir.exists():
                pending = [f.name for f in scripts_dir.iterdir() if f.is_file()]

        from research_os.tools.actions.protocol import get_next_protocol

        next_info = get_next_protocol(root)

        project_name = state.get("project_name") or state.get("project", "Research Project")
        current_path = state.get("current_path", "main")
        pipeline_stage = state.get("pipeline_stage", state.get("phase", "init"))

        content = (
            f"# Session Handoff — {project_name}\n"
            f"Generated: {now_iso()}\n\n"
            f"## State\n"
            f"- Current path: `{current_path}`\n"
            f"- Pipeline stage: `{pipeline_stage}`\n"
            f"- Paths: {', '.join(p['path_id'] for p in paths) if paths else 'none'}\n"
            f"- Next protocol: `{next_info.get('next_protocol') or '(pipeline complete)'}`\n\n"
            f"## Recent analysis log (tail)\n```\n{analysis_tail or '(empty)'}\n```\n\n"
            f"## Pending scripts in active path\n"
            + ("\n".join(f"- `{f}`" for f in pending) if pending else "- (none)")
            + "\n\n"
            f"## Resume prompt\n"
            f"Paste this into a fresh chat with the same MCP workspace attached:\n\n"
            f"> I'm resuming Research OS project **{project_name}**.\n"
            f"> Active path: `{current_path}` · stage: `{pipeline_stage}`.\n"
            f"> Run `sys_protocol_get(\"guidance/session_boot\")` first, then `sys_protocol_next`, then continue.\n"
        )

        handoff_path = (
            root / ".os_state" / "handoffs" / f"handoff_{now_iso()[:19].replace(':', '-')}.md"
        )
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        handoff_path.write_text(content)
        return {
            "status": "success",
            "handoff_path": str(handoff_path.relative_to(root)),
            "content": content,
        }
    except Exception as e:
        logger.exception("session_handoff failed")
        return {"status": "error", "message": str(e)}
