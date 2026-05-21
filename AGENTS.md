# Research Copilot — AI Agent Instructions

You are a research assistant using the Research Copilot system.

## System Location
- All system files are in `.research/` — user never edits this
- CLI tool: `.research/research.py`
- Agents: `.research/agents/`
- Skills: `.research/skills/`
- Workflows: `.research/workflows/`
- Config: `.research/config.yaml`
- System scripts: `.research/scripts/` and `.research/scripts/utils/`
- Environment: `environment/` — requirements.txt, setup scripts
- User data: `inputs/` — user provides, AI never modifies
- User intake: `inputs/intake.md`

## Output Structure (created by AI during research_init)
The template starts with ONLY `.research/`, `inputs/`, `environment/`, and `AGENTS.md`. The `research_init` agent creates:

```
docs/                    # Research documentation
  research_log.md        # Chronological log of ALL decisions
  methodology.md         # Methods used and WHY
  changelog.md           # What changed between iterations
  manifest.json          # Machine-readable directory registry
  iterations/            # Each research iteration documented
  decisions/             # Key methodological decisions with rationale
  dead_ends/             # Approaches tried and abandoned
reports/                 # Analysis outputs
  baseline/              # Initial research map, follow-ups
  literature/            # Literature corpus, evidence matrix
  analysis/              # Results by question (q1/, q2/, etc.)
  figures/               # Generated plots
  tables/                # Generated tables
  dashboards/            # Interactive summaries
  manuscript/            # Draft paper sections
  audit/                 # Audit reports
  summary/               # Key findings, executive summary
data/                    # Processed data pipeline
  01_ingested/           # Cleaned raw data
  02_processed/          # Transformed data
  03_analytical/         # Analysis-ready datasets
scripts/                 # USER'S analysis scripts (numbered: 01_, 02_, 03_...)
```

## CLI Commands
Always use `python .research/research.py <command>`:

| Command | Purpose |
|---------|---------|
| `status` | Project state, token budget, pipeline status, iterations, docs status |
| `scan` | Scan inputs/, build research map |
| `map` | Show research map (grounding context) |
| `intake` | Show intake form status |
| `intake-interview --start` | Start conversational intake interview (auto-generates intake.md) |
| `intake-interview --message "..."` | Reply to intake interview question |
| `followups` | Questions the user needs to answer |
| `iterations` | Show iteration history |
| `skills` | List all skills by category |
| `skill <name>` | Show a specific skill's methodology |
| `agents` | List all agents with descriptions |
| `agent <name>` | Show a specific agent's full instructions |
| `workflow` | Show current workflow, pipeline, iteration support |
| `budget` | Show token budget status and CTM history |
| `dag` | Show execution DAG summary |
| `dag-viewer` | Generate interactive DAG visualization HTML |
| `data-scale` | Show data scale analysis and library constraints |
| `preregistration` | Generate OSF-compatible pre-registration document |
| `reviewer2` | Run adversarial 'Reviewer 2' critique on findings |
| `dependency-check <script>` | Check for uninstalled imports in a script |
| `dependency-check <script> --auto-install` | Auto-install missing dependencies |
| `mcp` | Start MCP server for AI IDE integration |
| `branch <name>` | Create a new research branch (Git-like branching) |
| `branches` | List all research branches |
| `switch <name>` | Switch to a different branch |
| `merge <name>` | Merge a branch into target |
| `abandon <name>` | Abandon a research branch |
| `intent <query>` | Route a query through the intent router |
| `graph` | Show knowledge graph summary |
| `graph-stats` | Show knowledge graph statistics |
| `graph-query` | Query the knowledge graph |
| `taxonomy` | Show semantic file system taxonomy |

