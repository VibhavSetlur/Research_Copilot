# Research Copilot

A self-healing, citation-verified research engine that any LLM can operate — from raw data to publication-ready manuscript.

[Documentation](docs/) · [Quick Start](docs/GETTING_STARTED.md) · [CLI Reference](docs/CLI_REFERENCE.md) · [Architecture](docs/ARCHITECTURE.md) · [Contributing](docs/CONTRIBUTING.md)

---

## What It Does

Research Copilot transforms raw data into publication-ready research through a reproducible, AI-driven pipeline:

1. **Drop data** — CSV, Parquet, Excel, Stata, SPSS, SAS
2. **Describe your question** — plain English, no jargon
3. **Get a manuscript** — with verified citations, effect sizes, confidence intervals, and publication-ready figures

The system handles data profiling, method selection, statistical analysis, figure generation, literature search, citation verification, and adversarial review — automatically.

---

## Quick Start

```bash
pip install research-copilot
rcp init my-project
cd my-project
```

Drop your data into `00_inputs/raw_data/`, open your AI IDE, and say **"analyze my data."**

For a step-by-step guide, see [Getting Started](docs/GETTING_STARTED.md).

---

## Key Features

| Feature | Description |
|---------|-------------|
| **MCP Server** | 28+ native tools for AI IDEs (Cursor, opencode, Claude Desktop) |
| **Citation Verification** | Three-pass verification against CrossRef, Semantic Scholar, Retraction Watch |
| **Adversarial Review** | Reviewer 2 auto-critique with remediation loop |
| **Token Budget** | Context management with CTM handoff at 90% capacity |
| **Multi-Agent** | Route tasks to optimal LLMs (Gemini for literature, Claude for code) |
| **19 Domains** | Reporting standards for APA, STROBE, CONSORT, PRISMA, AEA, and more |
| **Reproducible** | Execution DAG, SHA-256 hashes, checkpoint/restore |

---

## Project Structure

```
my-project/
├── .research/                 # Project config (.research/config.yaml) + runtime cache
│   └── config.yaml            # Workflow, routing, thresholds
├── 00_inputs/                 # Immutable raw data (after ingest)
├── 01_workspace/              # Human-AI scratch space
├── 02_experiments/            # Isolated hypothesis branches
├── 03_synthesis/              # Manuscript and final outputs
├── environment/               # Reproducible dependencies
├── AGENTS.md                  # AI agent instructions
└── pyproject.toml             # Project metadata
```

**System assets** (agents, skills, workflows, domains) are bundled in the installed Python package (`research_copilot.assets`). The `.research/` folder contains only project configuration and auto-created cache.

---

## Documentation

| Document | Purpose |
|----------|---------|
| [Getting Started](docs/GETTING_STARTED.md) | Step-by-step onboarding for first-time users |
| [Architecture](docs/ARCHITECTURE.md) | Hook system, state ledger, DAG execution, token budget |
| [CLI Reference](docs/CLI_REFERENCE.md) | All commands, flags, and MCP tools |
| [MCP Integration](docs/MCP_INTEGRATION.md) | Connect AI IDEs to Research Copilot |
| [Workflows](docs/WORKFLOWS.md) | Pipeline types and when to use each |
| [Domains](docs/DOMAINS.md) | Domain profiles and reporting standards |
| [Iteration](docs/ITERATION.md) | Research iteration types and protocol |
| [Contributing](docs/CONTRIBUTING.md) | Development setup and contribution guide |
| [Changelog](docs/CHANGELOG.md) | Version history |

---

## Requirements

- Python 3.10+
- See [environment/requirements.txt](environment/requirements.txt) for full dependency list

```bash
pip install research-copilot[all]
```

---

## License

MIT
