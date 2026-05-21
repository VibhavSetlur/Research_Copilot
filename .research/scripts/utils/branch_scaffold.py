#!/usr/bin/env python3
"""Branch Workspace Scaffolding — auto-creates branch-specific directory structures.

When a new research branch is created, this module scaffolds the full directory
structure under branch-specific prefixes so parallel execution across branches
never overwrites core findings.

Usage:
    from branch_scaffold import BranchScaffold
    scaffold = BranchScaffold()
    scaffold.create_branch_workspace("hypothesis_B")
"""

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("research.branch_scaffold")

BRANCH_DIRS = [
    ("reports", "figures"),
    ("reports", "tables"),
    ("reports", "analysis"),
    ("reports", "manuscript"),
    ("reports", "audit"),
    ("scripts", "models"),
    ("scripts", "analysis"),
    ("data", "02_processed"),
    ("data", "03_analytical"),
    ("docs", "decisions"),
    ("docs", "iterations"),
]


class BranchScaffold:
    """Auto-scaffold branch-specific workspace directories."""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = self._find_project_root()
        self.root = Path(project_root)

    @staticmethod
    def _find_project_root() -> Path:
        p = Path.cwd()
        for _ in range(10):
            if (p / ".research").exists():
                return p
            if p.parent == p:
                break
            p = p.parent
        return Path.cwd()

    def create_branch_workspace(self, branch_id: str, hypothesis: str = "") -> dict:
        """Create full directory structure for a new branch.

        Args:
            branch_id: Unique branch identifier
            hypothesis: Research hypothesis for this branch

        Returns:
            Dict of created directories
        """
        prefix = branch_id
        created = {}

        for base, subdir in BRANCH_DIRS:
            dir_path = self.root / base / subdir / prefix
            dir_path.mkdir(parents=True, exist_ok=True)
            created[f"{base}/{subdir}/{prefix}"] = str(dir_path)

            readme = dir_path / "README.md"
            if not readme.exists():
                self._write_readme(readme, branch_id, hypothesis, f"{base}/{subdir}")

        self._write_branch_manifest(branch_id, hypothesis, created)
        self._update_root_manifests(branch_id)

        logger.info("Scaffolded workspace for branch '%s': %d directories", branch_id, len(created))
        return created

    def _write_readme(self, path: Path, branch_id: str, hypothesis: str, category: str):
        """Write a README.md for a branch-specific directory."""
        content = f"""# Branch: {branch_id} — {category}

**Hypothesis**: {hypothesis or "Exploratory branch"}
**Created**: {datetime.now(timezone.utc).isoformat()}
**Parent**: main

This directory contains {category} outputs specific to the `{branch_id}` branch.
These are isolated from the main workflow to enable parallel exploration.

## Merge Protocol
When this branch is merged into main:
1. Review all outputs in this directory
2. Synthesize findings into the main `{category}` directory
3. Update the main manuscript with branch-specific results
4. This directory is preserved (never deleted) for auditability
"""
        path.write_text(content)

    def _write_branch_manifest(self, branch_id: str, hypothesis: str, created: dict):
        """Write a branch-specific manifest.json."""
        manifest = {
            "branch_id": branch_id,
            "hypothesis": hypothesis,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "directories": created,
            "files": {},
            "merge_status": None,
        }

        docs_dir = self.root / "docs"
        branch_manifest_dir = docs_dir / "branches"
        branch_manifest_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = branch_manifest_dir / f"{branch_id}_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

    def _update_root_manifests(self, branch_id: str):
        """Update the root docs/manifest.json with branch information."""
        manifest_path = self.root / "docs" / "manifest.json"
        if not manifest_path.exists():
            return

        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        manifest.setdefault("branches", {})
        manifest["branches"][branch_id] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        }

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

    def get_branch_dirs(self, branch_id: str) -> dict:
        """Get all directories for a specific branch.

        Returns:
            Dict mapping category to directory path
        """
        prefix = branch_id
        result = {}

        for base, subdir in BRANCH_DIRS:
            dir_path = self.root / base / subdir / prefix
            if dir_path.exists():
                result[f"{base}/{subdir}"] = str(dir_path)

        return result

    def list_branch_workspaces(self) -> list:
        """List all branch workspaces that exist on disk."""
        branches = []

        reports_figures = self.root / "reports" / "figures"
        if reports_figures.exists():
            for d in reports_figures.iterdir():
                if d.is_dir() and d.name != "main":
                    branches.append(d.name)

        return sorted(set(branches))

    def cleanup_branch_workspace(self, branch_id: str, dry_run: bool = True) -> dict:
        """List files that would be removed for a branch workspace.

        Args:
            branch_id: Branch to clean up
            dry_run: If True, only list files; if False, actually remove

        Returns:
            Dict of affected paths
        """
        affected = {}

        for base, subdir in BRANCH_DIRS:
            dir_path = self.root / base / subdir / branch_id
            if dir_path.exists():
                if dry_run:
                    files = list(dir_path.rglob("*"))
                    affected[f"{base}/{subdir}/{branch_id}"] = {
                        "path": str(dir_path),
                        "file_count": len([f for f in files if f.is_file()]),
                        "action": "would_remove",
                    }
                else:
                    shutil.rmtree(dir_path)
                    affected[f"{base}/{subdir}/{branch_id}"] = {
                        "path": str(dir_path),
                        "action": "removed",
                    }

        return affected
