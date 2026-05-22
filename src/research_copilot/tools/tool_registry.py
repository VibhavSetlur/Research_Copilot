from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ToolMetadata(BaseModel):
    tool_name: str = Field(..., description="The exact name of the script or tool")
    capabilities: List[str] = Field(..., description="Semantic capabilities (e.g. claim_validation, literature_search)")
    cost: str = Field(..., description="low, medium, high")
    risk: str = Field(..., description="low, medium, high")
    failure_modes: List[str] = Field(default_factory=list, description="Known ways this tool can fail")
    preferred_when: List[str] = Field(default_factory=list, description="Conditions under which this tool is preferred")
    inputSchema: Dict[str, Any] = Field(default_factory=lambda: {"type": "object", "properties": {}}, description="JSON Schema for MCP")

class ToolRegistry:
    """Registry that maps semantic capabilities to specific tools."""
    
    def __init__(self):
        self._tools: Dict[str, ToolMetadata] = {}
        self._register_defaults()
        
    def _register_defaults(self):
        # Default tools for the Research Copilot
        self.register(ToolMetadata(
            tool_name="citation_verifier.py",
            capabilities=["claim_validation", "evidence_strengthening", "citation_check"],
            cost="medium",
            risk="low",
            failure_modes=["PDF not found", "Paywall"],
            preferred_when=["verifying explicit factual claims"]
        ))
        self.register(ToolMetadata(
            tool_name="statistical_analyzer.py",
            capabilities=["claim_validation", "data_analysis", "hypothesis_testing"],
            cost="high",
            risk="medium",
            failure_modes=["Data missing", "Assumptions violated"],
            preferred_when=["validating numeric data against a hypothesis"]
        ))
        self.register(ToolMetadata(
            tool_name="literature_scraper.py",
            capabilities=["literature_search", "evidence_gathering"],
            cost="low",
            risk="low",
            failure_modes=["Rate limits", "Empty results"],
            preferred_when=["exploring new domains"]
        ))
        self.register(ToolMetadata(
            tool_name="quick_search.py",
            capabilities=["literature_search"],
            cost="low",
            risk="low",
            failure_modes=["Ambiguous query"],
            preferred_when=["user asks a quick factual question"]
        ))

    def register(self, tool: ToolMetadata):
        self._tools[tool.tool_name] = tool
        
    def get_tool(self, tool_name: str) -> ToolMetadata:
        return self._tools.get(tool_name)
        
    def get_all(self) -> List[ToolMetadata]:
        return list(self._tools.values())
        
    def find_tools_by_capability(self, capability: str) -> List[ToolMetadata]:
        """Finds all tools that provide a specific capability."""
        matches = []
        for tool in self._tools.values():
            if capability in tool.capabilities:
                matches.append(tool)
        return matches
