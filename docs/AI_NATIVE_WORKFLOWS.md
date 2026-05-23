# AI Native Workflows

The IDE-driven research loop: how AI IDEs use Research OS tools to execute reproducible research.

---

## The IDE-Driven Loop

Research OS is not an autonomous agent. It's a tool server that provides the **hands**, **eyes**, and **memory** that your AI IDE uses to execute research. The IDE is the brain—it thinks, plans, and decides which tools to call.

```text
┌─────────────────────────────────────────────────────────┐
│                    AI IDE (Brain)                       │
│  Cursor / Windsurf / Claude Desktop                     │
│  ┌─────────────────────────────────────────────────┐    │
│  │  1. User types: "Clean the clinical dataset"    │    │
│  │  2. IDE plans the required steps                │    │
│  │  3. IDE calls: sys.file.read(...)               │    │
│  │  4. IDE calls: tool.python.exec(...)            │    │
│  │  5. IDE calls: mem.analysis.log(...)            │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────┘
                       │ MCP Protocol (stdio JSON-RPC)
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Research OS (Executor)                     │
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
└─────────────────────────────────────────────────────────┘
```

## Example Workflow

1. **Intake & Exploration**
   The IDE explores the workspace using `sys.file.read` and checks guidance with `sys.guidance.get`.

2. **Execution**
   The IDE runs data analysis by generating python code and executing it via `tool.python.exec`.

3. **Logging & Checkpointing**
   Important decisions are logged using `tool.log.decision`, and the IDE can persist the current state with `sys.checkpoint.create`.
