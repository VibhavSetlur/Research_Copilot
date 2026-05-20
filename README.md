# Research Copilot

A self-healing, citation-verified, multi-modal research engine that any LLM can operate — from raw data to publication-ready paper.

---

## Setup (Copy to Your Project)

This is a **template repository**. Do not clone it directly as your project. Instead:

```bash
# 1. Clone the template temporarily
git clone https://github.com/your-org/research-copilot-template.git _tmp
cd _tmp

# 2. Copy ONLY the required files to your project folder
cp -r .research ../your-project/
cp -r inputs ../your-project/
cp -r environment ../your-project/
cp AGENTS.md ../your-project/

# 3. Go to your project and clean up
cd ../your-project
rm -rf _tmp
```

Your project now has exactly 4 things:
- **`.research/`** — the entire system (16 agents, 95 skills, 19 domains, CLI, hooks, scripts)
- **`inputs/`** — where you put data and fill out one intake file
- **`environment/`** — reproducible dependencies (requirements.txt, setup scripts)
- **`AGENTS.md`** — tells your AI agent how to work with this system

You write your own `README.md`, `.gitignore`, and `scripts/` for your research.

---

## Environment Setup

```bash
# Using venv (recommended)
bash environment/setup.sh
source environment/venv/bin/activate

# Using Conda
bash environment/setup_conda.sh
conda activate research-copilot
```

---

## Using It

### Step 0 (Optional): Preflight check

```bash
python .research/research.py preflight
```

### Step 1: Put your data in `inputs/data/raw/`

CSV, Parquet, Excel, SAS, SPSS, Stata, JSON — any format, any number of files.

### Step 2: Fill out `inputs/intake.md` (or use conversational interview)

**Option A: Fill out manually**
One file with: project info, research questions, data overview, domain, constraints.

**Option B: Conversational Interview (Recommended for beginners)**
```bash
python .research/research.py intake-interview --start
# Then reply to each question until intake.md is auto-generated
```

### Step 3: Open your AI agent and paste the init prompt

**OR** use the MCP Server for seamless AI IDE integration:
```bash
python .research/research.py mcp
# Then configure your AI IDE (Claude Desktop, Cursor) to connect
```

```
I'm using the Research Copilot system. Here's how it works:

1. All system files are in .research/ — agents, skills, workflows, CLI tool, scripts
2. My data and context are in inputs/ — everything is in inputs/intake.md
3. Environment is in environment/ — requirements.txt, setup scripts
4. CLI: python .research/research.py preflight → runtime availability and connectivity
5. CLI: python .research/research.py status → project state, next step
6. CLI: python .research/research.py scan → scan inputs, build research map
6. Workflow: research_init → literature_deep → method_route → data_scaffold → execute_analysis → compile_outputs → audit_validate
7. At ANY point I can say "research_iterate" to explore, pivot, or investigate
8. Skills are in .research/skills/ — read with `research skill <name>`
9. Agents are in .research/agents/ — read with `research agent <name>`
10. Always cite sources, compare to literature, try to disprove conclusions

Start by running:
  python .research/research.py preflight
  python .research/research.py scan
  python .research/research.py status
Then read the intake and begin:
  python .research/research.py agent research_init
```

### Step 4: The AI creates your project structure

The `research_init` agent creates `docs/`, `reports/`, `data/`, `scripts/` with README.md in every directory.

### Step 5: Work through the pipeline

At each approval gate, review results:
```bash
python .research/research.py approve method_route    # Continue
python .research/research.py reject method_route --reason "Need more controls"  # Send back
```

Or launch the Panel dashboard:
```bash
python .research/research.py dashboard
```

### Step 6: When done, you have everything for your paper

- `docs/` — full research log, methodology, decisions, dead ends
- `reports/` — analysis results, figures, tables, manuscript drafts
- `data/` — processed data pipeline (ingested → processed → analytical)
- `scripts/` — your reproducible analysis code (numbered: 01_, 02_, 03_...)

---

## Project Structure

