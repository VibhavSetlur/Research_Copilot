from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ExecutionNode(BaseModel):
    id: str
    objective: str
    reasoning: str
    expected_outputs: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    confidence_threshold: float = Field(0.5)
    retry_policy: str = Field("exponential_backoff")
    validation_policy: str = Field("strict")
    status: str = Field("pending")

class PlanMutation(BaseModel):
    action: str = Field(..., description="insert | remove | rewire | pause | retry | split | merge")
    target_node: str
    new_node: ExecutionNode = None
    new_dependencies: List[str] = None

class DynamicPlanner:
    """AI dynamically generates and rewrites research plans as Mutable Execution Graphs."""
    def __init__(self, call_llm_fn):
        self.call_llm = call_llm_fn

    def generate_initial_plan(self, intent: str, goal: str) -> List[ExecutionNode]:
        """Generates the initial DAG."""
        # Stub implementation for Phase 3 structure
        n1 = ExecutionNode(id="step_1", objective="Gather literature", reasoning="Need context")
        n2 = ExecutionNode(id="step_2", objective="Extract claims", reasoning="To build hypothesis", dependencies=["step_1"])
        return [n1, n2]

    def check_replanning_triggers(self, state: Dict[str, Any]) -> List[str]:
        """Checks if replanning is needed."""
        triggers = []
        if state.get("evidence_contradiction"):
            triggers.append("evidence_contradiction")
        if state.get("failed_validation"):
            triggers.append("failed_validation")
        if state.get("user_correction"):
            triggers.append("user_correction")
        return triggers

    def replan(self, current_plan: List[ExecutionNode], triggers: List[str]) -> List[PlanMutation]:
        """Generates mutations to fix the plan based on triggers."""
        # If contradiction, insert a debate node
        if "evidence_contradiction" in triggers:
            new_node = ExecutionNode(id="debate_1", objective="Resolve contradiction via skeptic", reasoning="Triggered by contradiction")
            return [PlanMutation(action="insert", target_node="debate_1", new_node=new_node)]
        return []
