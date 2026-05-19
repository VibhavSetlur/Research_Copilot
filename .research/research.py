#!/usr/bin/env python3
"""Research Copilot CLI — context retrieval and project management for AI agents.

Design principle: The CLI NEVER creates output directories (docs/, reports/, data/, scripts/).
It only stores working cache in .research/cache/. The AI agent creates all output directories.
"""

import argparse
import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    yaml = None


def find_project_root():
    """Find project root by looking for .research/ directory."""
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


def load_yaml(path):
    """Load YAML file, return dict or empty dict."""
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


def load_json(path):
    """Load JSON file, return dict or empty dict."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_markdown(path):
    """Load markdown file, return text or empty string."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def save_json(path, data):
    """Save dict to JSON file, creating parent dirs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_config(root):
    """Load config with defaults."""
    config = load_yaml(root / ".research" / "config.yaml")
    defaults = {
        "default_workflow": "quick_exploratory",
        "intake_path": "inputs/intake.md",
        "data_raw": "inputs/data/raw",
        "context_dir": "inputs/context",
        "papers_dir": "inputs/papers",
        # CLI cache (inside .research/, never creates top-level dirs)
        "cache_dir": ".research/cache",
        "cache_research_map": ".research/cache/research_map.json",
        "cache_followups": ".research/cache/follow_up_questions.md",
        # AI-created output paths (checked for existence, not created by CLI)
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


def get_research_map(root, config):
    """Get research map from AI output or CLI cache."""
    # First check AI-created location
    ai_map = load_json(root / config["research_map"])
    if ai_map:
        return ai_map
    # Fall back to CLI cache
    return load_json(root / config["cache_research_map"])


def cmd_status(args):
    """Show project state, current phase, and next step."""
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

    # Check if AI has created the output structure
    docs_exists = (root / "docs").exists()
    reports_exists = (root / "reports").exists()
    data_pipeline_exists = (root / "data").exists()
    scripts_exists = (root / "scripts").exists()

    # Check progress using AI-created output paths
    def has_content(dir_path):
        """Check if directory has files other than README.md and .gitkeep."""
        if not dir_path.exists():
            return False
        for f in dir_path.iterdir():
            if f.is_file() and f.name not in ("README.md", ".gitkeep"):
                return True
        # Also check subdirectories
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
        "compile_outputs": (root / "reports/manuscript/research_findings.md").exists(),
        "audit_validate": (root / "reports/audit/full_audit_report.md").exists(),
    }

    pending = [p for p, done in phases.items() if not done]
    next_phase = pending[0] if pending else None

    print("=" * 60)
    print("RESEARCH PROJECT STATUS")
    print("=" * 60)
    print()

    # Project info
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

    # Directory structure status
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

    # Iteration info
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

    # Docs detail
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
    """Show the research map (grounding context)."""
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
    """Show intake form status."""
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


def cmd_skills(args):
    """List skills or show a specific skill."""
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    skills_dir = root / ".research" / "skills"

    if args.name:
        found = None
        for f in skills_dir.rglob("*.md"):
            if f.stem == args.name:
                found = f
                break
        if not found:
            print(f"Skill '{args.name}' not found.")
            print("Available skills:")
            for f in sorted(skills_dir.rglob("*.md")):
                if f.name != "SKILL_TEMPLATE.md":
                    print(f"  {f.parent.name}/{f.stem}")
            return
        print(f"--- {found} ---")
        print(load_markdown(found))
    else:
        print("=" * 60)
        print("SKILLS")
        print("=" * 60)
        print()
        for cat_dir in sorted(skills_dir.iterdir()):
            if cat_dir.is_dir() and cat_dir.name != "__pycache__":
                skills = [f.stem for f in cat_dir.glob("*.md") if f.name != "SKILL_TEMPLATE.md"]
                if skills:
                    print(f"  {cat_dir.name}/")
                    for s in sorted(skills):
                        print(f"    - {s}")
                    print()
        print("  Use: research skill <name> to view a skill")


def cmd_agents(args):
    """List agents or show a specific agent."""
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    agents_dir = root / ".research" / "agents"

    if args.name:
        agent_file = agents_dir / f"{args.name}.md"
        if not agent_file.exists():
            print(f"Agent '{args.name}' not found.")
            return
        print(f"--- {agent_file} ---")
        print(load_markdown(agent_file))
    else:
        print("=" * 60)
        print("AGENTS")
        print("=" * 60)
        print()
        for f in sorted(agents_dir.glob("*.md")):
            if f.name.startswith("00_"):
                continue
            content = load_markdown(f)
            desc = ""
            for line in content.split("\n")[:10]:
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip().strip('"')
                    break
            name = f.stem.split("_", 1)[1] if "_" in f.stem else f.stem
            print(f"  {name}")
            if desc:
                print(f"    {desc}")
            print()
        print("  Use: research agent <name> to view an agent")


def cmd_workflow(args):
    """Show current workflow and next steps."""
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    workflow_id = config["default_workflow"]
    workflow_file = root / ".research" / "workflows" / f"{workflow_id}.yaml"
    workflow = load_yaml(workflow_file)

    print("=" * 60)
    print(f"WORKFLOW: {workflow.get('name', workflow_id)}")
    print("=" * 60)
    print()
    print(f"  {workflow.get('description', '')}")
    print()

    agents = workflow.get("agents", [])
    print("  Pipeline:")
    for i, agent in enumerate(agents):
        print(f"    {i+1}. {agent}")
    print()

    iter_support = workflow.get("iteration_support", {})
    if iter_support.get("enabled"):
        print("  Iteration Support:")
        print(f"    Agent: {iter_support.get('agent', 'research_iterate')}")
        loop_points = iter_support.get("loop_points", [])
        for lp in loop_points:
            print(f"    After {lp.get('after', '?')}:")
            for opt in lp.get("options", []):
                if isinstance(opt, dict):
                    for k, v in opt.items():
                        print(f"      - {k}: {v}")
                else:
                    print(f"      - {opt}")
        print()

    branching = workflow.get("branching", [])
    if branching:
        print("  Branching rules:")
        for b in branching:
            print(f"    - after {b.get('after', '?')}: if {b.get('if', '?')} → {b.get('then', '?')}")
        print()

    feedback = workflow.get("feedback", [])
    if feedback:
        print("  Feedback loops:")
        for fb in feedback:
            print(f"    - {fb.get('from', '?')} → {fb.get('to', '?')} when {fb.get('when', '?')}")
        print()


def cmd_iterations(args):
    """Show iteration history."""
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    registry = load_json(root / config.get("iteration_registry", "docs/iterations/registry.json"))

    print("=" * 60)
    print("RESEARCH ITERATIONS")
    print("=" * 60)
    print()

    if not registry:
        print("  No iterations yet. Run research_init first.")
        print()
        return

    project = registry.get("project", "Unknown")
    total = registry.get("total", 0)
    current = registry.get("current_iteration", "000")

    print(f"  Project: {project}")
    print(f"  Total iterations: {total}")
    print(f"  Current: {current}")
    print()

    iterations = registry.get("iterations", [])
    for it in iterations:
        status_marker = "✓" if it.get("status") == "complete" else "○"
        print(f"  {status_marker} #{it['id']}: {it['type']}")
        print(f"     Trigger: {it.get('trigger', 'N/A')}")
        print(f"     Date: {it.get('date', 'N/A')}")
        if it.get("summary"):
            print(f"     Summary: {it['summary']}")
        if it.get("decision"):
            print(f"     Decision: {it['decision']}")
        print()


def cmd_followups(args):
    """Show follow-up questions for the user."""
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    research_map = get_research_map(root, config)
    map_followups = research_map.get("follow_up", [])

    followup_file = root / config["follow_up_questions"]
    followup = load_markdown(followup_file)
    if not followup:
        followup_file = root / config.get("cache_followups", ".research/cache/follow_up_questions.md")
        followup = load_markdown(followup_file)

    print("=" * 60)
    print("FOLLOW-UP QUESTIONS")
    print("=" * 60)
    print()

    if map_followups:
        for q in map_followups:
            print(f"  - {q}")
        print()

    if followup and "[Your answer]" not in followup:
        print("--- follow_up_questions.md ---")
        print(followup)
    elif not map_followups:
        print("  No follow-up questions. Intake is complete.")
    print()


def cmd_scan(args):
    """Scan inputs/ and save research map to .research/cache/. Does NOT create output directories."""
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    intake = load_markdown(root / config["intake_path"])

    data_dir = root / config["data_raw"]
    data_files = []
    if data_dir.exists():
        for f in data_dir.iterdir():
            if f.is_file() and not f.name.startswith("."):
                ext = f.suffix.lower()
                fmt_map = {
                    ".csv": "CSV", ".tsv": "TSV", ".parquet": "Parquet",
                    ".xlsx": "Excel", ".xls": "Excel", ".json": "JSON",
                    ".sav": "SPSS", ".dta": "Stata", ".sas7bdat": "SAS",
                    ".feather": "Feather", ".h5": "HDF5", ".hdf5": "HDF5",
                }
                data_files.append({
                    "path": str(f.relative_to(root)),
                    "format": fmt_map.get(ext, ext.lstrip(".").upper()),
                    "size_kb": round(f.stat().st_size / 1024, 1),
                })

    context_dir = root / config["context_dir"]
    context_files = []
    if context_dir.exists():
        for f in context_dir.iterdir():
            if f.is_file() and not f.name.startswith("."):
                context_files.append(str(f.relative_to(root)))

    papers_dir = root / config["papers_dir"]
    paper_count = len(list(papers_dir.glob("*.pdf"))) if papers_dir.exists() else 0

    # Parse all research questions from intake
    questions = []
    lines = intake.split("\n")
    current_q = None
    for line in lines:
        if line.startswith("### Question ") or line.startswith("## Question "):
            if current_q:
                questions.append(current_q)
            current_q = {"text": "", "type": "unknown", "hypothesis": "", "outcome": "", "predictor": "", "covariates": "", "files": "", "prep": "", "prior": ""}
            parts = line.split(":", 1)
            if len(parts) > 1:
                current_q["text"] = parts[1].strip()
            continue
        if current_q:
            if line.startswith("### ") and "Question" not in line:
                continue
            if line.startswith("## ") and "Question" not in line:
                break
            stripped = line.strip()
            if stripped.startswith("**Question**"):
                current_q["text"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Type**"):
                current_q["type"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Hypothesis**"):
                current_q["hypothesis"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Outcome variable"):
                current_q["outcome"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Predictor variable"):
                current_q["predictor"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Covariates"):
                current_q["covariates"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Data files"):
                current_q["files"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Data prep"):
                current_q["prep"] = stripped.split(":", 1)[-1].strip().strip("[]")
            elif stripped.startswith("**Prior research"):
                current_q["prior"] = stripped.split(":", 1)[-1].strip().strip("[]")
    if current_q and current_q["text"]:
        questions.append(current_q)

    # Extract project info
    project_title = ""
    domain = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("**Title**"):
            project_title = stripped.split(":", 1)[-1].strip().strip("[]")
        elif stripped.startswith("**Field**"):
            domain = stripped.split(":", 1)[-1].strip().strip("[]")

    question_summary = f"{len(questions)} question(s)" if questions else "N/A"

    research_map = {
        "schema_version": "6.0.0",
        "project": {"title": project_title},
        "questions": questions,
        "data": {
            "files": data_files,
        },
        "domain": {"name": domain, "reporting_standard": ""},
        "literature": {
            "user_findings": [],
            "papers_provided": paper_count,
        },
        "constraints": {"target": "", "timeline": "", "ethics_notes": ""},
        "feasibility": {
            "verdict": "go" if data_files and questions else "caution",
            "blockers": [],
        },
        "follow_up": [],
    }

    if not data_files:
        research_map["feasibility"]["verdict"] = "caution"
        research_map["follow_up"].append("No data files found in inputs/data/raw/. Add your data files there.")
    if not questions:
        research_map["feasibility"]["verdict"] = "caution"
        research_map["follow_up"].append("No research questions found in intake. Fill in inputs/intake.md.")

    # Save to CLI cache (inside .research/, no new top-level dirs)
    cache_path = root / config["cache_research_map"]
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(research_map, f, indent=2)

    print("=" * 60)
    print("SCAN COMPLETE")
    print("=" * 60)
    print()
    print(f"  Project: {project_title or 'Untitled'}")
    print(f"  Research questions: {question_summary}")
    for i, q in enumerate(questions[:3]):
        marker = "(Primary)" if "Primary" in q.get("text", "") or i == 0 else ""
        print(f"    Q{i+1}: {q['text'][:80]}{'...' if len(q['text']) > 80 else ''} {marker}")
    if len(questions) > 3:
        print(f"    ... and {len(questions) - 3} more")
    print()
    print(f"  Data files found: {len(data_files)}")
    for df in data_files:
        print(f"    - {df['path']} ({df['format']}, {df['size_kb']} KB)")
    print(f"  Context files: {len(context_files)}")
    for cf in context_files:
        print(f"    - {cf}")
    print(f"  Papers (PDF): {paper_count}")
    print()
    if domain:
        print(f"  Domain: {domain}")
        print()
    print(f"  Feasibility: {research_map['feasibility']['verdict']}")
    print()
    print(f"  Research map saved to: {cache_path}")
    print(f"  NOTE: Output directories (docs/, reports/, data/, scripts/) are NOT created.")
    print(f"  The AI agent (research_init) will create them when you run it.")
    print()

    if research_map["follow_up"]:
        print("  Follow-up:")
        for q in research_map["follow_up"]:
            print(f"    - {q}")
        print()


def cmd_init_dirs(args):
    """Create the full output directory structure with README.md in each.
    This is what the AI agent does during research_init. Can also be run manually.
    """
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

    # Parse intake for researcher info
    researcher = "Unknown"
    institution = "Unknown"
    for line in intake.split("\n"):
        stripped = line.strip()
        if stripped.startswith("**Researcher**"):
            researcher = stripped.split(":", 1)[-1].strip().strip("[]")
        elif stripped.startswith("**Institution**"):
            institution = stripped.split(":", 1)[-1].strip().strip("[]")

    # Define directory structure: (path, readme_content)
    dirs = {
        "docs": f"""# Research Documentation — {project_title}