```
your-project/
├── .research/                  # AI system (don't edit)
│   ├── research.py             # CLI tool (24 commands)
│   ├── agents/                 # 13 agent instructions
│   ├── skills/                 # 92 methodology skills
│   ├── workflows/              # 5 workflow templates
│   ├── domains/                # 19 domain profiles
│   ├── core/                   # Hook system, state ledger, checkpoints
│   ├── schemas/                # Pydantic models for validation
│   ├── scripts/                # System scripts
│   │   ├── 00_environment_check.py
│   │   ├── research_dashboard.py
│   │   └── utils/              # Core utilities (citation verifier, claim tracer, etc.)
│   └── config.yaml
├── inputs/                     # User-provided (AI never modifies)
│   ├── data/raw/               # Drop all data files here
│   ├── context/                # Optional: abstracts, notes, links
│   ├── papers/                 # Optional: PDFs
│   ├── intake.md               # Primary intake form
│   ├── intake.yaml             # Alternative YAML intake
│   └── intake.json             # Alternative JSON intake
├── environment/                # Reproducible dependencies
│   ├── requirements.txt        # Pinned Python dependencies
│   ├── setup.sh                # venv setup script
│   └── setup_conda.sh          # Conda setup script
├── scripts/                    # Created by AI — YOUR analysis code
│   ├── 01_data_prep.py         # Numbered in execution order
│   ├── 02_analysis.py
│   ├── 03_figures.py
│   └── ...
├── docs/                       # Created by AI — research documentation
├── reports/                    # Created by AI — analysis outputs
├── data/                       # Created by AI — processed data pipeline
└── AGENTS.md                   # AI agent instructions
```

---

## CLI Commands

### Core Commands

| Command | Purpose |
|---------|---------|
| `research preflight` | Run environment preflight checks |
| `research scan` | Scan inputs/, build research map |
| `research format-scan` | Run format router on raw data |
| `research status` | Project state, pipeline progress, next step |
| `research map` | Show research map (grounding context) |
| `research intake` | Show intake form status |
| `research followups` | Questions the user needs to answer |
| `research iterations` | Show iteration history |

### System Commands

| Command | Purpose |
|---------|---------|
| `research state` | Print current state.json ledger |
| `research resume --from <phase>` | Resume from checkpoint |
| `research budget` | Show token budget usage by phase |
| `research validate [phase]` | Run quality gate check |
| `research hooks` | Show registered hooks and execution log |

### Approval Gates

| Command | Purpose |
|---------|---------|
| `research approve <phase>` | Approve a pending phase gate |
| `research reject <phase> --reason "..."` | Reject with feedback |
| `research dashboard` | Launch Panel dashboard (localhost:5006) |

### Analysis Commands

| Command | Purpose |
|---------|---------|
| `research verify-citations` | Run three-pass citation verification |
| `research trace-claims` | Run claim-to-evidence graph builder |
| `research parallel --questions q1,q2,q3` | Run questions in parallel |
| `research debug <script>` | Auto-debug a failing script |
| `research tools` | List tools from registry |
| `research tool <name>` | Show details for a tool |

### Cache Management

| Command | Purpose |
|---------|---------|
| `research cache stats` | Show cache hit rates, size, table counts |
| `research cache clear --older-than 7d` | Prune old cache entries |

### New in v8.0

| Command | Purpose |
|---------|---------|
| `research mcp` | Start MCP server for AI IDE integration |
| `research intake-interview --start` | Conversational intake interview |
| `research preregistration` | Generate OSF pre-registration document |
| `research reviewer2` | Run adversarial 'Reviewer 2' critique |
| `research dependency-check <script>` | Check and auto-install missing dependencies |
| `research dag-viewer` | Generate interactive DAG visualization |

### Export Commands

| Command | Purpose |
|---------|---------|
| `research export --format latex` | Export manuscript to LaTeX |
| `research export --format pdf` | Export manuscript to PDF |
| `research export --format journal --journal nature` | Format for specific journal |

### Reference Commands

| Command | Purpose |
|---------|---------|
| `research skills` | List all 92 skills by category |
| `research skill <name>` | Show a specific skill's methodology |
| `research skill-search "time series"` | Search skills by keyword |
| `research agents` | List all 16 agents |
| `research agent <name>` | Show an agent's full instructions |
| `research workflow` | Show current workflow + iteration support |

