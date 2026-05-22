import pytest
from pathlib import Path

from research_copilot.core.state_ledger import ResearchLedger
from research_copilot.core.cognitive_tracker import CognitiveStateTracker

def test_citation_lineage_integrity(tmp_path: Path):
    """Test that a claim can trace its lineage back to a citation."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    tracker = CognitiveStateTracker(ledger)
    
    # 1. Add citation
    cit_id = tracker.add_citation("Deep Learning", ["LeCun"], "doi:10.1038")
    
    # 2. Add evidence from citation
    ev_id = tracker.add_evidence("Neural networks scale well", source_file=cit_id, provenance="Extract from Deep Learning")
    
    # 3. Add claim supported by evidence
    claim_id = tracker.add_claim("Scale is all you need", provenance="Derived from evidence", source_nodes=[ev_id])
    
    objects = tracker._get_cognitive_objects()
    
    claim = next(c for c in objects["claims"] if c["id"] == claim_id)
    assert claim["supporting_nodes"] == [ev_id]
    
    evidence = next(e for e in objects["evidence"] if e["id"] == ev_id)
    assert evidence["source_file"] == cit_id

def test_object_revision_history(tmp_path: Path):
    """Test that object revisions are tracked in the 'revisions' field."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    tracker = CognitiveStateTracker(ledger)
    
    claim_id = tracker.add_claim("Initial claim")
    
    tracker.update_claim_confidence(claim_id, 0.9, "Strong new evidence")
    tracker.update_claim_confidence(claim_id, 0.2, "Found a contradiction")
    
    objects = tracker._get_cognitive_objects()
    claim = next(c for c in objects["claims"] if c["id"] == claim_id)
    
    # Expected: 2 revisions
    assert len(claim["revisions"]) == 2
    assert "0.9" in claim["revisions"][0]["change"]
    assert "0.2" in claim["revisions"][1]["change"]

def test_branch_merge_conflicts(tmp_path: Path):
    """Test that merging branches captures the merged status in the ledger."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    
    # Initial state
    ledger.branch_state("hypothesis_a", hypothesis="Test A")
    
    # Switch and modify
    ledger.switch_branch("hypothesis_a")
    
    # Merge back to main
    ledger.merge_branch("hypothesis_a", target="main", commit_msg="Merged A")
    
    state = ledger.get()
    
    assert state["branches"]["hypothesis_a"]["status"] == "merged"
    assert state["branches"]["hypothesis_a"]["merge_commit"] is not None
    assert state["active_branch"] == "main"
