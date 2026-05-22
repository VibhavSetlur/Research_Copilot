# Connecting Agentic Research OS via MCP

Since Agentic Research OS acts as a Model Context Protocol (MCP) server, you can connect it directly to advanced AI IDEs like **Claude Desktop**, **Cursor**, or **Windsurf**. This allows the AI in your editor to securely call research tools, execute data pipelines, and read your lab notebook directly.

## 1. Claude Desktop

To connect the Research OS to Claude Desktop, you need to edit your Claude Desktop configuration file.

**Config Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following JSON configuration:

```json
{
  "mcpServers": {
    "research-os": {
      "command": "research-os",
      "args": [
        "research-copilot-mcp"
      ],
      "env": {
        "OPENAI_API_KEY": "your-key",
        "ANTHROPIC_API_KEY": "your-key",
        "SEMANTIC_SCHOLAR_API_KEY": "your-key"
      }
    }
  }
}
```

*Note: If `research-os` is not in your global PATH, provide the absolute path to your Python virtual environment's executable.*

## 2. Cursor

Cursor has built-in support for MCP servers.

1. Open Cursor Settings (`Cmd/Ctrl + ,`)
2. Navigate to **Features > MCP**
3. Click **+ Add new MCP server**
4. Configure as follows:
   - **Name:** `Agentic Research OS`
   - **Type:** `command`
   - **Command:** `research-copilot-mcp` (or the absolute path to your `bin/research-copilot-mcp`)

## 3. Windsurf

Windsurf (Codeium) supports MCP natively. 

1. Open the command palette (`Cmd/Ctrl + Shift + P`)
2. Type `Windsurf: Manage MCP Servers`
3. Add the server using the identical command as Cursor (`research-copilot-mcp`).
