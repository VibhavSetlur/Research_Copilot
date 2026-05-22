# Research Copilot

A self-healing, citation-verified research engine that any LLM can operate — from raw data to publication-ready manuscript.

## Architecture

Research Copilot uses an **Agentic Directed Acyclic Graph (DAG)** to model the research process. It is built natively on the **Model Context Protocol (MCP)**, allowing it to seamlessly integrate with standard open-source MCP servers for database and file system access.

### Key Features
- **MCP Native**: Standard JSON-RPC interface exposing research capabilities.
- **Agentic DAG**: Decomposes complex research goals into independent, reproducible nodes.
- **Self-Healing Execution**: Detects hallucinations and compilation errors, autonomously recovering state and replanning.
- **Semantic State Ledger**: Replaces fragmented manifest files with a single source of truth for the entire pipeline run.

## Getting Started

Check out [QUICKSTART.md](QUICKSTART.md) for installation and basic usage.
