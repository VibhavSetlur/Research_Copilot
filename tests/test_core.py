import tempfile
from pathlib import Path


from research_os.project_ops import (
    scaffold_minimal_workspace,
    load_state,
    create_numbered_experiment,
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
        assert (root / "workspace" / "workflow.mermaid").exists()
        assert (root / "workspace" / "01_experiment_baseline").exists()
        assert (root / "inputs" / "researcher_config.yaml").exists()

        state = load_state(root)
        assert state["project_name"] == "Test Project"
        assert state["current_branch"] == "main"
        assert "main" in state["branches"]


def test_path_create():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_minimal_workspace(root, "Test Project")

        res = create_numbered_experiment(
            root, "data_preparation", hypothesis="Clean data"
        )
        assert "data_preparation" in res["branch_id"]
        assert res["branch_id"].startswith("02_")
        assert (root / "workspace" / res["branch_id"]).exists()
        assert (root / "workspace" / res["branch_id"] / "data").exists()
        assert (root / "workspace" / res["branch_id"] / "scripts").exists()
        assert (root / "workspace" / res["branch_id"] / "README.md").exists()
        assert (root / "workspace" / res["branch_id"] / "conclusions.md").exists()

        state = load_state(root)
        assert res["branch_id"] in state["branches"]
        assert state["current_branch"] == res["branch_id"]


def test_path_create_auto_numbers():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_minimal_workspace(root, "Test")

        r1 = create_numbered_experiment(root, "first")
        assert r1["branch_id"] == "02_first"

        r2 = create_numbered_experiment(root, "second")
        assert r2["branch_id"] == "03_second"


def test_path_create_unique_per_number():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_minimal_workspace(root, "Test")
        r1 = create_numbered_experiment(root, "test_path")
        r2 = create_numbered_experiment(root, "test_path")
        assert r1["branch_id"] == "02_test_path"
        assert r2["branch_id"] == "03_test_path"
        assert r1["experiment_number"] + 1 == r2["experiment_number"]


def test_log_decision():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_minimal_workspace(root, "Test Project")

        log_decision("Choosing test", "Mann-Whitney U", "Data is skewed", root=root)

        decisions_path = root / "workspace" / "logs" / "decisions.yaml"
        assert decisions_path.exists()
        content = decisions_path.read_text()
        assert "Mann-Whitney U" in content
        assert "Data is skewed" in content
