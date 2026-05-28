"""MCP server unit tests — envelopes, rate limiter, tool definitions."""

import json

from research_os.server import (
    TOOL_DEFINITIONS,
    RateLimiter,
    _error,
    _log_search,
    _resolve_tool_name,
    _short_for_list,
    _success,
    _text,
)


def test_tool_definitions_nonempty():
    assert isinstance(TOOL_DEFINITIONS, dict)
    assert len(TOOL_DEFINITIONS) >= 40


def test_tool_definitions_have_description_and_schema():
    for name, schema in TOOL_DEFINITIONS.items():
        assert "description" in schema, name
        assert "inputSchema" in schema, name
        inp = schema["inputSchema"]
        assert inp.get("type") == "object", name
        if "required" in inp:
            for r in inp["required"]:
                assert r in inp.get("properties", {}), f"{name} required {r}"


def test_rate_limiter():
    limiter = RateLimiter(max_calls=2, window_seconds=60)
    assert limiter.is_allowed("alice")
    assert limiter.is_allowed("alice")
    assert not limiter.is_allowed("alice")
    assert limiter.is_allowed("bob")


def test_envelope_helpers():
    assert _success({"x": 1}) == {"status": "success", "data": {"x": 1}}
    assert _success() == {"status": "success", "data": {}}
    err = _error("oops")
    assert err == {"status": "error", "error": "oops"}


def test_text_helper():
    out = _text("hello")
    assert len(out) == 1
    assert out[0].text == "hello"

    payload = {"k": "v"}
    out = _text(payload)
    assert json.loads(out[0].text) == payload


def test_log_search_creates_jsonl(tmp_path):
    _log_search(tmp_path, "tool_search_web", "q1", 3)
    _log_search(tmp_path, "tool_search_web", "q2", 5)
    log = tmp_path / "workspace" / "logs" / "searches.log"
    assert log.exists()
    lines = log.read_text().strip().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["tool"] == "tool_search_web"
    assert first["results_count"] == 3


def test_dispatcher_resolves_dots_to_underscores():
    assert _resolve_tool_name("sys.state.get") == "sys_state_get"
    assert _resolve_tool_name("tool.search.web") == "tool_search_web"


def test_dispatcher_resolves_legacy_aliases():
    assert _resolve_tool_name("sys_guidance_get") == "sys_protocol_get"
    assert _resolve_tool_name("sys_md_validate") == "sys_file_validate_md"
    assert _resolve_tool_name("tool_audit_statistical_power") == "tool_audit_power"


def test_dispatcher_passes_underscore_names_through():
    assert _resolve_tool_name("sys_state_get") == "sys_state_get"


def test_routing_tools_registered():
    """sys_boot + tool_route + sys_tool_describe + plan tools must be wired."""
    for name in (
        "sys_boot",
        "tool_route",
        "tool_plan_advance",
        "tool_plan_clear",
        "sys_tool_describe",
    ):
        assert name in TOOL_DEFINITIONS, f"{name} missing from TOOL_DEFINITIONS"


def test_short_for_list_uses_short_field_when_present():
    schema = {
        "short": "Tight one-liner.",
        "description": "Long description that goes on and on and on...",
    }
    assert _short_for_list(schema) == "Tight one-liner."


def test_short_for_list_falls_back_to_first_sentence():
    schema = {
        "description": "First sentence here. Second sentence with more detail.",
    }
    short = _short_for_list(schema)
    assert short.startswith("First sentence here")
    assert len(short) <= 160


def test_short_for_list_caps_at_160_chars():
    schema = {"description": "x" * 500}
    assert len(_short_for_list(schema)) <= 160
