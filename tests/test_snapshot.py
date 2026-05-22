"""Snapshot tests for workspace state ledger serialization.

Tests that the workspace state ledger can be serialized and deserialized correctly.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path


class TestSnapshotSerialization:
    """Test workspace state ledger serialization."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        tmpdir = tempfile.mkdtemp()
        old_cwd = Path.cwd()
        import os
        os.chdir(tmpdir)
        Path("workspace").mkdir()
        Path("workspace/.os_state").mkdir()
        yield Path(tmpdir)
        os.chdir(old_cwd)
        shutil.rmtree(tmpdir)
    
    def test_state_ledger_serialization(self, temp_workspace):
        """Test that state ledger can be serialized and deserialized."""
        from research_os.state.state_ledger import ResearchLedger
        
        # Create a ledger
        ledger = ResearchLedger(temp_workspace / "workspace" / ".os_state")
        
        # Add some state
        ledger.update("current_branch", "main")
        ledger.update("pipeline_stage", "eda")
        ledger.add_checkpoint("checkpoint_1", {"test": "data"})
        
        # Serialize
        ledger.save()
        
        # Deserialize
        new_ledger = ResearchLedger(temp_workspace / "workspace" / ".os_state")
        new_ledger.load()
        
        # Verify state
        assert new_ledger.get("current_branch") == "main"
        assert new_ledger.get("pipeline_stage") == "eda"
        checkpoints = new_ledger.get("checkpoints", [])
        assert len(checkpoints) == 1
        assert checkpoints[0]["id"] == "checkpoint_1"
    
    def test_state_ledger_json_format(self, temp_workspace):
        """Test that state ledger is saved in valid JSON format."""
        from research_os.state.state_ledger import ResearchLedger
        
        # Create and populate ledger
        ledger = ResearchLedger(temp_workspace / "workspace" / ".os_state")
        ledger.update("test_key", "test_value")
        ledger.save()
        
        # Read the JSON file
        state_file = temp_workspace / "workspace" / ".os_state" / "state.json"
        assert state_file.exists()
        
        with open(state_file, "r") as f:
            data = json.load(f)
        
        # Verify JSON structure
        assert isinstance(data, dict)
        assert "test_key" in data
        assert data["test_key"] == "test_value"
    
    def test_checkpoint_serialization(self, temp_workspace):
        """Test that checkpoints can be serialized and restored."""
        from research_os.state.state_ledger import ResearchLedger
        
        ledger = ResearchLedger(temp_workspace / "workspace" / ".os_state")
        
        # Add checkpoint with complex data
        checkpoint_data = {
            "step": "eda",
            "timestamp": "2024-01-01T00:00:00Z",
            "files_created": ["data/clean.csv"],
            "methods_used": ["pandas.read_csv"]
        }
        ledger.add_checkpoint("checkpoint_1", checkpoint_data)
        ledger.save()
        
        # Restore
        new_ledger = ResearchLedger(temp_workspace / "workspace" / ".os_state")
        new_ledger.load()
        
        # Verify checkpoint
        checkpoints = new_ledger.get("checkpoints", [])
        assert len(checkpoints) == 1
        assert checkpoints[0]["id"] == "checkpoint_1"
        assert checkpoints[0]["data"]["step"] == "eda"
        assert checkpoints[0]["data"]["files_created"] == ["data/clean.csv"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