> Auto-generated by Research Copilot. Updated each iteration.

## Project Overview
- **Researcher**: {researcher}
- **Institution**: {institution}
- **Domain**: {domain}
- **Questions**: {q_count} research questions
- **Data files**: {file_count} files in inputs/data/raw/
- **Started**: {today}
- **Last updated**: {today}

## Research Questions
{chr(10).join(f"- **Q{i+1}**: {q.get('text', 'N/A')}" for i, q in enumerate(questions))}

## Directory Guide
| Directory | Purpose |
|-----------|---------|
| `iterations/` | Log of each research iteration |
| `decisions/` | Key methodological decisions with rationale |
| `dead_ends/` | Approaches tried and abandoned |
| `research_log.md` | Chronological log of ALL research activity |
| `methodology.md` | Methods used and WHY |
| `changelog.md` | What changed between iterations |
| `manifest.json` | Machine-readable directory registry |
""",
        "docs/iterations": f"""# Research Iterations — {project_title}

Each iteration documents a distinct phase of analysis.

## Current Iterations
| ID | Type | Trigger | Date | Status |
|----|------|---------|------|--------|
| — | — | — | — | — |

## How Iterations Work
1. Each iteration gets a numbered file: `iteration_XXX_[type].md`
2. Documents: what was tried, why, results, decision
3. Registry (`registry.json`) tracks all iterations
4. Previous iterations are NEVER deleted
""",
        "docs/decisions": f"""# Methodological Decisions — {project_title}

