# Research OS

**From data to publication-ready manuscript – your MCP-native research operating system.**

Research OS is a Model Context Protocol (MCP) server designed to manage and guide LLM agents (like Cursor, Claude Code, Antigravity, or custom scripts) through rigorous, reproducible academic research workflows.

## Quick Start

1. **Install the OS**
   ```bash
   pip install "research-os[all] @ git+https://github.com/VibhavSetlur/Research-OS.git"
   ```

2. **Initialize your Project**
   ```bash
   # Creates the folder and scaffolds the workspace
   research-os init --name "my_research_project_folder"
   cd my_research_project_folder
   ```

3. **Start the MCP Server**
   ```bash
   research-os start --workspace .
   ```
   *(Configure this command in your MCP client like Cursor or Claude Code)*

4. **Add Data and Analyze**
   Then drop your data files into `inputs/raw_data/` and ask:
   > "Analyze my data."

## Architecture

```text
+-------------------+       +-------------------+       +-------------------+       +-------------------+
|                   |       |                   |       |                   |       |                   |
|     AI IDE        | <---> |   MCP Protocol    | <---> |    Research OS    | <---> |     Workspace     |
| (Cursor / Claude / Antigravity) |       |                   |       |                   |       |                   |
+-------------------+       +-------------------+       +-------------------+       +-------------------+
```

## What This Is NOT

- **NOT an autonomous agent**: It does not think, plan, or make decisions on its own.
- **NOT an LLM**: It relies entirely on your AI IDE (e.g., Cursor, Claude) to provide the intelligence.
- **NOT a black box**: Every decision and change is logged for full transparency.

## Workspace File Tree
```text
<user-project>/
├── AGENTS.md                       # AI agent operating protocol (8 sections)
├── README.md                       # Auto-generated project overview
├── .os_state/                      # INTERNAL — OS state
│   ├── state_ledger.json           # Source of truth (YAML + JSON)
│   ├── manifest.json               # Auto-synced workspace file inventory
│   ├── os_state.md                 # Human-readable status snapshot
│   ├── protocol_execution_log.jsonl # Protocol execution history
│   ├── checkpoints/                # Workspace snapshots
│   └── cache/                      # API response cache
├── docs/                           # Human-written research docs
│   ├── research_question.md        # Main question + sub-questions
│   └── glossary.md                 # Term definitions
├── inputs/                         # IMMUTABLE — researcher provided
│   ├── researcher_config.yaml      # Researcher preferences, autonomy, API keys
│   ├── raw_data/                   # Source data (or symlinks)
│   ├── literature/                 # PDFs
│   ├── context/                    # Notes, past results, text files
│   ├── intake.md                   # Auto-generated research brief (SHA-256 table)
│   └── literature_index.yaml       # Filename → citation key mapping
├── workspace/                      # ACTIVE — iterative experiments
│   ├── methods.md                  # Append-only method log (structured entries)
│   ├── analysis.md                 # Chronological log + Mermaid workflow
│   ├── citations.md                # Running bibliography with verified flags
│   ├── workflow.mermaid            # Auto-updated workflow diagram (colored nodes)
│   ├── workflow.png                # Rendered diagram (via mmdc)
│   ├── logs/                       # Execution logs
│   │   ├── searches.log            # Every web search logged (JSON lines)
│   │   ├── state_changes.log       # Before/after state diffs
│   │   ├── notifications.log       # Researcher notifications
│   │   ├── data_inventory.json     # Auto-profiled data inventory
│   │   └── 01_baseline.log         # Per-step execution logs
│   ├── 01_experiment_baseline/
│   │   ├── README.md               # Goal, hypotheses, outcomes
│   │   ├── conclusions.md          # Key findings, bugs, routing decisions
│   │   ├── data/                   # Derived data
│   │   ├── scripts/                # Versioned (01_load_v1.py, 02_eda_v1.py)
│   │   ├── outputs/
│   │   │   ├── reports/
│   │   │   ├── figures/
│   │   │   ├── tables/
│   │   │   └── dashboards/
│   │   └── environment/            # Pinned dependencies
│   ├── 02_data_preparation/
│   │   └── ... (same structure)
│   └── .os_state/                  # Symlink to root .os_state/
├── synthesis/                      # FINAL — populated on completion
│   ├── abstract.md
│   ├── paper.tex / paper.pdf
│   ├── references.bib
│   ├── workflow_diagram.png
│   └── supplementary/
└── environment/                    # Global environment
    ├── requirements.txt
    └── Dockerfile
```

## Value Proposition

Why use Research OS?
- **Immutability First:** Your raw data (`inputs/raw_data/`) is strictly write-protected. All transformations are safely saved as derived data.
- **Methodological Provenance:** Every critical decision, applied method, and statistical result is atomically logged via strict append-only decision logging.
- **Pipeline Guidance:** 65 YAML protocols (33 full + 32 light) guide the AI through each research phase. `sys.protocol.next` recommends the next step based on what's been completed.
- **Turn Structure:** Protocols enforce `steps_per_turn` and `approval_required_before` gates per autonomy level (manual/supervised/autopilot), preventing information overload.
- **Chronological Experiment Paths:** Experiments run as numbered consecutive steps (`01_experiment_baseline/`, `02_data_preparation/`). Abandoned paths are renamed (e.g., `__DEAD_END__`) rather than deleted, preserving full history.
- **Model-Size Adaptability:** Supports `small`, `medium`, and `large` LLM profiles to optimize token economy and context window limits. Protocols auto-select light/full variants.
- **73 MCP Tools:** From `sys.state.health` (full pipeline state with workspace tree) to `tool.synthesize.plan` (section-by-section synthesis) to `sys.protocol.log` (execution history).
- **CLI Utilities:** `research-os status` (pipeline progress bar, key file health), `research-os pull <ide>` (add IDE config), `research-os doctor` (MCP server smoke test).

## Documentation
- **[GUIDE.md](docs/GUIDE.md)** — Installation, workspace layout, all 73 tools, 10-stage pipeline, AI session start procedure, workflow walkthrough, troubleshooting.
- **Project**: [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md) | [Code of Conduct](CODE_OF_CONDUCT.md)

## File Index

To help you navigate this repository:
- `src/research_os/server.py` - Core MCP server, 73 tool definitions, and handlers.
- `src/research_os/protocols/` - 65 YAML-based methodology protocols (33 full + 32 light).
- `src/research_os/tools/actions/` - Implementation of all OS actions (search, path, literature, config, synthesize, protocol).
- `src/research_os/state/` - State ledger and checkpoint logic.
- `src/research_os/project_ops.py` - Workspace scaffold, manifest sync, os_state.md, workflow mermaid, checkpointing.
- `src/research_os/cli.py` - CLI commands: `init`, `status`, `doctor`, `pull`, `start`.
- `scratch/smoke_test.py` - Checks all 73 tools, 65 protocols, CLI, pipeline.
- `scratch/researcher_session.py` - End-to-end simulation of a real research session.
- `scratch/RESEARCHER_WORKFLOW.md` - Documented researcher workflow example.
- `templates/` - Default rules and guides to feed to agents.

[![PyPI version](https://badge.fury.io/py/research-os.svg)](https://badge.fury.io/py/research-os)
[![Python versions](https://img.shields.io/pypi/pyversions/research-os.svg)](https://pypi.org/project/research-os/)
[![Tests](https://github.com/VibhavSetlur/Research-OS/actions/workflows/tests.yml/badge.svg)](https://github.com/VibhavSetlur/Research-OS/actions)
