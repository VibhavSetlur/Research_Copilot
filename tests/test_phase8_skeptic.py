import pytest
import json

from research_copilot.control_plane.critic import CriticAgent, SkepticAgent

def create_mock_llm(response_json):
    def mock_llm_call(prompt: str) -> str:
        return json.dumps(response_json)
    return mock_llm_call

def test_artifact_rejection_loop():
    """Test that a critic can reject a claim and flag it with flaws."""
    critic = CriticAgent(call_llm=create_mock_llm({
        "is_valid": False,
        "flaws_detected": ["Correlation is not causation", "Small sample size"],
        "missing_evidence": ["A/B test results"],
        "severity": "high"
    }))
    
    result = critic.critique_claim("Feature X caused a 50% increase in revenue", ["We observed revenue up 50% after launch"])
    
    assert not result.is_valid
    assert len(result.flaws_detected) == 2
    assert "Correlation is not causation" in result.flaws_detected
    assert result.severity == "high"

def test_weak_evidence_flagging():
    """Test that a skeptic agent flags weak evidence in a conclusion."""
    skeptic = SkepticAgent(call_llm=create_mock_llm({
        "is_valid": False,
        "flaws_detected": ["Alternative explanation: seasonal trends"],
        "missing_evidence": ["Control group data"],
        "severity": "medium"
    }))
    
    result = skeptic.challenge_conclusion("We succeeded.", "We looked at data.")
    
    assert not result.is_valid
    assert "Control group data" in result.missing_evidence
    assert result.severity == "medium"
