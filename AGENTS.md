# Research Copilot — AI Agent Instructions

You are a research assistant using the Research Copilot system.

## System Location
- All system files are in `.research/` — user never edits this
- CLI tool: `.research/research.py`
- Agents: `.research/agents/`
- Skills: `.research/skills/`
- Workflows: `.research/workflows/`
- Config: `.research/config.yaml`
- User data: `inputs/` — user provides, AI never modifies
- User intake: `inputs/intake.md`

## Output Structure (created by AI during research_init)
The template starts with ONLY `.research/` and `inputs/`. The `research_init` agent creates:

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
scripts/                 # Reproducible code
  utils/                 # Shared helpers
```

## CLI Commands
Always use `python .research/research.py <command>`:

| Command | Purpose |
|---------|---------|
| `status` | Project state, pipeline, iterations, docs status |
| `scan` | Scan inputs/, build research map |
| `map` | Show research map (grounding context) |
| `intake` | Show intake form status |
| `followups` | Questions the user needs to answer |
| `iterations` | Show iteration history |
| `skills` | List all skills by category |
| `skill <name>` | Show a specific skill's methodology |
| `agents` | List all agents with descriptions |
| `agent <name>` | Show a specific agent's full instructions |
| `workflow` | Show current workflow, pipeline, iteration support |

## Workflow
Run agents in this order:
1. `research_init` — parse intake, scan data, CREATE FULL DIRECTORY STRUCTURE, build research map
2. `literature_deep` — expand literature, build evidence matrix
3. `method_route` — select analysis methods
4. `data_scaffold` — build validated data pipeline
5. `execute_analysis` — run analysis, compare to literature
6. `compile_outputs` — assemble manuscript
7. `audit_validate` — multi-dimensional audit

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
7. Scripts are numbered in execution order (01_, 02_, 03_...)
8. Data pipeline stages are numbered (01_ingested, 02_processed, 03_analytical)
9. Figures/tables are numbered and organized by question (q1/, q2/, etc.)

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

## First Steps
1. Run `research scan`
2. Run `research status`
3. Read `inputs/intake.md`
4. Read `research agent research_init`
5. Execute the research_init protocol (this creates the full directory structure)
6. Continue through the pipeline, using `research_iterate` when the user wants to explore
