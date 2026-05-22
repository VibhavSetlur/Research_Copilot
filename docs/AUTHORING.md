# Tool Authoring

In Research OS, tools are **authored by the IDE** (via the MCP protocol), not by the OS itself. The OS provides a fixed set of 44+ tools that the IDE can call. The IDE is responsible for planning which tools to call and in what sequence.

---

## Tool Architecture

### Fixed Tool Set

Research OS provides a fixed set of tools defined in `src/research_os/server.py` in the `TOOL_DEFINITIONS` dictionary. These tools are:

- **System tools (`sys.*`):** State management, branching, checkpoints, synthesis
- **Memory tools (`mem.*`):** Methods logging, citations, literature indexing
- **View tools (`view.*`):** Workspace inspection, data preview, figure display
- **Tool tools (`tool.*`):** Statistical tests, figures, data transformation, literature search, LaTeX compilation

### Tool Registration

Tools are registered in the MCP server via the `TOOL_DEFINITIONS` dictionary. Each tool has:

- **name:** The tool identifier (e.g., `tool.statistical.test`)
- **description:** Human-readable description of what the tool does
- **inputSchema:** JSON Schema defining required and optional parameters

Example from `server.py`:
```python
TOOL_DEFINITIONS: dict[str, dict[str, Any]] = {
    "tool.statistical.test": {
        "description": "Run a statistical test (ttest, anova, chi_square, mann_whitney, kruskal) with automatic assumption checks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Absolute path to data file"},
                "test_type": {"type": "string", "enum": ["ttest", "anova", "chi_square", "mann_whitney", "kruskal"]},
                "x_column": {"type": "string", "description": "Primary column"},
                "group_column": {"type": "string", "description": "Grouping column"},
            },
            "required": ["filepath", "test_type", "x_column"],
        },
    },
}
```

---

## Tool Implementation

### Implementation Location

Tool implementations are in `src/research_os/tools/tool_impls.py`. Each tool is a standalone function:

```python
def statistical_test(
    filepath: str,
    test_type: str,
    x_column: str,
    y_column: str | None = None,
    group_column: str | None = None,
) -> dict:
    """Run a statistical test with automatic assumption checks."""
    # Implementation...
    return result
```

### Handler Registration

Tool handlers are registered in `server.py` in the `_handle_tool_call` function:

```python
if name == "tool.statistical.test":
    result = statistical_test(
        filepath=arguments.get("filepath"),
        test_type=arguments.get("test_type"),
        x_column=arguments.get("x_column"),
        # ...
    )
    return _text(_success_envelope(result))
```

---

## Adding a New Tool

To add a new tool to Research OS:

### 1. Implement the Function

Add a function to `src/research_os/tools/tool_impls.py`:

```python
def my_new_tool(param1: str, param2: int) -> dict:
    """Description of what this tool does."""
    # Implementation
    return {"result": "..."}
```

### 2. Add to Tool Definitions

Add the tool to `TOOL_DEFINITIONS` in `src/research_os/server.py`:

```python
"tool.my.new.tool": {
    "description": "Description of what this tool does",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First parameter"},
            "param2": {"type": "number", "description": "Second parameter"},
        },
        "required": ["param1"],
    },
},
```

### 3. Register Handler

Add the handler in `_handle_tool_call` in `server.py`:

```python
if name == "tool.my.new.tool":
    result = my_new_tool(
        param1=arguments.get("param1"),
        param2=arguments.get("param2"),
    )
    return _text(_success_envelope(result))
```

### 4. Update Documentation

Add the tool to `docs/MCP_TOOLS_REFERENCE.md` with:
- Description
- Input schema
- Output example
- Usage notes

---

## Tool Categories

### System Tools (`sys.*`)

These tools control the OS itself:
- `sys.state` - Return workspace snapshot
- `sys.heartbeat` - Health check
- `sys.checkpoint` - Create workspace snapshot
- `sys.rollback` - Restore from checkpoint
- `sys.branch.create` - Create experiment branch
- `sys.branch.merge` - Merge branch findings
- `sys.branch.abandon` - Mark branch as dead-end
- `sys.analysis.log` - Log to analysis.md
- `sys.synthesize` - Compile paper outputs
- `sys.workspace.scaffold` - Create workspace structure

