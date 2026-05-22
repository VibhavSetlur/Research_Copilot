import pytest
import json
from pathlib import Path
from research_copilot.state.state_ledger import ResearchLedger
from research_copilot.memory.memory_synthesizer import MemorySynthesizer

def test_synthesize_episode_mocked_llm(tmp_path, mocker):
    """Test synthesizing an episodic memory using a mocked LLM call."""
    ledger_path = tmp_path / "03_synthesis" / "state_ledger.json"
    ledger = ResearchLedger(ledger_path)
    
    # Mock the LLM to return a predictable JSON string
    mock_llm = mocker.Mock(return_value='{"summary": "Mocked episodic summary."}')
    
    synthesizer = MemorySynthesizer(ledger=ledger, call_llm_fn=mock_llm)
    
    recent_turns = [{"role": "user", "content": "hello"}, {"role": "agent", "content": "world"}]
    episode = synthesizer.synthesize_episode("test_trigger", recent_turns)
    
    assert episode.summary == "Mocked episodic summary."
    assert episode.trigger == "test_trigger"
    
    # Verify ledger was updated
    state = ledger.get()
    assert "memory" in state
    assert len(state["memory"]["episodic"]) == 1
    assert state["memory"]["episodic"][0]["summary"] == "Mocked episodic summary."

def test_roll_semantic_memory_mocked_llm(tmp_path, mocker):
    """Test rolling semantic memory with mocked LLM."""
    ledger_path = tmp_path / "03_synthesis" / "state_ledger.json"
    ledger = ResearchLedger(ledger_path)
    
    # Pre-populate episodic memory
    state = ledger.get()
    state["memory"] = {"episodic": [{"summary": "episode 1"}, {"summary": "episode 2"}]}
    ledger.update(memory=state["memory"])
    
    mock_response = '{"project_summary": "Project is going well.", "confidence_evolution": "High confidence."}'
    mock_llm = mocker.Mock(return_value=mock_response)
    
    synthesizer = MemorySynthesizer(ledger=ledger, call_llm_fn=mock_llm)
    synthesizer.roll_semantic_memory()
    
    state = ledger.get()
    assert "semantic" in state["memory"]
    assert state["memory"]["semantic"]["project_summary"] == "Project is going well."
    assert state["memory"]["semantic"]["confidence_evolution"] == "High confidence."
