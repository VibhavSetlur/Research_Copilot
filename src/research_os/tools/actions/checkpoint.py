"""Checkpoints — fast hardlinked workspace snapshots managed by ResearchLedger."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_os.state.state_ledger import ResearchLedger

logger = logging.getLogger("research_os.tools.checkpoint")


def _ledger(root: Path) -> ResearchLedger:
    return ResearchLedger(root / ".os_state" / "state_ledger.json")


def create_checkpoint(description: str, root: Path) -> dict[str, Any]:
    """Snapshot the workspace via hardlinks and record metadata in state."""
    try:
        checkpoint_id = f"ckpt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        ledger = _ledger(root)
        snap = ledger.snapshot_workspace(checkpoint_id, root=root)

        # Record description in a sidecar metadata file
        meta_path = root / ".os_state" / "checkpoints" / f"{checkpoint_id}.meta.json"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(
            json.dumps(
                {
                    "checkpoint_id": checkpoint_id,
                    "description": description,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "files_snapshotted": snap.get("files_snapshotted"),
                    "files_ref_only": snap.get("files_ref_only"),
                },
                indent=2,
            )
        )

        # Add to ledger's checkpoint history
        state = ledger.get()
        state.setdefault("checkpoint_history", []).append(
            {
                "id": checkpoint_id,
                "description": description,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "files": snap.get("files_snapshotted", 0),
            }
        )
        ledger._save(state)

        return {
            "status": "success",
            "checkpoint_id": checkpoint_id,
            "description": description,
            "files_snapshotted": snap.get("files_snapshotted"),
            "message": f"Checkpoint created: {checkpoint_id}",
        }
    except Exception as e:
        logger.exception("create_checkpoint failed")
        return {"status": "error", "message": str(e)}


def rollback_checkpoint(checkpoint_id: str, root: Path) -> dict[str, Any]:
    """Restore the workspace to a checkpoint (creates a backup first)."""
    try:
        ledger = _ledger(root)
        res = ledger.rollback(checkpoint_id, root=root)
        return {
            "status": "success",
            "checkpoint_id": res.get("checkpoint_id"),
            "backup_id": res.get("backup_id"),
            "files_restored": res.get("files_restored"),
            "message": f"Rolled back to {checkpoint_id}",
        }
    except FileNotFoundError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.exception("rollback_checkpoint failed")
        return {"status": "error", "message": str(e)}


def list_checkpoints(root: Path) -> dict[str, Any]:
    """List every checkpoint with its description."""
    try:
        checkpoints_dir = root / ".os_state" / "checkpoints"
        if not checkpoints_dir.exists():
            return {"status": "success", "checkpoints": []}

        out: list[dict[str, Any]] = []
        for meta in sorted(checkpoints_dir.glob("*.meta.json")):
            try:
                data = json.loads(meta.read_text())
                out.append(
                    {
                        "id": data.get("checkpoint_id"),
                        "description": data.get("description", ""),
                        "created_at": data.get("created_at"),
                        "files": data.get("files_snapshotted", 0),
                    }
                )
            except Exception:
                continue
        # Fallback: list directories that have no sidecar
        for d in sorted(checkpoints_dir.iterdir()):
            if d.is_dir() and not any(c["id"] == d.name for c in out):
                out.append({"id": d.name, "description": "(no metadata)"})
        return {"status": "success", "checkpoints": out}
    except Exception as e:
        logger.exception("list_checkpoints failed")
        return {"status": "error", "message": str(e)}
