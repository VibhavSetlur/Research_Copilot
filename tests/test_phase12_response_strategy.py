from pathlib import Path

from research_copilot.prompts.prompt_builder import PromptBuilder
from research_copilot.state.state_ledger import ResearchLedger
from research_copilot.cognition.cognitive_tracker import CognitiveStateTracker

def test_response_strategy_modes(tmp_path: Path):
    """Test that PromptBuilder injects the correct conversational mode rules."""
    ledger = ResearchLedger(tmp_path / "state.json")
    tracker = CognitiveStateTracker(ledger)
    
    pb = PromptBuilder(ledger, tracker)
    
    # Test exploratory mode
    prompt = pb.build_supervisor_prompt("hello", mode="exploratory")
    assert "Focus on brainstorming" in prompt or "exploratory" in prompt.lower()
    
    # Test skeptical mode
    prompt = pb.build_supervisor_prompt("hello", mode="skeptical")
    assert "skeptical" in prompt.lower() or "challenge" in prompt.lower()
