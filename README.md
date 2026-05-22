# Research OS

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/research-os.svg)](https://badge.fury.io/py/research-os)
[![Tests](https://github.com/VibhavSetlur/research-os/actions/workflows/test.yml/badge.svg)](https://github.com/VibhavSetlur/research-os/actions/workflows/test.yml)
[![MCP Conformance](https://img.shields.io/badge/MCP-1.0-brightgreen)](https://modelcontextprotocol.io/)

> **Research OS — The Hands, Eyes, and Memory for AI-Driven Research.**

Research OS is an **MCP server** that transforms your AI IDE (Cursor, Windsurf, Claude Desktop) into a rigorous research assistant. It provides the **tools** (hands), **observability** (eyes), and **state management** (memory) that the IDE uses to execute reproducible academic research — from raw data ingestion to publication-ready PDF.

---

## How It Works (30 Seconds)

```
You (in IDE chat) ──→ IDE brain ──→ MCP ──→ Research OS ──→ your workspace/
                      (thinks)      (protocol)  (executes)     (files + data)

  Example:
  "Run a t-test on income vs education"
       ↓
  IDE calls:  tool.statistical.test(filepath="...", test_type="ttest", ...)
       ↓
  Research OS:  loads data → checks assumptions → runs Welch t-test
       ↓
  Returns:  { status, statistic, p_value, assumptions_passed }
       ↓
  IDE reads result, logs to methods.md, updates analysis.md
```

The IDE is the **brain** — it thinks, plans, and decides which tools to call. Research OS is the **body** — it executes, records, and remembers.

---

## Quick Demo

```bash
# 1. Install
pip install research-os[all]

# 2. Initialize a project
ros init ~/my-research/

# 3. In your IDE, paste this MCP config:
# (see QUICKSTART.md for the exact JSON)

# 4. Type in IDE chat:
# "I have a CSV at inputs/raw_data/survey.csv.
#  Do an exploratory analysis, find key patterns,
#  and write a methods section."
```

---

## Why MCP?

The Model Context Protocol (MCP) is an open standard that lets AI applications (IDEs, chat clients) discover and call tools on external servers. Research OS implements MCP because:

- **Standardization:** MCP provides a consistent interface across all IDEs (Cursor, Windsurf, Claude Desktop, VS Code)
- **Tool Discovery:** IDEs automatically discover all available tools via `list_tools` without manual configuration
- **Stateless Execution:** Each tool call is independent, making the system robust and debuggable
- **Extensibility:** New tools can be added without changing IDE integration code
- **Security:** MCP's stdio transport keeps all execution within a controlled subprocess

Research OS is not an autonomous agent—it's a tool server. The IDE is the brain; Research OS is the hands, eyes, and memory.

---

## Philosophy

Research OS is built on three core principles:

### 1. IDE-Driven, Not Autonomous
The IDE (Cursor, Windsurf, Claude Desktop) is the cognitive layer. It understands natural language, plans research steps, and decides which tools to call. Research OS never makes autonomous decisions—it only executes tools on demand.

### 2. Reproducibility by Default
Every research project follows a strict directory structure. Inputs are immutable and SHA-256 hashed. Every method is logged to `methods.md`. Every step is recorded in `analysis.md` with a Mermaid workflow diagram. Checkpoints enable rollback to any prior state.

### 3. Transparency Over Magic
No black boxes. Every tool response includes checksums for all modified files. State changes are logged with before/after diffs. The entire workflow is visible in `analysis.md`. You can always trace how you got from raw data to final paper.

---

## What This Is NOT

- **Not an autonomous agent.** Research OS does not think, plan, or make decisions. It executes tools on demand and records results.
- **Not a replacement for your IDE.** The IDE (Coder, Claude Desktop) is the driver. Research OS is the engine.
- **Not a black box.** Every action is logged to `workspace/analysis.md` and `workspace/methods.md`. Every file has a SHA-256 checksum.
- **Not a notebook.** Research OS enforces a strict, reproducible directory structure. No ad-hoc file paths.

---

## Features

- **44+ MCP Tools** across four categories: `tool.*` (hands), `view.*` (eyes), `mem.*` (memory), `sys.*` (system)
- **Numbered Experiment Folders** (`workspace/01_exploration/`, `02_causal_model/`) with structured README.md per step
- **Automatic State Machine** — every tool call updates `analysis.md` (with Mermaid workflow diagram) and `state_ledger.yaml`
- **Checkpoint & Rollback** — snapshot the workspace before destructive operations, restore any prior state
- **Branch & Merge** — fork experiments with `sys.branch.create --from 01_baseline`, merge findings
- **Statistical Testing** — t-test, ANOVA, chi-square, Mann-Whitney, Kruskal-Wallis with automatic assumption checks
- **Publication-Quality Figures** — 300 DPI PNG via matplotlib/seaborn
- **LaTeX Compilation** — `pdflatex` + `bibtex` for paper production
- **Literature Search** — PubMed, Semantic Scholar, CrossRef, Google Scholar
- **Data Transformation** — normalize (StandardScaler), impute (SimpleImputer), encode (OneHot/Label)
- **Immutable Inputs** — `inputs/` is write-protected at the tool level
- **SHA-256 Everywhere** — every file write returns a checksum for provenance

---

## Directory Structure

```
project/
├── inputs/                  # IMMUTABLE — original data
│   ├── raw_data/            # Source CSVs, JSON, etc.
│   ├── literature/          # PDFs stay un-renamed
│   ├── literature_index.yaml  # Sidecar mapping filename → citation key
│   └── intake.md            # Auto-generated: SHA-256 hashes of all inputs
│
├── workspace/               # Active research area
│   ├── 01_exploration/      # Numbered experiment folders
│   │   ├── README.md        # Goal, methods, outcomes, next-step decision
│   │   ├── conclusions.md
│   │   ├── data/
│   │   ├── scripts/
│   │   └── outputs/ (figures/, reports/, dashboards/)
│   ├── 02_causal_model/
│   ├── ...
│   ├── analysis.md          # Chronological log + Mermaid workflow diagram
│   ├── methods.md           # Append-only record of every method used
│   ├── citations.md         # Running bibliography with verified flags
│   ├── logs/                # Execution logs and state change diffs
│   ├── figures/             # 300 DPI publication-ready PNGs
│   ├── dashboards/          # Interactive Panel/HTML dashboards
│   └── workflow.mermaid     # Auto-updated workflow state diagram
│
├── synthesis/               # Final outputs (populated on demand)
│   ├── abstract.md
│   ├── paper.tex
│   ├── references.bib
│   └── supplementary/
│
├── docs/                    # Research documentation
│   ├── research_question.md
│   ├── hypotheses.md
│   └── glossary.md
│
├── environment/             # Reproducible environments
├── .os_state/               # Internal state (DO NOT TOUCH)
│   ├── state_ledger.yaml    # Source of truth: branches, checkpoints, step
│   ├── checkpoints/         # Workspace snapshots
│   └── manifest.json
└── .research/               # Cache and configuration
```

---

## MCP Integration

Research OS speaks the **Model Context Protocol (MCP)** natively. Add it to any MCP-compatible IDE:

### Cursor / Windsurf

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

### Claude Desktop

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

See `docs/IDE_INTEGRATION.md` for detailed setup instructions.

---

## Tool Categories

| Prefix | Category | Purpose | Examples |
|--------|----------|---------|----------|
| `tool.` | **Hands** | Execute actions | `tool.statistical.test`, `tool.figure.create`, `tool.pubmed.search`, `tool.latex.compile` |
| `view.` | **Eyes** | Read/observe state | `view.workspace.tree`, `view.data.head`, `view.figure.show`, `view.analyze_intent` |
| `mem.` | **Memory** | Read/write state | `mem.methods.append`, `mem.citation.add`, `mem.literature.index`, `mem.regenerate.intake` |
| `sys.` | **System** | OS control | `sys.branch.create`, `sys.checkpoint`, `sys.rollback`, `sys.synthesize` |

---

## Installation

```bash
# From source
git clone https://github.com/VibhavSetlur/research-os.git
cd research-os
pip install -e .[all]

# Verify
ros doctor
```

Full requirements in `pyproject.toml`. External dependencies (optional):
- `mmdc` for Mermaid → PNG rendering: `npm install -g @mermaid-js/mermaid-cli`
- `pdflatex` for LaTeX compilation: install TeX Live
- `ollama` for ledger compression (optional)

---

## Documentation

| Document | Description |
|----------|-------------|
| `QUICKSTART.md` | 5-minute setup guide with MCP config for every IDE |
| `docs/WORKSPACE_TAXONOMY.md` | Detailed explanation of every folder and file |
| `docs/ITERATIVE_RESEARCH_GUIDE.md` | How to branch, checkpoint, rollback, and track state |
| `docs/IDE_INTEGRATION.md` | Step-by-step for Cursor, Windsurf, VS Code, Claude Desktop |
| `docs/EXAMPLE_WALKTHROUGH.md` | Full mock session from CSV to paper.pdf |
| `docs/ARCHITECTURE.md` | MCP-centric architecture overview |
| `docs/MCP_INTEGRATION.md` | Transport, tool discovery, debugging |
| `docs/AI_NATIVE_WORKFLOWS.md` | The IDE-driven research loop |
| `docs/AUTHORING.md` | How tools are authored |

---

## Contributing

We welcome contributions! See `CONTRIBUTING.md` for guidelines on:

- Architecture overview for new developers
- Adding new MCP tools
- Writing tests
- Documentation standards
- Code of conduct

---

## License

MIT
