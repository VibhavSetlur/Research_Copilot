import json
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone

from research_copilot.state.state_ledger import ResearchLedger
from research_copilot.assets.schemas.state_schema import EpisodicMemory, SemanticMemory, MemoryState

logger = logging.getLogger(__name__)

class MemorySynthesizer:
    """Compresses conversational turns into semantic and episodic memory."""

    def __init__(self, ledger: ResearchLedger, call_llm_fn=None):
        self.ledger = ledger
        if call_llm_fn:
            self.call_llm = call_llm_fn
        else:
            from research_copilot.chat import call_llm
            self.call_llm = call_llm

    def synthesize_episode(self, trigger: str, recent_turns: List[Dict[str, str]], decisions: List[str] = None, rejected: List[str] = None) -> EpisodicMemory:
        """Creates a new episodic memory from recent context and adds it to the ledger."""
        decisions = decisions or []
        rejected = rejected or []
        
        prompt = (
            "You are the MemorySynthesizer for Research Copilot.\n"
            "Summarize the following recent conversation into a concise episodic memory.\n"
            "Focus on the rationale behind any decisions made.\n\n"
            f"Recent Turns: {json.dumps(recent_turns)}\n"
            f"Decisions explicitly made: {json.dumps(decisions)}\n"
            "Return EXACTLY a JSON string with a 'summary' key."
        )
        
        raw_response = self.call_llm(prompt)
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        try:
            data = json.loads(raw_response.strip())
            summary = data.get("summary", "Failed to summarize.")
        except Exception as e:
            logger.error(f"Failed to parse memory summary: {e}")
            summary = "Error parsing summary."
            
        episode = EpisodicMemory(
            timestamp=datetime.now(timezone.utc).isoformat(),
            trigger=trigger,
            summary=summary,
            decisions_made=decisions,
            rejected_alternatives=rejected
        )
        
        # Save to state
        state = self.ledger.get()
        if "memory" not in state:
            state["memory"] = MemoryState().model_dump()
            
        state["memory"]["episodic"].append(episode.model_dump())
        self.ledger.update(memory=state["memory"])
        
        return episode

    def roll_semantic_memory(self):
        """Updates the global rolling semantic summary based on all episodes."""
        state = self.ledger.get()
        if "memory" not in state:
            return
            
        episodes = state["memory"].get("episodic", [])
        if not episodes:
            return
            
        prompt = (
            "You are the SemanticMemory Synthesizer.\n"
            "Based on the following chronological episodes, write a rolling summary of the entire project state and a narrative of how our confidence has evolved.\n"
            f"Episodes: {json.dumps([e['summary'] for e in episodes[-5:]])}\n" # Only look at last 5 for rolling
            "Return EXACTLY a JSON object:\n"
            "{\n"
            '  "project_summary": "...",\n'
            '  "confidence_evolution": "..."\n'
            "}"
        )
        
        raw_response = self.call_llm(prompt)
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        try:
            data = json.loads(raw_response.strip())
            semantic = SemanticMemory(
                project_summary=data.get("project_summary", ""),
                confidence_evolution=data.get("confidence_evolution", "")
            )
            state["memory"]["semantic"] = semantic.model_dump()
            self.ledger.update(memory=state["memory"])
        except Exception as e:
            logger.error(f"Failed to roll semantic memory: {e}")
