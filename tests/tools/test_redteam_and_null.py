"""Red-team scaffold + null-findings report tests."""

from pathlib import Path

from research_os.project_ops import scaffold_minimal_workspace
from research_os.tools.actions.audit.null_findings import write_null_findings
from research_os.tools.actions.audit.redteam import (
    redteam_scaffold,
    write_response_template,
)


def test_redteam_requires_paper(tmp_path: Path):
    scaffold_minimal_workspace(tmp_path, project_name="P", git_init=False, ide_flags=[])
    r = redteam_scaffold(tmp_path)
    assert r["status"] == "error"


def test_redteam_writes_scaffold(tmp_path: Path):
    scaffold_minimal_workspace(tmp_path, project_name="P", git_init=False, ide_flags=[])
    (tmp_path / "synthesis").mkdir(parents=True, exist_ok=True)
    (tmp_path / "synthesis" / "paper.md").write_text("# Paper\n\nResults: 1.23.")
    r = redteam_scaffold(tmp_path, persona="statistical_referee")
    assert r["status"] == "success"
    text = (tmp_path / r["review_path"]).read_text()
    assert "M1." in text
    assert "statistical_referee" in text


def test_response_template_pairs_with_review(tmp_path: Path):
    scaffold_minimal_workspace(tmp_path, project_name="P", git_init=False, ide_flags=[])
    (tmp_path / "synthesis").mkdir(parents=True, exist_ok=True)
    (tmp_path / "synthesis" / "paper.md").write_text("# Paper\n")
    redteam_scaffold(tmp_path)
    r = write_response_template(tmp_path)
    assert r["status"] == "success"
    body = (tmp_path / r["response_path"]).read_text()
    assert "Response to reviewers" in body


def test_null_findings_assembles(tmp_path: Path):
    scaffold_minimal_workspace(tmp_path, project_name="P", git_init=False, ide_flags=[])
    r = write_null_findings(tmp_path)
    assert r["status"] == "success"
    assert (tmp_path / r["report_path"]).exists()
