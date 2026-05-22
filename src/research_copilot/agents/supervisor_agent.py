import json
import logging

from research_copilot.schemas.orchestration_schema import ExecutionIntent
from research_copilot.state.state_ledger import ResearchLedger

logger = logging.getLogger("research.supervisor")

class SupervisorAgent:
    """Top-level cognitive orchestrator that interprets user intent and steers the execution graph."""

    MAX_ITERATIONS = 15

    def __init__(self, root, ledger: ResearchLedger, call_llm_fn=None):
        self.root = root
        self.ledger = ledger
        self.session_iterations = 0
        if call_llm_fn:
            self.call_llm = call_llm_fn
        else:
            from research_copilot.chat import call_llm
            self.call_llm = call_llm
            
        # We will initialize state engines here once built
        # self.cognitive_tracker = CognitiveStateTracker(ledger)
        # self.prompt_builder = PromptBuilder(self.ledger, self.cognitive_tracker)

    def process_request(self, user_request: str, mode: str = "exploratory") -> ExecutionIntent:
        """Determines the nature of the request and decides on next actions."""
        self.session_iterations += 1
        if self.session_iterations > self.MAX_ITERATIONS:
            logger.error("Halt-and-Catch-Fire: MAX_ITERATIONS reached.")
            raise RuntimeError(f"Safety limit reached: SupervisorAgent exceeded {self.MAX_ITERATIONS} iterations.")

        
        # Simple prompt for Phase 1
        prompt = f"""
You are the SupervisorAgent for an Autonomous Research OS.
Analyze the user request and determine the exact ExecutionIntent.
User Request: {user_request}

Determine the task_action from these options:
- continue: normal progression of the active plan
- modify: user wants to change a hypothesis or assumption mid-analysis
- branch: user wants to explore a new direction
- pause: wait for user action or data
- spawn_side_task: a tangent that does not mutate the main DAG
- replan: user changed research direction entirely
- answer_directly: answer a spontaneous question
- repair_state: execution failed or user corrected a mistake

Return EXACTLY a JSON object matching this schema:
{{
  "user_goal": "string",
  "intent_type": "string",
  "task_action": "continue | modify | branch | pause | spawn_side_task | replan | answer_directly | repair_state",
  "confidence": 0.95,
  "requires_human_input": false,
  "affected_research_objects": [],
  "planning_depth": "shallow | deep | exhaustive",
  "next_action_description": "string",
  "state_patch": {{}}
}}
"""
        
        raw_response = self.call_llm(prompt)
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        try:
            data = json.loads(raw_response.strip())
            
            # Apply any state patches
            if data.get("state_patch"):
                self.ledger.update(**data["state_patch"])
            
            return ExecutionIntent(**data)
        except Exception as e:
            logger.error(f"Failed to parse ExecutionIntent: {e}")
            return ExecutionIntent(
                user_goal="Error parsing intent",
                intent_type="unknown",
                task_action="answer_directly",
                confidence=0.0,
                requires_human_input=True,
                affected_research_objects=[],
                planning_depth="shallow",
                next_action_description="Ask user for clarification",
                state_patch={}
            )
