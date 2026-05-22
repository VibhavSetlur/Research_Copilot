import json
from pathlib import Path

from research_copilot.state.state_ledger import ResearchLedger
from research_copilot.agents.supervisor_agent import SupervisorAgent

class MockPlanner:
    def generate_plan(self, request, state):
        class Plan:
            def __init__(self):
                self.workflow_name = "test_workflow"
                self.workflow_steps = ["step1", "step2"]
            def model_dump(self):
                return {"workflow_name": "test_workflow", "workflow_steps": ["step1", "step2"]}
        return Plan()

class MockRouter:
    def get_minimal_context(self, query):
        return {"required_agents": ["analyst"]}

def create_mock_llm(responses):
    def mock_llm_call(prompt: str) -> str:
        # Look specifically at the user message portion to avoid matching history
        parts = prompt.split("--- USER MESSAGE ---")
        user_msg = parts[-1] if len(parts) > 1 else prompt
        for key, response in responses.items():
            if key in user_msg:
                return json.dumps(response)
        return "{}"
    return mock_llm_call

def test_conversational_branch(tmp_path: Path):
    """Test user changing hypothesis mid-analysis triggering a branch."""
    state_file = tmp_path / "state_ledger.json"
    ledger = ResearchLedger(state_file)
    ledger._save(ledger._default_state())
    
    responses = {
        "explore the dataset": {
            "intent": "exploratory",
            "task_type": "new_task",
            "urgency": "low",
            "needs_clarification": False,
            "needs_approval": False,
            "next_action": "Exploring...",
            "state_patch": {}
        },
        "change the hypothesis to focus on Bayesian": {
            "intent": "exploratory",
            "task_type": "branch",
            "urgency": "medium",
            "needs_clarification": False,
            "needs_approval": False,
            "next_action": "Branching and replanning...",
            "state_patch": {},
            "execution_intent": {
                "branch_name_override": "bayesian_focus"
            }
        }
    }
    
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=create_mock_llm(responses))
    supervisor.planner = MockPlanner()
    supervisor.router = MockRouter()
    
    # Start initial task
    supervisor.process_request("Can you explore the dataset?")
    state = ledger.get()
    assert state["current_plan"]["workflow_name"] == "test_workflow"
    
    # Change hypothesis -> Branch
    supervisor.process_request("Actually, change the hypothesis to focus on Bayesian methods.")
    state = ledger.get()
    assert state.get("active_branch") == "bayesian_focus"
    assert "bayesian_focus" in state.get("branches", {})

def test_conversational_replan(tmp_path: Path):
    """Test user uploading contradictory evidence triggering a replan."""
    state_file = tmp_path / "state_ledger.json"
    ledger = ResearchLedger(state_file)
    ledger._save(ledger._default_state())
    
    responses = {
        "This paper contradicts our assumption": {
            "intent": "causal",
            "task_type": "replan",
            "urgency": "high",
            "needs_clarification": False,
            "needs_approval": False,
            "next_action": "I will update the plan based on the new evidence.",
            "state_patch": {
                "dead_ends": ["Previous causal assumption"]
            }
        }
    }
    
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=create_mock_llm(responses))
    supervisor.planner = MockPlanner()
    supervisor.router = MockRouter()
    
    supervisor.process_request("This paper contradicts our assumption.")
    state = ledger.get()
    assert "Previous causal assumption" in state["dead_ends"]
    assert state["current_plan"]["workflow_name"] == "test_workflow"

def test_conversational_repair(tmp_path: Path):
    """Test user correcting a mistake requiring rollback (repair)."""
    state_file = tmp_path / "state_ledger.json"
    ledger = ResearchLedger(state_file)
    ledger._save(ledger._default_state())
    
    responses = {
        "You used the wrong column, go back": {
            "intent": "exploratory",
            "task_type": "repair",
            "urgency": "medium",
            "needs_clarification": False,
            "needs_approval": False,
            "next_action": "Rolling back and fixing.",
            "state_patch": {},
            "execution_intent": {
                "rollback_target": "step1_001"
            }
        }
    }
    
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=create_mock_llm(responses))
    supervisor.planner = MockPlanner()
    supervisor.router = MockRouter()
    
    supervisor.process_request("You used the wrong column, go back to step 1.")
    state = ledger.get()
    assert len(state.get("errors", [])) > 0
    assert "Rolling back to step1_001" in state["errors"][0]["message"]
