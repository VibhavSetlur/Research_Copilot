# Architecture

Research Copilot is built around a lifecycle hook system that intercepts every stage of the research pipeline.

## System Overview

```
User/AI Agent
    │
    ▼
┌─────────────────────────────────────────────┐
│  CLI (research.py / rcp)                    │
│  28 commands, MCP server, approval gates    │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Agents │ │ Skills │ │Domains │
│  13    │ │  92+   │ │  19    │
└────────┘ └────────┘ └────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│ State  │ │  DAG   │ │ Cache  │
│ Ledger │ │Manager │ │ (SQLite│
│        │ │        │ │ +Disk) │
└────────┘ └────────┘ └────────┘
```

## Lifecycle Hook System

Five hook stages intercept every pipeline operation:

### 1. `pre_routing` — Before Task Selection

- **Semantic skill router**: Matches user query against skill index, loads only 2-4 relevant skills (not all 92+)
- **Data scale detection**: Scans input files, enforces polars lazy frames for files >1GB
- **Token budget throttle**: Truncates context at 60/80/90% thresholds

### 2. `pre_execution` — Before Running Code

- **Token budget management**: Emergency split + CTM generation at 90%
- **Cache lookup**: Skips redundant computation if identical operation+params exist

### 3. `post_execution` — After Running Code

- **Code syntax validation**: AST parse of generated Python before execution
- **Dependency detection**: Auto-installs missing imports (if enabled)
- **Critic agent trigger**: Adversarial review for critical phases
- **Reviewer 2**: Aggressive critique after manuscript compilation

### 4. `pre_ledger_commit` — Before Saving State

- **Pydantic schema validation**: Rejects malformed outputs before serialization
- **Approval gate**: Blocks pipeline until human approves (30s auto-approve fallback)

### 5. `on_failure` — On Any Error

- **State freeze**: Serializes current state to snapshot
- **Recovery point**: Records where to resume
- **Dead end logging**: Documents failed approaches for future reference

## State Ledger

The state ledger (`.research/cache/state.json`) is the single source of truth for project state:

```json
{
  "run_id": "run_20260520_143022",
  "phase": "execute_analysis",
  "step": 3,
  "active_branch": "main",
  "decisions": [...],
  "dead_ends": [...],
  "resumable_from": "execute_analysis:step_3"
}
```

Key methods:
- `get_project_summary(max_tokens=500)` — Compact string for context injection
- `get_latest_checkpoint_summary()` — Latest checkpoint with key results

## Execution DAG

Every script execution is registered in the DAG (`.research/cache/execution_dag.json`):

```json
{
  "nodes": {
    "02_descriptive_stats_base_20260520": {
      "script": "02_descriptive_stats.py",
      "input_files": ["00_inputs/raw_data/survey.csv"],
      "output_files": ["outputs/analysis/descriptive_results.json"],
      "depends_on": ["01_data_ingestion_base_20260520"],
      "status": "complete",
      "duration": 2.3
    }
  }
}
```

The DAG enables:
- Reproducibility: replay exact execution order
- Parallel execution: identify independent nodes
- Incremental runs: skip already-complete nodes

## Token Budget Management

| Threshold | Action |
|-----------|--------|
| <60% | Full context available |
| 60% | Summarize completed phases |
| 80% | Flush non-essential skill docs |
| 90% | Force checkpoint, generate CTM, split conversation |

### Context Transfer Memorandum (CTM)

At 90% capacity, the system generates a CTM capturing:
- Abandoned paths and dead ends
- Micro-decisions made during analysis
- Immediate tactical goals
- Partial results and open questions

The CTM is saved to `.research/cache/context_transfer_memos/` and indexed in the knowledge graph.

## Knowledge Graph

Triplets extracted from literature are stored in a NetworkX graph (`.research/cache/knowledge_graph.pkl`):

```
[Variable X] -> [confounded_by] -> [Variable Y]
[Method A] -> [validated_by] -> [Paper B]
[Finding C] -> [contradicted_by] -> [Finding D]
```

Query via CLI:
```bash
rcp graph-query --confounders "income"
rcp graph-query --relation "mediates"
```

## Branching Engine

Research branches enable divergent hypotheses without overwriting core findings:

```bash
rcp branch hypothesis_B --hypothesis "Bayesian approach"
# ... run analysis on branch ...
rcp merge hypothesis_B    # Merge findings back to main
rcp abandon hypothesis_B  # Or abandon exploratory branch
```

Each branch creates an isolated experiment directory under `02_experiments/`.

## Anti-Hallucination System

1. **Citation verification**: Three-pass check (existence, content, retraction)
2. **Claim tracing**: Every claim traced to data or verified citation
3. **Context7 API**: Library signatures verified before code generation
4. **Schema enforcement**: Pydantic validation on all agent outputs
5. **Grounding rules**: Never invent p-values, effect sizes, or citations
