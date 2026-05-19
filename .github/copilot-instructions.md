# GitHub Copilot Work Space Instructions

This workspace implements a formal statistical research pipeline. All agents must follow the Universal compliance layer in `agents/00_core_guardrails.md`.

Use `@workspace` with the runner CLI tool to generate prompts and inspect state:
- Show status: `python scripts/research_runner.py status`
- Generate Prompt: `python scripts/research_runner.py prompt <init|route|scaffold|analyze|compile|audit>`
