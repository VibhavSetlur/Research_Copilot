# Research OS

A self-healing, citation-verified research engine that any LLM can operate — from raw data to publication-ready manuscript. It provides an autonomous execution layer with zero-to-research capabilities, tiered context memory, and cognitive state tracking.

## Architecture

Research OS uses an **Agentic Directed Acyclic Graph (DAG)** to model the research process. It is built natively on the **Model Context Protocol (MCP)**, allowing it to seamlessly integrate with standard open-source MCP servers for database and file system access.

### Key Features
- **Zero-to-Research Autonomous Initiation**: Describe your goal, and the OS dynamically compiles a rigorous execution DAG.
- **Absolute Token Economy**: Implements tiered memory (System, Working, Cold) and semantic distillation.
- **Execution Safety**: Embedded Stuck Loop detection and capability gating prevents catastrophic loops and hallucination side-effects.
- **MCP Native**: Standard JSON-RPC interface exposing research capabilities, daemonized for IDE integrations.
- **Semantic State Ledger**: Replaces fragmented manifest files with a single source of truth for the entire pipeline run.

## Getting Started

Check out [QUICKSTART.md](QUICKSTART.md) for installation and basic usage. Start the daemon with `research-os start --daemon` or `rcp start --daemon`.
