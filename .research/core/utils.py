"""Centralized utilities for Research Copilot.

Single source of truth for all shared functions used across CLI commands,
core modules, scripts, and utilities. Eliminates ~800-1000 lines of
duplicated code across 19+ files.

Usage:
    from core.utils import (
        find_project_root, load_yaml, load_json, save_json, save_json_atomic,
        load_markdown, load_text, get_config, get_research_map,
        compute_sha256, ensure_dir, now_iso, now_timestamp,
        require_project_root,
    )
"""

import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None


# =============================================================================
# Project Root Detection
# =============================================================================

def find_project_root() -> Optional[Path]:
    """Find project root by looking for .research/ directory.

    Walks up from CWD (max 10 levels) looking for a .research/ directory.
    Also handles the case where CWD is inside .research/ itself.

    Returns:
        Path to project root, or None if not found.
    """
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.name == ".research" and (p.parent / "inputs").exists():
            return p.parent
        if p.parent == p:
            break
        p = p.parent
    return None


def require_project_root() -> Path:
    """Find project root or exit with error message.

    Returns:
        Path to project root.

    Exits:
        sys.exit(1) if no .research/ directory found.
    """
    root = find_project_root()
    if root is None:
        print("ERROR: No .research/ directory found. Are you in a Research Copilot project?")
        sys.exit(1)
    return root


# =============================================================================
# File I/O
# =============================================================================

def load_yaml(path: Path) -> dict:
    """Load YAML file, return dict or empty dict.

    Falls back to manual key:value parsing if PyYAML is not installed.
    """
    if yaml is None:
        result = {}
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and ":" in line:
                        key, _, val = line.partition(":")
                        val = val.strip().strip('"').strip("'")
                        result[key.strip()] = val
        except FileNotFoundError:
            return {}
        return result
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (FileNotFoundError, Exception):
        return {}


def load_json(path: Path, default: Any = None) -> Any:
    """Load JSON file, return parsed data or default on error.

    Args:
        path: Path to JSON file
        default: Value to return on error (default: None)

    Returns:
        Parsed JSON data, or default if file not found / invalid JSON.
    """
    if default is None:
        default = {}
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def load_json_safe(path: Path, default: Any = None) -> Any:
    """Load JSON file safely, checking existence first.

    Alias for load_json() with existence check for callers that prefer it.
    """
    if not path.exists():
        return default if default is not None else {}
    return load_json(path, default)


def save_json(path: Path, data: Any) -> None:
    """Save data to JSON file, creating parent directories.

    Args:
        path: Output file path
        data: Data to serialize (must be JSON-serializable)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def save_json_atomic(path: Path, data: Any) -> None:
    """Save data to JSON file atomically (write to temp, then rename).

    Prevents file corruption if the process is interrupted during write.

    Args:
        path: Output file path
        data: Data to serialize (must be JSON-serializable)
    """
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


def load_markdown(path: Path) -> str:
    """Load markdown file, return text or empty string."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def load_text(path: Path) -> str:
    """Load text file, return content or empty string.

    Alias for load_markdown() — same behavior, different name for clarity.
    """
    return load_markdown(path)


def load_text_safe(path: Path) -> str:
    """Load text file safely, checking existence first."""
    if not path.exists():
        return ""
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return ""


