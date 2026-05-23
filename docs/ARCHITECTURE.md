# Research OS Architecture

Research OS is an **MCP server** that provides tools (hands), observability (eyes), and state management (memory) for AI-driven research. The IDE is the brain — it thinks, plans, and decides which tools to call. Research OS executes.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    AI IDE (Brain)                       │
│  Cursor / Windsurf / Claude Desktop                     │
│  ┌─────────────────────────────────────────────────┐    │
│  │  The IDE:                                       │    │
│  │  1. Receives user request (NLP)                 │    │
│  │  2. Decides which tools to call                 │    │
│  │  3. Calls tools in sequence                     │    │
│  │  4. Reads responses, updates chat               │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────┘
                       │ MCP Protocol (stdio JSON-RPC)
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Research OS (Executor)                     │
│                                                         │
│  ┌───────────────┐  ┌────────────────────────────────┐  │
│  │  Tool Router  │  │  State Ledger                  │  │
│  │  (server.py)  │  │  (.os_state/state_ledger.json) │  │
│  │               │  │  - current_branch              │  │
│  │  sys.*        │  │  - branches & statuses         │  │
│  │  tool.*       │  │  - checkpoint_history          │  │
│  │  mem.*        │  │  - pipeline_stage              │  │
│  └───────┬───────┘  └────────────────────────────────┘  │
│          │                                              │
│  ┌───────▼───────────────────────────────────────────┐  │
│  │  Tool Implementations                             │  │
│  │  ┌────────────────────┐ ┌────────────────────┐    │  │
│  │  │ System (sys.*)     │ │ Tools (tool.*)     │    │  │
│  │  │                    │ │                    │    │  │
│  │  │ file.read          │ │ search.pubmed      │    │  │
│  │  │ branch.create      │ │ python.exec        │    │  │
│  │  │ checkpoint.create  │ │ data.sample        │    │  │
│  │  │ guidance.validate  │ │ web.scrape         │    │  │
│  │  └────────────────────┘ └────────────────────┘    │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Project State (project_ops.py)                   │  │
│  │  - Workspace scaffold & conventions               │  │
│  │  - Branch creation                                │  │
│  │  - Checkpoint management                          │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    Workspace (Filesystem)               │
│                                                         │
│  inputs/    workspace/    synthesis/    .os_state/      │
│  (immutable) (active)     (outputs)     (internal)      │
└─────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. IDE is the Brain, OS is the Body

The IDE (Cursor, Windsurf, Claude Desktop) is the cognitive layer. It:
- Understands natural language requests
- Analyzes intent and plans tool sequences
- Calls tools in the right order
- Reads results and presents them to the user

Research OS never:
- Makes autonomous decisions
- Plans research steps
- Selects tools on its own
- Thinks or reasons about the problem

### 2. Tool Categories

| Category | Prefix | Responsibility | Examples |
|----------|--------|---------------|---------|
| System | `sys.` | Control the OS itself | `sys.branch.create`, `sys.file.read`, `sys.guidance.validate` |
| Tools | `tool.` | Execute actions on data | `tool.python.exec`, `tool.search.pubmed`, `tool.data.sample` |
| Memory | `mem.` | Read/write persistent state | `mem.methods.append`, `mem.analysis.log` |

### 3. State Ledger as Source of Truth

Every tool call updates `.os_state/state_ledger.yaml`:
- Atomic writes (temp file + rename)
- Before/after diffs logged to `workspace/logs/state_changes.log`
- JSON backup format for backward compatibility
- SHA-256 checksums on every file write

### 4. Immutable Inputs

The `inputs/` directory is write-protected at the tool level. Any tool that attempts to write to `inputs/` receives a `WriteProtectedError`. Data must be copied to `workspace/` for processing.

### 5. Numbered Experiment Folders

Experiments are created as `workspace/01_name/`, `02_name/`, etc. by `sys.branch.create`. Each folder is self-contained with README.md, conclusions.md, data/, scripts/, and outputs/.

---

## Component Details

### MCP Server (`server.py`)
- Listens on stdio (default) or SSE
- Exposes 44+ tools via `list_tools`
- Routes tool calls to handler functions
- Returns standardized JSON envelope with checksums

### Project Operations (`project_ops.py`)
- Workspace scaffold, intake regeneration
- State ledger read/write with YAML + JSON
- Numbered experiment folder creation
- Literature index and citation management
- Workflow diagram rendering

### Tool Implementations (`tools/tool_impls.py`)
- Standalone functions for each tool
- No side effects beyond file writes and tool responses
- All results returned as dicts

### Dependencies
- **Python**: pandas, numpy, scipy, scikit-learn, matplotlib, seaborn, statsmodels
- **Optional**: panel + plotly (dashboards), mmdc (Mermaid PNG), pdflatex (LaTeX)
- **Runtime**: Python 3.10+, MCP-compatible IDE
