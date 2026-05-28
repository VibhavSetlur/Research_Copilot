"""Pre-registration freeze/diff + dashboard test-suite scaffold."""

from pathlib import Path

from research_os.project_ops import scaffold_minimal_workspace
from research_os.tools.actions.audit.preregistration import (
    diff_preregistration,
    freeze_preregistration,
)
from research_os.tools.actions.viz.dashboard_tests import (
    generate_dashboard_test_suite,
    run_dashboard_tests,
)


def _scaffold(tmp_path: Path):
    scaffold_minimal_workspace(tmp_path, project_name="P", git_init=False, ide_flags=[])


def test_freeze_preregistration_writes_files(tmp_path: Path):
    _scaffold(tmp_path)
    r = freeze_preregistration(
        tmp_path, primary_outcomes="MoCA score change", target_n=200,
    )
    assert r["status"] == "success"
    prereg_dir = tmp_path / "workspace" / ".preregistration"
    files = list(prereg_dir.glob("prereg_*.md"))
    assert len(files) == 1
    # YAML companion present.
    assert list(prereg_dir.glob("prereg_*.yaml"))


def test_diff_preregistration_clean_with_no_changes(tmp_path: Path):
    _scaffold(tmp_path)
    freeze_preregistration(tmp_path)
    r = diff_preregistration(tmp_path)
    # No changes since freeze → success (or warning, but not error).
    assert r["status"] in {"success", "warning"}


def test_diff_returns_warning_when_no_prereg(tmp_path: Path):
    _scaffold(tmp_path)
    r = diff_preregistration(tmp_path)
    assert r["status"] == "warning"
    assert "pre-registration" in r["message"].lower()


def test_dashboard_test_suite_scaffold(tmp_path: Path):
    _scaffold(tmp_path)
    r = generate_dashboard_test_suite(tmp_path)
    assert r["status"] == "success"
    assert (tmp_path / "tests" / "dashboard" / "test_dashboard.py").exists()
    assert (tmp_path / "tests" / "dashboard" / "conftest.py").exists()


def test_dashboard_test_run_without_prereqs_is_explicit(tmp_path: Path):
    _scaffold(tmp_path)
    generate_dashboard_test_suite(tmp_path)
    # Create a dummy dashboard.
    (tmp_path / "synthesis").mkdir(parents=True, exist_ok=True)
    (tmp_path / "synthesis" / "dashboard.html").write_text("<html></html>")
    r = run_dashboard_tests(tmp_path)
    # When pytest-playwright is not installed → status='error' with install hint.
    # When it is → 'success' or 'warning'.
    assert r["status"] in {"success", "warning", "error"}
    if r["status"] == "error":
        assert "install" in r or "Playwright" in r.get("message", "")
