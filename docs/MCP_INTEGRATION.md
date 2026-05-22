# MCP Integration

Research OS implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) — an open standard for connecting AI applications with external tools.

---

## Transport

### stdio (Default)

The server communicates over stdin/stdout using JSON-RPC. This is the recommended transport for all IDEs.

```bash
ros start --transport stdio
```

The server reads JSON-RPC requests from stdin and writes responses to stdout. Logs and errors go to stderr (visible in the IDE's MCP output panel).

#### JSON-RPC Message Flow

```
→ {"jsonrpc":"2.0","id":1,"method":"list_tools"}
← {"jsonrpc":"2.0","id":1,"result":{"tools":[...]}}

→ {"jsonrpc":"2.0","id":2,"method":"call_tool","params":{"name":"sys.state","arguments":{}}}
← {"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"{...}"}]}}
```

### SSE (Experimental)

For remote connections, use Server-Sent Events:

```bash
ros start --transport sse --port 8080
```

Connect to `http://localhost:8080` from your IDE or custom client.

---

## Tool Discovery

### `list_tools`

Returns all available tools with their input schemas. The IDE calls this on startup to populate its tool palette.

**Request:**
```json
{"jsonrpc":"2.0","id":1,"method":"list_tools"}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "tool.statistical.test",
        "description": "Run a statistical test (ttest, anova, chi_square, ...) with automatic assumption checks",
        "inputSchema": {
          "type": "object",
          "properties": {
            "filepath": {"type": "string"},
            "test_type": {"type": "string", "enum": ["ttest", "anova", "chi_square", "mann_whitney", "kruskal"]},
            "x_column": {"type": "string"}
          },
          "required": ["filepath", "test_type", "x_column"]
        }
      }
    ]
  }
}
```

### `call_tool`

Execute a specific tool.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "call_tool",
  "params": {
    "name": "view.workspace.tree",
    "arguments": {"max_depth": 3}
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"status\":\"success\",\"data\":{\"tree\":\"workspace/...\",\"total_files\":42,\"total_dirs\":8}, ...}"
    }]
  }
}
```

---

## Standardized Response Envelope

Every tool response follows this format:

```json
{
  "status": "success" | "error",
  "data": { ... },
  "paths": {
    "created": ["/abs/path/to/new/file.csv"],
    "modified": ["/abs/path/to/analysis.md"]
  },
  "checksums": {
    "/abs/path/to/file.csv": "sha256:abc123..."
  },
  "next_suggested_tools": ["tool.statistical.test", "view.figure.show"],
  "warnings": ["mmdc not installed — Mermaid diagrams will not render as PNG"]
}
```

### Fields

| Field | Always Present | Description |
|-------|---------------|-------------|
| `status` | Yes | `"success"` or `"error"` |
| `data` | Yes | Tool-specific result |
| `paths.created` | No | Absolute paths of new files |
| `paths.modified` | No | Absolute paths of modified files |
| `checksums` | No | SHA-256 checksums for every path |
| `next_suggested_tools` | No | Tools the IDE should consider calling next |
| `warnings` | No | Non-blocking warnings (e.g., missing external deps) |

---

## Debugging

### Check if the server is running

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"list_tools"}' | ros start --transport stdio
```

### Verbose logging

```bash
ros start --transport stdio --log-level DEBUG
```

### Common debug commands

```bash
# List all tools
echo '{"jsonrpc":"2.0","id":1,"method":"list_tools"}' | ros start --transport stdio 2>/dev/null | python3 -m json.tool

# Check state
echo '{"jsonrpc":"2.0","id":2,"method":"call_tool","params":{"name":"sys.state","arguments":{}}}' | ros start --transport stdio 2>/dev/null | python3 -m json.tool

# Health check
echo '{"jsonrpc":"2.0","id":3,"method":"call_tool","params":{"name":"sys.heartbeat","arguments":{}}}' | ros start --transport stdio 2>/dev/null
```

---

## Tool Categories

| Prefix | Category | Count | Purpose |
|--------|----------|-------|---------|
| `tool.` | Hands | 8 | Statistical tests, figures, data transforms, literature search, LaTeX, dashboards |
| `view.` | Eyes | 3 | Directory tree, data head, figure preview, intent analysis |
| `mem.` | Memory | 5 | Methods log, citations, intake, literature index, checkpoint |
| `sys.` | System | 12 | State, heartbeat, scaffold, rollback, analysis log, synthesize, branches, checkpoints |
| *(Legacy)* | — | ~16 | Backward-compatible aliases and existing tools |

Total: 44+ tools available at runtime.

---

## Security

- The `inputs/` directory is **write-protected** — any tool attempting to write there receives a `WriteProtectedError`
- All file operations use absolute paths derived from the project root
- The server does not expose shell execution, network access, or arbitrary code execution tools
- The entire workspace is constrained to a single project directory
