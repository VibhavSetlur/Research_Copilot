import logging
from typing import Dict, Any
from pathlib import Path
from research_os.project_ops import now_iso

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
    # Write pending action to a state file
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

def session_handoff(root: Path) -> Dict[str, Any]:
    try:
        handoff_path = root / ".os_state" / "handoffs" / f"handoff_{now_iso()}.md"
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"# Session Handoff\n\nGenerated at: {now_iso()}\n\n## Summary\n(Please fill in the summary of completed tasks)\n\n## Next Steps\n(Please fill in what needs to be done next)\n\n## Prompt to resume\n```\nResume work from handoff.md. Review the next steps and continue execution.\n```\n"
        
        handoff_path.write_text(content)
        return {
            "status": "success", 
            "message": f"Handoff created at {handoff_path.relative_to(root)}. Researcher should start a new chat with the handoff prompt."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
