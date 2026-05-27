"""Audit tool tests."""

import pytest

from research_os.tools.actions.audit import audit_figure, audit_synthesis


@pytest.fixture
def workspace_root(tmp_path):
    (tmp_path / "workspace" / "logs").mkdir(parents=True)
    return tmp_path


def test_audit_synthesis_success_when_complete(workspace_root):
    paper_path = "synthesis/paper.md"
    p = workspace_root / paper_path
    p.parent.mkdir(parents=True)
    p.write_text(
        "# Title\n\n"
        "## Abstract\nbody\n\n"
        "## Introduction\nbody\n\n"
        "## Methods\nbody\n\n"
        "## Results\nbody\n\n"
        "## Discussion\nbody\n\n"
        "## References\n[1] Doe 2024.\n"
    )
    res = audit_synthesis(paper_path, workspace_root)
    assert res["status"] in {"success", "warning"}
    assert res["report"]["has_bibliography"] is True


def test_audit_synthesis_flags_missing_sections(workspace_root):
    p = workspace_root / "synthesis" / "p2.md"
    p.parent.mkdir(parents=True)
    p.write_text("# Title\n\n## Abstract\nminimal.\n")
    res = audit_synthesis("synthesis/p2.md", workspace_root)
    assert res["status"] == "warning"
    assert "methods" in res["report"]["missing_sections"]


def test_audit_synthesis_flags_causal_language(workspace_root):
    p = workspace_root / "synthesis" / "p3.md"
    p.parent.mkdir(parents=True)
    p.write_text(
        "## Abstract\n\n## Methods\n\n## Results\n"
        "The treatment causes improvement.\n\n## Discussion\nThis proves efficacy.\n\n## References\n[1]\n"
    )
    res = audit_synthesis("synthesis/p3.md", workspace_root)
    assert res["status"] == "warning"
    assert len(res["report"]["causal_language_hits"]) > 0


def test_audit_synthesis_paper_not_found(workspace_root):
    res = audit_synthesis("synthesis/no.md", workspace_root)
    assert res["status"] == "error"


def test_audit_figure_missing_file(workspace_root):
    res = audit_figure("workspace/01_eda/outputs/figures/ghost.png", workspace_root)
    assert res["status"] == "error"