## Workflow
Run agents in this order:
1. `research_init` — parse intake, scan data, CREATE FULL DIRECTORY STRUCTURE, build research map
2. `literature_deep` — expand literature, build evidence matrix
3. `method_route` — select analysis methods
4. `generate_preregistration` — create OSF-compatible pre-registration document
5. `data_scaffold` — build validated data pipeline
6. `execute_analysis` — run analysis, compare to literature
7. `replication_validator` — replicate similar studies from literature on project data
8. `compile_outputs` — assemble manuscript
9. `reviewer2_critic` — adversarial audit of findings
10. `audit_validate` — multi-dimensional audit

## Research Iteration
At ANY point, the user can request iteration. Use `research_iterate` agent:
- "Why did we get this result?" → investigate
- "Try a different method" → method_switch
- "What if we control for X?" → variable_change
- "Check if this holds up" → robustness
- "How does this compare to literature?" → literature_compare
- "What else is in the data?" → explore
- "Find a better approach" → optimize

Each iteration:
1. Gets a unique ID (001, 002, 003...)
2. Documents what was tried, why, results, decision
3. Updates docs/iterations/, manifest.json, research_log.md
4. NEVER deletes previous iterations
5. Updates README.md in affected directories

## Directory Management Rules
1. `research_init` creates the FULL directory structure — no pre-existing output dirs
2. Every directory has a README.md with project-specific content
3. README.md files are updated whenever the directory's contents change
4. `docs/manifest.json` tracks the entire structure — update it when creating/modifying dirs
5. Never delete previous iterations, decisions, or dead ends
6. Research log is append-only
7. Scripts are numbered in execution order (01_, 02_, 03_...) in `scripts/`
8. Data pipeline stages are numbered (01_ingested, 02_processed, 03_analytical)
9. Figures/tables are numbered and organized by question (q1/, q2/, etc.)
10. System scripts are in `.research/scripts/` — do NOT modify these
11. Iteration scripts use `_ITER<XXX>` branching — NEVER overwrite prior scripts
12. Execution DAG (`.research/cache/execution_dag.json`) tracks all script runs
13. Context Transfer Memoranda (CTMs) are generated at 90% token budget — read them when resuming

## Rules
1. Read agent instructions with `research agent <name>` before executing
2. Read skill methodology with `research skill <name>` when needed
3. Always cite sources for methodological choices
4. Always compare findings to prior literature
5. Always try to disprove your own conclusions
6. Report non-significant results with the same detail as significant ones
7. Never overclaim — causal language only for RCTs or valid identification strategies
8. Organize results by research question, not by statistical method
9. Keep the user informed at every step
10. Ask follow-up questions when information is missing
11. Document EVERY decision in docs/decisions/ or docs/research_log.md
12. Dead ends are valuable — document them in docs/dead_ends/

## Reproducibility Rules
1. ALWAYS check environment is active before running any code
2. ALWAYS run `.research/scripts/00_environment_check.py` to verify environment
3. ALWAYS record data lineage in `docs/data_lineage.json` after every transformation
4. ALWAYS compute SHA-256 hashes for raw data files
5. NEVER modify raw data files — only create new processed versions
6. ALWAYS pin package versions in `environment/requirements.txt`
7. Scripts MUST be numbered in execution order (01_, 02_, 03_...) in `scripts/`
8. Data pipeline MUST be reproducible: raw data + scripts = analytical data
9. NEVER overwrite analysis scripts during iterations — use `_ITER<XXX>` branching
10. ALWAYS register script executions in the execution DAG (`.research/cache/execution_dag.json`)
11. ALWAYS check data scale profile before loading data — use polars lazy for files >= 1GB
12. ALWAYS read the latest CTM when starting a new conversation after a token budget split

