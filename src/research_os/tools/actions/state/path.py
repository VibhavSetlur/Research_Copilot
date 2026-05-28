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
    # Refresh DAG best-effort.
    try:
        workflow_dag(root)
    except Exception:
        pass

    return {
        "status": "success",
        "original_path": path_name,
        "renamed_to": dead_end_name,
        "rationale": rationale,
        "files_preserved": True,
    }


def workflow_dag(
    root: Path,
    *,
    render_png: bool = False,
    output_dir: str = "docs",
) -> dict[str, Any]:
    """Build a dependency DAG of all numbered steps.

    Walks each step's ``data/input`` symlink to derive ancestor edges.
    Writes ``<output_dir>/workflow_dag.mermaid``. If ``render_png=True``
    AND ``mmdc`` (Mermaid CLI) is on PATH, also writes
    ``<output_dir>/workflow_dag.png``.

    A step's status (active | completed | dead_end) decides its node
    colour so the diagram is readable at a glance.
    """
    try:
        import shutil as _shutil
        import subprocess as _subprocess

        workspace_dir = root / "workspace"
        if not workspace_dir.exists():
            return {"status": "error", "message": "workspace/ not found"}

        steps = list_paths(root).get("paths", []) or []
        if not steps:
            return {
                "status": "success",
                "nodes": 0,
                "edges": 0,
                "message": "No numbered steps yet — DAG is empty.",
            }

        # Map path_id → node label (short).
        nodes: dict[str, dict[str, str]] = {}
        for s in steps:
            pid = s["path_id"]
            nodes[pid] = {
                "label": pid.replace("__DEAD_END", "")[:36],
                "status": s["status"],
                "full_id": pid,
            }

        # Derive edges from data/input symlinks: each step's
        # data/input may be a symlink to either inputs/raw_data or
        # another step's data/output.
        edges: list[tuple[str, str]] = []
        for s in steps:
            step_path = Path(s["experiment_dir"])
            data_in = step_path / "data" / "input"
            if not data_in.exists():
                continue
            # Could be a single symlink or a directory of symlinks; check both.
            link_targets: list[Path] = []
            if data_in.is_symlink():
                try:
                    link_targets.append(data_in.resolve())
                except OSError:
                    pass
            elif data_in.is_dir():
                for child in data_in.iterdir():
                    if child.is_symlink():
                        try:
                            link_targets.append(child.resolve())
                        except OSError:
                            pass
            for target in link_targets:
                # If target lives under another step's data/output,
                # add an edge from that step → this step.
                try:
                    rel = target.relative_to(workspace_dir)
                except ValueError:
                    continue
                parts = rel.parts
                if not parts or not re.match(r"^\d{2,3}_", parts[0]):
                    continue
                ancestor = parts[0]
                if ancestor in nodes and ancestor != s["path_id"]:
                    edge = (ancestor, s["path_id"])
                    if edge not in edges:
                        edges.append(edge)

        # Build mermaid.
        out_dir = root / output_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        mermaid_lines = [
            "graph TD",
            "    classDef active fill:#fff3cd,stroke:#856404,color:#333",
            "    classDef completed fill:#d4edda,stroke:#28a745,color:#155724",
            "    classDef dead_end fill:#f8d7da,stroke:#dc3545,color:#721c24",
        ]
        # Stable iteration order (numbered).
        for pid in sorted(nodes):
            node = nodes[pid]
            safe_id = re.sub(r"[^A-Za-z0-9_]", "_", pid)
            mermaid_lines.append(
                f'    {safe_id}["{node["label"]}"]:::{node["status"]}'
            )
        if not edges:
            # Show ingest from inputs/raw_data for the first step at least.
            first = sorted(nodes)[0]
            safe_first = re.sub(r"[^A-Za-z0-9_]", "_", first)
            mermaid_lines.append("    raw[\"inputs/raw_data\"]")
            mermaid_lines.append(f"    raw --> {safe_first}")
        else:
            for src, dst in edges:
                src_safe = re.sub(r"[^A-Za-z0-9_]", "_", src)
                dst_safe = re.sub(r"[^A-Za-z0-9_]", "_", dst)
                mermaid_lines.append(f"    {src_safe} --> {dst_safe}")

        mmd_path = out_dir / "workflow_dag.mermaid"
        mmd_path.write_text("\n".join(mermaid_lines) + "\n")

        png_path = None
        if render_png and _shutil.which("mmdc"):
            png_target = out_dir / "workflow_dag.png"
            try:
                res = _subprocess.run(
                    ["mmdc", "-i", str(mmd_path), "-o", str(png_target),
                     "-b", "transparent"],
                    capture_output=True, text=True, timeout=30,
                )
                if res.returncode == 0:
                    png_path = str(png_target.relative_to(root))
            except (OSError, _subprocess.TimeoutExpired):
                pass

        return {
            "status": "success",
            "mermaid_path": str(mmd_path.relative_to(root)),
            "png_path": png_path,
            "nodes": len(nodes),
            "edges": len(edges),
            "has_mmdc": bool(_shutil.which("mmdc")),
            "advice": (
                "Install mmdc (npm install -g @mermaid-js/mermaid-cli) and "
                "re-run with render_png=true for a PNG."
                if not _shutil.which("mmdc")
                else "Re-run with render_png=true to refresh the PNG."
            ),
        }
    except Exception as e:
        logger.exception("workflow_dag failed")
        return {"status": "error", "message": str(e)}


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
