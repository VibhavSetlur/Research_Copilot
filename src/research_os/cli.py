#!/usr/bin/env python3
"""Research OS CLI.

Two commands, by design:

    research-os init [dir] [--name X] [--ide all|cursor|claude|...]
        Scaffold a Research OS workspace.

    research-os start [--workspace .]
        Run the MCP server. Your AI IDE connects to this.

No `doctor`, no `pull`, no `env` — keep the surface tiny so researchers don't
need to memorise CLI commands. All real research work happens by talking to
the AI in the IDE.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from research_os.project_ops import scaffold_minimal_workspace
from research_os.utils.asset_manager import AssetManager

VALID_IDES = ("cursor", "claude", "antigravity", "opencode", "vscode")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _print_tree(path: Path, prefix: str = "") -> None:
    explanations = {
        "inputs": "Researcher-provided data — immutable.",
        "raw_data": "Source data files (CSV, Parquet, FASTQ, PDF, ...).",
        "literature": "PDFs of papers cited.",
        "context": "Notes, prior reports, background docs.",
        "workspace": "Active analysis — experiments live here.",
        "synthesis": "Final outputs — paper, abstract, dashboard.",
        "docs": "Research question, glossary, domain summary.",
        "environment": "Pinned dependency snapshots.",
        ".os_state": "Internal state (do not edit manually).",
    }
    try:
        entries = sorted(path.iterdir())
    except OSError:
        return
    for i, entry in enumerate(entries):
        if entry.name.startswith(".") and entry.name not in {".os_state", ".cursor", ".claude", ".antigravity", ".vscode"}:
            continue
        if entry.name in {"__pycache__", ".git"}:
            continue
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        label = entry.name + "/" if entry.is_dir() else entry.name
        hint = explanations.get(entry.name)
        print(f"{prefix}{connector}{label}" + (f"  ← {hint}" if hint else ""))
        if entry.is_dir():
            extension = "    " if is_last else "│   "
            _print_tree(entry, prefix + extension)


def _ide_choice(args_ide: str | None) -> list[str]:
    if not args_ide or args_ide == "all":
        return list(VALID_IDES)
    parts = [p.strip() for p in args_ide.split(",") if p.strip()]
    invalid = [p for p in parts if p not in VALID_IDES]
    if invalid:
        print(f"  ⚠  Unknown IDE(s): {', '.join(invalid)}. Falling back to 'cursor'.")
        return ["cursor"]
    return parts


def _print_mcp_snippet(project_root: Path, ide: str) -> None:
    snippet = {
        "research-os": {
            "command": "research-os",
            "args": ["start"],
            "env": {"RESEARCH_OS_WORKSPACE": str(project_root)},
        }
    }
    primary = ide if ide != "all" else "cursor"
    labels = {
        "cursor": "Cursor    → .cursor/mcp.json  (already created)",
        "claude": "Claude    → claude_desktop_config.json",
        "vscode": "VS Code   → .vscode/mcp.json   (already created)",
        "antigravity": "Antigravity → .antigravity/mcp.json (already created)",
        "opencode": "OpenCode  → opencode.json     (already created)",
    }
    label = labels.get(primary, "Your IDE  → its MCP config")
    print(f"\n  ┌─ {label} " + "─" * max(0, 60 - len(label)) + "┐")
    for line in json.dumps({"mcpServers": snippet}, indent=2).splitlines():
        print(f"  │ {line:<70} │")
    print("  └" + "─" * 72 + "┘\n")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> None:
    """Scaffold a Research OS workspace."""
    if args.name and args.directory is None:
        slug = re.sub(r"[^a-zA-Z0-9_-]", "-", args.name.replace(" ", "-")).lower()
        target_dir = (Path.cwd() / slug).resolve()
        created_new_folder = not target_dir.exists()
    elif args.directory:
        target_dir = Path(args.directory).resolve()
        created_new_folder = not target_dir.exists()
    else:
        target_dir = Path.cwd().resolve()
        created_new_folder = False

    project_name = args.name or target_dir.name

    already_initialized = (target_dir / ".os_state").exists()
    if already_initialized and not args.force:
        print(f"  ✗ Workspace already exists at: {target_dir}")
        print("  Pass --force to re-scaffold (preserves your data and config).")
        sys.exit(1)

    ide_flags = _ide_choice(args.ide)

    # Detect existing data files and symlink them into inputs/raw_data/ (best effort)
    linked: list[str] = []
    raw_data_sources: list[Path] = []
    if target_dir.exists() and not args.force:
        for pattern in ("*.csv", "*.tsv", "*.json", "*.jsonl", "*.xlsx", "*.xls",
                        "*.parquet", "*.feather", "*.pdf"):
            raw_data_sources.extend(list(target_dir.glob(pattern))[:5])

    config_overrides = {
        "project_name": project_name,
        "domain": args.domain or "",
        "research_question": args.question or "",
    }
    scaffold_minimal_workspace(
        target_dir,
        project_name,
        config_overrides=config_overrides,
        ide_flags=ide_flags,
        copy_agents=True,
    )

    if raw_data_sources:
        inputs_raw = target_dir / "inputs" / "raw_data"
        inputs_raw.mkdir(parents=True, exist_ok=True)
        for src in raw_data_sources:
            link = inputs_raw / src.name
            if link.exists():
                continue
            try:
                link.symlink_to(src.absolute())
                linked.append(src.name)
            except OSError:
                try:
                    shutil.copy2(src, link)
                    linked.append(src.name)
                except OSError as exc:
                    print(f"  ⚠  Could not link {src.name}: {exc}")

    if linked:
        try:
            from research_os.project_ops import load_state, save_state

            state = load_state(target_dir)
            linked_meta = state.setdefault("linked_external_data", [])
            for name in linked:
                if name not in linked_meta:
                    linked_meta.append(name)
            save_state(target_dir, state)
        except Exception:
            pass

    # ── Report ──────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  RESEARCH OS  ·  WORKSPACE READY")
    print("=" * 60)
    print(f"  Project   : {project_name}")
    print(f"  Location  : {target_dir}")
    if linked:
        print(f"  Linked    : {', '.join(linked)}")
    print()

    file_count = sum(1 for _ in target_dir.rglob("*") if _.is_file())
    if created_new_folder or file_count < 40:
        _print_tree(target_dir)

    print()
    print("  Next steps")
    n = 1
    if created_new_folder:
        print(f"  {n}. cd {target_dir}")
        n += 1
    print(f"  {n}. Drop your data into  inputs/raw_data/  and any PDFs into  inputs/literature/")
    n += 1
    print(f"  {n}. Edit (or have the AI fill in) inputs/researcher_config.yaml")
    n += 1
    print(f"  {n}. Open your AI IDE — the MCP server is pre-configured.")
    print( "       Then just say: \"start the project\" or \"analyse my data\".")
    if args.ide == "claude" or args.ide == "all":
        print(f"  {n+1}. For Claude Desktop, paste this snippet into claude_desktop_config.json:")
        _print_mcp_snippet(target_dir, "claude")
    print(f"  Config    : {target_dir / 'inputs' / 'researcher_config.yaml'}")
    print(f"  AGENTS    : {target_dir / 'AGENTS.md'}    ← the AI reads this first.")
    print()


def cmd_start(args: argparse.Namespace) -> None:
    """Start the MCP server for an existing workspace."""
    if args.workspace:
        workspace = Path(args.workspace).resolve()
    else:
        try:
            workspace = AssetManager.find_project_root()
        except Exception:
            workspace = Path.cwd()

    if not (workspace / ".os_state").exists():
        print(f"  ✗ Not a Research OS workspace: {workspace}")
        print("  Run 'research-os init' first, or pass --workspace <path>.")
        sys.exit(1)

    from research_os.server import main as server_main

    sys.argv = [sys.argv[0], "--transport", args.transport]
    sys.argv.extend(["--workspace", str(workspace)])
    server_main()


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-os",
        description=(
            "Research OS — an MCP-native research operating system.\n\n"
            "Two commands:\n"
            "  research-os init     scaffold a workspace\n"
            "  research-os start    run the MCP server (your IDE connects to it)\n\n"
            "Everything else happens by talking to the AI in your IDE."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser(
        "init",
        help="Initialise a Research OS workspace.",
        description="Scaffold a workspace directory ready for AI-driven research.",
    )
    p_init.add_argument(
        "directory",
        nargs="?",
        default=None,
        help="Target directory (default: current directory).",
    )
    p_init.add_argument("--name", help="Project name (default: directory name).")
    p_init.add_argument(
        "--domain",
        help="Domain hint (clinical / finance / nlp / genomics / ...). Optional.",
    )
    p_init.add_argument(
        "--question",
        help="Initial research question. The AI will refine it during project_startup.",
    )
    p_init.add_argument(
        "--ide",
        default="all",
        help="IDE(s) to wire up: all | cursor | claude | antigravity | opencode | vscode | comma-separated.",
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Re-scaffold even if the workspace already exists (does not overwrite data).",
    )

    p_start = sub.add_parser(
        "start",
        help="Start the MCP server for this workspace.",
        description="Run the MCP server. Your AI IDE connects to it via stdio.",
    )
    p_start.add_argument(
        "--workspace",
        default=None,
        help="Workspace path (default: auto-detect from cwd).",
    )
    p_start.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport (default: stdio).",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "start":
        cmd_start(args)
    else:
        parser.print_help()
        print()
        print("  Tip: 'research-os init' to scaffold, then open your IDE and chat with the AI.")


if __name__ == "__main__":
    main()
