"""R / Julia / Bash executor tests (subprocess mocked)."""

from unittest import mock

import pytest

from research_os.tools.actions.exec.scripts import (
    execute_bash_script,
    execute_julia_script,
    execute_r_script,
)


@pytest.fixture
def workspace_root(tmp_path):
    (tmp_path / "workspace" / "logs").mkdir(parents=True)
    return tmp_path


def test_r_script_success(workspace_root):
    p = workspace_root / "script.R"
    p.write_text('print("hello")')
    with mock.patch("shutil.which", return_value="/usr/bin/Rscript"), \
         mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.MagicMock(returncode=0, stdout="hello\n", stderr="")
        res = execute_r_script("script.R", workspace_root)
    assert res["status"] == "success"
    assert res["stdout"] == "hello\n"


def test_julia_script_success(workspace_root):
    p = workspace_root / "script.jl"
    p.write_text('println("hello")')
    with mock.patch("shutil.which", return_value="/usr/bin/julia"), \
         mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.MagicMock(returncode=0, stdout="hello\n", stderr="")
        res = execute_julia_script("script.jl", workspace_root)
    assert res["status"] == "success"


def test_bash_script_success(workspace_root):
    p = workspace_root / "script.sh"
    p.write_text('echo "hello"')
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.MagicMock(returncode=0, stdout="hello\n", stderr="")
        res = execute_bash_script("script.sh", workspace_root)
    assert res["status"] == "success"


def test_missing_script(workspace_root):
    res = execute_r_script("ghost.R", workspace_root)
    assert res["status"] == "error"


def test_missing_binary(workspace_root):
    p = workspace_root / "script.R"
    p.write_text('print("hello")')
    with mock.patch("shutil.which", return_value=None):
        res = execute_r_script("script.R", workspace_root)
    assert res["status"] == "error"


def test_bash_script_nonzero_exit_is_error(workspace_root):
    """Previously execute_bash_script returned status=success for any completed
    run regardless of exit code; downstream tools then reported a working
    pipeline when the script had crashed. Regression test."""
    p = workspace_root / "script.sh"
    p.write_text('exit 1')
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.MagicMock(
            returncode=2, stdout="", stderr="boom\n"
        )
        res = execute_bash_script("script.sh", workspace_root)
    assert res["status"] == "error"
    assert res["exit_code"] == 2
    assert res["code"] == 2  # legacy alias preserved
    assert "boom" in res.get("message", "")
