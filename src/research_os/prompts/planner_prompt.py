import json
from typing import Dict, Any

def build_planner_prompt(user_request: str, project_state: Dict[str, Any]) -> str:
    """[Deprecated] Builds a prompt for an autonomous planner.

    Planning is now the IDE's responsibility. The DAGValidator provides
    structural validation only — no LLM calls, no decision-making.
    """
    return (
        "You are the DynamicPlanner for Research OS.\n"
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
