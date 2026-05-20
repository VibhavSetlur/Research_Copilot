# Research Copilot

A self-healing, citation-verified, multi-modal research engine that any LLM can operate — from raw data to publication-ready paper.

## Pipeline Overview

```mermaid
flowchart LR
    A[Drop Data] --> B[Intake Form]
    B --> C[research_init]
    C --> D[literature_deep]
    D --> E[method_route]
    E --> F[data_scaffold]
    F --> G[execute_analysis]
    G --> H[replication_validator]
    H --> I[compile_outputs]
    I --> J[reviewer2_critic]
    J --> K[audit_validate]
    K --> L[Manuscript]
    
    style C fill:#4CAF50
    style G fill:#2196F3
    style J fill:#FF5722
    style K fill:#9C27B0
    style L fill:#FFC107
```

---

## Quick Start — Choose Your Path

### 🎓 For Students & Beginners

**Install and start in 3 commands:**

```bash
pip install research-copilot
rcp init my-research-project
cd my-research-project
```

Then add your data to `inputs/data/raw/` and open your AI IDE. That's it.

**No data yet?** Start a conversational interview — the AI will guide you:
```bash
python .research/research.py intake-interview --start
```

---

### 💻 For AI IDE Users (Cursor, opencode, Claude Desktop)

**This is the killer feature.** Connect your AI IDE directly to Research Copilot via MCP:

1. **Start the MCP server:**
   ```bash
   python .research/research.py mcp
   ```

2. **Configure your IDE:**

   **Cursor:** Add to `.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "research-copilot": {
         "command": "python",
         "args": ["/absolute/path/to/.research/mcp_server.py"]
       }
     }
   }
   ```

   **Claude Desktop:** Add to `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "research-copilot": {
         "command": "python",
         "args": ["/absolute/path/to/.research/mcp_server.py"]
       }
     }
   }
   ```

   **opencode:** Add to `opencode.json`:
   ```json
   {
     "mcp": {
       "research-copilot": {
         "command": "python",
         "args": [".research/mcp_server.py"]
       }
     }
   }
   ```

3. **Start your project:** Tell your AI:
   > "I'm starting a new Research Copilot project. Use the MCP tools to run preflight checks, scan inputs, and execute the research_init agent."

The AI now has **28 native tools** to control the entire research pipeline — no parsing stdout, no guessing commands.

---

### 🤖 For Autonomous / Hands-Free Execution

Set up multi-agent LLM delegation in `.research/models.yaml` and run the pipeline without human intervention:

```bash
# Set your API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AIza..."

# Check which models are available
python .research/research.py models

# Run the full pipeline
python .research/research.py status
```

The system automatically routes tasks to optimal models:
- **Gemini 2.5 Pro** (1M context) → Literature review
- **Claude Sonnet** → Orchestration, code generation, writing
- **OpenAI o3-mini** → Deep reasoning, adversarial review

**Missing an API key?** The system gracefully falls back to available models with a visible warning.

---

## Installation

### Option A: PyPI (Recommended)

```bash
pip install research-copilot
rcp init my-project
cd my-project
```

### Option B: From Source

```bash
git clone https://github.com/your-org/research-copilot.git
cd research-copilot
cp -r .research inputs/ environment/ AGENTS.md ../my-project/
cd ../my-project
```

### Environment Setup

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

### Step 1: Put your data in `inputs/data/raw/`

CSV, Parquet, Excel, SAS, SPSS, Stata, JSON — any format, any number of files.

### Step 2: Fill out the intake

**Option A: Conversational Interview (Recommended)**
```bash
python .research/research.py intake-interview --start
```

**Option B: Manual** — Edit `inputs/intake.md` directly.

### Step 3: Open your AI IDE

With MCP connected, your AI agent can discover and execute all commands. Simply say:
> "Start the research pipeline."

Or run manually:
```bash
python .research/research.py preflight
python .research/research.py scan
python .research/research.py status
```

### Step 4: Work through the pipeline

The `research_init` agent creates your full project structure. At each approval gate:

```bash
python .research/research.py approve method_route    # Continue
python .research/research.py reject method_route --reason "Need more controls"  # Send back
```

### Step 5: When done, you have everything for your paper

- `docs/` — full research log, methodology, decisions, dead ends
- `reports/` — analysis results, figures, tables, manuscript drafts
- `data/` — processed data pipeline (ingested → processed → analytical)
- `scripts/` — your reproducible analysis code (numbered: 01_, 02_, 03_...)

---

## Key Features

### MCP Server (Model Context Protocol)

All 28 CLI commands exposed as native MCP tools. Zero subprocess overhead — direct function invocation makes tool calls instantaneous.

```bash
python .research/research.py mcp
```

### Multi-Agent LLM Delegation

Configure different LLMs for different tasks. Graceful degradation when API keys are missing.

```bash
python .research/research.py models  # Show availability report
```

### Adversarial Reviewer 2 with Auto-Remediation

Before finalizing, run the adversarial critic. **Fatal flaws** (data leakage, severe confounding, causal overclaims) trigger automatic remediation attempts:

```bash
python .research/research.py reviewer2
```

If remediation fails, flaws are automatically appended to the manuscript's Limitations section.

### Conversational Intake

Beginners can use the interview mode. Interview completion **auto-triggers** project initialization:

```bash
python .research/research.py intake-interview --start
```

### OSF Pre-Registration

