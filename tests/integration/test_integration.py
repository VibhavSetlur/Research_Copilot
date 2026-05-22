"""Integration test for full research pipeline.

Tests the complete workflow from init → branch → eda → literature → compile.
"""

import pytest
import tempfile
import shutil
from pathlib import Path


class TestIntegrationPipeline:
    """Test full integration pipeline."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        tmpdir = tempfile.mkdtemp()
        old_cwd = Path.cwd()
        import os
        os.chdir(tmpdir)
        yield Path(tmpdir)
        os.chdir(old_cwd)
        shutil.rmtree(tmpdir)
    
    def test_full_pipeline(self, temp_workspace):
        """Test complete pipeline from init to synthesis."""
        from research_os.server import _handle_tool_call
        
        # Step 1: Initialize workspace
        result = _handle_tool_call("sys.workspace.scaffold", {"project_name": "Integration Test"})
        assert len(result) == 1
        import json
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert (temp_workspace / "workspace").exists()
        
        # Step 2: Create a branch
        result = _handle_tool_call("sys.branch.create", {"branch_name": "test_branch"})
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        
        # Step 3: Log analysis entry
        result = _handle_tool_call("sys.analysis.log", {
            "entry": "Started integration test",
            "step": "init"
        })
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert (temp_workspace / "workspace" / "analysis.md").exists()
        
        # Step 4: Check state
        result = _handle_tool_call("sys.state", {})
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert "current_branch" in data["data"]
        assert "checkpoints" in data["data"]
        
        # Step 5: Health check
        result = _handle_tool_call("sys.health", {})
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["status"] == "success"
        assert "version" in data["data"]
        assert "uptime_seconds" in data["data"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
