# Research Copilot

AI-driven research assistant. Drop data in `inputs/`, fill out one intake file, and let an AI agent run the full research pipeline — with full iteration support.

## Setup (30 seconds)

```bash
# 1. Clone this template
git clone https://github.com/your-org/research-copilot-template.git _tmp

# 2. Copy the system into your project folder
cp -r _tmp/.research ./
cp -r _tmp/inputs ./
cp _tmp/AGENTS.md ./

# 3. Delete the template
rm -rf _tmp
```

That's it. Your project now has:
- `.research/` — all AI instructions, skills, agents, workflows, and the CLI tool
- `inputs/` — where you put your data and fill out one intake file
- `AGENTS.md` — tells your AI agent how to work with this system

## Using It

### Step 1: Put your data in `inputs/data/raw/`

Drop any data files here — CSV, Parquet, Excel, SAS, SPSS, Stata, JSON. Any number of files, any state.

### Step 2: Fill out `inputs/intake.md`

One file. Everything in one place:
- **Project info** — title, researcher, institution
- **Research questions** — as many as you need, each with variables, hypothesis, data prep needed
- **Data overview** — describe your files, relationships between them, what cleaning is needed
- **Domain & constraints** — field, target journal, timeline, IRB status

### Step 3: Open your AI agent and paste the init prompt

Open opencode, Cursor, Claude, or any AI agent in your project folder and paste:

```
I'm using the Research Copilot system. Here's how it works:

1. All system files are in .research/ — agents, skills, workflows, and the CLI tool (.research/research.py)
2. My data and research context are in inputs/ — everything is in inputs/intake.md
3. The CLI has these commands:
   - python .research/research.py status       → project state, iterations, next step
   - python .research/research.py scan         → scan inputs, build research map
   - python .research/research.py map          → show research map (grounding context)
   - python .research/research.py intake       → show intake form status
   - python .research/research.py followups    → questions I need to answer
   - python .research/research.py iterations   → show iteration history
   - python .research/research.py skills       → list all skills
   - python .research/research.py skill <name> → show a skill's methodology
   - python .research/research.py agents       → list all agents
   - python .research/research.py agent <name> → show an agent's instructions
   - python .research/research.py workflow     → show current workflow + iteration support

4. The workflow is: research_init → literature_deep → method_route → data_scaffold → execute_analysis → compile_outputs → audit_validate
5. At ANY point I can say "research_iterate" to explore, pivot, or investigate results
6. Skills are in .research/skills/ — read them with `research skill <name>` for methodology
7. Agents are in .research/agents/ — read them with `research agent <name>` for next steps
8. Always cite sources for methodological choices
9. Always compare findings to literature
10. Always try to disprove your own conclusions

Start by running:
  python .research/research.py scan
  python .research/research.py status
Then read the intake and begin:
  python .research/research.py agent research_init
```

### Step 4: The AI creates your project structure

The `research_init` agent will:
- Parse your intake and scan your data
- Create the FULL directory structure (docs/, reports/, data/, scripts/)
- Write README.md in every directory with project-specific info
- Build the research map and assess feasibility
- Create the documentation system (research log, methodology, changelog, manifest)

### Step 5: Work with the AI through the pipeline

The AI proceeds through the workflow. At each step, you can:
- Ask about results: "What did you find?"
- Request iteration: "Why did we get this result?"
- Change methods: "Try a different approach"
- Add variables: "What if we control for X?"
- Check robustness: "Does this hold up?"
- Compare to literature: "How does this compare to prior work?"

Every iteration is documented. Nothing is ever deleted. You get a complete research trail.

### Step 6: When done, you have everything for your paper

- `docs/` — full research log, methodology, decisions, dead ends
- `reports/` — all analysis results, figures, tables, manuscript drafts
- `data/` — processed data pipeline (ingested → processed → analytical)
- `scripts/` — reproducible code for everything
- `reports/summary/` — key findings and executive summary

## Project Structure

```
your-project/
├── .research/              # AI system (don't edit)
│   ├── research.py         # CLI tool (11 commands)
│   ├── agents/             # 9 agent instructions (incl. research_iterate)
│   ├── skills/             # 57 methodology skills
│   ├── workflows/          # 5 workflow templates (all with iteration support)
│   ├── domains/            # 9 domain profiles
│   └── config.yaml         # configuration
├── inputs/                 # User-provided (AI never modifies)
│   ├── data/raw/           # Drop all data files here
│   ├── context/            # Optional: abstracts, notes, links
│   ├── papers/             # Optional: PDFs
│   └── intake.md           # Everything in one file
├── docs/                   # Created by AI — research documentation
│   ├── research_log.md     # Chronological log of ALL decisions
│   ├── methodology.md      # Methods used and WHY
│   ├── changelog.md        # What changed between iterations
│   ├── manifest.json       # Machine-readable directory registry
│   ├── iterations/         # Each research iteration documented
│   ├── decisions/          # Key methodological decisions
│   └── dead_ends/          # Approaches tried and abandoned
├── reports/                # Created by AI — analysis outputs
│   ├── baseline/           # Initial research map, follow-ups
│   ├── literature/         # Literature corpus, evidence matrix
│   ├── analysis/           # Results by question (q1/, q2/, etc.)
│   ├── figures/            # Generated plots
│   ├── tables/             # Generated tables
│   ├── dashboards/         # Interactive summaries
│   ├── manuscript/         # Draft paper sections
│   ├── audit/              # Audit reports
│   └── summary/            # Key findings, executive summary
├── data/                   # Created by AI — processed data
│   ├── 01_ingested/        # Cleaned raw data
│   ├── 02_processed/       # Transformed data
│   └── 03_analytical/      # Analysis-ready datasets
├── scripts/                # Created by AI — reproducible code
│   └── utils/              # Shared helpers
└── AGENTS.md               # AI agent instructions
```

## Workflows

| Workflow | When to use |
|----------|-------------|
| `quick_exploratory` | Fast analysis, no deep literature |
| `full_publication` | Complete pipeline with literature + audit |
| `systematic_review` | Literature-focused, PRISMA-compliant |
| `causal_investigation` | Causal inference with refutation |
| `predictive_modeling` | ML pipeline with cross-validation |

Change workflow in `.research/config.yaml`: `default_workflow: full_publication`

## Iteration Types

The `research_iterate` agent supports these iteration types:

| Type | User says | What happens |
|------|-----------|--------------|
| `investigate` | "Why did we get this result?" | Deep dive into existing results |
| `method_switch` | "Try a different method" | New analytical approach |
| `variable_change` | "What if we add/remove X?" | Change variables, re-run |
| `robustness` | "Check if this holds up" | Sensitivity analysis |
| `literature_compare` | "How does this compare?" | Compare to prior work |
| `explore` | "What else is in the data?" | Exploratory analysis |
| `optimize` | "Find a better approach" | Method optimization |
| `validate` | "Double-check this" | Replicate with different approach |

Each iteration gets a unique ID, is fully documented, and never deleted.
