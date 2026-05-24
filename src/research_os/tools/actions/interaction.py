import logging
from typing import Dict, Any
from pathlib import Path
from research_os.project_ops import now_iso, load_state

logger = logging.getLogger("research.tools.interaction")


def notify_researcher(message: str, level: str, root: Path) -> Dict[str, Any]:
    try:
        log_path = root / "workspace" / "logs" / "notifications.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{now_iso()}] [{level.upper()}] {message}\n")
        return {"status": "success", "message": "Notification logged."}
    except Exception as e:
        logger.error(f"Notify failed: {e}")
        return {"status": "error", "message": str(e)}


def checkpoint_pending(
    description: str, requires_approval: bool, root: Path
) -> Dict[str, Any]:
    try:
        pending_path = root / ".os_state" / "pending_approval.txt"
        pending_path.parent.mkdir(parents=True, exist_ok=True)
        pending_path.write_text(description)
        return {
            "status": "pending_approval",
            "message": "Awaiting researcher approval via sys.checkpoint.approve",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def checkpoint_approve(root: Path) -> Dict[str, Any]:
    try:
        pending_path = root / ".os_state" / "pending_approval.txt"
        if pending_path.exists():
            pending_path.unlink()
            return {"status": "success", "message": "Action approved."}
        return {"status": "error", "message": "No pending action found."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def session_handoff(
    root: Path,
    state: Dict[str, Any] = None,
    last_step: str = "",
    last_writing_task: str = "",
    next_writing_task: str = "",
    next_protocol: str = "",
    completed_summary: str = "",
    specific_next_action: str = ""
) -> Dict[str, Any]:
    try:
        from research_os.tools.actions.path import list_paths
        state = load_state(root)
        paths_data = list_paths(root)
        paths = paths_data.get("paths", [])
        active_path = next((p for p in paths if p["status"] == "active"), None)

        analysis_tail = ""
        analysis_md = root / "workspace" / "analysis.md"
        if analysis_md.exists():
            lines = analysis_md.read_text().splitlines()
            analysis_tail = "\n".join(lines[-10:])

        pending = []
        if active_path:
            scripts_dir = root / "workspace" / active_path["path_id"] / "scripts"
            if scripts_dir.exists():
                pending = [f.name for f in scripts_dir.iterdir() if f.is_file()]

        project_name = state.get("project_name", "Research Project")
        current_path = state.get("current_path", "main")
        pipeline_stage = state.get("pipeline_stage", "unknown")

        content = f"""# Session Handoff — {project_name}
Generated: {now_iso()}

## State
- Current path: {current_path}
- Phase: {pipeline_stage}
- Paths: {', '.join(p['path_id'] for p in paths) if paths else 'none'}

## Recent Analysis
{analysis_tail if analysis_tail else '(empty)'}

## Pending Work
{chr(10).join(f"- {f}" for f in pending) if pending else "- None identified"}

## To Resume This Session
Copy this prompt to your new chat:

---
I'm resuming work on a Research OS project. Current state:
- Project: {project_name}
- Active path: {current_path}
- Phase: {pipeline_stage}

Please run the session_boot protocol, then read workspace/analysis.md tail and conclusions.md to understand where we left off.
---
"""
        handoff_path = root / ".os_state" / "handoffs" / f"handoff_{now_iso()[:10]}.md"
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        handoff_path.write_text(content)
        return {
            "status": "success",
            "handoff_path": str(handoff_path.relative_to(root)),
            "content": content,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
