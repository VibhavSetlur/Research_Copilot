#!/usr/bin/env python3
"""Research Copilot CLI entry point — `rcp` command.

Usage:
    rcp init my-project
    rcp setup
    rcp status
"""

import argparse
import os
import shutil
import sys
from pathlib import Path


def cmd_init(args):
    """Initialize a new Research Copilot project."""
    project_name = args.name
    target_dir = Path(project_name)
    
    if target_dir.exists():
        if not args.force:
            print(f"Error: Directory '{project_name}' already exists.")
            print("Use --force to overwrite.")
            sys.exit(1)
        print(f"Overwriting existing directory '{project_name}'...")
        shutil.rmtree(target_dir)
    
    print(f"Creating Research Copilot project: {project_name}")
    print()
    
    # Find the template source (installed package location)
    package_dir = Path(__file__).parent.parent
    
    # Create project directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy system files
    sources = [
        (package_dir / ".research", ".research"),
        (package_dir / "inputs", "inputs"),
        (package_dir / "environment", "environment"),
        (package_dir / "AGENTS.md", "AGENTS.md"),
    ]
    
    for src, dest_name in sources:
        if src.exists():
            dest = target_dir / dest_name
            if src.is_dir():
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dest)
            print(f"  ✓ {dest_name}/")
        else:
            print(f"  ✗ {dest_name}/ (source not found)")
    
    # Create empty data directory
    data_dir = target_dir / "inputs" / "data" / "raw"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / ".gitkeep").touch()
    
    # Create placeholder README
    readme_content = f"""# {project_name}

Research project created with Research Copilot.

## Quick Start

```bash
cd {project_name}
rcp setup        # Verify installation
rcp status       # Check project state
```

## Adding Data

Place your data files in `inputs/data/raw/`.

## Running Research

Open your AI IDE (Cursor, opencode, Claude Desktop) and follow the prompts.
"""
    (target_dir / "README.md").write_text(readme_content)
    print("  ✓ README.md")
    
    # Create .gitignore
    gitignore = """# Research Copilot
.research/cache/
.research/__pycache__/
**/__pycache__/
*.pyc
.venv/
environment/venv/

# Data (optional — uncomment if you want to track data in git)
# inputs/data/raw/
# data/

# OS
.DS_Store
Thumbs.db
"""
    (target_dir / ".gitignore").write_text(gitignore)
    print("  ✓ .gitignore")
    
    print()
    print("=" * 60)
    print(f"Project '{project_name}' created successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print(f"  1. cd {project_name}")
    print("  2. rcp setup          # Verify installation")
    print("  3. rcp status         # Check project state")
    print("  4. Add data to inputs/data/raw/")
    print("  5. Open your AI IDE and start researching!")
    print()
    print("Or start a conversational intake interview:")
    print(f"  cd {project_name}")
    print("  python .research/research.py intake-interview --start")
    print()


def cmd_setup(args):
    """Run setup verification."""
    # Delegate to the research.py setup command
    research_py = Path(__file__).parent.parent / ".research" / "research.py"
    if research_py.exists():
        os.execl(sys.executable, sys.executable, str(research_py), "setup")
    else:
        print("Error: .research/research.py not found.")
        print("Are you in a Research Copilot project?")
        sys.exit(1)


def cmd_status(args):
    """Show project status."""
    research_py = Path(__file__).parent.parent / ".research" / "research.py"
    if research_py.exists():
        os.execl(sys.executable, sys.executable, str(research_py), "status")
    else:
        print("Error: .research/research.py not found.")
        print("Are you in a Research Copilot project?")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="rcp",
        description="Research Copilot — from raw data to publication-ready paper",
    )
    sub = parser.add_subparsers(dest="command")
    
    # rcp init <name>
    p_init = sub.add_parser("init", help="Initialize a new Research Copilot project")
    p_init.add_argument("name", help="Project name (creates a new directory)")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing directory")
    
    # rcp setup
    sub.add_parser("setup", help="Verify Research Copilot installation")
    
    # rcp status
    sub.add_parser("status", help="Show project status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        "init": cmd_init,
        "setup": cmd_setup,
        "status": cmd_status,
    }
    
    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
