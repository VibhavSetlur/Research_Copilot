"""Tool commands: tools, tool."""
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def find_project_root():
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return None


def load_yaml(path: Path):
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
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_config(root: Path):
    config = load_yaml(root / ".research" / "config.yaml")
    defaults = {
        "cache_dir": ".research/cache",
        "registries": {"tool_registry": ".research/domains/tool_registry.json"},
    }
    for k, v in defaults.items():
        config.setdefault(k, v)
    return config


def _load_tool_registry(root, config):
    registries = config.get("registries", {})
    registry_path = registries.get("tool_registry", ".research/domains/tool_registry.json")
    return load_json(root / registry_path)


def cmd_tools(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

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
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

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
