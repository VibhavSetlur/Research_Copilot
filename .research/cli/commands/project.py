"""Project commands: setup, preflight, init-dirs, status, map, intake."""
import json
import os
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
        "default_workflow": "quick_exploratory",
        "intake_path": "inputs/intake.md",
        "data_raw": "inputs/data/raw",
        "context_dir": "inputs/context",
        "papers_dir": "inputs/papers",
        "cache_dir": ".research/cache",
        "cache_research_map": ".research/cache/research_map.json",
        "cache_followups": ".research/cache/follow_up_questions.md",
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
    ai_map = load_json(root / config["research_map"])
    if ai_map:
        return ai_map
    return load_json(root / config["cache_research_map"])


def _load_format_router(root):
    import importlib.util
    router_path = root / ".research" / "scripts" / "utils" / "format_router.py"
    if not router_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("format_router", router_path)
    if not spec or not spec.loader:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_tool_registry(root, config):
    registries = config.get("registries", {})
    registry_path = registries.get("tool_registry", ".research/domains/tool_registry.json")
    return load_json(root / registry_path)


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

    import subprocess
    result = subprocess.run([sys.executable, str(script_path)], check=False)
    if result.returncode != 0:
        sys.exit(result.returncode)


def cmd_status(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    research_map = get_research_map(root, config)
    intake = load_markdown(root / config["intake_path"])
    manifest = load_json(root / config.get("manifest", "docs/manifest.json"))
    iteration_registry = load_json(root / config.get("iteration_registry", "docs/iterations/registry.json"))

    intake_filled = bool(intake and "[Your answer]" not in intake and "answer these 3" not in intake.lower())

    data_dir = root / config["data_raw"]
    data_files = [f for f in data_dir.iterdir() if f.is_file() and not f.name.startswith(".")] if data_dir.exists() else []

    docs_exists = (root / "docs").exists()
    reports_exists = (root / "reports").exists()
    data_pipeline_exists = (root / "data").exists()
    scripts_exists = (root / "scripts").exists()

    def has_content(dir_path):
        if not dir_path.exists():
            return False
        for f in dir_path.iterdir():
            if f.is_file() and f.name not in ("README.md", ".gitkeep"):
                return True
        for f in dir_path.rglob("*"):
            if f.is_file() and f.name not in ("README.md", ".gitkeep"):
                return True
        return False

    phases = {
        "research_init": (root / config["research_map"]).exists(),
        "literature_deep": (root / "reports/literature/literature_corpus.json").exists(),
        "method_route": (root / "reports/analysis/analysis_plan.md").exists(),
        "data_scaffold": has_content(root / config.get("data_ingested", "data/01_ingested")),
        "execute_analysis": has_content(root / config["data_analytical"]),
        "replication_validator": (root / "reports/analysis/replication_validation_report.md").exists(),
        "compile_outputs": (root / "reports/manuscript/research_findings.md").exists(),
        "audit_validate": (root / "reports/audit/full_audit_report.md").exists(),
    }

    pending = [p for p, done in phases.items() if not done]
    next_phase = pending[0] if pending else None

    print("=" * 60)
    print("RESEARCH PROJECT STATUS")
    print("=" * 60)
    print()

    if research_map:
        project = research_map.get("project", {})
        if project.get("title"):
            print(f"  Project:   {project['title']}")
            print()
        questions = research_map.get("questions", [])
        if questions:
            print(f"  Questions: {len(questions)}")
            for i, q in enumerate(questions[:3]):
                print(f"    Q{i+1}: {q.get('text', 'N/A')[:70]}{'...' if len(q.get('text', '')) > 70 else ''}")
            if len(questions) > 3:
                print(f"    ... and {len(questions) - 3} more")
            print()

    print("  Directory structure:")
    dirs_status = [
        ("docs/", docs_exists, "Research documentation"),
        ("reports/", reports_exists, "Analysis outputs"),
        ("data/", data_pipeline_exists, "Processed data pipeline"),
        ("scripts/", scripts_exists, "Reproducible code"),
    ]
    for path, exists, desc in dirs_status:
        marker = "✓" if exists else "○"
        print(f"    {marker} {path} — {desc}")
    print()

    total_iterations = iteration_registry.get("total", 0)
    current_iter = iteration_registry.get("current_iteration", "000")
    if total_iterations > 0:
        print(f"  Iterations: {total_iterations} (current: {current_iter})")
        iterations = iteration_registry.get("iterations", [])
        for it in iterations[-3:]:
            print(f"    #{it['id']}: {it['type']} — {it.get('summary', '')[:50]}")
        if len(iterations) > 3:
            print(f"    ... and {len(iterations) - 3} more")
        print()

    if docs_exists:
        iter_count = len(list((root / "docs/iterations").glob("iteration_*.md"))) if (root / "docs/iterations").exists() else 0
        decision_count = len(list((root / "docs/decisions").glob("decision_*.md"))) if (root / "docs/decisions").exists() else 0
        dead_end_count = len(list((root / "docs/dead_ends").glob("dead_end_*.md"))) if (root / "docs/dead_ends").exists() else 0
        print(f"  Documentation:")
        print(f"    Research log: {'yes' if (root / 'docs/research_log.md').exists() else 'no'}")
        print(f"    Methodology: {'yes' if (root / 'docs/methodology.md').exists() else 'no'}")
        print(f"    Iterations: {iter_count}")
        print(f"    Decisions: {decision_count}")
        print(f"    Dead ends: {dead_end_count}")
        print()

    if intake_filled:
        print("  Intake:    COMPLETE")
    else:
        print("  Intake:    NOT FILLED — answer inputs/intake.md")
    print()

    print(f"  Data files: {len(data_files)} in {config['data_raw']}/")
    for f in data_files[:5]:
        size = f.stat().st_size / 1024
        print(f"    - {f.name} ({size:.0f} KB)")
    if len(data_files) > 5:
        print(f"    ... and {len(data_files) - 5} more")
    print()

    format_manifest = root / config.get("cache_dir", ".research/cache") / "data_format_manifest.json"
    if format_manifest.exists():
        fmt = load_json(format_manifest)
        print("  Format scan:")
        print(f"    Tabular: {fmt.get('tabular_count', 0)}")
        print(f"    Non-tabular: {fmt.get('non_tabular_count', 0)}")
        print(f"    Manifest: {format_manifest}")
        print()

    tool_report = root / config.get("cache_dir", ".research/cache") / "tool_availability_report.json"
    if tool_report.exists():
        report = load_json(tool_report)
        tools = report.get("tools", [])
        statuses = {}
        for item in tools:
            status = item.get("status", "UNKNOWN")
            statuses[status] = statuses.get(status, 0) + 1
        print("  Tool availability:")
        for status, count in sorted(statuses.items()):
            print(f"    {status}: {count}")
        print(f"    Report: {tool_report}")
        print()

    print("  Pipeline:")
    for phase, done in phases.items():
        marker = "✓" if done else "○"
        print(f"    {marker} {phase}")
    print()

    if next_phase:
        print(f"  Next: run agent '{next_phase}'")
        print(f"  Command: research agent {next_phase}")
        if not docs_exists:
            print(f"  NOTE: Directory structure not yet created. The research_init agent will create it.")
        if total_iterations > 0:
            print(f"  Or iterate: research agent research_iterate")
    else:
        print("  Pipeline complete.")

    if research_map:
        feas = research_map.get("feasibility", {})
        verdict = feas.get("verdict", "unknown")
        if verdict == "stop":
            blockers = feas.get("blockers", [])
            print()
            print("  FEASIBILITY: STOP")
            for b in blockers:
                print(f"    - {b}")
        elif verdict == "caution":
            print()
            print("  FEASIBILITY: CAUTION — review follow_up_questions.md")

    print()


def cmd_map(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    research_map = get_research_map(root, config)

    if not research_map:
        print("No research map yet. Run: research scan")
        return

    print("=" * 60)
    print("RESEARCH MAP")
    print("=" * 60)
    print()

    project = research_map.get("project", {})
    if project.get("title"):
        print(f"  Project: {project['title']}")
        print()

    questions = research_map.get("questions", [])
    if questions:
        print(f"  Research Questions ({len(questions)}):")
        for i, q in enumerate(questions):
            print(f"    Q{i+1}: {q.get('text', 'N/A')}")
            print(f"       Type: {q.get('type', 'unknown')}")
            if q.get("hypothesis"):
                print(f"       Hypothesis: {q['hypothesis']}")
            if q.get("outcome"):
                print(f"       Outcome: {q['outcome']}")
            if q.get("predictor"):
                print(f"       Predictor: {q['predictor']}")
            if q.get("files"):
                print(f"       Data files: {q['files']}")
            if q.get("prep"):
                print(f"       Prep needed: {q['prep']}")
            print()
    else:
        q = research_map.get("question", {})
        print(f"  Question: {q.get('text', 'N/A')}")
        print(f"  Type:     {q.get('type', 'N/A')}")
        print()

    d = research_map.get("data", {})
    files = d.get("files", [])
    print(f"  Data: {len(files)} file(s)")
    for f in files:
        print(f"    - {f.get('path', '?')} ({f.get('format', '?')}, {f.get('size_kb', '?')} KB)")
    print()

    domain = research_map.get("domain", {})
    if domain.get("name"):
        print(f"  Domain: {domain['name']}")
        print()

    feas = research_map.get("feasibility", {})
    print(f"  Feasibility: {feas.get('verdict', 'unknown')}")
    print()

    followup = research_map.get("follow_up", [])
    if followup:
        print(f"  Follow-up questions ({len(followup)}):")
        for q_text in followup:
            print(f"    - {q_text}")
        print()


def cmd_intake(args):
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    intake = load_markdown(root / config["intake_path"])

    if not intake:
        print("No intake form found. Create inputs/intake.md")
        return

    placeholders = ["[Your answer]", "answer these 3", "answer the 3 required"]
    filled = not any(p.lower() in intake.lower() for p in placeholders)

    q_count = intake.count("### Question ")

    print("=" * 60)
    print("INTAKE STATUS")
    print("=" * 60)
    print()
    print(f"  Status: {'COMPLETE' if filled else 'INCOMPLETE'}")
    print(f"  Research questions: {q_count}")
    print()
    print(f"  Location: {config['intake_path']}")
    print()
    if not filled:
        print("  Required sections to fill:")
        print("    - Project title, researcher, institution")
        print("    - At least one research question with type, hypothesis, variables")
        print("    - Data file descriptions")
        print("    - Domain and target output")
    print()
    print("--- intake.md ---")
    print(intake)
