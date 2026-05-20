"""Analysis commands: validate, debug, parallel, export, dashboard."""
import json
import subprocess
import sys
from pathlib import Path

from core.utils import (
    find_project_root, load_json, load_markdown, get_config,
    get_research_map, require_project_root,
)


def cmd_validate(args):
    root = require_project_root()

    config = get_config(root)
    research_map = get_research_map(root, config)

    phase = args.phase if args.phase else None

    def _check_min_papers():
        corpus_path = root / config.get("literature_corpus", "reports/literature/literature_corpus.json")
        if not corpus_path.exists():
            return False
        corpus = load_json(corpus_path)
        papers = corpus.get("papers", [])
        min_papers = config.get("literature_min_papers", 10)
        return len(papers) >= min_papers

    def _has_analysis_results():
        analysis_dir = root / "reports/analysis"
        if not analysis_dir.exists():
            return False
        q_dirs = [d for d in analysis_dir.iterdir() if d.is_dir() and d.name.startswith("q")]
        return len(q_dirs) > 0

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
                ("Minimum papers met", lambda: _check_min_papers()),
            ]
        },
        "method_route": {
            "name": "Method Route",
            "checks": [
                ("Analysis plan exists", lambda: (root / config.get("analysis_plan", "reports/analysis/analysis_plan.md")).exists()),
                ("Methods routing JSON exists", lambda: (root / "reports/analysis/methods_routing.json").exists()),
            ]
        },
        "data_scaffold": {
            "name": "Data Scaffold",
            "checks": [
                ("Ingested data exists", lambda: (root / config.get("data_ingested", "data/01_ingested")).exists()),
                ("Processed data exists", lambda: (root / config.get("data_processed", "data/02_processed")).exists()),
                ("Analytical data exists", lambda: (root / config.get("data_analytical", "data/03_analytical")).exists()),
                ("Data lineage recorded", lambda: (root / config.get("data_lineage", "docs/data_lineage.json")).exists()),
                ("Format manifest exists", lambda: (root / config.get("cache_dir", ".research/cache") / "data_format_manifest.json").exists()),
                ("Tool availability report exists", lambda: (root / config.get("cache_dir", ".research/cache") / "tool_availability_report.json").exists()),
            ]
        },
        "execute_analysis": {
            "name": "Execute Analysis",
            "checks": [
                ("Results exist for all questions", lambda: _has_analysis_results()),
                ("Figures generated", lambda: bool(list((root / "reports/figures").glob("*.png"))) if (root / "reports/figures").exists() else False),
                ("Tables generated", lambda: bool(list((root / "reports/tables").glob("*"))) if (root / "reports/tables").exists() else False),
            ]
        },
        "replication_validator": {
            "name": "Replication Validator",
            "checks": [
                ("Replication report exists", lambda: (root / "reports/analysis/replication_validation_report.md").exists()),
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


def cmd_debug(args):
    root = require_project_root()

    script_path = Path(args.script) if Path(args.script).is_absolute() else root / args.script
    if not script_path.exists():
        print(f"ERROR: Script not found: {script_path}")
        sys.exit(1)

    sys.path.insert(0, str(root / ".research" / "scripts" / "utils"))
    from auto_debug import run_auto_debug

    fix_code = None
    if args.apply_fix:
        fix_path = Path(args.apply_fix) if Path(args.apply_fix).is_absolute() else root / args.apply_fix
        fix_code = fix_path.read_text()

    result = run_auto_debug(script_path, max_attempts=args.max_attempts, fix_code=fix_code, fix_func=args.fix_func)
    sys.exit(0 if result["success"] else 1)


def cmd_parallel(args):
    root = require_project_root()

    runner_path = root / ".research" / "scripts" / "utils" / "parallel_runner.py"
    if not runner_path.exists():
        print(f"ERROR: Parallel runner not found at {runner_path}")
        sys.exit(1)

    questions = args.questions or ""
    question_list = [q.strip() for q in questions.split(",") if q.strip()]

    if not question_list:
        print("ERROR: No questions specified. Use --questions q1,q2,q3")
        sys.exit(1)

    workers = args.workers or 4

    try:
        sys.path.insert(0, str(root / ".research" / "core"))
        from hooks import hook_engine
        __import__("interceptors")

        state = {
            "task": f"parallel_execution:{','.join(question_list)}",
            "phase": "execute_analysis",
            "token_budget": {"used": 0, "remaining": 200000, "limit": 200000},
        }
        state = hook_engine.trigger_sync("pre_routing", state)
        if state.get("loaded_skills"):
            print(f"  Loaded {state['skill_count']} relevant skills")
    except ImportError:
        pass

    print(f"Running {len(question_list)} questions in parallel with {workers} workers...")
    print(f"  Questions: {', '.join(question_list)}")
    print()

    cmd = [
        sys.executable, str(runner_path),
        "--questions", ",".join(question_list),
        "--max-workers", str(workers),
        "--state-ledger", str(root / ".research" / "cache" / "state.json"),
    ]

    try:
        result = subprocess.run(cmd, check=True, cwd=str(root))
        print()
        print("Parallel execution complete.")
    except subprocess.CalledProcessError as e:
        print(f"Parallel execution failed with exit code {e.returncode}")
        sys.exit(1)


def cmd_export(args):
    root = require_project_root()

    fmt = args.format or "markdown"
    journal = args.journal

    manuscript = root / "reports" / "manuscript" / "research_findings.md"
    if not manuscript.exists():
        print("ERROR: No manuscript found at reports/manuscript/research_findings.md")
        sys.exit(1)

    if fmt == "latex":
        print("Exporting to LaTeX...")
        try:
            import pypandoc
            output_path = root / "reports" / "manuscript" / "manuscript.tex"
            pypandoc.convert_file(
                str(manuscript), "latex", outputfile=str(output_path),
                extra_args=["--standalone", "--template=article"],
            )
            print(f"  LaTeX file: {output_path}")
        except ImportError:
            print("ERROR: pypandoc not installed. Run: pip install pypandoc")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: LaTeX export failed: {e}")
            sys.exit(1)

    elif fmt == "journal" and journal:
        print(f"Exporting to {journal} format...")
        print("  NOTE: Use the journal_formatter skill for full journal formatting.")
        print(f"  research skill journal_formatter")

    elif fmt == "pdf":
        print("Exporting to PDF...")
        try:
            import pypandoc
            output_path = root / "reports" / "manuscript" / "manuscript.pdf"
            pypandoc.convert_file(str(manuscript), "pdf", outputfile=str(output_path))
            print(f"  PDF file: {output_path}")
        except ImportError:
            print("ERROR: pypandoc not installed. Run: pip install pypandoc")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: PDF export failed: {e}")
            sys.exit(1)

    else:
        print(f"Unknown format: {fmt}")
        print("Supported formats: latex, journal, pdf")
        sys.exit(1)

    print()


def cmd_dashboard(args):
    root = require_project_root()

    dashboard_path = root / ".research" / "scripts" / "research_dashboard.py"
    if not dashboard_path.exists():
        print(f"ERROR: Dashboard script not found at {dashboard_path}")
        sys.exit(1)

    print("Launching Panel dashboard on http://localhost:5006...")
    try:
        subprocess.run(
            [sys.executable, "-m", "panel", "serve", str(dashboard_path), "--port", "5006", "--show"],
            check=True
        )
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    except Exception as e:
        print(f"ERROR launching dashboard: {e}")
        sys.exit(1)