---

## Architecture

### MCP Server (Model Context Protocol)

Research Copilot now exposes all CLI commands as MCP tools, allowing any MCP-compatible AI IDE (Claude Desktop, Cursor, etc.) to call research commands as native functions.

```bash
python .research/research.py mcp
```

Configure your AI IDE:
```json
{
  "mcpServers": {
    "research-copilot": {
      "command": "python",
      "args": ["/path/to/.research/mcp_server.py"]
    }
  }
}
```

### Multi-Agent LLM Delegation

Configure different LLMs for different tasks via `.research/models.yaml`:
- **Claude Sonnet**: Orchestration, code generation, writing
- **Gemini 2.5 Pro**: Literature review (1M token context)
- **OpenAI o3-mini**: Deep reasoning, adversarial review

### Conversational Intake

Beginners can use the interview mode instead of filling out a static form:
```bash
python .research/research.py intake-interview --start
```

### OSF Pre-Registration

Generate timestamped, OSF-compatible pre-registration documents:
```bash
python .research/research.py preregistration
```

### Adversarial Reviewer 2

Before finalizing, run the adversarial critic:
```bash
python .research/research.py reviewer2
```

### DAG Visualizer

Interactive web visualization of your data pipeline:
```bash
python .research/research.py dag-viewer
# Open: reports/dashboards/dag_viewer.html
```

### Dynamic Dependency Management

Auto-detect and install missing packages:
```bash
python .research/research.py dependency-check scripts/02_analysis.py --auto-install
```

### Cloud/HPC Execution

For TB-scale data, the system supports:
- SQL pushdown (Snowflake, BigQuery, Redshift)
- PySpark distributed compute
- Slurm batch jobs for HPC clusters

### Zotero & Semantic Scholar Integration

Sync with your reference manager for enhanced literature review.
Configure in `.research/config.yaml` under `literature:`.

---

## Architecture

### Lifecycle Hook System

The hook system intercepts pipeline execution at 5 stages, enabling any AI agent to use caching, validation, approval gates, and auto-debugging without async infrastructure.

```
User/Agent → research.py
    │
    ├── pre_routing ─────→ Skill router (loads only relevant skills)
    │                        Token budget throttle
    │                        Cache lookup (skip redundant computation)
    │
    ├── pre_execution ───→ Token budget management
    │                        Cache hit/miss checking
    │
    ├── post_execution ──→ Code syntax validation (AST parse)
    │                        Critic agent trigger
    │
    ├── pre_ledger_commit → Pydantic schema validation
    │                        Approval gate (blocks until human approves)
    │
    └── on_failure ──────→ State freeze + error logging
                             Recovery point for resume
```

### Schema Enforcement

Every agent output validates against Pydantic schemas before being accepted. Schemas in `.research/schemas/`.

### Citation Verification (Anti-Hallucination)

Three-pass verification: existence (CrossRef/arXiv/PubMed), content (Semantic Scholar), retraction (Retraction Watch).

Run: `research verify-citations`

### Claim Tracer

Builds a claim-to-evidence graph for the entire manuscript.

Run: `research trace-claims`

### Context7 Integration

Before writing any code using a library, agents MUST verify API signatures via Context7. Mandatory for: scipy, statsmodels, pandas, sklearn, lifelines, pymc, networkx, geopandas, altair, bokeh, panel, holoviews, dash, plotly.

---

## Workflows

| Workflow | When to use |
|----------|-------------|
| `quick_exploratory` | Fast analysis, no deep literature |
| `full_publication` | Complete pipeline with literature + audit |
| `systematic_review` | Literature-focused, PRISMA-compliant |
| `causal_investigation` | Causal inference with refutation |
| `predictive_modeling` | ML pipeline with cross-validation |

Change workflow in `.research/config.yaml`: `default_workflow: full_publication`

---

## Domains

19 domain profiles with reporting standards, effect size benchmarks, confounders, and preferred methods:

