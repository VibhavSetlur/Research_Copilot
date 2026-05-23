# Installation & Setup Guide

Step-by-step installation instructions for macOS, Linux, and Windows WSL, with exact MCP configuration JSON for all supported IDEs.

---

## Prerequisites

- **Python 3.10 or higher**
- **pip** (or `uv` for faster installs)
- **Git** (for installing from source)

---

## Installation

### macOS

```bash
# 1. Install Python 3.10+ (if not already installed)
brew install python@3.11

# 2. Clone the repository
git clone https://github.com/VibhavSetlur/research-os.git
cd research-os

# 3. Install with all dependencies
pip install -e .[all]

# 4. Verify installation
ros doctor
```

### Linux (Ubuntu/Debian)

```bash
# 1. Install Python 3.10+ (if not already installed)
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# 2. Clone the repository
git clone https://github.com/VibhavSetlur/research-os.git
cd research-os

# 3. Install with all dependencies
pip install -e .[all]

# 4. Verify installation
ros doctor
```

### Windows WSL

```bash
# 1. Install WSL2 (if not already installed)
wsl --install

# 2. Inside WSL, install Python 3.10+
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# 3. Clone the repository
git clone https://github.com/VibhavSetlur/research-os.git
cd research-os

# 4. Install with all dependencies
pip install -e .[all]

# 5. Verify installation
ros doctor
```

---

## Optional External Dependencies

These are optional but recommended for full functionality:

### Mermaid CLI (for workflow diagrams)

```bash
# macOS/Linux
npm install -g @mermaid-js/mermaid-cli

# If Puppeteer fails, install Playwright browsers:
npx playwright install chromium
```

### LaTeX (for paper compilation)

```bash
# macOS
brew install mactex

# Linux (Ubuntu/Debian)
sudo apt install texlive-latex-extra

# Windows WSL
sudo apt install texlive-latex-extra
```

### Ollama (optional, for ledger compression)

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

---

## MCP Configuration by IDE

### Cursor

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

**JSON Configuration:**
```json
{
  "name": "research-os",
  "type": "command",
  "command": "ros",
  "args": ["start", "--transport", "stdio"],
  "cwd": "/absolute/path/to/your/research-project"
}
```


### Claude Desktop

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

### VS Code (with GitHub OS MCP Preview)

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

---

## Verification

After installation and MCP configuration, verify everything works:

```bash
# Check Research OS installation
ros doctor

# Test MCP server manually
echo '{"jsonrpc":"2.0","id":1,"method":"list_tools"}' | ros start --transport stdio
```

In your IDE, you should see:
- A green "Connected" indicator in the MCP panel
- 44+ available tools listed
- Ability to call tools like `view.workspace.tree` or `sys.state`

---

## Troubleshooting

### `ros: command not found`

Ensure the installation directory is on your PATH:
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH=$PATH:~/.local/bin
```

### MCP tools not appearing in IDE

- Restart the IDE
- Verify `ros start --transport stdio` works in a terminal
- Check the IDE's MCP output panel for error messages

### `pdflatex not found`

Install TeX Live:
- **macOS:** `brew install mactex`
- **Linux:** `sudo apt install texlive-latex-extra`

### Mermaid diagrams not rendering as PNG

Install Mermaid CLI:
```bash
npm install -g @mermaid-js/mermaid-cli
```

If Puppeteer fails, install Playwright browsers:
```bash
npx playwright install chromium
```

### Permission errors on `inputs/`

The `inputs/` directory is write-protected by design. Use `workspace/` for all data processing.

---

## Next Steps

After installation:

1. Initialize a research project: `ros init ~/my-research-project/`
2. Add your data to `inputs/raw_data/`
3. Start researching in your IDE using MCP tools
4. Read `docs/ITERATIVE_RESEARCH_GUIDE.md` to learn about branching and state management
