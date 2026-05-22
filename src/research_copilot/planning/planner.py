import json
import logging
from typing import Dict, Any

from research_copilot.schemas.orchestration_schema import PlannerDecision

logger = logging.getLogger("research.planner")

class PlannerAgent:
    """Replaces manual workflow selection with automated LLM-based scoring and planning."""

    def __init__(self, root, call_llm_fn=None):
        self.root = root
        # Using a provided call_llm function or a fallback
        if call_llm_fn:
            self.call_llm = call_llm_fn
        else:
            from research_copilot.chat import call_llm
            self.call_llm = call_llm

    def generate_plan(self, user_request: str, project_state: Dict[str, Any]) -> PlannerDecision:
        """Scores the request and maps it to a workflow plan."""
        
        from research_copilot.prompts.planner_prompt import build_planner_prompt
        prompt = build_planner_prompt(user_request, project_state)
        
        raw_response = self.call_llm(prompt)
        
        # Parse response
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        try:
            data = json.loads(raw_response.strip())
            return PlannerDecision(**data)
        except Exception as e:
            logger.error(f"Failed to parse planner decision: {e}")
            # Fallback safe plan
            return PlannerDecision(
                workflow_name="exploratory_fallback",
                workflow_steps=["intake", "scan"],
                gating_points=[],
                expected_artifacts=[],
                fallback_plan="Ask user for clarification",
                stop_conditions=["Data missing"]
            )
