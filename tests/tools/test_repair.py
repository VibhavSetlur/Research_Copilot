"""Tests for tool_workspace_repair."""

from research_os.project_ops import scaffold_minimal_workspace
from research_os.tools.actions.state.repair import workspace_repair


def test_repair_healthy_workspace(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    res = workspace_repair(tmp_path)
    assert res["status"] == "success"
    assert res["issues_detected"] == 0


def test_repair_recreates_missing_dirs(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    # Nuke a top-level directory.
    import shutil
    shutil.rmtree(tmp_path / "synthesis")
    res = workspace_repair(tmp_path)
    assert res["status"] == "success"
    assert any("synthesis" in i for i in res["issues"])
    assert (tmp_path / "synthesis").exists()


def test_repair_recovers_corrupted_state_ledger(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    state_path = tmp_path / ".os_state" / "state_ledger.json"
    state_path.write_text("{ not valid json")
    res = workspace_repair(tmp_path)
    assert res["status"] == "success"
    assert any("corrupted" in i for i in res["issues"])
    # New file should be valid.
    import json
    data = json.loads(state_path.read_text())
    assert "paths" in data


def test_repair_dry_run_does_not_modify(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    import shutil
    shutil.rmtree(tmp_path / "synthesis")
    res = workspace_repair(tmp_path, dry_run=True)
    assert res["status"] == "success"
    assert res["issues_detected"] >= 1
    assert not (tmp_path / "synthesis").exists()
