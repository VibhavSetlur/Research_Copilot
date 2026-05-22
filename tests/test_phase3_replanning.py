import pytest
import os
import json
from pathlib import Path

from research_copilot.state.state_ledger import ResearchLedger
from research_copilot.graph.mutation_engine import PlanMutationEngine
from research_copilot.engine import ResearchEngine

def test_failed_statistical_analysis_alternate_selection(tmp_path: Path):
    """Test engine handles a dead-end and suggests alternative pathway."""
    
    # We will simulate the execute_node with a failing script
    engine = ResearchEngine(tmp_path, hitl_enabled=False)
    
    # Fake script that always fails
    failing_script = "raise ValueError('Statistical analysis failed due to missing assumption')"
    
    result = engine.execute_node(
        node_id="stat_analysis_001",
        script=failing_script,
        task_name=None,
        dead_end_retry=0
    )
    
    # Should automatically catch the dead end and return recovery info
    assert result["status"] == "failed"
    assert result.get("dead_end_recorded") is True
    assert "suggested_action" in result
    assert result["suggested_action"] == "select_alternative_pathway"
    
    state = engine.ledger.get()
    assert len(state.get("dead_ends", [])) > 0
    assert "stat_analysis_001" in state["dead_ends"][-1]

def test_literature_contradiction_mutates_dag(tmp_path: Path):
    """Test mutation engine inserts a node for deeper review."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    ledger._save(ledger._default_state())
    
    # Initialize basic DAG
    ledger.add_dag_node("lit_review_001", "script.py", [], [])
    
    mutation_engine = PlanMutationEngine(ledger)
    
    # Contradiction found -> insert deeper review
    mutation_engine.insert_node(
        node_id="deeper_review_002",
        script_path="deeper_review.py",
        depends_on=["lit_review_001"]
    )
    
    dag = ledger.get_dag()
    assert "deeper_review_002" in dag["nodes"]
    
    # Check edges
    edges = dag["edges"]
    assert any(e["from"] == "lit_review_001" and e["to"] == "deeper_review_002" for e in edges)

def test_rollback_restoration_mutation(tmp_path: Path):
    """Test mutation engine removing a node to rollback."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    ledger._save(ledger._default_state())
    
    # Initialize basic DAG A -> B -> C
    ledger.add_dag_node("A", "script.py", [], [])
    ledger.add_dag_node("B", "script.py", [], [], depends_on=["A"])
    ledger.add_dag_node("C", "script.py", [], [], depends_on=["B"])
    
    mutation_engine = PlanMutationEngine(ledger)
    
    # Rollback node B. C should rewire to A if rewire_children=True
    mutation_engine.remove_node("B", rewire_children=True)
    
    dag = ledger.get_dag()
    assert "B" not in dag["nodes"]
    assert "C" in dag["nodes"]
    
    # Check edges to see if C depends on A
    edges = dag["edges"]
    assert any(e["from"] == "A" and e["to"] == "C" for e in edges)
    assert not any(e["from"] == "B" for e in edges)