Every significant methodological choice is documented here.

## Decision Log
| ID | Decision | Rationale | Date |
|----|----------|-----------|------|
| — | — | — | — |
""",
        "docs/dead_ends": f"""# Dead Ends — {project_title}

Approaches that were tried and abandoned.

## Documented Dead Ends
| ID | Approach | Why Abandoned | Date |
|----|----------|---------------|------|
| — | — | — | — |

## Principle
A negative result is still a result. Document everything.
""",
        "reports": f"""# Analysis Reports — {project_title}

> All analysis outputs organized by type and research question.

## Structure
| Directory | Contents |
|-----------|----------|
| `baseline/` | Initial research map, follow-up questions |
| `literature/` | Literature corpus, evidence matrix |
| `analysis/` | Results by research question |
| `figures/` | Generated plots |
| `tables/` | Generated tables |
| `dashboards/` | Interactive summaries |
| `manuscript/` | Draft paper sections |
| `audit/` | Multi-dimensional audit reports |
| `summary/` | Key findings, executive summary |

## Status
- **Questions analyzed**: 0/{q_count}
- **Last updated**: {today}
""",
        "reports/baseline": f"""# Baseline — {project_title}

Initial research map and feasibility assessment.

## Files
- `research_map.json` — Machine-readable project state
- `follow_up_questions.md` — Questions needing user input
""",
        "reports/literature": f"""# Literature Review — {project_title}

