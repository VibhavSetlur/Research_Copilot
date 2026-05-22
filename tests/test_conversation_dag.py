import json
from pathlib import Path

from research_os.state.state_ledger import ResearchLedger
from research_os.agents.supervisor_agent import SupervisorAgent
from research_os.execution.scheduler import TaskScheduler

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

def mock_llm_call(prompt: str) -> str:
    """Mock LLM response for testing Supervisor logic."""
    if "Wait, what does this mean?" in prompt:
        # Interruption
        return json.dumps({
            "intent": "none",
            "task_type": "interruption",
            "urgency": "low",
            "needs_clarification": False,
            "needs_approval": False,
            "next_action": "I can explain that.",
            "state_patch": {}
        })
    else:
        # New task
        return json.dumps({
            "intent": "exploratory",
            "task_type": "new_task",
            "urgency": "medium",
            "needs_clarification": False,
            "needs_approval": False,
            "next_action": "I will execute the research.",
            "state_patch": {"phase": "running"}
        })

def test_conversation_dag_interruption(tmp_path: Path):
    """Test mid-run interruption and state ledger updates."""
    
    # Initialize state
    state_file = tmp_path / "state_ledger.json"
    ledger = ResearchLedger(state_file)
    ledger._save(ledger._default_state())
    
    supervisor = SupervisorAgent(tmp_path, ledger, call_llm_fn=mock_llm_call)
    # Monkeypatch for testing without actual LLM
    supervisor.planner = MockPlanner()
    supervisor.router = MockRouter()
    
    scheduler = TaskScheduler(ledger)
    
    # Turn 1: User asks for a new task
    decision = supervisor.process_request("Can you explore the dataset?")
    assert decision.task_type == "new_task"
    assert decision.intent == "exploratory"
    assert decision.selected_workflow == "test_workflow"
    
    state = ledger.get()
    assert state["active_user_intent"] == "exploratory"
    assert state["current_plan"]["workflow_name"] == "test_workflow"
    assert state["phase"] == "running"
    
    # Check scheduler step
    next_step = scheduler.get_next_executable_node(state["current_plan"])
    assert next_step == "step1"
    
    # Simulate step1 completion
    ledger.add_dag_node("step1_001", "step1.py", [], [])
    dag = ledger.get_dag()
    dag["nodes"]["step1_001"]["status"] = "success"
    ledger._save_to_path(ledger.get_dag_path(), dag)
    
    # Need to load the DAG into state representation for the scheduler
    # wait, the scheduler does state = ledger.get(), which doesn't include nodes
    # Let me check scheduler.py
    
    # Check next step
    next_step = scheduler.get_next_executable_node(state["current_plan"])
    assert next_step == "step2"
    
    # Turn 2: User interrupts mid-run
    decision = supervisor.process_request("Wait, what does this mean?")
    assert decision.task_type == "interruption"
    
    state = ledger.get()
    assert len(state["interrupt_stack"]) == 1
    paused_task = state["interrupt_stack"][0]
    assert paused_task["active_user_intent"] == "exploratory"
    
    # After interruption, pop from stack
    task = ledger.pop_interrupt()
    assert task["active_user_intent"] == "exploratory"
    assert len(ledger.get()["interrupt_stack"]) == 0
