import logging
import os
import signal
import json
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("research.tools.task")

_TASK_REGISTRY_FILE = ".os_state/tasks.json"


def _load_tasks(root: Path) -> Dict[str, Any]:
    registry = root / _TASK_REGISTRY_FILE
    if registry.exists():
        try:
            return json.loads(registry.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_tasks(root: Path, tasks: Dict[str, Any]) -> None:
    registry = root / _TASK_REGISTRY_FILE
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(json.dumps(tasks, indent=2, default=str))


def task_create(description: str, root: Path) -> Dict[str, Any]:
    import uuid

    task_id = str(uuid.uuid4())[:8]
    tasks = _load_tasks(root)
    tasks[task_id] = {
        "task_id": task_id,
        "description": description,
        "status": "running",
        "pid": None,
        "created_at": str(__import__("datetime").datetime.now()),
    }
    _save_tasks(root, tasks)
    return {"status": "success", "task_id": task_id}


def task_monitor(task_id: str, root: Optional[Path] = None) -> Dict[str, Any]:
    tasks = _load_tasks(root) if root else {}
    if task_id in tasks:
        entry = tasks[task_id]
        pid = entry.get("pid")
        if pid:
            try:
                os.kill(pid, 0)
                entry["status"] = "running"
            except OSError:
                entry["status"] = "completed"
        return {"status": "success", "task": entry}
    return {"status": "success", "message": f"Monitoring task {task_id}"}


def task_kill(task_id: str, root: Optional[Path] = None) -> Dict[str, Any]:
    tasks = _load_tasks(root) if root else {}
    if task_id in tasks:
        entry = tasks[task_id]
        pid = entry.get("pid")
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                entry["status"] = "killed"
                _save_tasks(root, tasks)
                return {
                    "status": "success",
                    "message": f"Killed task {task_id} (PID {pid})",
                }
            except ProcessLookupError:
                entry["status"] = "completed"
                _save_tasks(root, tasks)
                return {
                    "status": "success",
                    "message": f"Task {task_id} already completed",
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to kill task {task_id}: {e}",
                }
        entry["status"] = "killed"
        _save_tasks(root, tasks)
        return {"status": "success", "message": f"Task {task_id} killed (no PID)"}
    return {"status": "success", "message": f"Killed task {task_id}"}
