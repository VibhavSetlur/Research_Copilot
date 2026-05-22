import pytest
from pathlib import Path

from research_copilot.core.state_ledger import ResearchLedger
from research_copilot.core.cognitive_tracker import CognitiveStateTracker

def test_contradictory_paper_ingestion(tmp_path: Path):
    """Test logging a contradiction reduces confidence in related claims."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    tracker = CognitiveStateTracker(ledger)
    
    # 1. Add a claim
    claim_id = tracker.add_claim("Smoking causes lung cancer", provenance="Initial assumption")
    
    # 2. Add an evidence
    tracker.add_evidence("Study shows no correlation in sample X", source_file="study_x.pdf")
    
    # 3. Log a contradiction
    tracker.log_contradiction("Study X contradicts the claim", related_claims=[claim_id])
    
    objects = tracker._get_cognitive_objects()
    claim = next((c for c in objects["claims"] if c["id"] == claim_id), None)
    
    assert claim is not None
    # Confidence should decay by 0.3 from default 0.5
    assert claim["confidence"] == pytest.approx(0.2)
    
    contra = objects["contradictions"][0]
    assert claim_id in contra["related_claims"]

def test_invalidated_hypothesis(tmp_path: Path):
    """Test invalidating a hypothesis logs to dead ends and zeroes confidence."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    tracker = CognitiveStateTracker(ledger)
    
    hyp_id = tracker.add_hypothesis("The earth is flat")
    tracker.invalidate_hypothesis(hyp_id, "Satellite imagery confirms spherical shape")
    
    objects = tracker._get_cognitive_objects()
    hyp = next((h for h in objects["hypotheses"] if h["id"] == hyp_id), None)
    
    assert hyp is not None
    assert hyp["status"] == "invalidated"
    assert hyp["confidence"] == 0.0
    
    state = ledger.get()
    assert "Satellite imagery confirms spherical shape" in state["dead_ends"]

def test_claim_confidence_reduction(tmp_path: Path):
    """Test manual reduction of claim confidence."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    tracker = CognitiveStateTracker(ledger)
    
    claim_id = tracker.add_claim("Water boils at 100C everywhere")
    tracker.update_claim_confidence(claim_id, 0.1, "Altitude affects boiling point")
    
    objects = tracker._get_cognitive_objects()
    claim = next((c for c in objects["claims"] if c["id"] == claim_id), None)
    
    assert claim is not None
    assert claim["confidence"] == 0.1
    assert "Altitude affects boiling point" in claim["revisions"][-1]["change"]

def test_evidence_linkage_to_hypothesis(tmp_path: Path):
    """Test linking evidence to hypothesis (supporting and contradicting)."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    tracker = CognitiveStateTracker(ledger)
    
    hyp_id = tracker.add_hypothesis("A causes B")
    ev1_id = tracker.add_evidence("Experiment 1 shows A -> B")
    ev2_id = tracker.add_evidence("Experiment 2 shows A -> C (not B)")
    
    tracker.link_evidence_to_hypothesis(ev1_id, hyp_id, supports=True)
    tracker.link_evidence_to_hypothesis(ev2_id, hyp_id, supports=False)
    
    objects = tracker._get_cognitive_objects()
    hyp = next((h for h in objects["hypotheses"] if h["id"] == hyp_id), None)
    
    assert ev1_id in hyp["supporting_evidence"]
    assert ev2_id in hyp["contradicting_evidence"]