## Files
- `literature_corpus.json` — Structured literature database
- `evidence_matrix.md` — Findings from prior work
- `gap_analysis.md` — Where our work fits

## Status
- **Papers reviewed**: 0
- **Last updated**: {today}
""",
        "reports/analysis": f"""# Analysis Results — {project_title}

Results organized by research question.

## Questions
{chr(10).join(f"- **Q{i+1}**: {q.get('text', 'N/A')[:60]}{'...' if len(q.get('text', '')) > 60 else ''}" for i, q in enumerate(questions))}

## Status
| Question | Status | Last Updated |
|----------|--------|-------------|
{chr(10).join(f"| Q{i+1} | pending | — |" for i in range(q_count))}
""",
        "reports/figures": f"""# Figures — {project_title}

All generated plots, organized by research question.

## Figure Index
| ID | Question | Description | File | Date |
|----|----------|-------------|------|------|
| — | — | — | — | — |

## Conventions
- Named: `fig_XXX_[question]_[description].[ext]`
""",
        "reports/tables": f"""# Tables — {project_title}

All generated tables, organized by research question.

## Table Index
| ID | Question | Description | File | Date |
|----|----------|-------------|------|------|
| — | — | — | — | — |

## Conventions
- Named: `tbl_XXX_[question]_[description].[ext]`
""",
        "reports/dashboards": f"""# Dashboards — {project_title}

