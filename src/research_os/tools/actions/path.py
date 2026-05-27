"""Experiment-path management.

A *path* is a numbered experiment folder under ``workspace/``. Paths are the
chronological backbone of the project — every meaningful analysis lives in one.
"""

from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path
from typing import Any

logger = logging.getLogger("research_os.tools.path")


def create_path(name: str, root: Path, hypothesis: str = "") -> dict[str, Any]:
    """Create the next numbered experiment folder.

    Delegates to :func:`project_ops.create_numbered_experiment` so that state,
    manifest, and mermaid diagram are updated atomically.
    """
    from research_os.project_ops import create_numbered_experiment

    try:
        return {"status": "success", **create_numbered_experiment(root, name, hypothesis=hypothesis)}
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.exception("create_path failed")
        return {"status": "error", "message": str(e)}


def abandon_path(path_name: str, rationale: str, root: Path) -> dict[str, Any]:
    """Rename a path to ``<name>__DEAD_END`` and log the rationale."""
    from research_os.project_ops import (
        _update_manifest,
        _update_workflow_mermaid,
        load_state,
        now_iso,
        save_state,
    )

    workspace_dir = root / "workspace"
    target_dir = workspace_dir / path_name
    if not target_dir.exists() or not target_dir.is_dir():
        return {"status": "error", "message": f"Path '{path_name}' not found in workspace/"}
    if not re.match(r"^\d{2}_", path_name):
        return {"status": "error", "message": f"'{path_name}' is not a numbered experiment path"}

    dead_end_name = f"{path_name}__DEAD_END"
    dead_end_dir = workspace_dir / dead_end_name
    if dead_end_dir.exists():
        shutil.rmtree(dead_end_dir, ignore_errors=True)
    target_dir.rename(dead_end_dir)

    analysis_path = root / "workspace" / "analysis.md"
    analysis_path.parent.mkdir(parents=True, exist_ok=True)
    with open(analysis_path, "a") as f:
        f.write(
            f"\n## Abandoned `{path_name}` ({now_iso()})\n\n"
            f"**Rationale:** {rationale}\n\n"
        )

    state = load_state(root)
    paths = state.setdefault("paths", {})
    if path_name in paths:
        paths[path_name]["status"] = "dead_end"
        paths[path_name]["abandoned_at"] = now_iso()
        paths[path_name]["abandon_rationale"] = rationale
    dead_ends = state.setdefault("dead_ends", [])
    if path_name not in dead_ends:
        dead_ends.append(path_name)
    if state.get("current_path") == path_name:
        # Roll back to most recent active path, or 'main'.
        remaining = [
            p for p, info in paths.items()
            if info.get("status") == "active" and p != path_name
        ]
        state["current_path"] = remaining[-1] if remaining else "main"
    save_state(root, state)

    _update_workflow_mermaid(root)
    _update_manifest(root)

    return {
        "status": "success",
        "original_path": path_name,
        "renamed_to": dead_end_name,
        "rationale": rationale,
        "files_preserved": True,
    }


def list_paths(root: Path) -> dict[str, Any]:
    """List every numbered experiment path with status and metadata."""
    workspace_dir = root / "workspace"
    paths: list[dict[str, Any]] = []
    if not workspace_dir.exists():
        return {"status": "success", "paths": paths, "paths_count": 0}

    for p in sorted(workspace_dir.iterdir()):
        if not p.is_dir():
            continue
        m = re.match(r"^(\d{2,3})_(.+?)(__DEAD_END)?$", p.name)
        if not m:
            continue
        number = int(m.group(1))
        name = m.group(2)
        is_dead = m.group(3) is not None

        if is_dead:
            status = "dead_end"
        else:
            conc = p / "conclusions.md"
            has_conclusions = conc.exists() and conc.stat().st_size > 100
            has_outputs = any(
                (p / "outputs" / sub).exists()
                and any((p / "outputs" / sub).iterdir())
                for sub in ("reports", "figures", "tables")
                if (p / "outputs" / sub).exists()
            )
            status = "completed" if (has_conclusions and has_outputs) else "active"

        paths.append(
            {
                "path_id": p.name,
                "number": number,
                "name": name,
                "status": status,
                "experiment_dir": str(p.absolute()),
                "has_readme": (p / "README.md").exists(),
                "has_conclusions": (p / "conclusions.md").exists(),
            }
        )

    return {"status": "success", "paths": paths, "paths_count": len(paths)}
