#!/usr/bin/env python3
"""Research Copilot CLI — context retrieval and project management for AI agents.

Design principle: The CLI NEVER creates output directories (docs/, reports/, data/, scripts/).
It only stores working cache in .research/cache/. The AI agent creates all output directories.

Command implementations are in cli/commands/*.py modules.
"""

import argparse
import sys
from pathlib import Path

_core_path = Path(__file__).parent / "core"
_cli_path = Path(__file__).parent
if str(_core_path) not in sys.path:
    sys.path.insert(0, str(_core_path))
if str(_cli_path) not in sys.path:
    sys.path.insert(0, str(_cli_path))

from cli.commands.project import cmd_setup, cmd_preflight, cmd_status, cmd_map, cmd_intake
from cli.commands.scan import cmd_scan, cmd_format_scan
from cli.commands.tools import cmd_tools, cmd_tool
from cli.commands.info import cmd_agents, cmd_skills, cmd_skill_search, cmd_workflow, cmd_iterations, cmd_followups
from cli.commands.tracking import cmd_state, cmd_resume, cmd_budget, cmd_dag, cmd_data_scale, cmd_hooks
from cli.commands.analysis import cmd_validate, cmd_debug, cmd_parallel, cmd_export, cmd_dashboard
from cli.commands.approval import cmd_approve, cmd_reject
from cli.commands.cache import cmd_cache
from cli.commands.citations import cmd_verify_citations, cmd_trace_claims
from cli.commands.init import cmd_init_dirs
from cli.commands.intake_interview import run_intake_interview
from cli.commands.preregistration import generate_preregistration
from cli.commands.reviewer2 import run_reviewer2
from cli.commands.dependency_check import check_dependencies


