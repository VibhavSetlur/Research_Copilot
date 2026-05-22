#!/usr/bin/env python3
"""Runtime selector and configuration for execution environments."""

import shutil
import subprocess
from datetime import datetime, timezone
from typing import Dict, Any, List

from research_copilot.utils.common import find_project_root, load_json, save_json

RUNTIME_PROFILES = {
    "local_fast": {"engine": "local", "timeout": 300, "parallel": True, "container": None},
    "docker_isolated": {"engine": "docker", "timeout": 3600, "parallel": False, "container": "research-copilot:latest"},
    "slurm_cluster": {"engine": "slurm", "timeout": 86400, "parallel": True, "container": "research-copilot:hpc"},
    "aws_batch": {"engine": "aws_batch", "timeout": 86400, "parallel": True, "container": "research-copilot:cloud"}
}

def get_profile(name: str) -> Dict[str, Any]:
    """Retrieve runtime profile configuration."""
    return RUNTIME_PROFILES.get(name, RUNTIME_PROFILES["local_fast"])

def list_docker_images() -> List[str]:
    if not shutil.which("docker"):
        return []
    try:
        proc = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return []
        return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    except Exception:
        return []

def scan_runtime_availability() -> Dict[str, Any]:
    """Scan and report available runtime environments."""
    root = find_project_root()
    blueprint_path = root / ".research" / "cache" / "analysis_blueprint.json"
    
    required = []
    if blueprint_path.exists():
        blueprint = load_json(blueprint_path)
        required = blueprint.get("required_containers", []) if isinstance(blueprint, dict) else []
        if not isinstance(required, list):
            required = []

    images = list_docker_images()
    available = []
    missing = []
    for container in required:
        if any(img.startswith(container + ":") or img == container for img in images):
            available.append(container)
        else:
            missing.append(container)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "blueprint": str(blueprint_path) if blueprint_path.exists() else None,
        "required_containers": required,
        "available": available,
        "missing": missing,
        "engine": "docker" if shutil.which("docker") else "none",
        "profiles": list(RUNTIME_PROFILES.keys())
    }

def main() -> int:
    report = scan_runtime_availability()
    root = find_project_root()
    
    # Save report to cache dir instead of environment dir
    report_path = root / ".research" / "cache" / "runtime_report.json"
    save_json(report_path, report)

    print("=" * 60)
    print("RUNTIME SELECTOR")
    print("=" * 60)
    print(f"Required Containers: {len(report['required_containers'])}")
    for c in report['required_containers']:
        status = "AVAILABLE" if c in report['available'] else "MISSING"
        print(f"  - {c}: {status}")
    print(f"Report: {report_path}")

    return 1 if report['missing'] else 0

if __name__ == "__main__":
    raise SystemExit(main())
