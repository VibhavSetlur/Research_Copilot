# Quickstart — 5 Minutes to Your First Research Session

## Prerequisites

- Python 3.10+
- pip (or uv for faster installs)
- An MCP-compatible IDE: [Cursor](https://cursor.com), [Windsurf](https://codeium.com/windsurf), [VS Code](https://code.visualstudio.com) (with OS), or [Claude Desktop](https://claude.ai/download)

---

## Step 1: Install Research OS

```bash
# macOS / Linux / WSL
pip install research-os[all]

# Or from source:
git clone https://github.com/VibhavSetlur/research-os.git
cd research-os
pip install -e .[all]
```

Verify it works:

```bash
ros doctor
# → Research OS v10.0.0 — All checks passed
```

---

## Step 2: Initialize a Research Project

```bash
ros init ~/my-research-project/
```

This creates:
```
my-research-project/
├── inputs/          # Put your CSV/data files here
├── workspace/       # Active experimentation area
├── synthesis/       # Paper output (populated on demand)
├── docs/            # Research documentation
├── environment/     # Reproducible environments
└── .os_state/       # Internal state ledger
```

---

## Step 3: Add Your Data

Copy your research data into `inputs/raw_data/`:

```bash
cp ~/Downloads/survey_data.csv ~/my-research-project/inputs/raw_data/
```

Research OS will auto-compute SHA-256 hashes and generate `inputs/intake.md`.

---

## Step 4: Connect Your IDE

### Option A: Cursor

1. Open Cursor → Settings → MCP Servers
2. Add a new server:

```json
{
  "name": "research-os",
  "type": "command",
  "command": "ros",
  "args": ["start", "--transport", "stdio"],
  "cwd": "/home/you/my-research-project"
}
```

3. Click "Save" — the tools will appear in Cursor's MCP panel.

### Option B: Windsurf

1. Open Windsurf → Settings → MCP Servers
2. Add:

```json
{
  "mcpServers": {
    "research-os": {
      "command": "ros",
      "args": ["start", "--transport", "stdio"],
      "env": {}
    }
  }
}
```

### Option C: Claude Desktop

1. Open Claude → Settings → Developer → Edit Config
2. Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "research-os": {
      "command": "ros",
      "args": ["start", "--transport", "stdio", "--workspace", "/home/you/my-research-project"],
      "env": {}
    }
  }
}
```

### Option D: VS Code (with OS MCP Preview)

1. Create `.vscode/mcp.json` in your project:

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

2. Restart VS Code — the tools appear in the MCP tool list.

---

## Step 5: Run Your First Research Session

Type this in your IDE's chat/agent panel:

> "I have a CSV at `inputs/raw_data/survey.csv`. Do an exploratory analysis, find key patterns, and write a methods section."

The IDE will:
1. Call `view.data.head(filepath="inputs/raw_data/survey.csv")` to inspect the data
2. Call `tool.figure.create(filepath="...", chart_type="hist")` to visualize distributions
3. Call `tool.statistical.test(filepath="...", test_type="ttest", ...)` to test hypotheses
4. Call `mem.methods.append(method="Exploratory data analysis", ...)` to log the method
5. Call `sys.analysis.log(entry="01_exploration complete", status="complete")` to update the workflow

Review results in `workspace/01_exploration/`.

---

## Step 6: Iterate

Ask follow-up questions:

> "That's good. Now test whether education level predicts income."

The IDE will:
1. Call `sys.branch.create(name="education_income", from_step="01_exploration")`
2. Run the analysis in the new branch
3. Present results

---

## Step 7: Compile the Paper

When you're done:

> "I'm done. Compile the paper."

The IDE calls `sys.synthesize` → `synthesis/paper.pdf` appears.

---

## Next Steps

- Read `docs/WORKSPACE_TAXONOMY.md` to understand every folder
- Read `docs/ITERATIVE_RESEARCH_GUIDE.md` to master branching and state
- Run `ros doctor` anytime to check for missing dependencies

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ros: command not found` | Ensure `pip install -e .` ran; check `~/.local/bin` is on `PATH` |
| MCP tools not appearing in IDE | Restart IDE; verify `ros start --transport stdio` works in terminal |
| `pdflatex not found` | Install TeX Live: `apt install texlive-latex-extra` (Linux) or MacTeX (macOS) |
| Mermaid diagrams not rendering as PNG | `npm install -g @mermaid-js/mermaid-cli` |
