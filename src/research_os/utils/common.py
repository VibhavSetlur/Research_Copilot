"""Shared utility functions used across the Research OS package."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

from research_os.utils.asset_manager import AssetManager


# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------


def find_project_root(start: Optional[Path] = None) -> Optional[Path]:
    """Walk up from *start* looking for a ``.os_state`` directory.

    Returns ``None`` if no workspace is found within 10 ancestors.
    """
    return AssetManager.find_project_root(start)


def require_project_root() -> Path:
    """Find project root or exit (used by CLI commands)."""
    root = find_project_root()
    if root is None:
        print(
            "ERROR: not in a Research OS workspace (no .os_state/ found).\n"
            "Run `research-os init` first.",
            file=sys.stderr,
        )
        sys.exit(1)
    return root


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------


def load_yaml(path: Path) -> dict:
    if yaml is None:
        return {}
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (FileNotFoundError, OSError, yaml.YAMLError):  # type: ignore[attr-defined]
        return {}


def load_json(path: Path, default: Any = None) -> Any:
    if default is None:
        default = {}
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def save_json_atomic(path: Path, data: Any) -> None:
    """Write JSON via temp file + os.replace — never leaves a half-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(tmp_path, str(path))
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def load_text(path: Path) -> str:
    try:
        return path.read_text()
    except (FileNotFoundError, OSError):
        return ""


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def compute_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (FileNotFoundError, PermissionError, OSError):
        return "error"


# ---------------------------------------------------------------------------
# Timestamps
# ---------------------------------------------------------------------------


def now_iso() -> str:
    """Current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def now_timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    return datetime.now(timezone.utc).strftime(fmt)