| Domain | Reporting Standard | Effect Size |
|--------|-------------------|-------------|
| Psychology & Social Sciences | APA 7th | Cohen's d |
| Epidemiology | STROBE | Risk ratio / OR |
| Econometrics | AEA | AME / IV |
| Finance | Journal of Finance | Alpha / Beta |
| Education | APA | Cohen's d / Hedges' g |
| Genomics | Nature Genetics | log2FC |
| NLP/Computational | ACL | F1 / BLEU |
| Ecology | Ecology | Effect ratio |
| Climate Science | AGU | Anomaly magnitude |
| Materials Science | ACS | Property change % |
| Neuroscience | APA + SfN | Cohen's d + BOLD % |
| Computational Biology | PLOS | log2FC |
| Political Science | APSR | AME |
| Anthropology | AAA | Thematic / Cohen's d |
| Sociology | ASA | Standardized coefficient |
| Empirical Legal Studies | Bluebook | Odds ratio |
| Public Policy | Policy brief | Impact magnitude |
| Bayesian-First (any domain) | HDI not CI | Posterior mean + HDI |
| Custom template | Configurable | Configurable |

---

## Iteration Types

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

---

## Key Features

### Anti-Hallucination Rules (Non-Negotiable)

1. Never invent a citation. If you cannot find a real DOI, write `[CITATION NEEDED]`.
2. Never invent a p-value, effect size, or sample size. Compute or mark `[COMPUTED NEEDED]`.
3. Never assume a file exists without checking via `Path.exists()`.
4. Never assume a variable name exists in data without checking `schema_cache.json`.
5. If unsure about a library API, invoke Context7 before writing code.
6. If a number in your output cannot be traced to a file, flag it.
7. When uncertain: understate, not overstate. Use "may" not "demonstrates".

### Auto-Healing Audit

The `audit_validate` agent runs 8 audits with auto-healing (up to 3 attempts):

| Audit | What It Checks | Auto-Healing |
|-------|---------------|--------------|
| Reproducibility | Scripts reproduce results | Fix imports, paths, re-run |
| Statistical Reporting | Every test has stat, df, p, effect size, CI | Re-compute missing values |
| Causal Language | Claims match study design | Fix language, add limitations |
| Figure Completeness | All referenced figures exist | Generate missing figures |
| Code Quality | Style, error handling, no hardcoded paths | Fix code issues |
| Citation Verification | Three-pass: existence, content, retraction | Find correct DOI, remove retractions |
| Claim Tracing | Every claim traced to data or citation | Find traces or remove claims |
| Visualization Standards | DPI, colorblind safety, axis labels | Re-render with correct parameters |

### Token Budget Management

| Threshold | Action |
|-----------|--------|
| 60% | Summarize completed phases into 3-sentence abstracts |
| 80% | Flush non-essential skill docs, keep only active skill |
| 90% | Force checkpoint, split into new conversation with state transfer |

Check: `research budget`

---

## Reproducibility Rules

1. ALWAYS install dependencies from `environment/requirements.txt` before running any code
2. ALWAYS run `.research/scripts/00_environment_check.py` to verify environment
3. ALWAYS record data lineage in `docs/data_lineage.json` after every transformation
4. ALWAYS compute SHA-256 hashes for raw data files
5. NEVER modify raw data files — only create new processed versions
6. ALWAYS pin package versions in `environment/requirements.txt`
7. Scripts MUST be numbered in execution order (01_, 02_, 03_...) in `scripts/`
8. Data pipeline MUST be reproducible: raw data + scripts = analytical data

---

## Requirements

See `environment/requirements.txt` for full list. Key dependencies:

- **Data**: pandas, numpy, scipy, polars, pyarrow
- **Statistics**: statsmodels, scikit-learn, pingouin
- **Visualization**: matplotlib, seaborn, plotly, altair, bokeh, panel, holoviews
- **Literature**: habanero (CrossRef), semanticscholar, metapub (PubMed)
- **State**: diskcache, SQLAlchemy, pydantic
- **Export**: pypandoc (LaTeX/PDF)

```bash
bash environment/setup.sh
source environment/venv/bin/activate
```

---

## License

MIT
