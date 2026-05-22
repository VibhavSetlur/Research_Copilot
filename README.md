# Research OS v3.0

> **A publication-grade Research Guidance Engine for Agentic AI.**

Research OS transforms any MCP-capable LLM into a rigorous, protocol-following researcher. Rather than providing rigid "tools" that execute hidden analysis (like a black-box t-test), Research OS provides **Guidance Protocols**—structured YAML decision trees that guide the AI on *how* to do research properly, leaving the execution up to transparent, auditable python code.

## 🧭 The "Hands, Eyes, Memory" Philosophy

1. **Hands**: Minimal OS-level MCP tools (`sys.file.*`, `tool.python.exec`, `sys.branch.*`). The AI writes its own scripts.
2. **Eyes**: Context gathering through `tool.search.*`, `sys.guidance.get`, and `tool.web.scrape`.
3. **Memory**: Immutable state tracking in `.os_state/`, with branching, checkpoints, and sidecar JSON provenance logs.

## 📁 Workspace Architecture

Research OS enforces a publication-ready directory structure instantly via `sys.workspace.scaffold`:

```text
├── .os_state/       # Immutable state, checkpoints, and ledger
├── docs/            # Hypotheses, glossary, research questions
├── environment/     # requirements.txt, Dockerfiles
├── inputs/          # Raw data, literature, context
├── synthesis/       # Paper drafts, final bibliography
└── workspace/       # Active experimentation (scripts, figures, data)
```

## 🚀 Getting Started

See [QUICKSTART.md](QUICKSTART.md) to initialize your first project.
For deep-dives into how the AI uses the system, see the `docs/` folder:
- [Guidance System](docs/GUIDANCE_SYSTEM.md)
- [Researcher Guide](docs/RESEARCHER_GUIDE.md)
- [AI Integration](docs/AI_INTEGRATION.md)
