# IDE Integration Guide

Connect Research OS to your preferred IDE via the Model Context Protocol (MCP).

---

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io) is an open standard that lets AI applications (IDEs, chat clients) discover and call tools on external servers. Research OS implements the **stdio transport** — it runs as a subprocess that communicates with the IDE over stdin/stdout using JSON-RPC.

```
IDE ──stdin/stdout──→ Research OS (ros start --transport stdio)
```

---

## Quick Setup

All IDEs require the same basic command:

```bash
ros start --transport stdio
```

Optionally specify a non-default workspace:

```bash
ros start --transport stdio --workspace /path/to/project
```

---

## Cursor

### Setup

1. Open Cursor → Settings → MCP Servers
2. Click **"Add new MCP server"**
3. Fill in:

| Field | Value |
|-------|-------|
| Name | `research-os` |
| Type | `command` |
| Command | `ros` |
| Args | `start`, `--transport`, `stdio` |
| Working Directory | Path to your research project |

### Verify

- The MCP panel should show a green "Connected" indicator
- You should see 44+ available tools listed

### Usage

Type in Cursor's chat/agent panel:

> "Use `view.workspace.tree` to show me the project structure"

Cursor will call the tool and display results inline.

---

## VS Code (with GitHub OS MCP Preview)

### Setup

1. Create `.vscode/mcp.json` in the root of your project:

```json
{
  "servers": {
    "research-os": {
      "command": "ros",
      "args": ["start", "--transport", "stdio"],
      "env": {}
    }
  }
}
```

2. Restart VS Code
3. Open the MCP tool panel (View → Open View → MCP Tools)

### Alternative: VS Code CLI

Use the VS Code command palette:
```
> MCP: Add Server
```

Enter:
```
ros start --transport stdio
```

---

## Claude Desktop

### Setup

1. Open Claude → Settings → Developer → Edit Config
2. Open (or create) `claude_desktop_config.json`
3. Add:

```json
{
  "mcpServers": {
    "research-os": {
      "command": "ros",
      "args": [
        "start",
        "--transport",
        "stdio",
        "--workspace",
        "/absolute/path/to/your/research-project"
      ],
      "env": {}
    }
  }
}
```

4. Save and restart Claude Desktop

### Verify

- Look for the hammer icon (tools) in the chat input area
- Click it to see available tools

---

## Manual Testing

To verify the server works outside any IDE:

```bash
# Start the server
ros start --transport stdio

# In another terminal, send a JSON-RPC request:
echo '{"jsonrpc":"2.0","id":1,"method":"list_tools"}' | ros start --transport stdio
```

---

## Transport Options

### stdio (default)

Recommended for all IDEs. The server reads JSON-RPC requests from stdin and writes responses to stdout. Error logs go to stderr.

```bash
ros start --transport stdio
```

### SSE (Server-Sent Events) (experimental)

For remote connections:

```bash
ros start --transport sse --port 8080
```

Then configure the IDE to connect to `http://localhost:8080`.

---

## Debugging MCP Connections

### Check if the server starts

```bash
ros doctor
```

### View server logs

Run the server manually to see stderr logs:

```bash
ros start --transport stdio 2>&1 | tee /tmp/ros.log
```

### Test a specific tool

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"list_tools"}' | \
  ros start --transport stdio 2>/dev/null
```

### Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ros: command not found` | Not on PATH | `export PATH=$PATH:~/.local/bin` |
| "Connection refused" | Wrong transport | Use `--transport stdio` for IDEs |
| Tools not showing up | IDE needs restart | Quit and reopen the IDE |
| "Unknown tool" errors | Wrong tool name | Check case: `tool.statistical.test` not `tool.StatisticalTest` |
| Permission errors on inputs/ | Write to protected dir | Use `workspace/` instead | 
