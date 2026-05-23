# Research OS

**From data to publication-ready manuscript – your MCP-native research operating system.**

Research OS is a Model Context Protocol (MCP) server designed to manage and guide LLM agents (like Cursor, Windsurf, or custom scripts) through rigorous, reproducible academic research workflows.

## Quick Start

1. **Install the OS**
   ```bash
   pip install research-os
   
   # Or install with all optional tools (like MCP and Dev):
   pip install research-os[all]
   ```

2. **Start the MCP Server**
   ```bash
   python -m research_os.server
   ```
   *(Configure this command in your MCP client like Cursor or Windsurf).*

3. **Initialize your Project**
   In your AI IDE, prompt the agent:
   > "Please scaffold my new project using `sys.workspace.scaffold` with the name 'My First Study'."

## Architecture

```text
+-------------------+       +-------------------+       +-------------------+       +-------------------+
|                   |       |                   |       |                   |       |                   |
|     AI IDE        | <---> |   MCP Protocol    | <---> |    Research OS    | <---> |     Workspace     |
| (Cursor/Windsurf) |       |                   |       |                   |       |                   |
+-------------------+       +-------------------+       +-------------------+       +-------------------+
```

## What This Is NOT

- **NOT an autonomous agent**: It does not think, plan, or make decisions on its own.
- **NOT an LLM**: It relies entirely on your AI IDE (e.g., Cursor, Claude) to provide the intelligence.
- **NOT a black box**: Every decision and change is logged for full transparency.

## Workspace File Tree
```text
workspace/
├── .os_state/
│   └── state_ledger.json
├── inputs/
│   ├── literature/
│   └── raw_data/
├── methodology/
│   └── protocols/
├── src/
├── synthesis/
└── workspace_logs/
    └── analysis.md
```

## Value Proposition

Why use Research OS?
- **Immutability First:** Your raw data (`inputs/raw_data/`) is strictly write-protected. All transformations are safely saved as derived data.
- **Methodological Provenance:** Every critical decision, applied method, and statistical result is atomically logged via strict append-only decision logging.
- **Isolated Experimentation:** Try risky analyses safely by spinning up a branch (`sys.branch.create`), without polluting your main findings.
- **Model-Size Adaptability:** Supports `small`, `medium`, and `large` LLM profiles to optimize token economy and context window limits.

## Documentation
- **Manuals**: [Researcher Guide (Operational Manual)](docs/manuals/RESEARCHER_GUIDE.md) - Learn how to run your first project.
- **Tutorials**: [Quickstart](docs/tutorials/QUICKSTART.md), [Example Walkthrough](docs/tutorials/EXAMPLE_WALKTHROUGH.md)
- **Architecture**: [AI Integration](docs/architecture/AI_INTEGRATION.md), [Guidance System](docs/architecture/GUIDANCE_SYSTEM.md)
- **Templates**: [Agents Guide](templates/AGENTS.md) - Strict rules for LLM agents operating in this workspace.
- **Project**: [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md) | [Code of Conduct](CODE_OF_CONDUCT.md)

## File Index

To help you navigate this repository:
- `src/research_os/server.py` - Core MCP server and tool definitions.
- `src/research_os/protocols/` - The YAML-based methodology guidelines.
- `src/research_os/tools/` - Implementation of all OS actions (search, literature, branch, etc.).
- `src/research_os/state/` - State ledger and checkpoint logic.
- `templates/` - Default rules and guides to feed to agents.

[![PyPI version](https://badge.fury.io/py/research-os.svg)](https://badge.fury.io/py/research-os)
[![Python versions](https://img.shields.io/pypi/pyversions/research-os.svg)](https://pypi.org/project/research-os/)
[![Tests](https://github.com/VibhavSetlur/Research-OS/actions/workflows/tests.yml/badge.svg)](https://github.com/VibhavSetlur/Research-OS/actions)