def ensure_dir(path: Path) -> Path:
    """Create directory (and parents) if it doesn't exist.

    Returns:
        The path (for chaining).
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


# =============================================================================
# Configuration
# =============================================================================

_DEFAULT_CONFIG = {
    "project_id": "research-copilot",
    "schema_version": "8.0.0",
    "default_workflow": "quick_exploratory",
    "intake_path": "inputs/intake.md",
    "data_raw": "inputs/data/raw",
    "context_dir": "inputs/context",
    "papers_dir": "inputs/papers",
    "cache_dir": ".research/cache",
    "cache_research_map": ".research/cache/research_map.json",
    "cache_followups": ".research/cache/follow_up_questions.md",
    "docs_dir": "docs",
    "reports_dir": "reports",
    "research_map": "reports/baseline/research_map.json",
    "follow_up_questions": "reports/baseline/follow_up_questions.md",
    "manifest": "docs/manifest.json",
    "iteration_registry": "docs/iterations/registry.json",
    "research_log": "docs/research_log.md",
    "data_ingested": "data/01_ingested",
    "data_processed": "data/02_processed",
    "data_analytical": "data/03_analytical",
    "dag_json": ".research/workflow_dag.json",
    "state_ledger": ".research/cache/state.json",
    "checkpoint_dir": ".research/cache/checkpoints",
    "token_budget_limit": 200000,
    "literature_corpus": "reports/literature/literature_corpus.json",
    "evidence_matrix": "reports/literature/evidence_matrix.md",
    "bibliography": "reports/literature/bibliography.bib",
    "analysis_plan": "reports/analysis/analysis_plan.md",
    "full_audit": "reports/audit/full_audit_report.md",
    "manuscript_findings": "reports/manuscript/research_findings.md",
    "key_findings": "reports/summary/key_findings.md",
    "executive_summary": "reports/summary/executive_summary.md",
    "layman_summary": "reports/summary/layman_summary.md",
    "preregistration_dir": "reports/literature",
    "reviewer2_critique": "reports/audit/reviewer2_critique.md",
    "dag_viewer": "reports/dashboards/dag_viewer.html",
    "requirements_file": "environment/requirements.txt",
    "environment_check_script": ".research/scripts/00_environment_check.py",
    "quality_gates_enabled": True,
    "gate_fail_blocks_pipeline": True,
}


def get_config(root: Optional[Path] = None, defaults: Optional[dict] = None) -> dict:
    """Load config.yaml with defaults.

    Args:
        root: Project root path (auto-detected if None)
        defaults: Override default config values (merged with built-in defaults)

    Returns:
        Config dict with all keys populated.
    """
    if root is None:
        root = require_project_root()

    config = load_yaml(root / ".research" / "config.yaml")
    merged_defaults = {**_DEFAULT_CONFIG}
    if defaults:
        merged_defaults.update(defaults)

    for k, v in merged_defaults.items():
        config.setdefault(k, v)
    return config


def get_research_map(root: Path, config: dict) -> dict:
    """Get research map from AI output or CLI cache.

    Tries the AI-generated path first, falls back to CLI cache.
    """
    ai_map = load_json(root / config["research_map"])
    if ai_map:
        return ai_map
    return load_json(root / config["cache_research_map"])


# =============================================================================
# Hashing
# =============================================================================

def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file using chunked reading.

    Args:
        file_path: Path to file

    Returns:
        Hex digest string, or "error" if file cannot be read.
    """
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (FileNotFoundError, PermissionError, OSError):
        return "error"


# =============================================================================
# Timestamps
# =============================================================================

def now_iso() -> str:
    """Current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def now_timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """Current UTC time formatted as string.

    Args:
        fmt: strftime format string (default: "%Y%m%d_%H%M%S")

    Returns:
        Formatted timestamp string.
    """
    return datetime.now(timezone.utc).strftime(fmt)


# =============================================================================
# Data Scale Thresholds
# =============================================================================

def get_data_scale_thresholds(config: Optional[dict] = None) -> dict:
    """Load data scale thresholds from config or use defaults.

    Args:
        config: Config dict (loaded automatically if None)

    Returns:
        Dict with keys: medium_mb, large_gb, massive_gb
    """
    defaults = {"medium_mb": 100, "large_gb": 1, "massive_gb": 10}
    if config is None:
        config = get_config()
    thresholds = config.get("data_scale_thresholds", {})
    return {
        "medium_mb": thresholds.get("medium_mb", defaults["medium_mb"]),
        "large_gb": thresholds.get("large_gb", defaults["large_gb"]),
        "massive_gb": thresholds.get("massive_gb", defaults["massive_gb"]),
    }


# =============================================================================
# State Ledger Helpers
# =============================================================================

def load_state(root: Optional[Path] = None) -> dict:
    """Load the research state ledger.

    Args:
        root: Project root path (auto-detected if None)

    Returns:
        State dict, or empty dict if not found.
    """
    if root is None:
        root = find_project_root()
        if root is None:
            return {}
    state_path = root / ".research" / "cache" / "state.json"
    return load_json(state_path)


def save_state(data: dict, root: Optional[Path] = None) -> None:
    """Save the research state ledger atomically.

    Args:
        data: State dict to save
        root: Project root path (auto-detected if None)
    """
    if root is None:
        root = require_project_root()
    state_path = root / ".research" / "cache" / "state.json"
    save_json_atomic(state_path, data)
