"""Tests for the workspace/scratch sandbox."""

from research_os.project_ops import scaffold_minimal_workspace
from research_os.tools.actions.state.scratch import (
    scratch_clear,
    scratch_list,
    scratch_run,
    scratch_write,
)


def test_scratch_write_creates_file(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    res = scratch_write("hello.py", "print('hi')\n", tmp_path)
    assert res["status"] == "success"
    f = tmp_path / "workspace" / "scratch" / "hello.py"
    assert f.exists()


def test_scratch_write_rejects_path_traversal(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    res = scratch_write("../evil.py", "x=1", tmp_path)
    assert res["status"] == "error"


def test_scratch_run_python(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    scratch_write("smoke.py", "print('OK')\n", tmp_path)
    res = scratch_run("smoke.py", tmp_path, timeout=30)
    assert res["status"] == "success"
    assert res["exit_code"] == 0
    assert "OK" in res["stdout"]


def test_scratch_run_unknown_extension(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    scratch_write("nope.xyz", "irrelevant", tmp_path)
    res = scratch_run("nope.xyz", tmp_path)
    assert res["status"] == "error"


def test_scratch_list_and_clear(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    scratch_write("a.py", "x=1", tmp_path)
    scratch_write("b.py", "y=2", tmp_path)
    listed = scratch_list(tmp_path)
    assert listed["status"] == "success"
    assert listed["count"] == 2
    cleared = scratch_clear(tmp_path)
    assert cleared["status"] == "success"
    assert cleared["removed"] >= 2
    assert scratch_list(tmp_path)["count"] == 0