Interactive summaries (if applicable).
""",
        "reports/manuscript": f"""# Manuscript — {project_title}

Draft paper sections.

## Sections
| Section | Status | Last Updated |
|---------|--------|-------------|
| Abstract | not started | — |
| Introduction | not started | — |
| Methods | not started | — |
| Results | not started | — |
| Discussion | not started | — |
| Limitations | not started | — |
| References | not started | — |

## Target Venue
[from intake]
""",
        "reports/audit": f"""# Audit Reports — {project_title}

Multi-dimensional audit reports.
""",
        "reports/summary": f"""# Summary — {project_title}

Executive summaries and key findings.

## Files
- `key_findings.md` — Bullet-point summary
- `executive_summary.md` — Narrative summary
- `next_steps.md` — Recommended follow-ups
""",
        "data": f"""# Data Pipeline — {project_title}

Raw data in `inputs/data/raw/`. This directory contains processed versions.

## Pipeline Stages
| Stage | Directory | Purpose |
|-------|-----------|---------|
| Raw | `inputs/data/raw/` | Original files (never modified) |
| Ingested | `01_ingested/` | Cleaned, standardized |
| Processed | `02_processed/` | Merged, filtered, transformed |
| Analytical | `03_analytical/` | Analysis-ready datasets |

## Data Files
{chr(10).join(f"- {f['path']} ({f['format']}, {f['size_kb']} KB)" for f in data_files) if data_files else "(none yet)"}
""",
        "data/01_ingested": f"""# Ingested Data — {project_title}

Raw data cleaned and standardized.

## Transformations Applied
- [ ] Encoding standardized
- [ ] Column names normalized
- [ ] Missing values coded
- [ ] Date formats standardized
""",
        "data/02_processed": f"""# Processed Data — {project_title}

