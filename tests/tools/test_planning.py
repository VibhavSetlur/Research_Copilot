"""Tests for the iterative-planning tools."""

from unittest.mock import patch

from research_os.project_ops import scaffold_minimal_workspace
from research_os.tools.actions.research.planning import (
    branch_recommendation,
    plan_next_step,
)


def test_plan_next_step_writes_report(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    with patch(
        "research_os.tools.actions.search.search.search_semantic_scholar",
        return_value=[{"title": "T", "authors": ["A"], "year": 2024,
                       "url": "http://x", "doi": "10.1/x", "abstract": ""}],
    ), patch(
        "research_os.tools.actions.search.search.search_web",
        return_value={"results": [{"title": "tool",
                                   "url": "http://t", "description": "d"}]},
    ):
        res = plan_next_step(tmp_path, goal="baseline EDA")
    assert res["status"] == "success"
    plan = tmp_path / res["plan_path"]
    assert plan.exists()
    body = plan.read_text()
    assert "Next-step plan" in body
    assert "baseline EDA" in body or "Recommended next steps" in body


def test_plan_next_step_with_no_providers(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    with patch(
        "research_os.tools.actions.search.search.search_semantic_scholar",
        side_effect=Exception("offline"),
    ), patch(
        "research_os.tools.actions.search.search.search_web",
        side_effect=Exception("offline"),
    ):
        res = plan_next_step(tmp_path, goal="anything")
    assert res["status"] == "success"
    assert res["literature_hits"] == 0


def test_branch_recommendation_returns_guidance(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Test")
    res = branch_recommendation(tmp_path, reason="alternative model")
    assert res["status"] == "success"
    assert res["recommendation"] in {"branch", "extend_current"}
    assert "guidance" in res
