from typing import Dict, Any
import json

class IntentToGraphTranslator:
    """Translates high-level natural language intents into specific graph mutations."""
    def __init__(self, call_llm):
        self.call_llm = call_llm

    def translate(self, intent: str) -> Dict[str, Any]:
        prompt = (
            "You are the Intent-to-Graph Translator.\n"
            f"User Intent: {intent}\n"
            "Translate this into specific graph mutations, priority changes, or methodology changes.\n"
            "Return JSON with 'mutations', 'priority_changes', 'methodology_changes'."
        )
        
        raw_response = self.call_llm(prompt)
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        try:
            mutations = json.loads(raw_response.strip())
            return mutations
        except Exception:
            return {"mutations": [], "priority_changes": {}, "methodology_changes": {}}