Data merged, filtered, and transformed.
""",
        "data/03_analytical": f"""# Analytical Data — {project_title}

Final analysis-ready datasets. One per research question.
""",
        "scripts": f"""# Analysis Scripts — {project_title}

Reproducible code for the entire analysis pipeline.

## Execution Order
| Order | Script | Purpose | Status |
|-------|--------|---------|--------|
| 1 | `01_data_prep.py` | Data cleaning | not started |
| 2 | `02_analysis.py` | Statistical analysis | not started |
| 3 | `03_figures.py` | Generate figures | not started |
| 4 | `04_tables.py` | Generate tables | not started |
""",
        "scripts/utils": f"""# Utility Functions — {project_title}

Shared helper functions.
""",
    }

    created = []
    for dir_path, readme_content in dirs.items():
        full_path = root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        readme_path = full_path / "README.md"
        with open(readme_path, "w") as f:
            f.write(readme_content)
        created.append(dir_path)

    # Create manifest.json
    manifest = {
        "schema_version": "6.0.0",
        "project": {
            "title": project_title,
            "researcher": researcher,
            "institution": institution,
            "domain": domain,
        },
        "created": today,
        "last_updated": today,
        "structure": {path: "Created by research_init" for path in dirs.keys()},
        "iterations": [
            {
                "id": "001",
                "type": "initial_setup",
                "trigger": "research_init agent executed",
                "date": today,
                "status": "complete",
                "summary": "Full directory structure created, intake parsed, data scanned"
            }
        ],
        "current_phase": "research_init",
        "total_iterations": 1,
        "research_questions": q_count,
        "data_files": file_count,
    }
    manifest_path = root / config.get("manifest", "docs/manifest.json")
    save_json(manifest_path, manifest)

    # Create research_log.md
    log_path = root / config.get("research_log", "docs/research_log.md")
    with open(log_path, "w") as f:
        f.write(f"""# Research Log — {project_title}

> Chronological record of ALL research activity.

## Log

### {today} — Initial Setup
- **Agent**: research_init
- **Action**: Parsed intake, scanned data, created project structure
- **Questions**: {q_count} research questions identified
- **Data**: {file_count} files found in inputs/data/raw/
- **Feasibility**: {research_map.get('feasibility', {}).get('verdict', 'unknown')}
- **Next step**: Continue through the pipeline
""")

    # Create methodology.md
    method_path = root / config.get("methodology", "docs/methodology.md")
    with open(method_path, "w") as f:
        f.write(f"""# Methodology — {project_title}

> Methods used and WHY they were chosen. Updated each iteration.

## Current Methods
Methods will be selected based on question types during method_route phase.

## Question Types
{chr(10).join(f"- **Q{i+1}**: {q.get('type', 'unknown')}" for i, q in enumerate(questions))}
""")

    # Create changelog.md
    changelog_path = root / config.get("changelog", "docs/changelog.md")
    with open(changelog_path, "w") as f:
        f.write(f"""# Changelog — {project_title}

> What changed between iterations.

