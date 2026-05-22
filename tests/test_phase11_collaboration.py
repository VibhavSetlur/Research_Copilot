import json
from pathlib import Path

from research_os.agents.supervisor_agent import SupervisorAgent
from research_os.state.state_ledger import ResearchLedger

def test_user_removing_evidence(tmp_path: Path):
    """Test that a user correction to remove evidence modifies the state ledger."""
    ledger = ResearchLedger(tmp_path / "state.json")
    ledger.update(loaded_data=["data1.csv", "bad_evidence.csv"])
    
    def mock_llm(prompt: str) -> str:
        return json.dumps({
            "intent": "remove_evidence",
            "task_type": "modify",
            "urgency": "low",
            "needs_clarification": False,
            "needs_approval": False,
            "selected_agents": [],
            "next_action": "Removed bad evidence.",
            "state_patch": {
                "loaded_data": ["data1.csv"]
            }
        })
        
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=mock_llm)
    
    # User says: "ignore bad_evidence.csv"
    supervisor.process_request("ignore bad_evidence.csv")
    
    state = ledger.get()
    assert "bad_evidence.csv" not in state["loaded_data"]
    assert "data1.csv" in state["loaded_data"]

def test_user_modifying_assumptions(tmp_path: Path):
    """Test that user overriding assumptions updates hypotheses."""
    ledger = ResearchLedger(tmp_path / "state.json")
    ledger.add_hypothesis("H1", "testing")
    
    def mock_llm(prompt: str) -> str:
        return json.dumps({
            "intent": "modify_hypothesis",
            "task_type": "modify",
            "urgency": "low",
            "needs_clarification": False,
            "needs_approval": False,
            "selected_agents": [],
            "next_action": "Invalidated H1 based on user feedback.",
            "state_patch": {
                "active_hypotheses": [
                    {"id": "H1", "status": "invalidated", "effect": None}
                ]
            }
        })
        
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=mock_llm)
    
    # User says: "that assumption is wrong"
    supervisor.process_request("that assumption is wrong")
    
    state = ledger.get()
    h1 = next(h for h in state["active_hypotheses"] if h["id"] == "H1")
    assert h1["status"] == "invalidated"
