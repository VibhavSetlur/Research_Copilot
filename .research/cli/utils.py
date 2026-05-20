"""Shared CLI utilities for Research Copilot."""

from pathlib import Path
import json

try:
    import yaml
except ImportError:
    yaml = None


def find_project_root():
    """Find project root by looking for .research/ directory."""
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


def load_yaml(path: Path):
    """Load YAML file, return dict or empty dict."""
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


def load_json(path: Path):
    """Load JSON file, return dict or empty dict."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_markdown(path: Path):
    """Load markdown file, return text or empty string."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def save_json(path: Path, data):
    """Save dict to JSON file, creating parent dirs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_config(root: Path):
    """Load config with defaults."""
    config = load_yaml(root / ".research" / "config.yaml")
    defaults = {
        "default_workflow": "quick_exploratory",
        "intake_path": "inputs/intake.md",
        "data_raw": "inputs/data/raw",
        "context_dir": "inputs/context",
        "papers_dir": "inputs/papers",
        # CLI cache (inside .research/, never creates top-level dirs)
        "cache_dir": ".research/cache",
        "cache_research_map": ".research/cache/research_map.json",
        "cache_followups": ".research/cache/follow_up_questions.md",
        # AI-created output paths (checked for existence, not created by CLI)
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
    }
    for k, v in defaults.items():
        config.setdefault(k, v)
    return config


def get_research_map(root: Path, config: dict):
    """Get research map from AI output or CLI cache."""
    ai_map = load_json(root / config["research_map"])
    if ai_map:
        return ai_map
    return load_json(root / config["cache_research_map"])
