#!/usr/bin/env python3
"""Runtime selector for containerized execution.

Reads analysis blueprint to determine required containers and reports availability.
"""
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

try:
    import yaml
except ImportError:
    yaml = None


def load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None:
        return {}
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def find_project_root() -> Path:
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return Path.cwd()


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


def main() -> int:
    root = find_project_root()
    config = load_yaml(root / ".research" / "config.yaml")
    blueprint_path = root / ".research" / "cache" / "analysis_blueprint.json"
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

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "blueprint": str(blueprint_path),
        "required_containers": required,
        "available": available,
        "missing": missing,
        "engine": "docker" if shutil.which("docker") else "none",
    }

    report_path = root / "environment" / "runtime_report.json"
    save_json(report_path, report)

    print("=" * 60)
    print("RUNTIME SELECTOR")
    print("=" * 60)
    print(f"Required: {len(required)}")
    for c in required:
        status = "AVAILABLE" if c in available else "MISSING"
        print(f"  - {c}: {status}")
    print(f"Report: {report_path}")

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
