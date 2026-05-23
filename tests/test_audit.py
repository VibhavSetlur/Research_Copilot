import pytest
from research_os.tools.actions.audit import audit_synthesis


@pytest.fixture
def workspace_root(tmp_path):
    root = tmp_path / "test_workspace"
    root.mkdir()
    return root


def test_audit_synthesis_success(workspace_root):
    paper_path = "synthesis/paper.md"
    p = workspace_root / paper_path
    p.parent.mkdir(parents=True)
    p.write_text("""
    Abstract: Good.
    Methods: Used ML.
    Results: Accuracy 99%.
    Discussion: Great.
    References: [1] Doe 2023.
    """)

    res = audit_synthesis(paper_path, workspace_root)
    assert res["status"] == "success"
    assert len(res["report"]["missing_sections"]) == 0
    assert len(res["report"]["causal_language_found"]) == 0
    assert res["report"]["has_bibliography"] is True


def test_audit_synthesis_warning(workspace_root):
    paper_path = "synthesis/paper2.md"
    p = workspace_root / paper_path
    p.parent.mkdir(parents=True)
    p.write_text("""
    Abstract: Missing sections.
    Results: Proves that x causes y.
    """)

    res = audit_synthesis(paper_path, workspace_root)
    assert res["status"] == "warning"
    assert "methods" in res["report"]["missing_sections"]
    assert "discussion" in res["report"]["missing_sections"]
    assert len(res["report"]["causal_language_found"]) > 0
    assert res["report"]["has_bibliography"] is False


def test_audit_synthesis_empty_paper(workspace_root):
    paper_path = "synthesis/empty.md"
    p = workspace_root / paper_path
    p.parent.mkdir(parents=True)
    p.write_text("")

    res = audit_synthesis(paper_path, workspace_root)
    assert res["status"] == "warning"
    assert len(res["report"]["missing_sections"]) > 0


def test_audit_synthesis_causal_in_observational(workspace_root):
    paper_path = "synthesis/causal_obs.md"
    p = workspace_root / paper_path
    p.parent.mkdir(parents=True)
    p.write_text("""
    Abstract: Observational study.
    Methods: We observed the data.
    Results: The treatment causes improvement.
    Discussion: This proves efficacy.
    References: [1] Study 2023.
    """)

    res = audit_synthesis(paper_path, workspace_root)
    assert res["status"] == "warning"
    assert len(res["report"]["causal_language_found"]) > 0


def test_audit_synthesis_paper_not_found(workspace_root):
    res = audit_synthesis("synthesis/nonexistent.md", workspace_root)
    assert res["status"] == "error"
    assert "not found" in res["message"].lower()
