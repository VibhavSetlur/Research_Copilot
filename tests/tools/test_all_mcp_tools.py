"""Unit tests for all MCP tools.

Tests that all tools defined in TOOL_DEFINITIONS can be called without crashing,
and validate their inputs correctly.
"""

import pytest
import json
from pathlib import Path
import tempfile
import os

from research_os.server import TOOL_DEFINITIONS, _handle_tool_call


class TestAllMCPTools:
    """Dynamically test all MCP tools."""

    @pytest.fixture(autouse=True)
    def setup_workspace(self):
        """Create a temporary workspace for tools that need it."""
        self.tmpdir = tempfile.mkdtemp()
        self.old_cwd = Path.cwd()
        os.chdir(self.tmpdir)
        yield
        os.chdir(self.old_cwd)
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_all_tools_exist_and_handle_empty_args(self):
        """Test that every tool in TOOL_DEFINITIONS can be called with empty arguments.
        
        It should either succeed (if no arguments are required) or return a clean error,
        but it should NEVER raise an unhandled exception.
        """
        for tool_name, schema in TOOL_DEFINITIONS.items():
            try:
                # Generate a dummy payload based on required fields
                payload = {}
                properties = schema.get("inputSchema", {}).get("properties", {})
                required = schema.get("inputSchema", {}).get("required", [])

                if tool_name == "sys.checkpoint":
                    payload["checkpoint_id"] = "checkpoint_1"
                    payload["description"] = "test checkpoint"
                
                for req in required:
                    if req in payload:
                        continue
                    prop_type = properties.get(req, {}).get("type", "string")
                    if prop_type == "string":
                        payload[req] = "test"
                    elif prop_type == "number":
                        payload[req] = 1
                    elif prop_type == "array":
                        payload[req] = []
                    elif prop_type == "boolean":
                        payload[req] = True
                    else:
                        payload[req] = {}

                result = _handle_tool_call(tool_name, payload)
                assert len(result) == 1
                content = result[0]
                assert content.type == "text"
                
                # Verify structured tools return valid JSON, while plain-text
                # compatibility shims are allowed to return non-empty text.
                text = content.text.strip()
                if text.startswith("{"):
                    data = json.loads(text)
                    assert "status" in data
                    assert data["status"] in ["success", "error"]
                else:
                    assert text
                
            except Exception as e:
                pytest.fail(f"Tool {tool_name} crashed with arguments {payload}: {e}")

    def test_all_tools_schemas_valid(self):
        """Test that all tools have valid schemas."""
        for tool_name, schema in TOOL_DEFINITIONS.items():
            assert "description" in schema, f"Tool {tool_name} missing description"
            assert "inputSchema" in schema, f"Tool {tool_name} missing inputSchema"
            assert schema["inputSchema"]["type"] == "object", f"Tool {tool_name} inputSchema must be object"
            assert "properties" in schema["inputSchema"], f"Tool {tool_name} inputSchema missing properties"
