# MCP Integration

Connect AI IDEs to Research Copilot via the Model Context Protocol for native tool access.

## Overview

The MCP server exposes 28+ Research Copilot commands as native tools. This eliminates subprocess overhead and enables direct function invocation from AI IDEs.

## Start the Server

```bash
rcp mcp
```

The server runs on stdin/stdout by default (stdio transport).

## Configure Your IDE

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "research-copilot": {
      "command": "python",
      "args": ["/absolute/path/to/.research/mcp_server.py"]
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "research-copilot": {
      "command": "python",
      "args": ["/absolute/path/to/.research/mcp_server.py"]
    }
  }
}
```

### opencode

Add to `opencode.json`:

```json
{
  "mcp": {
    "research-copilot": {
      "command": "python",
      "args": [".research/mcp_server.py"]
    }
  }
}
```

## Available Tools

All 28+ CLI commands are available as MCP tools:

### Project Management
- `init`, `status`, `scan`, `map`, `preflight`

### Intake
- `intake`, `intake_interview`, `followups`

### Agents & Skills
- `agents`, `agent`, `skills`, `skill`

### Workflow
- `workflow`, `iterations`, `intent`

### Approval
- `approve`, `reject`

### Analysis
- `preregistration`, `reviewer2`, `parallel`, `debug`

### Branching
- `branch`, `branches`, `switch`, `merge`, `abandon`

### Cache & DAG
- `cache_stats`, `cache_clear`, `dag`, `dag_viewer`

### Data & Knowledge
- `data_scale`, `graph`, `graph_stats`, `graph_query`, `taxonomy`

### Export
- `export`

### Dependencies
- `dependency_check`

### Session
- `restore`, `snapshot`, `budget`

## Usage Example

After connecting, tell your AI:

> "Run preflight checks, scan inputs, and execute the research_init agent."

The AI will call MCP tools directly — no parsing stdout, no guessing commands.

## Troubleshooting

### Server won't start

```bash
# Check Python version (requires 3.10+)
python --version

# Check MCP dependencies
pip install mcp starlette uvicorn
```

### IDE can't connect

- Use absolute paths in IDE configuration
- Ensure the `.research/mcp_server.py` file exists
- Check that no other process is using the MCP transport

### Tools not appearing

- Restart the MCP server after adding new commands
- Check server logs for import errors
- Verify `.research/config.yaml` is valid YAML
