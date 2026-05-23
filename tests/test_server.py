import json


from research_os.server import (
    TOOL_DEFINITIONS,
    RateLimiter,
    _envelope,
    _error_envelope,
    _log_search,
    _success_envelope,
    _text,
)


def test_tool_definitions_nonempty():
    assert isinstance(TOOL_DEFINITIONS, dict)
    assert len(TOOL_DEFINITIONS) > 0


def test_tool_definitions_have_description_and_input_schema():
    for name, schema in TOOL_DEFINITIONS.items():
        assert "description" in schema, f"{name} missing 'description'"
        assert "inputSchema" in schema, f"{name} missing 'inputSchema'"


def test_tool_definitions_input_schema_valid():
    for name, schema in TOOL_DEFINITIONS.items():
        inp = schema["inputSchema"]
        assert isinstance(inp, dict), f"{name} inputSchema not a dict"
        assert inp.get("type") == "object", f"{name} inputSchema.type is not 'object'"
        assert "properties" in inp, f"{name} inputSchema missing 'properties'"
        assert isinstance(inp["properties"], dict), f"{name} properties not a dict"
        if "required" in inp:
            assert isinstance(inp["required"], list), f"{name} 'required' not a list"
            for r in inp["required"]:
                assert r in inp["properties"], (
                    f"{name} required field '{r}' not in properties"
                )


def test_rate_limiter_allows_within_limit():
    limiter = RateLimiter(max_calls=3, window_seconds=60)
    for _ in range(3):
        assert limiter.is_allowed("alice")


def test_rate_limiter_blocks_after_limit():
    limiter = RateLimiter(max_calls=2, window_seconds=60)
    assert limiter.is_allowed("bob")
    assert limiter.is_allowed("bob")
    assert not limiter.is_allowed("bob")


def test_rate_limiter_independent_clients():
    limiter = RateLimiter(max_calls=1, window_seconds=60)
    assert limiter.is_allowed("c1")
    assert not limiter.is_allowed("c1")
    assert limiter.is_allowed("c2")


def test_envelope_with_data():
    result = _envelope({"foo": "bar"}, status="success")
    assert result == {"status": "success", "data": {"foo": "bar"}}


def test_envelope_defaults():
    result = _envelope()
    assert result == {"status": "success", "data": {}}


def test_success_envelope():
    result = _success_envelope({"done": True})
    assert result == {"status": "success", "data": {"done": True}}


def test_error_envelope():
    result = _error_envelope("fail")
    assert result == {"status": "error", "data": {"error": "fail"}}


def test_text_string():
    result = _text("plain output")
    assert len(result) == 1
    assert result[0].type == "text"
    assert result[0].text == "plain output"


def test_text_dict():
    payload = {"key": "value", "num": 42}
    result = _text(payload)
    assert len(result) == 1
    assert result[0].type == "text"
    assert json.loads(result[0].text) == payload


def test_log_search_creates_file(tmp_path):
    _log_search(tmp_path, "tool.search.web", "test query", 3)
    log_file = tmp_path / "workspace" / "logs" / "searches.log"
    assert log_file.exists()
    data = json.loads(log_file.read_text().strip())
    assert data["tool"] == "tool.search.web"
    assert data["query"] == "test query"
    assert data["results_count"] == 3


def test_log_search_appends(tmp_path):
    _log_search(tmp_path, "t1", "q1", 1)
    _log_search(tmp_path, "t2", "q2", 2)
    log_file = tmp_path / "workspace" / "logs" / "searches.log"
    lines = log_file.read_text().strip().split("\n")
    assert len(lines) == 2


def test_log_search_entry_structure(tmp_path):
    _log_search(tmp_path, "my_tool", "my query", 7)
    log_file = tmp_path / "workspace" / "logs" / "searches.log"
    entry = json.loads(log_file.read_text().strip())
    assert "timestamp" in entry
    assert "tool" in entry
    assert "query" in entry
    assert "results_count" in entry
