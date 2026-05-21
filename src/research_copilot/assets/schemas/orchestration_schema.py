from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class SupervisorDecision(BaseModel):
    intent: str = Field(..., description="The inferred primary intent of the user (e.g., exploratory, causal, predictive)")
    task_type: Literal["new_task", "continuation", "interruption"] = Field(..., description="Whether this is a new task, continuing an existing one, or an interruption")
    urgency: Literal["low", "medium", "high"] = Field(..., description="The urgency of the request")
    needs_clarification: bool = Field(..., description="Whether the request is too ambiguous and needs user clarification")
    needs_approval: bool = Field(..., description="Whether the proposed action requires user approval before execution")
    selected_workflow: Optional[str] = Field(None, description="The name of the workflow to run, if applicable")
    selected_agents: List[str] = Field(default_factory=list, description="The sub-agents that should be invoked")
    next_action: str = Field(..., description="The immediate next action to take")
    state_patch: Dict[str, Any] = Field(default_factory=dict, description="Key-value pairs to update in the state ledger")

class PlannerDecision(BaseModel):
    workflow_name: str = Field(..., description="The inferred workflow name")
    workflow_steps: List[str] = Field(..., description="The sequence of steps to execute")
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