def main():
    parser = argparse.ArgumentParser(
        description="Research Copilot CLI — context retrieval for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
    preflight       Run environment preflight checks
    setup           First-run setup check
    status          Show project state, directory structure, next step
    map             Show the research map (grounding context)
    intake          Show intake form status
    intake-interview --start  Start conversational intake interview
    intake-interview --message "..."  Reply to interview question
    scan            Scan inputs/, save research map to .research/cache/
    format-scan     Run format router on inputs/data/raw
    init-dirs       Create full output directory structure (AI does this)
    validate [phase]  Run quality gate check (all phases or specific)
    state           Print current state.json ledger
    resume --from <phase>  Resume from checkpoint
    budget          Show token budget usage
    cache stats     Show cache hit rates, size
    cache clear --older-than 7d  Prune old cache entries
    verify-citations  Run citation verification on current bibliography
    trace-claims    Run claim tracer on current manuscript
    parallel --questions q1,q2,q3  Run multiple questions in parallel
    export --format latex --journal nature  Export manuscript
    dashboard       Launch the Panel dashboard on port 5006
    skills          List all skills
    skill <name>    Show a specific skill
    skill-search <query>  Search for matching skills
    agents          List all agents
    agent <name>    Show a specific agent
    tools           List tools from registry
    tool <name>     Show details for a specific tool
    workflow        Show current workflow + iteration support
    followups       Show follow-up questions
    iterations      Show iteration history
    dag             Show execution DAG summary
    dag-viewer      Generate interactive DAG visualization HTML
    data-scale      Show data scale analysis and library constraints
    hooks           Show registered hooks and execution log
    approve         Approve a pending phase gate request
    reject          Reject a pending phase gate request with feedback
    preregistration  Generate OSF-compatible pre-registration document
    reviewer2       Run adversarial 'Reviewer 2' critique
    dependency-check <script>  Check for uninstalled imports
    dependency-check <script> --auto-install  Auto-install missing deps

    Branching:
    branch <name>   Create a new research branch
    branches        List all research branches
    switch <name>   Switch to a different branch
    merge <name>    Merge a branch into target
    abandon <name>  Abandon a research branch

    Intent Routing:
    intent <query>  Route a query through the intent router

    Knowledge Graph:
    graph           Show knowledge graph summary
    graph-stats     Show knowledge graph statistics
    graph-query     Query the knowledge graph

    Semantic File System:
    taxonomy        Show semantic file system taxonomy

    mcp             Start MCP server for AI IDE integration

Design:
  - CLI stores working data in .research/cache/ (no new top-level dirs)
  - AI agent (research_init) creates all output directories
  - Run 'research init-dirs' to create dirs manually if needed
  - Run 'research validate' to check phase completion

Examples:
    research preflight
    research setup
    research status
    research scan
    research format-scan
    research init-dirs
    research validate research_init
    research validate
    research skill profile_tabular
    research agent research_init
    research agent literature_pipeline
    research map
    research iterations
    research dag
        """,
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("setup", help="First-run setup check — verify system is ready")
    sub.add_parser("preflight", help="Run environment preflight checks")
    sub.add_parser("status", help="Show project state and next step")
    sub.add_parser("map", help="Show research map")
    sub.add_parser("intake", help="Show intake form status")
    sub.add_parser("scan", help="Scan inputs/, save to cache")
    sub.add_parser("format-scan", help="Run format router on inputs/data/raw")
    sub.add_parser("init-dirs", help="Create full output directory structure")

    p_skill = sub.add_parser("skill", help="Show a specific skill")
    p_skill.add_argument("name", help="Skill name")
    sub.add_parser("skills", help="List all skills by category")
    p_skill_search = sub.add_parser("skill-search", help="Search for matching skills by query")
    p_skill_search.add_argument("query", help="Search query string")

    p_agent = sub.add_parser("agent", help="Show a specific agent")
    p_agent.add_argument("name", help="Agent name")
    sub.add_parser("agents", help="List all agents")

    sub.add_parser("tools", help="List tools from registry")
    p_tool = sub.add_parser("tool", help="Show a specific tool")
    p_tool.add_argument("name", help="Tool ID")

    sub.add_parser("workflow", help="Show current workflow")
    sub.add_parser("followups", help="Show follow-up questions")
    sub.add_parser("iterations", help="Show iteration history")

    p_validate = sub.add_parser("validate", help="Run quality gate check")
    p_validate.add_argument("phase", nargs="?", help="Phase to validate (or all if omitted)")

    sub.add_parser("state", help="Print current state.json ledger")

    p_resume = sub.add_parser("resume", help="Resume from checkpoint")
    p_resume.add_argument("--from", dest="phase", help="Phase to resume from")

    sub.add_parser("budget", help="Show token budget usage")

    p_approve = sub.add_parser("approve", help="Approve a pending phase gate request")
    p_approve.add_argument("phase", help="Phase to approve")

    p_reject = sub.add_parser("reject", help="Reject a pending phase gate request with feedback")
    p_reject.add_argument("phase", help="Phase to reject")
    p_reject.add_argument("--reason", required=True, help="Reason for rejection")

    sub.add_parser("dashboard", help="Launch the Panel dashboard on port 5006")

    p_debug = sub.add_parser("debug", help="Auto-debug a failing script")
    p_debug.add_argument("script", help="Path to the failing script")
    p_debug.add_argument("--max-attempts", type=int, default=3, help="Max debug attempts")
    p_debug.add_argument("--apply-fix", help="Path to file with fixed function code")
    p_debug.add_argument("--fix-func", help="Name of function to replace")

    p_cache = sub.add_parser("cache", help="Manage research cache")
    p_cache.add_argument("action", choices=["stats", "clear"], help="Cache action")
    p_cache.add_argument("--older-than", help="Clear entries older than this (e.g., 7d, 30d)")

    sub.add_parser("verify-citations", help="Run citation verification on bibliography")
    sub.add_parser("trace-claims", help="Run claim tracer on manuscript")

    p_parallel = sub.add_parser("parallel", help="Run multiple questions in parallel")
    p_parallel.add_argument("--questions", help="Comma-separated question IDs (q1,q2,q3)")
    p_parallel.add_argument("--workers", type=int, default=4, help="Number of parallel workers")

    p_export = sub.add_parser("export", help="Export manuscript in specific format")
    p_export.add_argument("--format", choices=["latex", "journal", "pdf"], default="markdown", help="Export format")
    p_export.add_argument("--journal", help="Target journal name (for journal format)")

    sub.add_parser("hooks", help="Show registered hooks and execution log")
    sub.add_parser("dag", help="Show execution DAG summary")
    sub.add_parser("data-scale", help="Show data scale analysis and library constraints")

    p_intake_interview = sub.add_parser("intake-interview", help="Start conversational intake interview to auto-generate intake.md")
    p_intake_interview.add_argument("--start", action="store_true", help="Start a new interview")
    p_intake_interview.add_argument("--message", help="Response to current interview question")

    p_preregistration = sub.add_parser("preregistration", help="Generate OSF-compatible pre-registration document")
    p_preregistration.add_argument("--hypotheses", nargs="*", help="List of hypotheses to pre-register")
    p_preregistration.add_argument("--analysis-plan", help="Path to analysis plan file")

    p_reviewer2 = sub.add_parser("reviewer2", help="Run adversarial 'Reviewer 2' critique on research findings")
    p_reviewer2.add_argument("--findings-path", help="Path to research findings file")

    p_dep_check = sub.add_parser("dependency-check", help="Check for uninstalled imports and auto-resolve dependencies")
    p_dep_check.add_argument("script", help="Path to Python script to check")
    p_dep_check.add_argument("--auto-install", action="store_true", help="Automatically install missing dependencies")

    p_dag_viewer = sub.add_parser("dag-viewer", help="Generate interactive DAG visualization HTML")
    p_dag_viewer.add_argument("--output", default="reports/dashboards/dag_viewer.html", help="Output HTML path")

    # Branching commands
    p_branch = sub.add_parser("branch", help="Create a new research branch")
    p_branch.add_argument("name", help="Branch name (e.g., hypothesis_B, bayesian_approach)")
    p_branch.add_argument("--hypothesis", default="", help="Research hypothesis for this branch")
    p_branch.add_argument("--from", dest="parent", default=None, help="Parent branch to fork from")

    sub.add_parser("branches", help="List all research branches")

    p_switch = sub.add_parser("switch", help="Switch to a different branch")
    p_switch.add_argument("name", help="Branch to switch to")

    p_merge = sub.add_parser("merge", help="Merge a branch into target")
    p_merge.add_argument("name", help="Branch to merge")
    p_merge.add_argument("--into", default="main", help="Target branch (default: main)")
    p_merge.add_argument("--message", default="", help="Merge commit message")

    p_abandon = sub.add_parser("abandon", help="Abandon a research branch")
    p_abandon.add_argument("name", help="Branch to abandon")
    p_abandon.add_argument("--reason", default="", help="Reason for abandonment")

    # Intent routing command
    p_intent = sub.add_parser("intent", help="Route a query through the intent router")
    p_intent.add_argument("query", help="Natural language query to route")

    # Knowledge graph commands
    sub.add_parser("graph", help="Show knowledge graph summary")
    sub.add_parser("graph-stats", help="Show knowledge graph statistics")

    p_graph_query = sub.add_parser("graph-query", help="Query the knowledge graph")
    p_graph_query.add_argument("--relation", default=None, help="Filter by relation type")
    p_graph_query.add_argument("--subject", default=None, help="Filter by subject")
    p_graph_query.add_argument("--object", default=None, help="Filter by object")
    p_graph_query.add_argument("--confounders", default=None, help="Get confounders for a variable")

    # Semantic filesystem command
    sub.add_parser("taxonomy", help="Show semantic file system taxonomy")

    sub.add_parser("mcp", help="Start the MCP server for AI IDE integration")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "setup": cmd_setup,
        "preflight": cmd_preflight,
        "status": cmd_status,
        "map": cmd_map,
        "intake": cmd_intake,
        "scan": cmd_scan,
        "format-scan": cmd_format_scan,
        "init-dirs": cmd_init_dirs,
        "workflow": cmd_workflow,
        "followups": cmd_followups,
        "iterations": cmd_iterations,
        "tools": cmd_tools,
        "tool": cmd_tool,
        "validate": cmd_validate,
        "state": cmd_state,
        "resume": cmd_resume,
        "budget": cmd_budget,
        "approve": cmd_approve,
        "reject": cmd_reject,
        "dashboard": cmd_dashboard,
        "debug": cmd_debug,
        "cache": cmd_cache,
        "verify-citations": cmd_verify_citations,
        "trace-claims": cmd_trace_claims,
        "parallel": cmd_parallel,
        "export": cmd_export,
        "hooks": cmd_hooks,
        "dag": cmd_dag,
        "data-scale": cmd_data_scale,
    }

    def cmd_intake_interview_handler(args):
        result = run_intake_interview(start=args.start, message=args.message or "")
        print(result)

    def cmd_preregistration_handler(args):
        result = generate_preregistration(
            hypotheses=args.hypotheses,
            analysis_plan=args.analysis_plan or "",
        )
        print(result)

    def cmd_reviewer2_handler(args):
        result = run_reviewer2(findings_path=args.findings_path or "")
        print(result)

    def cmd_dep_check_handler(args):
        result = check_dependencies(
            script=args.script,
            auto_install=args.auto_install,
        )
        print(result)

    def cmd_dag_viewer_handler(args):
        from scripts.dag_viewer import cmd_dag_viewer as _dag_viewer
        _dag_viewer(args)

    def cmd_mcp_handler(args):
        import subprocess
        mcp_path = Path(__file__).parent / "mcp_server.py"
        subprocess.run([sys.executable, str(mcp_path)])

    def cmd_branch_handler(args):
        from core.state_ledger import ResearchLedger
        from scripts.utils.branch_scaffold import BranchScaffold
        ledger = ResearchLedger()
        scaffold = BranchScaffold()
        try:
            ledger.branch_state(args.name, hypothesis=args.hypothesis, parent=args.parent)
            scaffold.create_branch_workspace(args.name, hypothesis=args.hypothesis)
            print(f"Branch '{args.name}' created and scaffolded successfully.")
            if args.hypothesis:
                print(f"  Hypothesis: {args.hypothesis}")
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_branches_handler(args):
        from core.state_ledger import ResearchLedger
        ledger = ResearchLedger()
        branches = ledger.list_branches()
        print(f"{'Branch':<25} {'Parent':<15} {'Status':<12} {'Active':<8} Hypothesis")
        print("-" * 80)
        for b in branches:
            active = "▶" if b["active"] else " "
            print(f"{active} {b['branch_id']:<23} {b['parent']:<15} {b['status']:<12} {'Yes' if b['active'] else 'No':<8} {b['hypothesis']}")

    def cmd_switch_handler(args):
        from core.state_ledger import ResearchLedger
        ledger = ResearchLedger()
        try:
            ledger.switch_branch(args.name)
            print(f"Switched to branch '{args.name}'.")
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_merge_handler(args):
        from core.state_ledger import ResearchLedger
        ledger = ResearchLedger()
        try:
            ledger.merge_branch(args.name, target=args.into, commit_msg=args.message)
            print(f"Branch '{args.name}' merged into '{args.into}'.")
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_abandon_handler(args):
        from core.state_ledger import ResearchLedger
        ledger = ResearchLedger()
        try:
            ledger.abandon_branch(args.name, reason=args.reason)
            print(f"Branch '{args.name}' abandoned.")
            if args.reason:
                print(f"  Reason: {args.reason}")
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_intent_handler(args):
        from scripts.utils.intent_router import IntentRouter
        router = IntentRouter()
        result = router.route(args.query)
        print(f"Intent: {result['classification']['primary_intent']}")
        print(f"Null space excluded: {', '.join(result['null_space'])}")
        print(f"Estimated token savings: ~{result['excluded']['estimated_token_savings']} tokens")
        print(f"\nSkills to load:")
        for s in result['context']['skills']:
            print(f"  - {s}")
        print(f"\nAgents to invoke:")
        for a in result['context']['agents']:
            print(f"  - {a}")

    def cmd_graph_handler(args):
        from scripts.utils.knowledge_graph import ResearchKnowledgeGraph
        try:
            kg = ResearchKnowledgeGraph()
            print(kg.summary())
        except ImportError:
            print("Error: networkx is required. Install with: pip install networkx")
        except FileNotFoundError:
            print("Knowledge graph not found. Run literature analysis first to populate it.")

    def cmd_graph_stats_handler(args):
        from scripts.utils.knowledge_graph import ResearchKnowledgeGraph
        try:
            kg = ResearchKnowledgeGraph()
            stats = kg.get_statistics()
            print("Knowledge Graph Statistics:")
            print(f"  Total nodes: {stats['total_nodes']}")
            print(f"    Papers: {stats['paper_nodes']}")
            print(f"    Entities: {stats['entity_nodes']}")
            print(f"  Total edges: {stats['total_edges']}")
            print(f"  Relation types:")
            for rel, count in sorted(stats['relation_types'].items(), key=lambda x: -x[1]):
                print(f"    - {rel}: {count}")
        except ImportError:
            print("Error: networkx is required. Install with: pip install networkx")
        except FileNotFoundError:
            print("Knowledge graph not found.")

    def cmd_graph_query_handler(args):
        from scripts.utils.knowledge_graph import ResearchKnowledgeGraph
        try:
            kg = ResearchKnowledgeGraph()
            if args.confounders:
                results = kg.get_confounders(args.confounders)
                print(f"Confounders for '{args.confounders}':")
            else:
                results = kg.query(
                    relation=args.relation,
                    subject=args.subject,
                    obj=args.object,
                )
                print(f"Query results:")
            if not results:
                print("  No matching triplets found.")
            else:
                for r in results:
                    print(f"  {r['subject']} --[{r['relation']}]--> {r['object']}")
                    if r.get('source'):
                        print(f"    Source: {r['source']}")
                    if r.get('confidence'):
                        print(f"    Confidence: {r['confidence']}")
        except ImportError:
            print("Error: networkx is required. Install with: pip install networkx")
        except FileNotFoundError:
            print("Knowledge graph not found.")

    def cmd_taxonomy_handler(args):
        from scripts.utils.semantic_filesystem import SemanticFilesystemEnforcer
        enforcer = SemanticFilesystemEnforcer()
        print(enforcer.summary())

    if args.command == "skill":
        cmd_skills(argparse.Namespace(name=args.name))
    elif args.command == "skills":
        cmd_skills(argparse.Namespace(name=None))
    elif args.command == "skill-search":
        cmd_skill_search(args)
    elif args.command == "agent":
        cmd_agents(argparse.Namespace(name=args.name))
    elif args.command == "agents":
        cmd_agents(argparse.Namespace(name=None))
    elif args.command == "intake-interview":
        cmd_intake_interview_handler(args)
    elif args.command == "preregistration":
        cmd_preregistration_handler(args)
    elif args.command == "reviewer2":
        cmd_reviewer2_handler(args)
    elif args.command == "dependency-check":
        cmd_dep_check_handler(args)
    elif args.command == "dag-viewer":
        cmd_dag_viewer_handler(args)
    elif args.command == "mcp":
        cmd_mcp_handler(args)
    elif args.command == "branch":
        cmd_branch_handler(args)
    elif args.command == "branches":
        cmd_branches_handler(args)
    elif args.command == "switch":
        cmd_switch_handler(args)
    elif args.command == "merge":
        cmd_merge_handler(args)
    elif args.command == "abandon":
        cmd_abandon_handler(args)
    elif args.command == "intent":
        cmd_intent_handler(args)
    elif args.command == "graph":
        cmd_graph_handler(args)
    elif args.command == "graph-stats":
        cmd_graph_stats_handler(args)
    elif args.command == "graph-query":
        cmd_graph_query_handler(args)
    elif args.command == "taxonomy":
        cmd_taxonomy_handler(args)
    else:
        handler = commands.get(args.command)
        if handler:
            handler(args)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