## Quality Gate Rules
1. ALWAYS run quality gate check (`research validate <phase>`) before moving to next phase
2. NEVER proceed if a quality gate FAILS — fix the issue first
3. ALL checks in a gate must pass (warnings are noted but don't block)
4. Gate results are recorded in `docs/quality_gates/`
5. Failed gates are documented in docs/research_log.md with remediation steps

## Visualization Rules
1. ALWAYS read `viz_design_system` skill before creating ANY figure or dashboard
2. ALWAYS read `viz_code_standards` skill before writing ANY visualization code
3. Use Okabe-Ito palette for ALL categorical data — never default matplotlib colors
4. NEVER use rainbow/jet colormaps — use viridis or perceptually uniform palettes
5. ALL figures MUST be colorblind-safe — test with simulator
6. ALL dashboards MUST use component-based architecture — no monolithic files
7. ALL plotting MUST be function-based — no inline plotting code
8. ALL figures MUST have axis labels with units
9. NEVER show p-value without effect size and confidence interval
10. NEVER use pie charts or 3D charts
11. Dashboard main app ≤200 lines — all logic in component files
12. ALWAYS apply theme module (viz_theme.py) — no manual styling
13. MINIMALIST DESIGN: Remove top/right spines, use subtle grid lines (alpha ≤ 0.2), no decorative elements
14. INTERPRETATIVE COUPLING: Every figure MUST have an accompanying `.interpret.md` file in docs/decisions/

## First Steps
1. Run `research setup` — verify all system files are in place
2. Run `research scan` — scan inputs, build research map
3. Run `research status` — check project state
4. Read `inputs/intake.md`
5. Read `research agent research_init`
6. Execute the research_init protocol (this creates the full directory structure)
7. Continue through the pipeline, using `research_iterate` when the user wants to explore

## Branching Engine (Non-Linear Execution)
The system supports Git-like branching for divergent hypotheses:

### Creating a Branch
```bash
research branch hypothesis_B --hypothesis "Bayesian approach to the primary model"
```
This creates:
- A new branch in the state ledger
- Scaffolded directories: `reports/figures/hypothesis_B/`, `scripts/models/hypothesis_B/`, etc.
- Branch-specific README.md files in each directory

### Branch Workflow
1. `research branch <name>` — Create and switch to new branch
2. Run analysis on the branch (isolated from main)
3. `research branches` — List all branches and status
4. `research merge <name>` — Merge findings back to main
5. `research abandon <name>` — Abandon exploratory branch

### Parallel Execution
Branches enable the `parallel` command to execute across different hypotheses simultaneously without overwriting core findings.

## Intent Router (Token Optimization)
Before DAG initialization, the intent router maps user queries to minimal required context:

### How It Works
1. User provides natural language query
2. Router classifies intent (exploratory, hypothesis_test, causal, etc.)
3. Computes null space — skills/agents NOT needed
4. Compiles transient workflow YAML with only necessary steps
5. Excludes ~6,000+ tokens of unnecessary context

### Usage
```bash
research intent "find out what's driving the variance in this dataset"
```

## Knowledge Graph (Context Management)
Replaces dense text CTMs with graph-based retrieval:

### How It Works
1. Literature agent extracts triplets: `[Variable X] -> [confounded_by] -> [Variable Y]`
2. Triplets stored in NetworkX graph (`.research/cache/knowledge_graph.pkl`)
3. Analysis agents query graph instead of reading 10,000-token summaries

### Usage
```bash
research graph                    # Summary
research graph-stats              # Statistics
research graph-query --confounders "income"  # Get confounders
research graph-query --relation "mediates"   # Query by relation
```

## Semantic File System
Every AI-generated artifact is forced into a rigorous taxonomy:

| Category | Pattern | Destination |
|----------|---------|-------------|
| raw_data | *.csv, *.parquet | inputs/data/raw/ (immutable) |
| decision_doc | *decision*.md | docs/decisions/ |
| ingest_script | 01_*.py | scripts/01_ingest/ |
| eda_script | 02_*.py | scripts/02_eda/ |
| model_script | 03_*.py | scripts/03_models/ |
| figure | *.png, *.pdf | reports/figures/ |
| manuscript | *manuscript*.md | reports/manuscript/ |

### Usage
```bash
research taxonomy  # Show full taxonomy
```

## Interpretative Coupling
Every figure MUST have an accompanying `.interpret.md` file:
- Auto-generated in `docs/decisions/`
- Contains visual description, statistical interpretation, key takeaways, caveats
- Ensures users receive curated visual evidence, not just charts

