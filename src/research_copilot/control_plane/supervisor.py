import json
import logging
from typing import Dict, Any

from research_copilot.assets.schemas.orchestration_schema import SupervisorDecision
from research_copilot.control_plane.planner import PlannerAgent
from research_copilot.intent_router import IntentRouter
from research_copilot.control_plane.prompt_builder import PromptBuilder
from research_copilot.core.state_ledger import ResearchLedger

logger = logging.getLogger("research.supervisor")

class SupervisorAgent:
    """Top-level orchestrator that owns conversation, task decomposition, and state transitions."""

    def __init__(self, root, ledger: ResearchLedger, call_llm_fn=None):
        self.root = root
        self.ledger = ledger
        if call_llm_fn:
            self.call_llm = call_llm_fn
        else:
            from research_copilot.chat import call_llm
            self.call_llm = call_llm
            
        self.planner = PlannerAgent(root, self.call_llm)
        self.router = IntentRouter(root)
        self.prompt_builder = PromptBuilder(self.ledger)

    def process_request(self, user_request: str) -> SupervisorDecision:
        """Determines the nature of the request and decides on next actions."""
        
        # Build prompt using state-aware builder
        prompt = self.prompt_builder.build_supervisor_prompt(user_request)
        
        raw_response = self.call_llm(prompt)
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        try:
            data = json.loads(raw_response.strip())
            
            # Record user turn
            self.ledger.add_conversation_turn("user", user_request)
            
            # Apply any state patches
            if data.get("state_patch"):
                self.ledger.update(**data["state_patch"])
            
            project_state = self.ledger.get()
            
            # If it's a new task or continuation, invoke the planner and router
            if data.get("task_type") in ("new_task", "continuation") and not data.get("needs_clarification"):
                plan = self.planner.generate_plan(user_request, project_state)
                # We can also get skill routing info
                router_output = self.router.get_minimal_context(user_request)
                
                data["selected_workflow"] = plan.workflow_name
                # Combine planned steps and agents
                data["selected_agents"] = router_output.get("required_agents", [])
                
                # Save active plan
                self.ledger.update(
                    active_user_intent=data.get("intent", "none"),
                    current_plan=plan.model_dump()
                )
                
            elif data.get("task_type") == "interruption":
                # Push the old task context
                active_task_summary = self.ledger.get_active_task_summary()
                if active_task_summary:
                    self.ledger.push_interrupt({"active_user_intent": project_state.get("active_user_intent"), "current_plan": project_state.get("current_plan")})
            
            # Record assistant action
            self.ledger.add_conversation_turn("assistant", data.get("next_action", ""))
                
            return SupervisorDecision(**data)
        except Exception as e:
            logger.error(f"Failed to parse supervisor decision: {e}")
            return SupervisorDecision(
                intent="unknown",
                task_type="interruption",
                urgency="low",
                needs_clarification=True,
                needs_approval=False,
                selected_agents=[],
                next_action="Ask user for clarification",
                state_patch={}
            )