## {today} — Initial Setup
- Created full directory structure ({len(created)} directories)
- Parsed {q_count} research questions
- Scanned {file_count} data files
- Feasibility: {research_map.get('feasibility', {}).get('verdict', 'unknown')}
""")

    # Create iteration registry
    registry_path = root / config.get("iteration_registry", "docs/iterations/registry.json")
    save_json(registry_path, {
        "schema_version": "6.0.0",
        "project": project_title,
        "iterations": [
            {
                "id": "001",
                "type": "initial_setup",
                "trigger": "research_init agent",
                "date": today,
                "status": "complete",
                "summary": "Initial project structure created, intake parsed, data scanned"
            }
        ],
        "total": 1,
        "current_iteration": "001"
    })

    # Copy research map from cache to reports/baseline/
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


def cmd_validate(args):
    """Run quality gate check for a specific phase."""
    root = find_project_root()
    if not root:
        print("ERROR: No .research/ directory found.")
        sys.exit(1)

    config = get_config(root)
    research_map = get_research_map(root, config)

    phase = args.phase if args.phase else None

    gates = {
        "research_init": {
            "name": "Research Init",
            "checks": [
                ("Intake filled", lambda: bool(load_markdown(root / config["intake_path"]) and "[Your answer]" not in load_markdown(root / config["intake_path"]))),
                ("Research questions defined", lambda: len(research_map.get("questions", [])) > 0),
                ("Data files exist", lambda: len(research_map.get("data", {}).get("files", [])) > 0),
                ("Research map created", lambda: (root / config["research_map"]).exists()),
                ("Feasibility verdict assigned", lambda: bool(research_map.get("feasibility", {}).get("verdict"))),
                ("Directory: docs/", lambda: (root / "docs").exists()),
                ("Directory: reports/", lambda: (root / "reports").exists()),
                ("Directory: data/", lambda: (root / "data").exists()),
                ("Directory: scripts/", lambda: (root / "scripts").exists()),
                ("manifest.json exists", lambda: (root / config.get("manifest", "docs/manifest.json")).exists()),
                ("research_log.md exists", lambda: (root / config.get("research_log", "docs/research_log.md")).exists()),
                ("Iteration registry exists", lambda: (root / config.get("iteration_registry", "docs/iterations/registry.json")).exists()),
            ]
        },
        "literature_deep": {
            "name": "Literature Deep",
            "checks": [
                ("Literature corpus exists", lambda: (root / config.get("literature_corpus", "reports/literature/literature_corpus.json")).exists()),
                ("Evidence matrix exists", lambda: (root / config.get("evidence_matrix", "reports/literature/evidence_matrix.md")).exists()),
                ("Gap analysis exists", lambda: (root / config.get("gap_analysis", "reports/literature/gap_analysis.md")).exists()),
                ("Minimum papers met", lambda: _check_min_papers(root, config)),
            ]
        },
        "method_route": {
            "name": "Method Route",
            "checks": [
                ("Analysis plan exists", lambda: (root / config.get("analysis_plan", "reports/analysis/analysis_plan.md")).exists()),
            ]
        },
        "data_scaffold": {
            "name": "Data Scaffold",
            "checks": [
                ("Ingested data exists", lambda: (root / config.get("data_ingested", "data/01_ingested")).exists()),
                ("Processed data exists", lambda: (root / config.get("data_processed", "data/02_processed")).exists()),
                ("Analytical data exists", lambda: (root / config.get("data_analytical", "data/03_analytical")).exists()),
                ("Data lineage recorded", lambda: (root / config.get("data_lineage", "docs/data_lineage.json")).exists()),
            ]
        },
        "execute_analysis": {
            "name": "Execute Analysis",
            "checks": [
                ("Results exist for all questions", lambda: _has_analysis_results(root)),
                ("Figures generated", lambda: bool(list((root / "reports/figures").glob("*.png"))) if (root / "reports/figures").exists() else False),
                ("Tables generated", lambda: bool(list((root / "reports/tables").glob("*"))) if (root / "reports/tables").exists() else False),
            ]
        },
        "compile_outputs": {
            "name": "Compile Outputs",
            "checks": [
                ("Manuscript draft exists", lambda: (root / config.get("manuscript_findings", "reports/manuscript/research_findings.md")).exists()),
                ("Key findings summary exists", lambda: (root / config.get("key_findings", "reports/summary/key_findings.md")).exists()),
                ("Executive summary exists", lambda: (root / config.get("executive_summary", "reports/summary/executive_summary.md")).exists()),
            ]
        },
        "audit_validate": {
            "name": "Audit Validate",
            "checks": [
                ("Full audit report exists", lambda: (root / config.get("full_audit", "reports/audit/full_audit_report.md")).exists()),
            ]
        },
    }

    if phase and phase not in gates:
        print(f"Unknown phase: {phase}")
        print(f"Available phases: {', '.join(gates.keys())}")
        return

    phases_to_check = {phase: gates[phase]} if phase else gates

    for phase_id, gate in phases_to_check.items():
        print("=" * 60)
        print(f"QUALITY GATE: {gate['name'].upper()}")
        print("=" * 60)
        print()

        passed = 0
        failed = 0
        for check_name, check_fn in gate["checks"]:
            try:
                result = check_fn()
                status = "PASS" if result else "FAIL"
                if result:
                    passed += 1
                else:
                    failed += 1
                marker = "✓" if result else "✗"
                print(f"  {marker} {check_name}")
            except Exception as e:
                failed += 1
                print(f"  ✗ {check_name} — ERROR: {e}")

        total = passed + failed
        pct = round(passed / total * 100) if total > 0 else 0
        print()
        print(f"  Result: {passed}/{total} passed ({pct}%)")

        if failed == 0:
            print(f"  Status: PASS — Ready to proceed")
        else:
            print(f"  Status: FAIL — {failed} check(s) must pass before proceeding")
        print()


def _check_min_papers(root, config):
    """Check if minimum paper count is met."""
    corpus_path = root / config.get("literature_corpus", "reports/literature/literature_corpus.json")
    if not corpus_path.exists():
        return False
    corpus = load_json(corpus_path)
    papers = corpus.get("papers", [])
    min_papers = config.get("literature_min_papers", 10)
    return len(papers) >= min_papers


def _has_analysis_results(root):
    """Check if analysis results exist for all questions."""
    analysis_dir = root / "reports/analysis"
    if not analysis_dir.exists():
        return False
    q_dirs = [d for d in analysis_dir.iterdir() if d.is_dir() and d.name.startswith("q")]
    return len(q_dirs) > 0


def main():
    parser = argparse.ArgumentParser(
        description="Research Copilot CLI — context retrieval for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  status          Show project state, directory structure, next step
  map             Show the research map (grounding context)
  intake          Show intake form status
  scan            Scan inputs/, save research map to .research/cache/
  init-dirs       Create full output directory structure (AI does this)
  validate [phase]  Run quality gate check (all phases or specific)
  skills          List all skills
  skill <name>    Show a specific skill
  agents          List all agents
  agent <name>    Show a specific agent
  workflow        Show current workflow + iteration support
  followups       Show follow-up questions
  iterations      Show iteration history

Design:
  - CLI stores working data in .research/cache/ (no new top-level dirs)
  - AI agent (research_init) creates all output directories
  - Run 'research init-dirs' to create dirs manually if needed
  - Run 'research validate' to check phase completion

Examples:
  research status
  research scan
  research init-dirs
  research validate research_init
  research validate
  research skill profile_tabular
  research agent research_init
  research agent literature_pipeline
  research map
  research iterations
        """,
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show project state and next step")
    sub.add_parser("map", help="Show research map")
    sub.add_parser("intake", help="Show intake form status")
    sub.add_parser("scan", help="Scan inputs/, save to cache")
    sub.add_parser("init-dirs", help="Create full output directory structure")

    p_skill = sub.add_parser("skill", help="Show a specific skill")
    p_skill.add_argument("name", help="Skill name")
    sub.add_parser("skills", help="List all skills by category")

    p_agent = sub.add_parser("agent", help="Show a specific agent")
    p_agent.add_argument("name", help="Agent name")
    sub.add_parser("agents", help="List all agents")

    sub.add_parser("workflow", help="Show current workflow")
    sub.add_parser("followups", help="Show follow-up questions")
    sub.add_parser("iterations", help="Show iteration history")

    p_validate = sub.add_parser("validate", help="Run quality gate check")
    p_validate.add_argument("phase", nargs="?", help="Phase to validate (or all if omitted)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "skill":
        cmd_skills(argparse.Namespace(name=args.name))
    elif args.command == "skills":
        cmd_skills(argparse.Namespace(name=None))
    elif args.command == "agent":
        cmd_agents(argparse.Namespace(name=args.name))
    elif args.command == "agents":
        cmd_agents(argparse.Namespace(name=None))
    else:
        commands = {
            "status": cmd_status,
            "map": cmd_map,
            "intake": cmd_intake,
            "scan": cmd_scan,
            "init-dirs": cmd_init_dirs,
            "workflow": cmd_workflow,
            "followups": cmd_followups,
            "iterations": cmd_iterations,
            "validate": cmd_validate,
        }
        commands[args.command](args)


if __name__ == "__main__":
    main()
