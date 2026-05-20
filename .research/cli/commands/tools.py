"""Tool commands: tools, tool."""
import sys
from pathlib import Path

from core.utils import find_project_root, load_json, load_markdown, get_config, require_project_root


def _load_tool_registry(root, config):
    registries = config.get("registries", {})
    registry_path = registries.get("tool_registry", ".research/domains/tool_registry.json")
    return load_json(root / registry_path)


def cmd_tools(args):
    root = require_project_root()

    config = get_config(root)
    registry = _load_tool_registry(root, config)
    tools = registry.get("tools", [])
    if not tools:
        print("No tools found in registry.")
        return

    report_path = root / config.get("cache_dir", ".research/cache") / "tool_availability_report.json"
    report = load_json(report_path) if report_path.exists() else {}
    status_map = {t.get("tool_id"): t.get("status") for t in report.get("tools", [])}

    print("=" * 60)
    print("TOOLS")
    print("=" * 60)
    print()
    for tool in tools:
        tool_id = tool.get("id")
        status = status_map.get(tool_id, "UNKNOWN")
        print(f"  {tool_id} — {tool.get('category', 'unknown')} [{status}]")
    print()
    if not report:
        print("  NOTE: Tool availability report not found. Run tool_capability_check.py to generate it.")


def cmd_tool(args):
    root = require_project_root()

    config = get_config(root)
    registry = _load_tool_registry(root, config)
    tools = registry.get("tools", [])
    needle = args.name.strip().lower()
    match = None
    for tool in tools:
        if tool.get("id", "").lower() == needle:
            match = tool
            break

    if not match:
        print(f"Tool '{args.name}' not found in registry.")
        return

    print("=" * 60)
    print(f"TOOL: {match.get('id')}")
    print("=" * 60)
    print()
    print(f"  Category: {match.get('category')}")
    print(f"  Language: {match.get('language')}")
    print(f"  Container: {match.get('container')}")
    print(f"  Invocation: {match.get('invocation')}")
    print(f"  Install check: {match.get('install_check')}")
    print(f"  Install cmd: {match.get('install_cmd')}")
    print(f"  Inputs: {', '.join(match.get('input_formats', []))}")
    print(f"  Outputs: {', '.join(match.get('output_formats', []))}")
    print(f"  Citation: {match.get('citation')}")
    print(f"  Notes: {match.get('notes', '')}")
