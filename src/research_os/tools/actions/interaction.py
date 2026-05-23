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

def session_handoff(
    root: Path,
    state: Dict[str, Any] = None,
    last_step: str = "Unknown",
    last_writing_task: str = "None",
    next_writing_task: str = "Unknown",
    next_protocol: str = "writing_core",
    completed_summary: str = "Summary of completed tasks",
    specific_next_action: str = "Determine next steps"
) -> Dict[str, Any]:
    if state is None:
        state = {}
    try:
        handoff_path = root / ".os_state" / "handoffs" / f"handoff_{now_iso()}.md"
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""# Session Handoff
Generated at: {now_iso()}

## Current State
- Current path: {state.get('current_path', 'default')}
- Last completed step: {last_step}

## Writing Status
- Last writing task: {last_writing_task}
- Next writing task: {next_writing_task}
- Protocol to load: {next_protocol}

## Summary
{completed_summary}

## Next Steps
1. Load protocol: {next_protocol}
2. {specific_next_action}

## Prompt to Resume
```
Load protocol {next_protocol}. Review the current state below and continue execution.
```
"""
        
        handoff_path.write_text(content)
        return {
            "status": "success", 
            "message": f"Handoff created at {handoff_path.relative_to(root)}. Researcher should start a new chat with the handoff prompt."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
