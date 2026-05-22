import json
from pathlib import Path

from research_copilot.agents.supervisor_agent import SupervisorAgent
from research_copilot.state.state_ledger import ResearchLedger

def test_handoff_context_preservation(tmp_path: Path):
    """Test that supervisor preserves context when routing to specialized agents."""
    ledger = ResearchLedger(tmp_path / "state.json")
    ledger.update(active_user_intent="citation_check")
    
    call_count = [0]
    def mock_llm(prompt: str) -> str:
        call_count[0] += 1
        if call_count[0] == 1:
            return json.dumps({
                "intent": "citation_check",
                "task_type": "new_task",
                "urgency": "low",
                "needs_clarification": False,
                "needs_approval": False,
                "selected_agents": ["CitationAgent"],
                "next_action": "Delegating to CitationAgent",
                "state_patch": {}
            })
        else:
            return json.dumps({
                "workflow_name": "citation_workflow",
                "workflow_steps": ["check"],
                "mutations": []
            })
        
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=mock_llm)
    
    decision = supervisor.process_request("Please verify citations.")
    
    assert "CitationAgent" in decision.selected_agents
    assert decision.intent == "citation_check"

def test_agent_specialization_boundaries(tmp_path: Path):
    """Test that specialized agents only handle tasks within their authority."""
    from research_copilot.agents.specialized_agents import CitationAgent, RecoveryAgent
    
    def mock_llm(prompt: str) -> str:
        return json.dumps({"success": True, "output": {"verified": True}})
        
    citation_agent = CitationAgent(call_llm=mock_llm)
    recovery_agent = RecoveryAgent(call_llm=mock_llm)
    
    assert citation_agent.authority == "citation_management"
    assert recovery_agent.authority == "error_recovery"
