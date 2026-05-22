import json
from typing import Dict, Any

class ConversationalDiffEngine:
    """Translates user corrections automatically into DAG mutations and state updates."""
    def __init__(self, ledger, call_llm):
        self.ledger = ledger
        self.call_llm = call_llm

    def compute_diff(self, user_correction: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates what needs to change in the graph/memory based on user correction."""
        prompt = (
            "You are the Conversational Diff Engine.\n"
            f"User Correction: {user_correction}\n"
            "Identify the necessary mutations for the DAG, hypotheses, and evidence graph.\n"
            "Return JSON with 'dag_mutations', 'hypothesis_updates', 'evidence_updates'."
        )
        
        raw_response = self.call_llm(prompt)
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        try:
            diff = json.loads(raw_response.strip())
            return diff
        except Exception:
            return {"dag_mutations": [], "hypothesis_updates": [], "evidence_updates": []}
