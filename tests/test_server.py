"""MCP server unit tests — envelopes, rate limiter, tool definitions."""

import json

from research_os.server import (
    TOOL_DEFINITIONS,
    RateLimiter,
    _envelope,
    _error_envelope,
    _log_search,
    _resolve_tool_name,
    _success_envelope,
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
    assert _envelope({"x": 1}) == {"status": "success", "data": {"x": 1}}
    assert _envelope() == {"status": "success", "data": {}}
    assert _success_envelope({"y": 2}) == {"status": "success", "data": {"y": 2}}
    err = _error_envelope("oops")
    assert err["status"] == "error"
    assert err["data"]["error"] == "oops"


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
