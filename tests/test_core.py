import os
import tempfile
from pathlib import Path

import pytest

from research_os.project_ops import (
    scaffold_minimal_workspace,
    load_state,
    create_experiment_branch,
    log_decision,
)


def test_scaffold_workspace():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_minimal_workspace(root, "Test Project")

        assert (root / ".os_state").exists()
        assert (root / "docs").exists()
        assert (root / "inputs").exists()
        assert (root / "workspace").exists()
        assert (root / "synthesis").exists()
        assert (root / "environment").exists()

        state = load_state(root)
        assert state["project_name"] == "Test Project"
        assert state["current_branch"] == "main"
        assert "main" in state["branches"]


def test_branching():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_minimal_workspace(root, "Test Project")

        res = create_experiment_branch("test_branch", "test hypothesis", root=root)
        assert "test_branch" in res["branch_id"]

        state = load_state(root)
        branch_id = res["branch_id"]
        assert branch_id in state["branches"]
        assert state["current_branch"] == branch_id
        assert state["branches"][branch_id]["parent_branch"] == "main"


def test_log_decision():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_minimal_workspace(root, "Test Project")

        res = log_decision(
            "Choosing test", "Mann-Whitney U", "Data is skewed", root=root
        )

        decisions_path = root / "workspace" / "logs" / "decisions.yaml"
        assert decisions_path.exists()
        content = decisions_path.read_text()
        assert "Mann-Whitney U" in content
        assert "Data is skewed" in content
