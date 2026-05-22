import pytest
import os
from pathlib import Path
import json

from research_copilot.state.state_ledger import ResearchLedger
from research_copilot.replay.session_replay import SessionReplayManager

def test_strict_determinism_check(tmp_path: Path):
    """Test that ledger automatically captures a snapshot on every update."""
    # We will instantiate ResearchLedger, which should now use SessionReplayManager
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    
    # Check if a replay log was created
    replay_manager = SessionReplayManager(tmp_path / "replay_logs")
    
    # Default state save + explicit update
    ledger.update(active_user_intent="exploratory")
    ledger.update(active_user_intent="publication")
    
    logs = replay_manager.load_replay_log()
    assert len(logs) >= 2
    assert logs[-2]["state_snapshot"]["active_user_intent"] == "exploratory"
    assert logs[-1]["state_snapshot"]["active_user_intent"] == "publication"

def test_partial_state_recovery(tmp_path: Path):
    """Test that we can recover state from an exact snapshot index."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    
    ledger.update(phase="1")
    ledger.update(phase="2")
    ledger.update(phase="3")
    
    replay_manager = SessionReplayManager(tmp_path / "replay_logs")
    
    # Recover state before phase 3
    # index -2 should be phase 2
    recovered_state = replay_manager.get_snapshot_at(-2)
    assert recovered_state["phase"] == "2"
