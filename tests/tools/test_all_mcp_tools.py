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
                result = _handle_tool_call(tool_name, {})
                assert len(result) == 1
                content = result[0]
                assert content.type == "text"
                
                # Verify it returns valid JSON
                data = json.loads(content.text)
                assert "status" in data
                assert data["status"] in ["success", "error"]
                
                # If the schema requires arguments, it should ideally return an error
                # if we pass empty arguments, unless the required arguments have defaults.
                # Here we just verify it doesn't crash.
                
            except Exception as e:
                pytest.fail(f"Tool {tool_name} crashed with empty arguments: {e}")

    def test_all_tools_schemas_valid(self):
        """Test that all tools have valid schemas."""
        for tool_name, schema in TOOL_DEFINITIONS.items():
            assert "description" in schema, f"Tool {tool_name} missing description"
            assert "inputSchema" in schema, f"Tool {tool_name} missing inputSchema"
            assert schema["inputSchema"]["type"] == "object", f"Tool {tool_name} inputSchema must be object"
            assert "properties" in schema["inputSchema"], f"Tool {tool_name} inputSchema missing properties"
