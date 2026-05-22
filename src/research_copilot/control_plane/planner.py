import json
import logging
from typing import Dict, Any

from research_copilot.assets.schemas.orchestration_schema import PlannerDecision

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
        
        prompt = (
            "You are the DynamicPlanner for Research Copilot.\n"
            "Score the following user request on these dimensions (0-10): novelty, statistical complexity, "
            "literature dependence, reproducibility requirements, sensitivity to missing assumptions, "
            "expected token cost, and need for human approval.\n\n"
            "Based on these scores, generate a structured workflow plan. Do not ask the user for a depth or workflow name.\n"
            "If the request implies replanning or mutating the DAG (e.g. inserting validation steps, removing bad nodes), "
            "include them in the 'mutations' array. Operations: insert, remove, rewire.\n"
            "Return EXACTLY a JSON object matching this schema:\n"
            "{\n"
            '  "workflow_name": "string (e.g. quick_exploratory, causal_investigation)",\n'
            '  "workflow_steps": ["step1", "step2"],\n'
            '  "mutations": [\n'
            '     {"action": "insert|remove|rewire", "node_id": "step_id", "script_path": "path", "depends_on": ["parent"]}\n'
            '  ],\n'
            '  "gating_points": ["step_requiring_approval"],\n'
            '  "expected_artifacts": ["artifact1.md"],\n'
            '  "fallback_plan": "string describing what to do if it fails",\n'
            '  "stop_conditions": ["condition1"]\n'
            "}\n\n"
            f"Project State: {json.dumps(project_state)}\n"
            f"User Request: {user_request}\n"
        )
        
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
