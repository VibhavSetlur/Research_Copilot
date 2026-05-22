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
        ledger = ResearchLedger(temp_workspace / "workspace" / ".os_state" / "state_ledger.json")
        
        # Add some state
        ledger.update(current_branch="main", pipeline_stage="eda")
        checkpoints = ledger.get().get("checkpoints", {})
        checkpoints["checkpoint_1"] = "complete"
        ledger.update(checkpoints=checkpoints)
        
        # Serialize
        ledger._save(ledger.get())
        
        # Deserialize is handled automatically on next load() via get()
        new_ledger = ResearchLedger(temp_workspace / "workspace" / ".os_state" / "state_ledger.json")
        
        assert new_ledger.get().get("current_branch") == "main"
        assert new_ledger.get().get("pipeline_stage") == "eda"
        checkpoints = new_ledger.get().get("checkpoints", {})
        assert "checkpoint_1" in checkpoints
        assert checkpoints["checkpoint_1"] == "complete"
    
    def test_state_ledger_json_format(self, temp_workspace):
        """Test that state ledger is saved in valid JSON format."""
        from research_os.state.state_ledger import ResearchLedger
        
        # Create and populate ledger
        ledger = ResearchLedger(temp_workspace / "workspace" / ".os_state" / "state_ledger.json")
        ledger.update(test_key="test_value")
        ledger._save(ledger.get())
        
        # Read the JSON file
        state_file = temp_workspace / "workspace" / ".os_state" / "state_ledger.json"
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
        
        ledger = ResearchLedger(temp_workspace / "workspace" / ".os_state" / "state_ledger.json")
        
        # Add checkpoint with complex data to the ledger
        checkpoint_data = {
            "step": "eda",
            "timestamp": "2024-01-01T00:00:00Z",
            "files_created": ["data/clean.csv"],
            "methods_used": ["pandas.read_csv"]
        }
        # In reality, checkpoints are string statuses in the ledger,
        # but let's test storing an object for robustness
        checkpoints = ledger.get().get("checkpoints", {})
        checkpoints["checkpoint_1"] = checkpoint_data
        ledger.update(checkpoints=checkpoints)
        ledger._save(ledger.get())
        
        # Restore
        new_ledger = ResearchLedger(temp_workspace / "workspace" / ".os_state" / "state_ledger.json")
        
        # Verify checkpoint
        checkpoints = new_ledger.get().get("checkpoints", {})
        assert "checkpoint_1" in checkpoints
        assert checkpoints["checkpoint_1"]["step"] == "eda"
        assert checkpoints["checkpoint_1"]["files_created"] == ["data/clean.csv"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
