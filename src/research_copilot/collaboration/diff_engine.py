from typing import Dict, Any, List
from pydantic import BaseModel, Field
import json

class GraphPatch(BaseModel):
    action: str = Field(..., description="remove_evidence, redirect_analysis, modify_assumption, override_conclusion")
    target_id: str = Field(..., description="The ID of the hypothesis, assumption, or node to modify")
    new_value: str = Field(default="", description="The new value or directive")

class ConversationalDiffEngine:
    """Translates user natural language corrections into direct state graph and evidence mutations."""
    
    def __init__(self, call_llm, cognitive_tracker=None, mutation_engine=None):
        self.call_llm = call_llm
        self.cognitive_tracker = cognitive_tracker
        self.mutation_engine = mutation_engine
        
    def parse_user_correction(self, user_input: str, current_state: Dict[str, Any]) -> List[GraphPatch]:
        """Analyzes conversational feedback and extracts necessary structural mutations."""
        prompt = f"""
        The user has provided conversational feedback or a correction.
        Translate this feedback into structural graph mutations.
        
        Current State Context: {json.dumps(current_state)[:1000]} # Truncated for token limit
        User Input: "{user_input}"
        
        Available Actions: remove_evidence, redirect_analysis, modify_assumption, override_conclusion
        
        Return a JSON list of patch objects. Each object must have:
        - action (string)
        - target_id (string)
        - new_value (string)
        """
        
        raw_response = self.call_llm(prompt)
        if raw_response.startswith("```json"): raw_response = raw_response[7:]
        if raw_response.endswith("```"): raw_response = raw_response[:-3]
        
        try:
            data = json.loads(raw_response.strip())
            return [GraphPatch(**item) for item in data]
        except Exception:
            return []
            
    def apply_patches(self, patches: List[GraphPatch]):
        """Applies the resolved patches to the system state."""
        for patch in patches:
            if patch.action == "remove_evidence" and self.cognitive_tracker:
                # E.g., target_id is the citation ID to remove
                self.cognitive_tracker.log_contradiction(f"User removed evidence: {patch.new_value}", related_claims=[patch.target_id])
            elif patch.action == "redirect_analysis" and self.mutation_engine:
                # Inject a new step dynamically
                self.mutation_engine.insert_node(patch.target_id, patch.new_value, [])
            elif patch.action == "modify_assumption" and self.cognitive_tracker:
                self.cognitive_tracker.invalidate_hypothesis(patch.target_id, patch.new_value)
            elif patch.action == "override_conclusion" and self.cognitive_tracker:
                self.cognitive_tracker.add_claim(f"Overridden by user: {patch.new_value}", provenance="User override")
