#!/usr/bin/env python3
"""Preflight environment check for Research Copilot.

Checks runtime availability and basic connectivity. Writes a report to
environment/preflight_report.json.
"""
import json
import os
import platform
import shutil
import socket
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

try:
    import yaml
except ImportError:
    yaml = None


from research_copilot.utils.common import find_project_root


def _check_binary(name: str) -> bool:
    return shutil.which(name) is not None


def _check_url(url: str, timeout: int = 5) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout):
            return True
    except Exception:
        return False


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def _load_models(root: Path) -> Dict[str, Any]:
    models_path = root / ".research" / "models.yaml"
    if not models_path.exists() or yaml is None:
        return {}
    try:
        with open(models_path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def main() -> int:
    root = find_project_root()
    report_path = root / "environment" / "preflight_report.json"

    runtimes = {
        "python": True,
        "docker": _check_binary("docker"),
        "podman": _check_binary("podman"),
        "singularity": _check_binary("singularity"),
        "conda": _check_binary("conda"),
        "r": _check_binary("Rscript"),
        "julia": _check_binary("julia"),
        "nextflow": _check_binary("nextflow"),
        "snakemake": _check_binary("snakemake"),
        "pandoc": _check_binary("pandoc"),
    }

    connectivity = {
        "pypi": _check_url("https://pypi.org/simple/"),
        "conda_forge": _check_url("https://conda.anaconda.org/conda-forge"),
        "bioconductor": _check_url("https://bioconductor.org"),
    }

    models = _load_models(root)
    api_keys = {}
    for task, model in models.get("models", {}).items():
        env_var = model.get("api_key_env")
        if env_var:
            api_keys[task] = {
                "provider": model.get("provider"),
                "model": model.get("model"),
                "api_key_env": env_var,
                "available": bool(os.environ.get(env_var)),
            }
    fallback = models.get("fallback", {})
    fallback_env = fallback.get("api_key_env", "")

    format_manifest = root / ".research" / "cache" / "data_format_manifest.json"
    manifest = _load_json(format_manifest) if format_manifest.exists() else {}
    domain_hint = None
    if manifest.get("files"):
        hints = {}
        for item in manifest["files"]:
            hint = item.get("domain_hint")
            if hint:
                hints[hint] = hints.get(hint, 0) + 1
        if hints:
            domain_hint = sorted(hints.items(), key=lambda x: x[1], reverse=True)[0][0]

    data_dir = root / "inputs" / "data" / "raw"
    total_size = 0
    if data_dir.exists():
        for f in data_dir.rglob("*"):
            if f.is_file():
                total_size += f.stat().st_size

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "hostname": socket.gethostname(),
        "runtimes": runtimes,
        "connectivity": connectivity,
        "models": {
            "tasks": api_keys,
            "fallback": {
                "provider": fallback.get("provider"),
                "model": fallback.get("model"),
                "api_key_env": fallback_env,
                "available": bool(os.environ.get(fallback_env)) if fallback_env else False,
            },
        },
        "data": {
            "total_size_gb": round(total_size / (1024 ** 3), 3),
            "domain_hint": domain_hint,
        },
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))

    print("=" * 60)
    print("PREFLIGHT CHECK")
    print("=" * 60)
    print(f"Platform: {report['platform']}")
    print(f"Python:   {report['python']}")
    print("Runtimes:")
    for k, v in runtimes.items():
        print(f"  {k}: {'yes' if v else 'no'}")
    print("Connectivity:")
    for k, v in connectivity.items():
        print(f"  {k}: {'ok' if v else 'fail'}")
    if api_keys:
        available = sum(1 for item in api_keys.values() if item["available"])
        print("LLM API keys:")
        print(f"  task routes available: {available}/{len(api_keys)}")
        print(f"  fallback: {'available' if report['models']['fallback']['available'] else 'missing'} ({fallback_env or 'not configured'})")
    print(f"Data size (GB): {report['data']['total_size_gb']}")
    if domain_hint:
        print(f"Domain hint: {domain_hint}")
    print(f"Report: {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
