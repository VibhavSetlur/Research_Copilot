from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

InterruptionClass = Literal["informational", "corrective", "branching", "speculative", "destructive", "replanning"]

class SideTask(BaseModel):
    task_id: str = Field(..., description="Unique ID for the side task")
    description: str = Field(..., description="Description of the side task")
    interruption_class: InterruptionClass = Field(..., description="Type of interruption")
    return_to_main_thread: bool = Field(True, description="Whether to resume the main task after this completes")

class ExecutionIntent(BaseModel):
    """Captures exactly what the execution engine must do next based on the Supervisor's decision."""
    target_nodes: List[str] = Field(default_factory=list, description="Specific nodes to execute or re-execute")
    branch_name_override: Optional[str] = Field(None, description="If branching, the new branch name")
    rollback_target: Optional[str] = Field(None, description="If repairing/rolling back, the node to revert to")
    suspend_execution: bool = Field(False, description="If True, execution is paused (e.g. for HITL approval or answering a question)")
    interruption_class: Optional[InterruptionClass] = Field(None, description="Type of interruption if task_type is interruption")
    side_task: Optional[SideTask] = Field(None, description="Side task details if this is a temporary detour")

class ConversationState(BaseModel):
    """Structures conversational memory."""
    turns: List[Dict[str, str]] = Field(default_factory=list, description="List of dicts with role and content")
    active_intent: str = Field(default="none", description="The current inferred user intent")
    unanswered_questions: List[str] = Field(default_factory=list, description="Questions pending user response")

class SupervisorDecision(BaseModel):
    intent: str = Field(..., description="The inferred primary intent of the user (e.g., exploratory, causal, predictive)")
    task_type: Literal[
        "new_task", "continuation", "interruption", "modify", "branch", "answer", "pause", "replan", "repair", "request_approval"
    ] = Field(..., description="The nature of the action to take")
    urgency: Literal["low", "medium", "high"] = Field(..., description="The urgency of the request")
    needs_clarification: bool = Field(..., description="Whether the request is too ambiguous and needs user clarification")
    needs_approval: bool = Field(..., description="Whether the proposed action requires user approval before execution")
    selected_workflow: Optional[str] = Field(None, description="The name of the workflow to run, if applicable")
    selected_agents: List[str] = Field(default_factory=list, description="The sub-agents that should be invoked")
    next_action: str = Field(..., description="The immediate next action to take")
    state_patch: Dict[str, Any] = Field(default_factory=dict, description="Key-value pairs to update in the state ledger")
    execution_intent: Optional[ExecutionIntent] = Field(None, description="Detailed instructions for the execution engine, if applicable")

class GraphMutation(BaseModel):
    action: Literal["insert", "remove", "rewire"] = Field(..., description="The type of mutation")
    node_id: str = Field(..., description="The target node ID")
    script_path: Optional[str] = Field(None, description="Script path (for insert)")
    depends_on: Optional[List[str]] = Field(None, description="Dependencies (for insert or rewire)")

class PlannerDecision(BaseModel):
    workflow_name: str = Field(..., description="The inferred workflow name")
    workflow_steps: List[str] = Field(..., description="The sequence of steps to execute")
    mutations: List[GraphMutation] = Field(default_factory=list, description="Graph mutations to apply to the execution DAG (if replanning)")
    gating_points: List[str] = Field(default_factory=list, description="Steps that require human approval")
    expected_artifacts: List[str] = Field(default_factory=list, description="List of artifacts that should be produced")
    fallback_plan: str = Field(..., description="What to do if the workflow fails")
    stop_conditions: List[str] = Field(default_factory=list, description="Conditions under which execution should halt")

class SkillPlannerOutput(BaseModel):
    relevant_skills: List[str] = Field(..., description="Skills to be loaded into context")
    excluded_skills: List[str] = Field(default_factory=list, description="Skills explicitly excluded from this workflow")
    required_agents: List[str] = Field(..., description="Agents required to complete the steps")
    workflow_steps: List[str] = Field(..., description="The steps to execute")
    expected_outputs: List[str] = Field(default_factory=list, description="Expected outputs from the workflow")
    confidence_score: float = Field(..., description="Confidence in this skill selection (0.0 to 1.0)")
