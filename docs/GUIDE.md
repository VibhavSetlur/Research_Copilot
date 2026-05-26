# Research OS Guide

Research OS is an MCP server that gives AI coding IDEs (Cursor, Claude Desktop, etc.)
73 tools to do reproducible, citation-verified research. The IDE is the brain (it plans,
reasons, calls tools). Research OS is the body (it executes, records state, enforces
immutability).

---

## Quick Setup

```bash
pip install "research-os[web,literature,viz,poster] @ git+https://github.com/VibhavSetlur/Research-OS.git"

mkdir my-project && cd my-project
research-os init --name "My Study"
research-os start --workspace .
```

Connect your IDE to the MCP server (command: `research-os start --workspace .`).
Put raw data in `inputs/raw_data/`, papers in `inputs/literature/`.

---

## Workspace Layout

```
my-project/
├── AGENTS.md                       # AI agent operating protocol
├── README.md                       # Auto-generated project overview
├── .os_state/                      # INTERNAL — OS state (DO NOT EDIT)
│   ├── state_ledger.json           # Primary state (paths, stage, checkpoints)
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
│   ├── raw_data/                   # Source data (CSV, Parquet, JSON, etc.)
│   ├── literature/                 # PDF papers
│   ├── context/                    # Notes, past results, text files
│   ├── intake.md                   # Auto-generated research brief (SHA-256 table)
│   └── literature_index.yaml       # Filename → citation key mapping
├── workspace/                      # ACTIVE — iterative experiments
│   ├── methods.md                  # Append-only method log
│   ├── analysis.md                 # Chronological log + Mermaid workflow
│   ├── citations.md                # Running bibliography with verified flags
│   ├── workflow.mermaid            # Auto-updated workflow diagram (colored nodes)
│   ├── workflow.png                # Rendered diagram (via mmdc)
│   ├── logs/
│   │   ├── searches.log            # Every web search logged (JSON lines)
│   │   ├── state_changes.log       # Before/after state diffs
│   │   ├── notifications.log       # Researcher notifications
│   │   ├── data_inventory.json     # Auto-profiled data inventory
│   │   └── 01_baseline.log         # Per-step execution logs
│   ├── 01_experiment_baseline/     # Numbered experiment steps
│   │   ├── README.md               # Goal, hypotheses, outcomes
│   │   ├── conclusions.md          # Key findings, routing decisions
│   │   ├── data/                   # Derived data
│   │   ├── scripts/                # Versioned scripts
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

Key rules:
- **`inputs/` is immutable** — tools reject writes there. Copy to `workspace/` to process.
- **Experiments are chronological** — `sys.path.create` auto-numbers folders `01_`, `02_`, ...
- **`methods.md` is append-only** — append via `mem.methods.append`.
- **State is atomic** — updates use temp-file + rename on every tool call.

---

## All 73 MCP Tools

### System (`sys.*`) — 39 tools

| Tool | What it does |
|------|-------------|
| `sys.guidance.get` | Load a protocol YAML (tells AI what steps to run) |
| `sys.guidance.list` | List all available protocols |
| `sys.guidance.validate` | Check if protocol expected outputs exist |
| `sys.protocol.next` | Recommend next protocol based on pipeline stage |
| `sys.protocol.log` | Record a protocol execution to the log |
| `sys.protocol.history` | Read recent protocol execution history |
| `sys.workspace.scaffold` | Create full project directory structure |
| `sys.workspace.tree` | Return structured tree of `workspace/` |
| `sys.file.read` | Read a file |
| `sys.file.write` | Write a file (cannot write to `inputs/` or overwrite `synthesis/` without force) |
| `sys.file.list` | List files in a directory |
| `sys.file.delete` | Delete a file |
| `sys.state.get` | Full workspace state |
| `sys.state.summary` | Brief state summary |
| `sys.state.summary_md` | Read `.os_state/os_state.md` |
| `sys.state.health` | Context estimate, paths, handoff recommendation |
| `sys.state.minimal_context` | ≤500 token snapshot for small models |
| `sys.session.handoff` | Generate structured markdown session summary |
| `sys.checkpoint.create` | Snapshot workspace |
| `sys.checkpoint.rollback` | Rollback to a checkpoint |
| `sys.checkpoint.list` | List checkpoints |
| `sys.checkpoint.pending` | Register a pending action for approval |
| `sys.checkpoint.approve` | Approve pending action |
| `sys.path.create` | Create next numbered experiment folder |
| `sys.path.abandon` | Mark a path as dead end |
| `sys.path.list` | List experiment paths |
| `sys.config.init` | Initialize researcher config |
| `sys.config.get` | Read config |
| `sys.config.set` | Set a config value |
| `sys.config.validate` | Validate config and API keys |
| `sys.config.profile` | Return autonomy/expertise/model in <100 tokens |
| `sys.config.explain` | Document any config key |
| `sys.notify` | Notify researcher |
| `sys.external_mcp.discover` | Discover external MCP servers |
| `sys.task.monitor` | Check background task status |
| `sys.task.kill` | Kill a background task |
| `sys.tool.info` | Get full schema for a tool |
| `sys.tool.search` | Search tools by name/description |
| `sys.md.validate` | Validate a .md file against a writing protocol |
| `sys.env.snapshot` | Snapshot Python/R/Julia environment |
| `sys.env.docker.generate` | Generate Dockerfile from environment snapshot |

### Tool (`tool.*`) — 25 tools

| Tool | What it does |
|------|-------------|
| `tool.task.create` | Create a background task |
| `tool.audit.synthesis` | Audit manuscript completeness and claims |
| `tool.audit.statistical_power` | Compute post-hoc power (warns if < 0.8) |
| `tool.audit.assumptions` | Re-run assumption checks on model outputs |
| `tool.audit.figure_quality` | Validate DPI, colorblind-friendly, labels |
| `tool.audit.reproducibility_full` | Full Docker-based reproducibility check |
| `tool.search.semantic_scholar` | Search Semantic Scholar |
| `tool.search.pubmed` | Search PubMed |
| `tool.search.crossref` | Search Crossref |
| `tool.search.web` | Web search |
| `tool.web.scrape` | Scrape a webpage |
| `tool.literature.download` | Download a paper PDF |
| `tool.python.exec` | Execute a Python script |
| `tool.r.exec` | Execute an R script |
| `tool.julia.exec` | Execute a Julia script |
| `tool.bash.exec` | Execute a Bash script |
| `tool.package.install` | Install Python packages |
| `tool.env.freeze` | (Deprecated, use sys.env.snapshot) |
| `tool.env.restore` | Restore a frozen environment |
| `tool.latex.compile` | Compile synthesis/paper.tex to PDF |
| `tool.poster.create` | Generate LaTeX poster |
| `tool.data.sample` | Sample rows from a dataset |
| `tool.data.convert` | Convert between CSV/RDS/Feather/Parquet |
| `tool.log.decision` | Log a reasoning decision |
| `tool.synthesize` | Compile workspace findings into synthesis/paper.md |
| `tool.synthesize.plan` | Show available sections and recommended ordering |

### Memory (`mem.*`) — 4 tools

| Tool | What it does |
|------|-------------|
| `mem.analysis.log` | Append to `workspace/analysis.md` |
| `mem.methods.append` | Append structured method entry to `workspace/methods.md` |
| `mem.citations.generate` | Generate `workspace/citations.md` from literature index |
| `mem.intake.regenerate` | Regenerate `inputs/intake.md` with file hashes |

### View (`view.*`) — 1 tool

| Tool | What it does |
|------|-------------|
| `view.workspace.tree` | Alias for `sys.workspace.tree` |

---

## Pipeline (10 Stages)

The pipeline guides the research from start to finish:

| # | Protocol | Trigger | Completed when |
|---|----------|---------|---------------|
| 1 | `guidance/session_boot` | Every session start | Config read, autonomy set, model profile set |
| 2 | `guidance/project_startup` | After session_boot | `workspace/01_baseline_eda/conclusions.md` exists |
| 3 | `domain/domain_analysis` | After startup | `workspace/logs/domain_analysis.log` exists |
| 4 | `domain/research_design` | After domain analysis | `docs/research_question.md` exists |
| 5 | `methodology/methodology_selection` | After design | `workspace/methods.md` exists |
| 6 | `literature/literature_search` | After method selection | `inputs/literature_index.yaml` exists |
| 7 | `guidance/analysis_plan` | After literature | `workspace/02_data_preparation/README.md` exists |
| 8 | `reproducibility/reproducibility` | After analysis | `workspace/*/environment/requirements.txt` exists |
| 9 | `audit/audit_and_validation` | After reproducibility | `workspace/logs/audit.log` exists |
| 10 | `synthesis/synthesis_paper` | After audit | `synthesis/paper.md` exists |

Call `sys.protocol.next` at any time to find out what should run next.
Each protocol also comes in a **light** variant (loaded for small models).

---

## Natural Language Workflow

Research OS is designed for you to talk to the AI in plain English. Here is
exactly what happens when you give a prompt:

### Example Session

**You (in your IDE):**
> "I put air pollution data in inputs. Analyze it and tell me what you find."

**What the AI does (automatically, behind the scenes):**

| # | AI Action | Tool Call |
|---|-----------|-----------|
| 1 | Read project status | `sys.state.summary_md` |
| 2 | Read my profile | `sys.config.profile` |
| 3 | Read full config | `sys.config.get` |
| 4 | See workspace layout | `sys.workspace.tree` |
| 5 | Read full state | `sys.state.get` |
| 6 | Load session boot protocol | `sys.guidance.get` → `guidance/session_boot` |
| 7 | Confirm next action | `sys.protocol.next` → `guidance/project_startup` |
| 8 | Load project startup protocol | `sys.guidance.get` → `guidance/project_startup` |
| 9 | Re-generate intake with checksums | `mem.intake.regenerate` |
| 10 | Create experiment folder | `sys.path.create` → `workspace/01_baseline_eda/` |
| 11 | Write and run analysis script | `tool.python.exec` |
| 12 | Log findings | `mem.analysis.log` |
| 13 | Register method used | `mem.methods.append` |
| 14 | Mark protocol complete | `sys.protocol.log` → `project_startup completed` |
| 15 | Check what to do next | `sys.protocol.next` → `domain/domain_analysis` |

**AI says:** *"I analyzed your air pollution data. PM2.5 is strongly correlated
with respiratory cases (r=0.985). I created 01_baseline_eda with the full
analysis. Next step: domain_analysis. Should I continue?"*

### More Prompts

| You say | AI does |
|---------|---------|
| "Continue with domain analysis" | Loads `domain/domain_analysis` protocol, follows its steps |
| "Search for related literature" | `tool.search.semantic_scholar` + `tool.search.pubmed` |
| "This approach isn't working, abandon it" | `sys.path.abandon` with rationale |
| "Run a statistical power check" | `tool.audit.statistical_power` on results |
| "Write the methods section" | Loads `writing/writing_methods` protocol, calls `tool.synthesize` |
| "Generate the paper" | Follows pipeline to `synthesis/synthesis_paper`, calls `tool.synthesize` |
| "What should I do next?" | `sys.protocol.next` — returns current pipeline stage |
| "What happened in the last session?" | `sys.protocol.history` — shows protocol execution log |
| "Check if my methods are correct" | `sys.md.validate` against the writing protocol template |

The AI never guesses — it always loads the protocol YAML and follows the
numbered steps. You can inspect any protocol yourself by running
`sys.guidance.list` to see available ones, then `sys.guidance.get` to read one.

---

## Key CLI Commands

| Command | What it does |
|---------|-------------|
| `research-os init [--name "X"]` | Scaffold a new project |
| `research-os start --workspace .` | Start MCP server |
| `research-os doctor` | Check system health |
| `research-os status [--json]` | Show workspace status and pipeline progress |
| `research-os pull cursor\|claude\|opencode\|vscode\|antigravity\|all` | Add IDE MCP config to workspace |
| `research-os env` | Show environment info |

---

## Config & API Keys

When you scaffold a project, `inputs/researcher_config.yaml` is created. The AI
will ask you for values through a config interview:

```yaml
# inputs/researcher_config.yaml
project_id: "My Study"
research_question: "What is the effect of PM2.5 on respiratory health?"
domain: "environmental_health"
default_depth: "academic"
model_profile: "medium"          # small | medium | large
interaction:
  autonomy_level: "supervised"   # manual | supervised | autopilot
researcher:
  expertise_level: "intermediate"  # beginner | intermediate | advanced | pi
api_keys:
  firecrawl: ""                  # Injected as FIRECRAWL env var at server start
  semantic_scholar: ""           # Injected as SEMANTIC_SCHOLAR env var
```

API keys are injected as environment variables at server start, so search tools
use them transparently.

### Model Profiles

The `model_profile` field changes how protocols load:

| Profile | Effect |
|---------|--------|
| **large** | Full protocol YAML, full tool descriptions |
| **medium** | Standard protocols, standard descriptions |
| **small** | Light protocol variants (shorter steps, step-by-step), truncated tool descriptions |

Light protocols are auto-selected when profile is `small`. If a protocol has no
light variant, the full version is used as fallback.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `research-os: command not found` | Add `~/.local/bin` to PATH |
| `WriteProtectedError` | Can't write to `inputs/` — copy data to `workspace/` |
| `Protocol not found` | Run `sys.guidance.list` to see valid names |
| Tools not appearing in IDE | Restart IDE, check MCP panel for errors |
| Mermaid not rendering | `npm install -g @mermaid-js/mermaid-cli` |

---

## Architecture (Brief)

```
AI IDE (Cursor/Claude) ←→ MCP stdio → Research OS server.py
                                              │
                                   ┌──────────┼──────────┐
                                   │          │          │
                              sys.*      tool.*     mem.*
                              (39)       (25)       (4)
                                   │          │          │
                                   └──────────┼──────────┘
                                              │
                                       Workspace files
                                    (state, data, logs)
```

The IDE plans and decides. Research OS executes, records, and enforces rules.
No autonomous decisions happen in Research OS — the AI model is always in control.
