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
        parts = prompt.split("--- USER MESSAGE ---")
        user_msg = parts[-1] if len(parts) > 1 else prompt
        for key, response in responses.items():
            if key in user_msg:
                return json.dumps(response)
        return "{}"
    return mock_llm_call

def test_interruption_during_active_workflow(tmp_path: Path):
    """Test interruption during active workflow."""
    state_file = tmp_path / "state_ledger.json"
    ledger = ResearchLedger(state_file)
    ledger._save(ledger._default_state())
    
    responses = {
        "start the task": {
            "intent": "exploratory",
            "task_type": "new_task",
            "next_action": "Starting...",
            "state_patch": {}
        },
        "pause for a second, what was the data size?": {
            "intent": "informational",
            "task_type": "interruption",
            "next_action": "Answering question...",
            "state_patch": {}
        }
    }
    
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=create_mock_llm(responses))
    supervisor.planner = MockPlanner()
    supervisor.router = MockRouter()
    
    supervisor.process_request("start the task")
    state = ledger.get()
    assert state["current_plan"]["workflow_name"] == "test_workflow"
    
    supervisor.process_request("pause for a second, what was the data size?")
    state = ledger.get()
    assert len(state.get("interrupt_stack", [])) > 0

def test_spontaneous_follow_up_questions(tmp_path: Path):
    """Test spontaneous follow-up questions."""
    state_file = tmp_path / "state_ledger.json"
    ledger = ResearchLedger(state_file)
    ledger._save(ledger._default_state())
    
    responses = {
        "start the task": {
            "intent": "exploratory",
            "task_type": "new_task",
            "next_action": "Starting...",
            "state_patch": {}
        },
        "can you also explain what step 1 does?": {
            "intent": "informational",
            "task_type": "interruption",
            "next_action": "Explaining step 1...",
            "state_patch": {}
        }
    }
    
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=create_mock_llm(responses))
    supervisor.planner = MockPlanner()
    supervisor.router = MockRouter()
    
    supervisor.process_request("start the task")
    supervisor.process_request("can you also explain what step 1 does?")
    state = ledger.get()
    assert len(state.get("interrupt_stack", [])) > 0

def test_clarification_without_dag_corruption(tmp_path: Path):
    """Test clarification without DAG corruption."""
    state_file = tmp_path / "state_ledger.json"
    ledger = ResearchLedger(state_file)
    ledger._save(ledger._default_state())
    
    responses = {
        "do something": {
            "intent": "exploratory",
            "task_type": "new_task",
            "needs_clarification": True,
            "next_action": "I need clarification...",
            "state_patch": {}
        }
    }
    
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=create_mock_llm(responses))
    supervisor.planner = MockPlanner()
    supervisor.router = MockRouter()
    
    supervisor.process_request("do something")
    state = ledger.get()
    assert state.get("current_plan") is None
