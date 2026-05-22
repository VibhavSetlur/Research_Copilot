import json
import logging
from typing import List, Dict, Optional

from research_copilot.tools.tool_registry import ToolRegistry, ToolMetadata

logger = logging.getLogger(__name__)

class CapabilityPlanner:
    """Maps research goals to semantic capabilities to specific tools."""
    
    def __init__(self, registry: ToolRegistry, call_llm_fn=None):
        self.registry = registry
        if call_llm_fn:
            self.call_llm = call_llm_fn
        else:
            from research_copilot.chat import call_llm
            self.call_llm = call_llm

    def select_tools_for_goal(self, goal: str, constraints: dict = None) -> List[ToolMetadata]:
        """Uses the LLM to identify the required semantic capabilities for a goal, then maps them to tools."""
        
        tools_dump = [t.model_dump() for t in self.registry.get_all()]
        
        prompt = (
            "You are the CapabilityPlanner for Research Copilot.\n"
            "Your job is to select the most appropriate tool(s) to achieve a given research goal.\n"
            "Choose tools based on their 'capabilities', 'cost', 'risk', and 'preferred_when' conditions.\n\n"
            f"Goal: {goal}\n"
            f"Constraints: {constraints or {}}\n"
            f"Available Tools: {json.dumps(tools_dump)}\n\n"
            "Return EXACTLY a JSON array of selected tool names (strings)."
        )
        
        raw_response = self.call_llm(prompt)
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        try:
            selected_names = json.loads(raw_response.strip())
            if not isinstance(selected_names, list):
                selected_names = [selected_names]
        except Exception as e:
            logger.error(f"Failed to parse capability planner output: {e}")
            return []
            
        selected_tools = []
        for name in selected_names:
            tool = self.registry.get_tool(name)
            if tool:
                selected_tools.append(tool)
                
        return selected_tools
        
    def get_fallback_tool(self, failed_tool_name: str, goal: str) -> Optional[ToolMetadata]:
        """Finds an alternative tool with similar capabilities to a failed tool."""
        failed_tool = self.registry.get_tool(failed_tool_name)
        if not failed_tool:
            return None
            
        # Try to find another tool that shares capabilities
        for cap in failed_tool.capabilities:
            candidates = self.registry.find_tools_by_capability(cap)
            for candidate in candidates:
                if candidate.tool_name != failed_tool_name and candidate.risk != "high":
                    return candidate
                    
        return None
