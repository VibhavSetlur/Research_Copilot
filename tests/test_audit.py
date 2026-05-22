import pytest
from pathlib import Path
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
