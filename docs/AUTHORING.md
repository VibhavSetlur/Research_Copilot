# Tool Authoring

In Research OS, tools are exposed via the Model Context Protocol (MCP) to be driven by the AI IDE. The OS provides a fixed set of capabilities (hands, memory, system controls) that the IDE can call.

---

## Tool Architecture

### Fixed Tool Set

Research OS provides a set of tools defined in `src/research_os/server.py` in the `TOOL_DEFINITIONS` dictionary. These tools are logically grouped:

- **System tools (`sys.*`):** State management, file IO, checkpoints, configuration
- **Memory tools (`mem.*`):** Analysis logging and methodological tracking
- **Action tools (`tool.*`):** Search, code execution, environment freezing

### Tool Registration

Tools are registered in the MCP server via the `TOOL_DEFINITIONS` dictionary. Each tool has:

- **name:** The tool identifier (e.g., `tool.python.exec`)
- **description:** Human-readable description of what the tool does
- **inputSchema:** JSON Schema defining required and optional parameters

Example from `server.py`:
```python
TOOL_DEFINITIONS: dict[str, dict[str, Any]] = {
    "tool.python.exec": {
        "description": "Execute python code within the workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"}
            },
            "required": ["code"],
        },
    },
}
```

---

## Tool Implementation

### Implementation Location

Tool implementations are categorized into separate files inside `src/research_os/tools/actions/` (e.g. `search.py`, `environment.py`, `literature.py`). Each tool is a standalone function:

```python
# src/research_os/tools/actions/search.py
def search_pubmed(query: str, max_results: int = 10) -> dict:
    """Search PubMed for biomedical literature."""
    # Implementation...
    return {"status": "success", "results": results}
```

### Handler Registration

Tool handlers are registered in `server.py` inside the core request router (e.g. `_handle_tool_call` or equivalent):

```python
if name == "tool.search.pubmed":
    result = search_pubmed(
        query=arguments.get("query"),
        max_results=arguments.get("max_results", 10)
    )
    return _text(_success_envelope(result))
```

---

## Adding a New Tool

To add a new tool to Research OS:

### 1. Implement the Function

Add a function to the appropriate file in `src/research_os/tools/actions/` (or create a new one):

```python
def my_new_tool(param1: str, param2: int) -> dict:
    """Description of what this tool does."""
    # Implementation
    return {"result": "..."}
```

### 2. Export and Register

Import the tool into `server.py` and map it into the routing logic.

### 3. Add to Tool Definitions

Add the tool's JSON schema to `TOOL_DEFINITIONS` in `src/research_os/server.py`.