Generate timestamped, OSF-compatible pre-registration documents:

```bash
python .research/research.py preregistration
```

### DAG Visualizer

Interactive web visualization of your data pipeline:

```bash
python .research/research.py dag-viewer
```

### Dynamic Dependency Management

Auto-detect and install missing packages:

```bash
python .research/research.py dependency-check scripts/02_analysis.py --auto-install
```

### Anti-Hallucination System

- Three-pass citation verification (CrossRef, Semantic Scholar, Retraction Watch)
- Claim-to-evidence graph tracing
- Context7 API signature verification before code generation

### Token Budget Management

| Threshold | Action |
|-----------|--------|
| 60% | Summarize completed phases |
| 80% | Flush non-essential context |
| 90% | Force checkpoint, split session with CTM |

---

## Project Structure

```
your-project/
├── .research/                  # AI system (don't edit)
│   ├── research.py             # CLI tool (28 commands)
│   ├── mcp_server.py           # MCP server (instant tool calls)
│   ├── models.yaml             # Multi-agent LLM routing
│   ├── agents/                 # 13 agent instructions
│   ├── skills/                 # 92 methodology skills
│   ├── workflows/              # 5 workflow templates
│   ├── domains/                # 19 domain profiles
│   ├── core/                   # Hook system, state ledger, model resolver
│   ├── schemas/                # Pydantic models for validation
│   └── scripts/                # System scripts + utilities
├── inputs/                     # User-provided (AI never modifies)
│   ├── data/raw/               # Drop all data files here
│   ├── context/                # Optional: abstracts, notes, links
│   ├── papers/                 # Optional: PDFs
│   └── intake.md               # Primary intake form
├── environment/                # Reproducible dependencies
├── scripts/                    # Created by AI — YOUR analysis code
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
| `rcp init <name>` | Create a new Research Copilot project |
| `research preflight` | Run environment preflight checks |
| `research scan` | Scan inputs/, build research map |
| `research status` | Project state, pipeline progress, next step |
| `research map` | Show research map (grounding context) |
| `research intake` | Show intake form status |

### MCP Tools (28 available)

All commands above + `research_agent`, `research_skill`, `research_validate`, `research_approve`, `research_reject`, `research_budget`, `research_dag`, `research_data_scale`, `research_hooks`, `research_verify_citations`, `research_trace_claims`, `research_debug`, `research_cache_stats`, `research_cache_clear`, `research_intake_interview`, `research_preregistration`, `research_reviewer2`, `research_dependency_check`, and more.

### Approval Gates

| Command | Purpose |
|---------|---------|
| `research approve <phase>` | Approve a pending phase gate |
| `research reject <phase> --reason "..."` | Reject with feedback |

### Analysis Commands

| Command | Purpose |
|---------|---------|
| `research verify-citations` | Run three-pass citation verification |
| `research trace-claims` | Run claim-to-evidence graph builder |
| `research parallel --questions q1,q2,q3` | Run questions in parallel |
| `research debug <script>` | Auto-debug a failing script |
| `research reviewer2` | Run adversarial Reviewer 2 critique |

### Cache Management

| Command | Purpose |
|---------|---------|
| `research cache stats` | Show cache hit rates, size |
| `research cache clear --older-than 7d` | Prune old cache entries |

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
| `research agents` | List all 13 agents |
| `research agent <name>` | Show an agent's full instructions |
| `research workflow` | Show current workflow + iteration support |

---

## Architecture

### Lifecycle Hook System

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
    │                        Reviewer 2 adversarial review
    │
    ├── pre_ledger_commit → Pydantic schema validation
    │                        Approval gate (blocks until human approves)
    │
    └── on_failure ──────→ State freeze + error logging
                             Recovery point for resume
```

### Schema Enforcement

Every agent output validates against Pydantic schemas before being accepted.

### Reviewer 2 Remediation Loop

```
reviewer2_critic → Detect fatal flaws
    │
    ├── Data leakage → method_switch → Re-run with train/test separation
    ├── Severe confounding → variable_change → Add controls, re-run regression
    ├── Causal overclaim → investigate → Downgrade language
    └── Missing uncertainty → validate → Compute CIs and effect sizes
         │
         ├── Success → Re-run reviewer2
         └── Failure → Append to manuscript Limitations section
```

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

## Anti-Hallucination Rules (Non-Negotiable)

1. Never invent a citation. If you cannot find a real DOI, write `[CITATION NEEDED]`.
2. Never invent a p-value, effect size, or sample size. Compute or mark `[COMPUTED NEEDED]`.
3. Never assume a file exists without checking via `Path.exists()`.
4. Never assume a variable name exists in data without checking `schema_cache.json`.
5. If unsure about a library API, invoke Context7 before writing code.
6. If a number in your output cannot be traced to a file, flag it.
7. When uncertain: understate, not overstate. Use "may" not "demonstrates".

---

## Requirements

See `environment/requirements.txt` for full list. Key dependencies:

- **Data**: pandas, numpy, scipy, polars, pyarrow
- **Statistics**: statsmodels, scikit-learn, pingouin
- **Visualization**: matplotlib, seaborn, plotly, altair, bokeh, panel
- **Literature**: habanero (CrossRef), semanticscholar, metapub (PubMed)
- **State**: diskcache, SQLAlchemy, pydantic
- **Export**: pypandoc (LaTeX/PDF)

```bash
pip install research-copilot[all]
```

---

## License

MIT
