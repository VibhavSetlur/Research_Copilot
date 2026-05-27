# Research OS

[![tests](https://github.com/VibhavSetlur/Research-OS/actions/workflows/test.yml/badge.svg)](https://github.com/VibhavSetlur/Research-OS/actions/workflows/test.yml)
[![python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://github.com/VibhavSetlur/Research-OS)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**From raw data to publication-ready manuscript — an MCP-native research
operating system. Works with any AI IDE (Claude Code, OpenCode, Antigravity,
Cursor, VS Code, Windsurf, Continue, Aider) without managing any LLM
provider keys.**

Research OS is a [Model Context Protocol](https://modelcontextprotocol.io)
server that exposes ~75 research tools and 34 YAML protocols. The AI in your
IDE plans and reasons; Research OS executes, records state, enforces
immutability, and walks the AI through the right protocol for the current
pipeline stage.

---

## Quick start (≤60 seconds)

```bash
pip install "research-os[all] @ git+https://github.com/VibhavSetlur/Research-OS.git"

mkdir my-project && cd my-project
research-os init                     # scaffolds + drops an MCP config for every IDE
```

Open your AI IDE on the project. Drop your data into `inputs/raw_data/`,
papers into `inputs/literature/`, notes into `inputs/context/`. Then say:

> "fill out the intake"   *(reads everything, proposes a research question, hypotheses, domain)*

> "what should I do next?"   *(iterative-planning protocol: literature, tools, options, recommendation)*

> "run a baseline EDA"   *(creates `workspace/01_baseline_eda/`, atomic versioned scripts, conclusions)*

> "write the paper"   *(IMRAD synthesis with **verified, real** citations only — no hallucinations)*

The CLI is two commands by design:

| Command                              | What it does                              |
|--------------------------------------|-------------------------------------------|
| `research-os init [dir]`             | Scaffold a workspace.                     |
| `research-os start [--workspace .]`  | Run the MCP server (your IDE talks to it). |

---

## Why use it

| Pain | What Research OS does about it |
|---|---|
| AI hallucinates citations | `tool_synthesize` pulls every citation from real providers (Crossref / Semantic Scholar / PubMed / arXiv), drops unverified entries, and caps per-section (3 for abstracts, 6 for posters, 40 for papers). |
| AI guesses methodology from training memory | `tool_research_method` mandates literature grounding before any choice; `mem_decision_log` records the rationale + citations. |
| AI writes 400-line one-shot scripts | `tool_plan_step` forces breakdown into atomic, versioned sub-tasks; protocol forbids mega-shots. |
| Researcher just wants to dump files and talk | `tool_intake_autofill` reads `inputs/`, classifies the domain, extracts the research question + hypotheses, fills `intake.md`. Every config field is optional. |
| Researcher mid-flow drops a new paper | `tool_context_intake` auto-routes the new file into the right `inputs/` subfolder and (optionally) re-runs intake autofill. |
| AI gets stuck / workspace looks broken | `tool_workspace_repair` heals missing dirs, regenerates manifest + mermaid, backs up corrupted state — never deletes. |
| Long jobs on shared HPC | `tool_task_run` (real `Popen`) backgrounds them, `tool_task_status` polls without blocking the conversation. |
| Multi-language / notebook / Quarto workflows | First-class `.py`, `.R`, `.jl`, `.sh`, `.ipynb`, `.Rmd`, `.qmd`. |
| Custom analyses (not just off-the-shelf libs) | Protocols explicitly support custom methodology — `mem_methods_append implementation="custom"`. Use `workspace/scratch/` to prototype. |
| Iterating on direction (researcher wants AI to propose) | `guidance/iterative_planning` protocol reads state + searches literature + tools + proposes 2-3 options with rationale. |
| Multiple hypotheses to track | `mem_hypothesis_add` / `_update` / `_list` maintains a ledger across experiment steps. |

---

## Workspace layout (created by `research-os init`)

```text
my-project/
├── AGENTS.md                       # AI operating rules — read first every session
├── inputs/                         # IMMUTABLE — researcher provides
│   ├── researcher_config.yaml      # config + API keys (gitignored)  ← auto-created
│   ├── raw_data/                   # source files
│   ├── literature/                 # PDFs
│   ├── context/                    # notes, prior reports
│   ├── intake.md                   # auto-filled by tool_intake_autofill
│   └── literature_index.yaml       # filename → citation_key
├── docs/                           # human-readable: research question, glossary
├── workspace/                      # ACTIVE — experiments live here
│   ├── methods.md / analysis.md / citations.md / workflow.mermaid
│   ├── logs/                       # search + error + audit logs
│   ├── scratch/                    # AI sandbox (gitignored)
│   └── 01_baseline_eda/            # numbered experiment steps
│       ├── README.md / conclusions.md
│       ├── scripts/                # versioned: 01_baseline_eda_v1.py …
│       ├── data/{input,output}/    # input symlinked to previous step
│       ├── outputs/{reports,figures,tables,dashboards}/
│       └── environment/            # requirements.txt / renv.lock / Project.toml
├── synthesis/                      # FINAL outputs (only when explicitly built)
│   ├── paper.md / paper.tex / paper.pdf
│   ├── abstract.md / poster.tex / dashboard.html / references.bib
└── environment/                    # global env baseline
```

`.os_state/` (state, manifest, checkpoints, handoffs, cache) is internal and
gitignored beyond the state ledger.

---

## Architecture (45 seconds)

```
AI IDE (Claude Code / OpenCode / Antigravity / Cursor / Claude / VS Code)
        │ MCP stdio
        ▼
research-os MCP server
        │
        ├── sys.*    workspace, state, paths, checkpoints, config, files, repair
        ├── tool.*   search, exec, audit, synthesis, scratch, tasks, research, intake
        └── mem.*    append-only methods/analysis/citations/decisions/hypotheses
        │
        ▼
    Workspace files  (immutable inputs · iterative workspace · final synthesis)
```

The IDE plans and decides; Research OS executes and records. No autonomous
decisions in Research OS — your model is always in control.

---

## Documentation

* **[docs/GUIDE.md](docs/GUIDE.md)** — Full reference: every tool, every
  protocol, the pipeline, FAQ for power users (custom tools, branching,
  scratch, mid-flow context, repair).
* **[templates/AGENTS.md](templates/AGENTS.md)** — The AI operating manual
  dropped into every workspace. Read this to understand how the AI is
  expected to behave.
* **[CHANGELOG.md](CHANGELOG.md)** — Release history.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues + PRs welcome.
