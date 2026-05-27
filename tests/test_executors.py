"""R / Julia / Bash executor tests (subprocess mocked)."""

from unittest import mock

import pytest

from research_os.tools.actions.execution import (
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
