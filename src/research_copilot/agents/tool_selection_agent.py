import json
import logging
from typing import List
from research_copilot.tools.capability_registry import CapabilityRegistry, CapabilityMetadata

logger = logging.getLogger(__name__)

class ToolSelectionAgent:
    """Autonomous execution chain generation based on capabilities."""
    def __init__(self, registry: CapabilityRegistry, call_llm_fn):
        self.registry = registry
        self.call_llm = call_llm_fn

    def plan_execution_chain(self, goal: str) -> List[str]:
        """Maps a goal to a sequence of tools based on capabilities."""
        available_caps = {name: meta.capabilities for name, meta in self.registry.registry.items()}
        
        prompt = (
            "You are the ToolSelectionAgent.\n"
            f"Goal: {goal}\n"
            f"Available Tools and Capabilities: {json.dumps(available_caps)}\n"
            "Return EXACTLY a JSON array of tool names to execute in sequence."
        )
        
        raw_response = self.call_llm(prompt)
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        try:
            chain = json.loads(raw_response.strip())
            if isinstance(chain, list):
                return chain
            return []
        except Exception as e:
            logger.error(f"Failed to parse tool execution chain: {e}")
            return []
