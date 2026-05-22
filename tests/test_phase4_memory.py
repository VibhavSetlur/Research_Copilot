import json
from pathlib import Path

from research_os.state.state_ledger import ResearchLedger
from research_os.agents.supervisor_agent import SupervisorAgent

class MockPlanner:
    def generate_plan(self, request, state):
        class Plan:
            def __init__(self):
                self.workflow_name = "test_workflow"
                self.workflow_steps = ["step1"]
            def model_dump(self):
                return {"workflow_name": "test_workflow", "workflow_steps": ["step1"]}
        return Plan()

class MockRouter:
    def get_minimal_context(self, query):
        return {"required_agents": ["analyst"]}

def create_mock_llm(responses):
    def mock_llm_call(prompt: str) -> str:
        # If it's the memory synthesizer prompting for episodic summary
        if "Summarize the following recent conversation" in prompt:
            return json.dumps({"summary": "User asked 10 questions and we answered them."})
        # If it's rolling semantic memory
        if "write a rolling summary of the entire project state" in prompt:
            return json.dumps({
                "project_summary": "We are exploring data.",
                "confidence_evolution": "Confidence is growing."
            })
            
        parts = prompt.split("--- USER MESSAGE ---")
        user_msg = parts[-1] if len(parts) > 1 else prompt
        for key, response in responses.items():
            if key in user_msg:
                return json.dumps(response)
        
        # Default response for normal turns
        return json.dumps({
            "intent": "exploratory",
            "task_type": "new_task",
            "urgency": "low",
            "needs_clarification": False,
            "needs_approval": False,
            "next_action": "Processing turn...",
            "state_patch": {}
        })
    return mock_llm_call

def test_long_session_continuity_triggers_compression(tmp_path: Path):
    """Test that reaching 10 turns triggers memory synthesis and reduces turns list."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    ledger._save(ledger._default_state())
    
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=create_mock_llm({}))
    supervisor.planner = MockPlanner()
    supervisor.router = MockRouter()
    
    # 4 requests -> 8 turns (user + assistant) -> should just accumulate
    for i in range(4):
        supervisor.process_request(f"Turn {i}")
        
    state = ledger.get()
    assert len(state.get("conversation_turns", [])) == 8
    assert "memory" not in state
    
    # 5th request -> 10th turn -> triggers compression
    supervisor.process_request("Turn 4")
    
    state = ledger.get()
    # Should reduce to the last 2 turns
    assert len(state.get("conversation_turns", [])) == 2
    
    # Episodic and semantic memory should be populated
    assert "memory" in state
    assert len(state["memory"]["episodic"]) == 1
    assert state["memory"]["episodic"][0]["summary"] == "User asked 10 questions and we answered them."
    
    assert state["memory"]["semantic"]["project_summary"] == "We are exploring data."
    assert state["memory"]["semantic"]["confidence_evolution"] == "Confidence is growing."

def test_memory_restoration_after_restart(tmp_path: Path):
    """Test that restoring a ledger with memory correctly exposes the memory to the system."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    
    # Create fake existing state
    state = ledger._default_state()
    state["memory"] = {
        "episodic": [
            {
                "timestamp": "2023-01-01T00:00:00Z",
                "trigger": "turn_threshold_reached",
                "summary": "Previous session explored X.",
                "decisions_made": [],
                "rejected_alternatives": []
            }
        ],
        "semantic": {
            "project_summary": "Exploring X.",
            "confidence_evolution": "Stable."
        }
    }
    ledger._save(state)
    
    # Re-initialize supervisor and planner
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=create_mock_llm({}))
    
    # The supervisor uses the prompt builder which includes memory in the prompt
    prompt = supervisor.prompt_builder.build_supervisor_prompt("new request")
    
    # Assert that the semantic memory is injected into the prompt
    assert "Exploring X." in prompt
    assert "Previous session explored X." in prompt
