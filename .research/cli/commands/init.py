"""Init commands: setup, preflight, init-dirs."""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
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
        if p.name == ".research" and (p.parent / "inputs").exists():
            return p.parent
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


def load_markdown(path: Path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_config(root: Path):
    config = load_yaml(root / ".research" / "config.yaml")
    defaults = {
        "intake_path": "inputs/intake.md",
        "data_raw": "inputs/data/raw",
        "cache_dir": ".research/cache",
        "cache_research_map": ".research/cache/research_map.json",
        "research_map": "reports/baseline/research_map.json",
        "manifest": "docs/manifest.json",
        "iteration_registry": "docs/iterations/registry.json",
        "research_log": "docs/research_log.md",
        "methodology": "docs/methodology.md",
        "changelog": "docs/changelog.md",
        "data_ingested": "data/01_ingested",
        "data_processed": "data/02_processed",
        "data_analytical": "data/03_analytical",
    }
    for k, v in defaults.items():
        config.setdefault(k, v)
    return config


def get_research_map(root: Path, config: dict):
    ai_map = load_json(root / config["research_map"])
    if ai_map:
        return ai_map
    return load_json(root / config["cache_research_map"])


def cmd_setup(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        print("This doesn't look like a Research Copilot project.")
        print("Copy .research/, inputs/, environment/, and AGENTS.md from the template.")
        sys.exit(1)

    config = get_config(root)

    print("=" * 60)
    print("RESEARCH COPILOT — SETUP CHECK")
    print("=" * 60)
    print()

    all_ok = True

    print("  System files:")
    system_checks = [
        (".research/research.py", "CLI tool"),
        (".research/config.yaml", "Configuration"),
        ("AGENTS.md", "AI agent instructions"),
    ]
    for path, desc in system_checks:
        exists = (root / path).exists()
        marker = "✓" if exists else "✗"
        print(f"    {marker} {path} — {desc}")
        if not exists:
            all_ok = False
    print()

    print("  System directories:")
    dir_checks = [
        (".research/agents", "Agent instructions"),
        (".research/skills", "Methodology skills"),
        (".research/workflows", "Workflow templates"),
        (".research/domains", "Domain profiles"),
        (".research/core", "Hook system & state ledger"),
        (".research/schemas", "Pydantic validation models"),
        (".research/scripts", "System scripts"),
        (".research/scripts/utils", "System utility scripts"),
    ]
    for path, desc in dir_checks:
        exists = (root / path).exists()
        marker = "✓" if exists else "✗"
        print(f"    {marker} {path}/ — {desc}")
        if not exists:
            all_ok = False
    print()

    print("  Environment:")
    env_checks = [
        ("environment/requirements.txt", "Pinned dependencies"),
        ("environment/setup.sh", "venv setup script"),
        ("environment/setup_conda.sh", "Conda setup script"),
    ]
    for path, desc in env_checks:
        exists = (root / path).exists()
        marker = "✓" if exists else "✗"
        print(f"    {marker} {path} — {desc}")
        if not exists:
            all_ok = False

    venv_active = sys.prefix != sys.base_prefix
    conda_active = "CONDA_DEFAULT_ENV" in os.environ
    if venv_active or conda_active:
        env_name = os.environ.get("CONDA_DEFAULT_ENV", sys.prefix.split("/")[-1])
        print(f"    ✓ Active environment: {env_name}")
    else:
        print(f"    ○ No virtual environment active")
        print(f"      Run: source environment/venv/bin/activate  (or conda activate research-copilot)")
    print()

    print("  User inputs:")
    input_checks = [
        ("inputs/intake.md", "Intake form"),
        ("inputs/data/raw", "Data directory"),
        ("inputs/context", "Context directory"),
        ("inputs/papers", "Papers directory"),
    ]
    for path, desc in input_checks:
        exists = (root / path).exists()
        marker = "✓" if exists else "✗"
        print(f"    {marker} {path}/ — {desc}")
        if not exists:
            all_ok = False

    data_dir = root / config["data_raw"]
    if data_dir.exists():
        data_files = [f for f in data_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
        if data_files:
            print(f"    ✓ {len(data_files)} data file(s) found")
        else:
            print(f"    ○ No data files yet — add files to inputs/data/raw/")
    print()

    print("  Utility scripts:")
    script_checks = [
        (".research/scripts/00_environment_check.py", "Environment check"),
        (".research/scripts/utils/cache_manager.py", "Cache manager"),
        (".research/scripts/utils/citation_verifier.py", "Citation verifier"),
        (".research/scripts/utils/claim_tracer.py", "Claim tracer"),
        (".research/scripts/utils/parallel_runner.py", "Parallel runner"),
        (".research/scripts/utils/figure_validator.py", "Figure validator"),
        (".research/scripts/utils/auto_debug.py", "Auto debugger"),
        (".research/scripts/research_dashboard.py", "Dashboard"),
    ]
    for path, desc in script_checks:
        exists = (root / path).exists()
        marker = "✓" if exists else "✗"
        print(f"    {marker} {path} — {desc}")
        if not exists:
            all_ok = False
    print()

    print("  Core modules:")
    core_checks = [
        (".research/core/hooks.py", "Hook registry"),
        (".research/core/interceptors.py", "Hook interceptors"),
        (".research/core/state_ledger.py", "State ledger"),
        (".research/core/checkpoint_manager.py", "Checkpoint manager"),
    ]
    for path, desc in core_checks:
        exists = (root / path).exists()
        marker = "✓" if exists else "✗"
        print(f"    {marker} {path} — {desc}")
        if not exists:
            all_ok = False
    print()

    print("=" * 60)
    if all_ok:
        print("  STATUS: READY")
        print()
        print("  Next steps:")
        print("    1. Fill out inputs/intake.md")
        print("    2. Add data files to inputs/data/raw/")
        print("    3. Open your AI agent and run: python .research/research.py scan")
    else:
        print("  STATUS: INCOMPLETE")
        print()
        print("  Some system files are missing. Re-copy from the template:")
        print("    cp -r template/.research ./")
        print("    cp -r template/inputs ./")
        print("    cp -r template/environment ./")
        print("    cp template/AGENTS.md ./")
    print()


def cmd_preflight(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    script_path = root / "environment" / "preflight_check.py"
    if not script_path.exists():
        print(f"ERROR: preflight script not found at {script_path}")
        sys.exit(1)

    result = subprocess.run([sys.executable, str(script_path)], check=False)
    if result.returncode != 0:
        sys.exit(result.returncode)


def cmd_init_dirs(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    research_map = get_research_map(root, config)
    intake = load_markdown(root / config["intake_path"])

    project_title = research_map.get("project", {}).get("title", "Untitled")
    questions = research_map.get("questions", [])
    domain = research_map.get("domain", {}).get("name", "Unknown")
    data_files = research_map.get("data", {}).get("files", [])
    q_count = len(questions)
    file_count = len(data_files)
    today = datetime.now().strftime("%Y-%m-%d")

    researcher = "Unknown"
    institution = "Unknown"
    for line in intake.split("\n"):
        stripped = line.strip()
        if stripped.startswith("**Researcher**"):
            researcher = stripped.split(":", 1)[-1].strip().strip("[]")
        elif stripped.startswith("**Institution**"):
            institution = stripped.split(":", 1)[-1].strip().strip("[]")

    dirs = {
        "docs": f"# Research Documentation — {project_title}\n\n> Auto-generated by Research Copilot.\n\n## Project\n- **Researcher**: {researcher}\n- **Institution**: {institution}\n- **Domain**: {domain}\n- **Questions**: {q_count}\n- **Data files**: {file_count}\n- **Started**: {today}",
        "docs/iterations": f"# Research Iterations — {project_title}\n\nEach iteration documents a distinct phase of analysis.",
        "docs/decisions": f"# Methodological Decisions — {project_title}\n\nEvery significant methodological choice is documented here.",
        "docs/dead_ends": f"# Dead Ends — {project_title}\n\nApproaches that were tried and abandoned.",
        "reports": f"# Analysis Reports — {project_title}\n\n> All analysis outputs organized by type and research question.",
        "reports/baseline": f"# Baseline — {project_title}\n\nInitial research map and feasibility assessment.",
        "reports/literature": f"# Literature Review — {project_title}\n\n## Files\n- `literature_corpus.json`\n- `evidence_matrix.md`\n- `gap_analysis.md`",
        "reports/analysis": f"# Analysis Results — {project_title}\n\nResults organized by research question.",
        "reports/figures": f"# Figures — {project_title}\n\nAll generated plots, organized by research question.",
        "reports/tables": f"# Tables — {project_title}\n\nAll generated tables, organized by research question.",
        "reports/dashboards": f"# Dashboards — {project_title}\n\nInteractive summaries.",
        "reports/manuscript": f"# Manuscript — {project_title}\n\nDraft paper sections.",
        "reports/audit": f"# Audit Reports — {project_title}\n\nMulti-dimensional audit reports.",
        "reports/summary": f"# Summary — {project_title}\n\nExecutive summaries and key findings.",
        "data": f"# Data Pipeline — {project_title}\n\nRaw data in `inputs/data/raw/`. This directory contains processed versions.",
        "data/01_ingested": f"# Ingested Data — {project_title}\n\nRaw data cleaned and standardized.",
        "data/02_processed": f"# Processed Data — {project_title}\n\nData merged, filtered, and transformed.",
        "data/03_analytical": f"# Analytical Data — {project_title}\n\nFinal analysis-ready datasets.",
        "scripts": f"# Analysis Scripts — {project_title}\n\nReproducible code for the entire analysis pipeline.",
    }

    created = []
    for dir_path, readme_content in dirs.items():
        full_path = root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        readme_path = full_path / "README.md"
        with open(readme_path, "w") as f:
            f.write(readme_content)
        created.append(dir_path)

    manifest = {
        "schema_version": "6.0.0",
        "project": {"title": project_title, "researcher": researcher, "institution": institution, "domain": domain},
        "created": today,
        "last_updated": today,
        "structure": {path: "Created by research_init" for path in dirs.keys()},
        "iterations": [{"id": "001", "type": "initial_setup", "trigger": "research_init agent executed", "date": today, "status": "complete", "summary": "Full directory structure created, intake parsed, data scanned"}],
        "current_phase": "research_init",
        "total_iterations": 1,
        "research_questions": q_count,
        "data_files": file_count,
    }
    manifest_path = root / config.get("manifest", "docs/manifest.json")
    save_json(manifest_path, manifest)

    log_path = root / config.get("research_log", "docs/research_log.md")
    with open(log_path, "w") as f:
        f.write(f"# Research Log — {project_title}\n\n> Chronological record of ALL research activity.\n\n## Log\n\n### {today} — Initial Setup\n- **Agent**: research_init\n- **Action**: Parsed intake, scanned data, created project structure\n- **Questions**: {q_count} research questions identified\n- **Data**: {file_count} files found in inputs/data/raw/\n- **Feasibility**: {research_map.get('feasibility', {}).get('verdict', 'unknown')}\n- **Next step**: Continue through the pipeline\n")

    method_path = root / config.get("methodology", "docs/methodology.md")
    with open(method_path, "w") as f:
        f.write(f"# Methodology — {project_title}\n\n> Methods used and WHY they were chosen.\n\n## Current Methods\nMethods will be selected based on question types during method_route phase.\n")

    changelog_path = root / config.get("changelog", "docs/changelog.md")
    with open(changelog_path, "w") as f:
        f.write(f"# Changelog — {project_title}\n\n> What changed between iterations.\n\n## {today} — Initial Setup\n- Created full directory structure ({len(created)} directories)\n- Parsed {q_count} research questions\n- Scanned {file_count} data files\n")

    registry_path = root / config.get("iteration_registry", "docs/iterations/registry.json")
    save_json(registry_path, {
        "schema_version": "6.0.0",
        "project": project_title,
        "iterations": [{"id": "001", "type": "initial_setup", "trigger": "research_init agent", "date": today, "status": "complete", "summary": "Initial project structure created, intake parsed, data scanned"}],
        "total": 1,
        "current_iteration": "001"
    })

    cache_map = root / config["cache_research_map"]
    if cache_map.exists():
        dest = root / config["research_map"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cache_map, dest)

    print("=" * 60)
    print("DIRECTORY STRUCTURE CREATED")
    print("=" * 60)
    print()
    print(f"  Project: {project_title}")
    print(f"  Directories created: {len(created)}")
    for d in created:
        print(f"    ✓ {d}/")
    print()
    print(f"  Files created:")
    print(f"    ✓ docs/manifest.json")
    print(f"    ✓ docs/research_log.md")
    print(f"    ✓ docs/methodology.md")
    print(f"    ✓ docs/changelog.md")
    print(f"    ✓ docs/iterations/registry.json")
    print(f"    ✓ reports/baseline/research_map.json (copied from cache)")
    print()
    print(f"  Next: Continue with the pipeline agents.")
    print()