### Memory Tools (`mem.*`)

These tools read/write persistent state:
- `mem.methods.append` - Log method to methods.md
- `mem.citation.add` - Add citation to citations.md
- `mem.regenerate.intake` - Re-scan inputs/
- `mem.citations.generate` - Generate citations.md
- `mem.literature.index` - Index literature PDFs

### View Tools (`view.*`)

These tools read/observe state:
- `view.analyze_intent` - Analyze user query
- `view.workspace.tree` - Return directory tree
- `view.data.head` - Preview data file
- `view.figure.show` - Return figure as base64

### Tool Tools (`tool.*`)

These tools execute actions on data:
- `tool.latex.compile` - Compile LaTeX to PDF
- `tool.pubmed.search` - Search PubMed
- `tool.semantic_scholar.search` - Search Semantic Scholar
- `tool.google.scholar.search` - Search Google Scholar
- `tool.data.transform` - Apply data transformations
- `tool.statistical.test` - Run statistical tests
- `tool.figure.create` - Create figures
- `tool.dashboard.create` - Generate dashboards

---

## Tool Naming Conventions

- **System tools:** `sys.*` (e.g., `sys.state`, `sys.branch.create`)
- **Memory tools:** `mem.*` (e.g., `mem.methods.append`, `mem.citation.add`)
- **View tools:** `view.*` (e.g., `view.data.head`, `view.workspace.tree`)
- **Tool tools:** `tool.*` (e.g., `tool.statistical.test`, `tool.figure.create`)

Use lowercase with dots for hierarchy. Use descriptive names that indicate the tool's purpose.

---

## Response Envelope

All tools return a standardized response envelope:

```python
def _envelope(
    data: Any = None,
    *,
    status: str = "success",
    paths_created: list[str] | None = None,
    paths_modified: list[str] | None = None,
    next_suggested_tools: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict:
    """Build the standardized response envelope."""
    checksums: dict[str, str] = {}
    for path_list in ([], paths_created or [], paths_modified or []):
        for p in path_list:
            fp = Path(p)
            if fp.exists():
                checksums[p] = f"sha256:{compute_file_hash(fp)}"
    return {
        "status": status,
        "data": data or {},
        "paths": {
            "created": paths_created or [],
            "modified": paths_modified or [],
        },
        "checksums": checksums,
        "next_suggested_tools": next_suggested_tools or [],
        "warnings": warnings or [],
    }
```

This ensures:
- **Consistency:** All tools return the same structure
- **Provenance:** File checksums track changes
- **Guidance:** `next_suggested_tools` helps IDE plan next steps
- **Transparency:** `warnings` inform about non-critical issues

---

## Error Handling

Tools should return errors via the envelope:

```python
if not data_path.exists():
    return _error_envelope(f"File not found: {filepath}")
```

The IDE will receive:
```json
{
  "status": "error",
  "data": {"error": "File not found: survey.csv"}
}
```

The IDE should then adjust its approach and retry.

---

## Testing Tools

Each tool should have unit tests in `tests/`. Test:
- Input validation
- Output schema compliance
- Error cases
- Edge cases

Example:
```python
def test_statistical_test_ttest():
    result = statistical_test(
        filepath="tests/fixtures/test_data.csv",
        test_type="ttest",
        x_column="income",
        group_column="education"
    )
    assert result["status"] == "success"
    assert "results" in result
    assert result["results"]["significant"] == True
```

---

## IDE Integration

The IDE discovers tools via the MCP `list_tools` method. The IDE then:
1. Calls `view.analyze_intent` to understand user intent
2. Receives suggested tools
3. Calls tools in sequence
4. Interprets results
5. Logs methods via `mem.methods.append`
6. Updates analysis log via `sys.analysis.log`

The IDE is responsible for:
- Planning tool sequences
- Interpreting tool results
- Handling errors
- Logging methods
- Managing research workflow

Research OS is responsible for:
- Executing tools
- Managing state
- Enforcing immutability
- Providing provenance (checksums)
- Logging state changes
