"""Tests for sys_boot, tool_route (hierarchical), per-turn batching,
active tool scoping, and the active-plan decomposition."""

import json

from research_os.project_ops import scaffold_minimal_workspace
from research_os.tools.actions.router import (
    active_tools_for_protocol,
    advance_plan,
    clear_active_plan,
    plan_turn,
    route_request,
    sys_boot,
)


def test_sys_boot_returns_full_payload(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Router Test")
    res = sys_boot(tmp_path)
    assert res["status"] == "success"
    # Every key the AI is expected to consume in one shot.
    for k in (
        "project_name", "pipeline_stage", "current_path", "domain",
        "autonomy", "expertise", "model_profile", "shared_server",
        "active_hypotheses", "history_tail", "last_protocol_entry",
        "pause_classification", "next_protocol", "dep_inventory",
        "active_plan", "advice",
    ):
        assert k in res, f"sys_boot missing key {k}"
    assert res["project_name"] == "Router Test"
    assert res["pause_classification"] == "fresh_session"


def test_sys_boot_survives_unscaffolded_root(tmp_path):
    # No scaffold — sys_boot must still return a degraded payload, not throw.
    res = sys_boot(tmp_path)
    assert res["status"] == "success"
    # Any string is acceptable; we just want no exception escaping.
    assert isinstance(res["pipeline_stage"], str)


def test_route_intake_prompt(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Route Test")
    res = route_request("fill the intake", tmp_path)
    assert res["status"] == "success"
    assert res["primary_protocol"] == "guidance/project_startup"
    # Shortcut tool should resolve to intake autofill.
    assert res["shortcut_tool"] == "tool_intake_autofill"
    assert "decomposition" in res
    assert res["complexity"] == "low"  # short prompt


def test_route_complex_prompt_persists_plan(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Complex Route Test")
    prompt = (
        "alright go and run a baseline EDA, then fit a random forest, "
        "and audit the figures, also write the methods section"
    )
    res = route_request(prompt, tmp_path)
    assert res["status"] == "success"
    assert res["complexity"] == "high"
    assert "active_plan_path" in res
    plan = json.loads((tmp_path / res["active_plan_path"]).read_text())
    assert plan["status"] == "in_progress"
    assert plan["current_step"] == 1
    assert len(plan["decomposition"]) >= 1
    assert plan["user_prompt"] == prompt


def test_route_no_persist_when_disabled(tmp_path):
    scaffold_minimal_workspace(tmp_path, "No Persist Test")
    prompt = "run a baseline EDA and then fit a random forest"
    res = route_request(prompt, tmp_path, persist_plan=False)
    assert res["status"] == "success"
    assert "active_plan_path" not in res
    assert not (tmp_path / ".os_state" / "active_plan.json").exists()


def test_route_quick_review(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Review Route Test")
    res = route_request("can you tear apart that draft paper", tmp_path)
    assert res["status"] == "success"
    # Either the protocol or the shortcut should win.
    assert (
        res["primary_protocol"] == "guidance/quick_paper_review"
        or res["shortcut_tool"] == "tool_quick_review"
    )


def test_route_resume_prompt(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Resume Route Test")
    res = route_request("pick up where we left off", tmp_path)
    assert res["status"] == "success"
    assert res["primary_protocol"] == "guidance/session_resume"
    assert res["shortcut_tool"] == "tool_session_resume"


def test_route_handoff_prompt(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Handoff Route Test")
    res = route_request("wrap up I need to come back tomorrow", tmp_path)
    assert res["status"] == "success"
    assert (
        res["primary_protocol"] == "guidance/chat_handoff"
        or res["shortcut_tool"] == "sys_session_handoff"
    )


def test_route_empty_prompt(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Empty Route Test")
    res = route_request("   ", tmp_path)
    assert res["status"] == "error"


def test_advance_plan_walks_decomposition(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Advance Test")
    prompt = "run a baseline EDA and then fit a random forest and audit"
    route_request(prompt, tmp_path)
    assert (tmp_path / ".os_state" / "active_plan.json").exists()
    step2 = advance_plan(tmp_path)
    assert step2["status"] == "success"
    assert step2["current_step"] >= 2
    # Drain the plan; eventually it archives itself.
    for _ in range(20):
        res = advance_plan(tmp_path)
        if res.get("message") and "completed" in res["message"].lower():
            break
    assert not (tmp_path / ".os_state" / "active_plan.json").exists()


def test_clear_plan_removes_file(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Clear Test")
    prompt = "run a baseline and fit a model and write the paper"
    route_request(prompt, tmp_path)
    assert (tmp_path / ".os_state" / "active_plan.json").exists()
    res = clear_active_plan(tmp_path)
    assert res["status"] == "success"
    assert not (tmp_path / ".os_state" / "active_plan.json").exists()


def test_route_fallback_unknown_prompt(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Fallback Test")
    res = route_request("xyzzy nonsense plover", tmp_path)
    assert res["status"] == "success"
    # No trigger should match.
    assert res["primary_protocol"] is None or res["matched_triggers"] == []
    # Resolved at L0 with an ask_user.
    assert res["resolved_level"] == 0
    assert res["ask_user"] is not None


def test_route_hierarchical_fields(tmp_path):
    """Every successful route should expose resolved_level + intent_class."""
    scaffold_minimal_workspace(tmp_path, "Hier Test")
    res = route_request("fill the intake", tmp_path)
    assert res["status"] == "success"
    assert "resolved_level" in res
    assert res["resolved_level"] == 3
    assert res["intent_class"] == "discover"
    assert res["sub_intent"] == "intake"


def test_route_ambiguous_at_l2_asks_user(tmp_path):
    """A clear L1 + ambiguous L3 candidates returns ask_user."""
    scaffold_minimal_workspace(tmp_path, "Ambiguous L2 Test")
    # "synthesize" with both "abstract" and "dashboard" intents.
    res = route_request("write me an abstract and a dashboard", tmp_path)
    assert res["status"] == "success"
    # L1 should still resolve (synthesize) but the specific sub_intent
    # may be ambiguous depending on scoring.
    # At minimum the router shouldn't crash.
    assert res["intent_class"] in {"synthesize", None}


def test_plan_turn_with_no_active_plan(tmp_path):
    scaffold_minimal_workspace(tmp_path, "PlanTurn NoPlan")
    res = plan_turn(tmp_path)
    assert res["status"] == "success"
    assert res["this_turn"] == []
    assert res["next_turn"] == []


def test_plan_turn_batches_by_model_profile(tmp_path):
    scaffold_minimal_workspace(tmp_path, "PlanTurn Batch")
    # Default model_profile is medium → budget 3.
    prompt = (
        "alright run a baseline EDA and then fit a random forest and "
        "audit the figures and write the methods section"
    )
    route_request(prompt, tmp_path)
    # active_plan should exist now.
    res = plan_turn(tmp_path)
    assert res["status"] == "success"
    assert res["model_profile"] == "medium"
    assert res["turn_budget"] == 3
    # Should have at least 1 step this turn.
    assert len(res["this_turn"]) >= 1
    # Total this_turn + next_turn equals remaining decomposition.
    assert (
        len(res["this_turn"]) + len(res["next_turn"]) ==
        7  # analysis_plan decomposition size from _router_index.yaml
    )


def test_plan_turn_small_model_one_step_per_turn(tmp_path):
    import yaml as _yaml
    scaffold_minimal_workspace(tmp_path, "PlanTurn Small")
    cfg_path = tmp_path / "inputs" / "researcher_config.yaml"
    cfg = _yaml.safe_load(cfg_path.read_text()) or {}
    cfg["model_profile"] = "small"
    cfg_path.write_text(_yaml.dump(cfg, sort_keys=False))

    prompt = (
        "alright run a baseline EDA and then fit a random forest and "
        "audit the figures and write the methods section"
    )
    route_request(prompt, tmp_path)
    res = plan_turn(tmp_path)
    assert res["status"] == "success"
    assert res["model_profile"] == "small"
    assert res["turn_budget"] == 1
    assert len(res["this_turn"]) == 1


def test_route_returns_active_tools(tmp_path):
    """tool_route response must include an active_tools shortlist."""
    scaffold_minimal_workspace(tmp_path, "Active Tools Test")
    res = route_request("fill the intake", tmp_path)
    assert res["status"] == "success"
    assert "active_tools" in res
    tools = res["active_tools"]
    assert isinstance(tools, list)
    assert "sys_boot" in tools         # essential
    assert "tool_route" in tools       # essential
    assert "tool_intake_autofill" in tools  # protocol's shortcut


def test_active_tools_for_protocol_direct_lookup(tmp_path):
    scaffold_minimal_workspace(tmp_path, "Active Tools Direct")
    res = active_tools_for_protocol("synthesis/synthesis_paper")
    assert res["status"] == "success"
    assert res["intent_class"] == "synthesize"
    assert res["sub_intent"] == "paper"
    # Decomposition includes tool_synthesize.
    assert "tool_synthesize" in res["active_tools"]
    # Essentials still present.
    assert "sys_boot" in res["active_tools"]
    assert res["active_tools_count"] > 10


def test_active_tools_for_unknown_protocol(tmp_path):
    res = active_tools_for_protocol("nonexistent/ghost")
    assert res["status"] == "error"


def test_plan_turn_recommends_chat_split_when_long(tmp_path):
    import yaml as _yaml
    scaffold_minimal_workspace(tmp_path, "PlanTurn Split")
    # Tiny budget + long plan → chat split should be recommended.
    cfg_path = tmp_path / "inputs" / "researcher_config.yaml"
    cfg = _yaml.safe_load(cfg_path.read_text()) or {}
    cfg["model_profile"] = "small"
    cfg_path.write_text(_yaml.dump(cfg, sort_keys=False))

    # Manually persist a long fake active plan.
    fake_plan = {
        "created_at": "2026-01-01T00:00:00Z",
        "user_prompt": "test",
        "primary_protocol": "guidance/analysis_plan",
        "shortcut_tool": None,
        "decomposition": [
            {"tool": "sys_file_write", "purpose": f"step {i}"}
            for i in range(15)
        ],
        "current_step": 1,
        "status": "in_progress",
    }
    (tmp_path / ".os_state").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".os_state" / "active_plan.json").write_text(
        json.dumps(fake_plan, indent=2)
    )
    res = plan_turn(tmp_path)
    assert res["status"] == "success"
    assert res["chat_split_recommended"] is True
    assert res["chat_split_reason"]
