#!/usr/bin/env python3
"""Tool capability check.

Reads the analysis blueprint, checks required tools against the tool registry,
and writes a tool availability report to .research/cache/.
"""

import argparse
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

try:
    import yaml
except ImportError:
    yaml = None


from research_os.utils.common import find_project_root, load_yaml, load_json, save_json


def get_config(root: Path) -> Dict[str, Any]:
    config = load_yaml(root / ".research" / "config.yaml")
    return config if isinstance(config, dict) else {}


def extract_required_tools(blueprint: Dict[str, Any]) -> List[str]:
    required = set()
    for key in ("required_tools", "tools"):
        for item in (
            blueprint.get(key, []) if isinstance(blueprint.get(key, []), list) else []
        ):
            if isinstance(item, str):
                required.add(item)
            elif isinstance(item, dict):
                tool_id = item.get("tool_id") or item.get("id")
                if tool_id:
                    required.add(tool_id)

    for key in ("selected_methods", "methods"):
        for item in (
            blueprint.get(key, []) if isinstance(blueprint.get(key, []), list) else []
        ):
            if isinstance(item, dict):
                tool_id = item.get("tool_id") or item.get("id")
                if tool_id:
                    required.add(tool_id)

    return sorted(required)


def check_tool(tool: Dict[str, Any], container_engine: str) -> Dict[str, Any]:
    cmd = tool.get("install_check") or tool.get("invocation")
    result = {
        "tool_id": tool.get("id"),
        "status": "UNKNOWN",
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "install_cmd": tool.get("install_cmd"),
        "container": tool.get("container"),
    }
    if not cmd:
        result["status"] = "UNKNOWN"
        return result

    try:
        proc = subprocess.run(
            cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        result["exit_code"] = proc.returncode
        result["stdout"] = (proc.stdout or "").strip()
        result["stderr"] = (proc.stderr or "").strip()
        if proc.returncode == 0:
            result["status"] = "AVAILABLE"
            return result
    except Exception as e:
        result["stderr"] = str(e)

    engine_available = shutil.which(container_engine) is not None
    if tool.get("container") and not engine_available:
        result["status"] = "MISSING_REQUIRES_CONTAINER"
    else:
        result["status"] = "INSTALLABLE"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Tool capability check")
    parser.add_argument("--blueprint", help="Path to analysis blueprint JSON")
    parser.add_argument("--report", help="Path to output report JSON")
    args = parser.parse_args()

    root = find_project_root()
    config = get_config(root)
    registries = config.get("registries", {}) if isinstance(config, dict) else {}
    tool_registry_path = registries.get(
        "tool_registry", ".research/domains/tool_registry.json"
    )
    tool_registry = load_json(root / tool_registry_path)

    blueprint_path = (
        Path(args.blueprint)
        if args.blueprint
        else root / ".research" / "cache" / "analysis_blueprint.json"
    )
    blueprint = load_json(blueprint_path)

    required_tools = extract_required_tools(blueprint)
    tools_by_id = {t.get("id"): t for t in tool_registry.get("tools", [])}
    container_engine = config.get("execution", {}).get("container_engine", "docker")

    results = []
    missing = False
    for tool_id in required_tools:
        tool = tools_by_id.get(tool_id)
        if not tool:
            results.append({"tool_id": tool_id, "status": "MISSING_FROM_REGISTRY"})
            missing = True
            continue
        res = check_tool(tool, container_engine)
        if res["status"] in ("MISSING_FROM_REGISTRY", "MISSING_REQUIRES_CONTAINER"):
            missing = True
        results.append(res)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "blueprint": str(blueprint_path),
        "tools": results,
    }

    report_path = (
        Path(args.report)
        if args.report
        else root / ".research" / "cache" / "tool_availability_report.json"
    )
    save_json(report_path, report)

    print(f"Tool availability report saved to: {report_path}")
    print(f"Required tools: {len(required_tools)}")
    for item in results:
        print(f"  - {item.get('tool_id')}: {item.get('status')}")

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
