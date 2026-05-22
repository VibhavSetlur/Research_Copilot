import pytest
import json
from pathlib import Path

from research_copilot.state.state_ledger import ResearchLedger
from research_copilot.agents.supervisor import SupervisorAgent

class MockPlanner:
    def generate_plan(self, request, state):
        class Plan:
            def __init__(self, workflow_name="test_workflow"):
                self.workflow_name = workflow_name
                self.workflow_steps = ["step1", "step2"]
            def model_dump(self):
                return {"workflow_name": self.workflow_name, "workflow_steps": ["step1", "step2"]}
        
        # Determine plan name based on request
        if "side task" in request:
            return Plan("side_task")
        elif "start" in request:
            return Plan("main_task")
        elif "resume" in request:
            return Plan("main_task")
            
        return Plan()

class MockRouter:
    def get_minimal_context(self, query):
        return {"required_agents": ["analyst"]}

def create_mock_llm(responses):
    def mock_llm_call(prompt: str) -> str:
        parts = prompt.split("User says: ")
        user_msg = parts[-1].split("\n")[0].strip() if len(parts) > 1 else prompt
        
        for key, response in responses.items():
            if key == user_msg:
                # Add missing defaults if not provided in mock response
                response.setdefault("urgency", "low")
                response.setdefault("needs_clarification", False)
                response.setdefault("needs_approval", False)
                return json.dumps(response)
        
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

def test_nested_interruptions(tmp_path: Path):
    """Test pushing multiple tasks to the interrupt stack."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    ledger._save(ledger._default_state())
    
    responses = {
        "start the main task": {
            "intent": "exploratory",
            "task_type": "new_task",
            "next_action": "Starting main task..."
        },
        "pause, let's do a side task": {
            "intent": "exploratory",
            "task_type": "interruption",
            "next_action": "Pushing main to stack..."
        },
        "actually, pause that side task, answer a question": {
            "intent": "informational",
            "task_type": "interruption",
            "next_action": "Pushing side task to stack..."
        }
    }
    
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=create_mock_llm(responses))
    supervisor.planner = MockPlanner()
    supervisor.router = MockRouter()
    
    # 1. Start main
    supervisor.process_request("start the main task")
    assert ledger.get()["current_plan"]["workflow_name"] == "main_task"
    
    # 2. First interrupt
    supervisor.process_request("pause, let's do a side task")
    assert len(ledger.get().get("interrupt_stack", [])) == 1
    
    # 3. Start side task explicitly as new task while main is paused
    responses["start the side task"] = {
        "intent": "exploratory",
        "task_type": "new_task",
        "next_action": "Starting side task..."
    }
    supervisor.process_request("start the side task")
    assert ledger.get()["current_plan"]["workflow_name"] == "side_task"
    
    # 4. Second interrupt
    supervisor.process_request("actually, pause that side task, answer a question")
    assert len(ledger.get().get("interrupt_stack", [])) == 2

def test_return_to_main_thread(tmp_path: Path):
    """Test popping tasks from the interrupt stack."""
    ledger = ResearchLedger(tmp_path / "state_ledger.json")
    ledger._save(ledger._default_state())
    
    responses = {
        "start the main task": {
            "intent": "exploratory",
            "task_type": "new_task",
            "next_action": "Starting..."
        },
        "pause": {
            "intent": "exploratory",
            "task_type": "interruption",
            "next_action": "Pausing..."
        },
        "resume": {
            "intent": "exploratory",
            "task_type": "continuation",
            "next_action": "Resuming..."
        }
    }
    
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=create_mock_llm(responses))
    supervisor.planner = MockPlanner()
    supervisor.router = MockRouter()
    
    supervisor.process_request("start the main task")
    assert ledger.get()["current_plan"]["workflow_name"] == "main_task"
    
    supervisor.process_request("pause")
    assert len(ledger.get().get("interrupt_stack", [])) == 1
    
    # Set current plan to none to simulate doing something else
    ledger.update(current_plan={})
    
    supervisor.process_request("resume")
    
    state = ledger.get()
    assert len(state.get("interrupt_stack", [])) == 0
    assert state["current_plan"]["workflow_name"] == "main_task"
