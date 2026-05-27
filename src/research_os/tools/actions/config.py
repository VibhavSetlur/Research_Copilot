"""Researcher config — read/write/validate ``inputs/researcher_config.yaml``.

This file is the source of truth for how the AI behaves in the workspace.
The config is created on init via ``init_config`` and edited by the researcher
(or by the AI on the researcher's behalf during ``project_startup``).
"""

from __future__ import annotations

import copy
import logging
import os
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("research_os.tools.config")


CONFIG_TEMPLATE = """# Research OS — Researcher Configuration
# This file is the SOURCE OF TRUTH for AI behaviour in this workspace.
# Edit any time. Research OS does not call any LLM itself — your AI client owns the model.

# ── Project ──────────────────────────────────────────────────────────────
project_name: "{project_name}"
research_question: "{research_question}"
domain: "{domain}"

# ── Who you are ──────────────────────────────────────────────────────────
researcher:
  name: ""
  field: ""
  expertise_level: "intermediate"   # beginner | intermediate | advanced | pi
  institution: ""
  orcid: ""

# ── How the AI should behave ────────────────────────────────────────────
interaction:
  autonomy_level: "supervised"      # manual | supervised | autopilot

# ── Model profile (controls protocol verbosity) ─────────────────────────
model_profile: "medium"             # small | medium | large

# ── What you want to produce ────────────────────────────────────────────
research_goal:
  output_types:
    - "paper"                       # any of: paper | abstract | poster | dashboard | report | exploratory
  target_venue: "journal"           # journal | conference | preprint | dissertation | report
  reporting_standard: ""            # auto-filled by domain_analysis
  poster_dimensions: "36x48"

# ── Writing preferences ──────────────────────────────────────────────────
writing_preferences:
  citation_style: "apa"             # apa | vancouver | acm | ieee | nature
  language: "en-US"

# ── API keys (optional — leave blank for free public endpoints) ──────────
api_keys:
  firecrawl: ""                     # https://firecrawl.io
  semantic_scholar: ""              # https://www.semanticscholar.org/product/api
  pubmed: ""                        # https://www.ncbi.nlm.nih.gov/account/
  crossref: ""
  serpapi: ""

# ── Notification preferences ────────────────────────────────────────────
notifications:
  on_step_complete: true
  on_error: true
  on_decision_required: true
"""


def _config_path(root: Path) -> Path:
    return root / "inputs" / "researcher_config.yaml"


def _mask_api_keys(config: dict[str, Any]) -> dict[str, Any]:
    safe = copy.deepcopy(config)
    keys = safe.get("api_keys")
    if isinstance(keys, dict):
        for k, v in keys.items():
            if not isinstance(v, str) or not v:
                continue
            if len(v) > 8:
                safe["api_keys"][k] = f"{v[:4]}…{v[-4:]}"
            else:
                safe["api_keys"][k] = "***"
    return safe


def get_config(root: Path) -> dict[str, Any]:
    try:
        cfg_path = _config_path(root)
        if not cfg_path.exists():
            return {"status": "error", "message": "researcher_config.yaml not found — run `research-os init`."}

        warning = None
        if os.name != "nt":
            try:
                mode = os.stat(cfg_path).st_mode
                if mode & 0o004:
                    warning = (
                        "WARNING: inputs/researcher_config.yaml is world-readable. "
                        "Run `chmod 600 inputs/researcher_config.yaml` to protect API keys."
                    )
            except Exception:
                pass

        config = yaml.safe_load(cfg_path.read_text()) or {}
        safe = _mask_api_keys(config)

        result: dict[str, Any] = {"status": "success", "config": safe}
        if warning:
            result["warning"] = warning
        return result
    except Exception as e:
        logger.exception("get_config failed")
        return {"status": "error", "message": str(e)}


def set_config(key: str, value: Any, root: Path) -> dict[str, Any]:
    """Set a single config value with dot notation (e.g. researcher.expertise_level)."""
    try:
        cfg_path = _config_path(root)
        config = yaml.safe_load(cfg_path.read_text()) if cfg_path.exists() else {}
        config = config or {}

        parts = key.split(".")
        cursor = config
        for part in parts[:-1]:
            if part not in cursor or not isinstance(cursor[part], dict):
                cursor[part] = {}
            cursor = cursor[part]
        cursor[parts[-1]] = value

        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))
        return {"status": "success", "key": key, "value": value}
    except Exception as e:
        logger.exception("set_config failed")
        return {"status": "error", "message": str(e)}


def init_config(root: Path, overrides: dict | None = None) -> dict[str, Any]:
    """Create ``inputs/researcher_config.yaml`` if missing, then merge overrides."""
    overrides = overrides or {}
    cfg_path = _config_path(root)
    already_exists = cfg_path.exists()
    if not already_exists:
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(
            CONFIG_TEMPLATE.format(
                project_name=overrides.get("project_name", ""),
                research_question=overrides.get("research_question", ""),
                domain=overrides.get("domain", ""),
            )
        )

    if overrides:
        try:
            config = yaml.safe_load(cfg_path.read_text()) or {}
            if overrides.get("project_name"):
                config["project_name"] = overrides["project_name"]
            if overrides.get("domain"):
                config["domain"] = overrides["domain"]
            if overrides.get("research_question"):
                config["research_question"] = overrides["research_question"]
            if overrides.get("depth"):
                config.setdefault("research_goal", {})["target_venue"] = overrides["depth"]
            cfg_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))
        except Exception as e:
            logger.warning(f"Failed to apply config overrides: {e}")

    if os.name != "nt":
        try:
            os.chmod(cfg_path, 0o600)
        except Exception:
            pass

    gitignore = root / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if "inputs/researcher_config.yaml" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# secrets\ninputs/researcher_config.yaml\n")

    if already_exists:
        return {"status": "success", "message": "Config already exists; overrides applied."}
    return {
        "status": "success",
        "message": "Initialised researcher_config.yaml and locked permissions to 600.",
    }


def validate_config(root: Path) -> dict[str, Any]:
    """Report which keys are present + whether API keys are configured."""
    res = get_config(root)
    if res.get("status") != "success":
        return res
    config = res.get("config", {}) or {}

    required_paths = [
        ("project_name", config.get("project_name")),
        ("researcher.expertise_level", (config.get("researcher") or {}).get("expertise_level")),
        ("interaction.autonomy_level", (config.get("interaction") or {}).get("autonomy_level")),
        ("model_profile", config.get("model_profile")),
        ("research_goal.output_types", (config.get("research_goal") or {}).get("output_types")),
    ]

    missing = [k for k, v in required_paths if not v]

    api_keys = config.get("api_keys") or {}
    keys_present = sorted(k for k, v in api_keys.items() if v and v != "***" and not str(v).endswith("…"))
    keys_missing = sorted(k for k, v in api_keys.items() if not v)

    return {
        "status": "success",
        "required_fields_missing": missing,
        "api_keys_configured": keys_present,
        "api_keys_blank": keys_missing,
        "message": (
            "Config OK." if not missing else f"Missing required fields: {', '.join(missing)}"
        ),
    }
