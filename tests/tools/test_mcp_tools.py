"""Unit tests for MCP tools.

Tests input validation, output schema, and error cases for each MCP tool.
"""

import pytest
from pathlib import Path
import tempfile


class TestSystemTools:
    """Test system tools (sys.*)."""
    
    def test_sys_health_output_schema(self):
        """Test sys.health returns correct schema."""
        from research_os.server import _handle_tool_call
        
        result = _handle_tool_call("sys.health", {})
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"
        
        # Parse the JSON response
        import json
        data = json.loads(content.text)
        assert data["status"] == "success"
        assert "version" in data["data"]
        assert "uptime_seconds" in data["data"]
        assert "loaded_tools" in data["data"]
        assert "python_version" in data["data"]
        assert "timestamp" in data["data"]
    
    def test_sys_heartbeat_output_schema(self):
        """Test sys.heartbeat returns correct schema."""
        from research_os.server import _handle_tool_call
        
        result = _handle_tool_call("sys.heartbeat", {})
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"
        
        import json
        data = json.loads(content.text)
        assert data["status"] == "success"
        assert "version" in data["data"]
    
    def test_sys_state_output_schema(self):
        """Test sys.state returns correct schema."""
        from research_os.server import _handle_tool_call
        
        result = _handle_tool_call("sys.state", {})
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"
        
        import json
        data = json.loads(content.text)
        assert data["status"] == "success"
        assert "workspace_root" in data["data"]
        assert "folder_tree" in data["data"]
        assert "current_branch" in data["data"]
    
    def test_sys_workspace_scaffold_creates_structure(self):
        """Test sys.workspace.scaffold creates directory structure."""
        from research_os.server import _handle_tool_call
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            os.chdir(tmpdir)
            
            result = _handle_tool_call("sys.workspace.scaffold", {"project_name": "Test Project"})
            assert len(result) == 1
            content = result[0]
            
            import json
            data = json.loads(content.text)
            assert data["status"] == "success"
            assert "workspace" in data["data"]
            assert Path(tmpdir / "workspace").exists()


class TestMemoryTools:
    """Test memory tools (mem.*)."""
    
    def test_mem_methods_append(self):
        """Test mem.methods.append adds a method entry."""
        from research_os.server import _handle_tool_call
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            os.chdir(tmpdir)
            # Create minimal workspace structure
            Path("workspace").mkdir()
            Path("workspace/methods.md").write_text("")
            
            result = _handle_tool_call("mem.methods.append", {
                "entry": "Test method: Used t-test with alpha=0.05"
            })
            assert len(result) == 1
            
            import json
            data = json.loads(result[0].text)
            assert data["status"] == "success"


class TestViewTools:
    """Test view tools (view.*)."""
    
    def test_view_workspace_tree(self):
        """Test view.workspace.tree returns folder structure."""
        from research_os.server import _handle_tool_call
        
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            os.chdir(tmpdir)
            Path("workspace").mkdir()
            Path("workspace/data").mkdir()
            
            result = _handle_tool_call("view.workspace.tree", {"max_depth": 2})
            assert len(result) == 1
            
            import json
            data = json.loads(result[0].text)
            assert data["status"] == "success"
            assert "tree" in data["data"]


class TestToolTools:
    """Test tool tools (tool.*)."""
    
    def test_tool_data_transform_validation(self):
        """Test tool.data.transform validates required parameters."""
        from research_os.server import _handle_tool_call
        
        # Missing required parameter
        result = _handle_tool_call("tool.data.transform", {
            "operations": []
        })
        
        import json
        data = json.loads(result[0].text)
        # Should return error for missing filepath
        assert data["status"] == "error"
    
    def test_tool_statistical_test_validation(self):
        """Test tool.statistical.test validates required parameters."""
        from research_os.server import _handle_tool_call
        
        # Missing required parameters
        result = _handle_tool_call("tool.statistical.test", {})
        
        import json
        data = json.loads(result[0].text)
        # Should return error for missing parameters
        assert data["status"] == "error"


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_blocks_excessive_calls(self):
        """Test that rate limiter blocks calls after limit."""
        from research_os.server import _rate_limiter
        
        # Make calls up to the limit
        for _ in range(100):
            assert _rate_limiter.is_allowed() is True
        
        # Next call should be blocked
        assert _rate_limiter.is_allowed() is False
        
        # Wait for window to expire (in real scenario, this would be time-based)
        # For testing, we can reset
        _rate_limiter.calls.clear()
        assert _rate_limiter.is_allowed() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
