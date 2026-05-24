"""Validate protocol YAML files for consistency between light and full variants."""
import yaml
import sys
from pathlib import Path

PROTOCOLS_DIR = Path(__file__).resolve().parent.parent / "src/research_os/protocols"

errors = []
warnings = []

def e(msg):
    errors.append(msg)

def w(msg):
    warnings.append(msg)

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)

for yaml_file in sorted(PROTOCOLS_DIR.rglob("*.yaml")):
    rel = yaml_file.relative_to(PROTOCOLS_DIR).with_suffix("").as_posix()
    key = rel.replace("light/", "")
    is_light = rel.startswith("light/")

    try:
        data = load_yaml(yaml_file)
    except yaml.YAMLError as exc:
        e(f"{rel}: YAML parse error: {exc}")
        continue

    if not isinstance(data, dict):
        e(f"{rel}: not a mapping")
        continue

    name = data.get("name", "")
    steps = data.get("steps", [])
    version = data.get("version", "")

    # 1. Every protocol must have a name matching the file name
    if name != key.split("/")[-1]:
        w(f"{rel}: name '{name}' != filename stem '{key.split('/')[-1]}'")

    # 2. Every protocol must have a steps list
    if not steps:
        e(f"{rel}: no steps defined")
        continue

    # 3. Every step must have id, name, description
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            e(f"{rel}: step {i} is not a mapping")
            continue
        for field in ("id", "name", "description"):
            if field not in step:
                e(f"{rel}: step {i} missing '{field}'")

    # 4. Every protocol must have a protocol_completion step
    if not any(s.get("id") == "protocol_completion" for s in steps):
        e(f"{rel}: missing protocol_completion step")

    # 5. Check for truncated descriptions (ending with . without completing)
    for step in steps:
        desc = step.get("description", "")
        if isinstance(desc, str) and desc.endswith(":") and len(desc) < 60:
            w(f"{rel}: step '{step.get('id')}' description may be truncated: '{desc}'")

    # 6. next_protocol should be set (except terminal protocols)
    terminal_suffixes = {"synthesis_paper", "synthesis_poster", "synthesis_abstract",
                         "synthesis_dashboard", "figure_guidelines",
                         "writing_analysis_log", "writing_conclusions", "writing_citations",
                         "writing_readme", "writing_standards", "glossary_update",
                         "hypothesis_tracking", "dead_end_routing"}
    terminal = {f"light/{s}" for s in terminal_suffixes} | terminal_suffixes
    short_key = key.split("/")[-1]
    if "next_protocol" not in data and short_key not in terminal and key not in terminal:
        w(f"{rel}: missing next_protocol")

    # 7. Every protocol must have schema_version
    if "schema_version" not in data:
        w(f"{rel}: missing schema_version")

    # 8. Light/full pair consistency: compare step ids
    if is_light:
        full_path = PROTOCOLS_DIR / f"{key}.yaml"
        if full_path.exists():
            full_data = load_yaml(full_path)
            full_step_ids = [s.get("id") for s in full_data.get("steps", [])]
            light_step_ids = [s.get("id") for s in steps]
            # Check every light step id exists in full (not vice versa — light can skip)
            for sid in light_step_ids:
                if sid not in full_step_ids:
                    e(f"{rel}: step '{sid}' not found in full version '{key}.yaml'")

    # 9. Check version consistency
    if is_light:
        full_path = PROTOCOLS_DIR / f"{key}.yaml"
        if full_path.exists():
            full_data = load_yaml(full_path)
            full_version = full_data.get("version", "")
            if version and full_version and version != full_version:
                w(f"{rel}: version {version} != full version {full_version}")

# Summary
if errors:
    print(f"ERRORS ({len(errors)}):")
    for err in errors:
        print(f"  - {err}")
if warnings:
    print(f"WARNINGS ({len(warnings)}):")
    for warn in warnings:
        print(f"  - {warn}")

if errors:
    sys.exit(1)
else:
    print("All validations passed!")
    sys.exit(0)
