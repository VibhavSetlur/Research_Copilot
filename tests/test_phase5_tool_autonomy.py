import json

from research_copilot.tools.tool_registry import ToolRegistry
from research_copilot.planning.capability_planner import CapabilityPlanner

def create_mock_llm(response_json):
    def mock_llm_call(prompt: str) -> str:
        return json.dumps(response_json)
    return mock_llm_call

def test_multiple_tool_candidates():
    """Test that the planner can select multiple tools for a complex goal."""
    registry = ToolRegistry()
    
    # We mock the LLM to return two tools
    planner = CapabilityPlanner(registry, call_llm_fn=create_mock_llm([
        "literature_scraper.py", 
        "citation_verifier.py"
    ]))
    
    tools = planner.select_tools_for_goal("Find literature and verify claims.")
    
    assert len(tools) == 2
    assert tools[0].tool_name == "literature_scraper.py"
    assert tools[1].tool_name == "citation_verifier.py"

def test_incorrect_tool_selection_recovery():
    """Test that if the LLM hallucinates a tool, it gracefully drops it or ignores it."""
    registry = ToolRegistry()
    
    # Mock LLM returns a real tool and a fake one
    planner = CapabilityPlanner(registry, call_llm_fn=create_mock_llm([
        "quick_search.py", 
        "hallucinated_tool.py"
    ]))
    
    tools = planner.select_tools_for_goal("Quick search something.")
    
    assert len(tools) == 1
    assert tools[0].tool_name == "quick_search.py"

def test_fallback_tools():
    """Test that fallback finds another tool with the same capability."""
    registry = ToolRegistry()
    planner = CapabilityPlanner(registry, call_llm_fn=create_mock_llm([]))
    
    # literature_scraper.py has capability "literature_search"
    # quick_search.py also has capability "literature_search"
    
    fallback = planner.get_fallback_tool("literature_scraper.py", "Find some papers")
    
    assert fallback is not None
    assert fallback.tool_name == "quick_search.py"
    assert "literature_search" in fallback.capabilities
