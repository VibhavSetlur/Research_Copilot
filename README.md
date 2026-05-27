# Research OS

[![tests](https://github.com/VibhavSetlur/Research-OS/actions/workflows/test.yml/badge.svg)](https://github.com/VibhavSetlur/Research-OS/actions/workflows/test.yml)
[![python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://github.com/VibhavSetlur/Research-OS)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**From raw data to publication-ready manuscript — an MCP-native research
operating system. Works with any AI IDE (Claude Code, OpenCode, Antigravity,
Cursor, VS Code, Windsurf, Continue, Aider) without managing any LLM
provider keys.**

Research OS is a [Model Context Protocol](https://modelcontextprotocol.io)
server exposing ~85 research tools and 34 YAML protocols. The AI in your
IDE plans and reasons; Research OS executes, records state, enforces
immutability, and walks the AI through the right protocol for the current
pipeline stage. Every citation in every final output is verified online —
no hallucinations leak through.

---

## Quick start (≤60 seconds)

```bash
pip install "research-os[all] @ git+https://github.com/VibhavSetlur/Research-OS.git"

mkdir my-project && cd my-project
research-os init                     # scaffolds + drops MCP config for every IDE
```

Open your AI IDE on the project. Drop your data into `inputs/raw_data/`,
papers into `inputs/literature/`, notes into `inputs/context/`. Then say:

> *"fill out the intake"* — AI reads everything, proposes research question + hypotheses + domain.

> *"what should I do next?"* — iterative planning: literature + tools + 2-3 options.

> *"run a baseline EDA"* — creates `workspace/01_baseline_eda/`, atomic versioned scripts, conclusions.

> *"write the paper for a journal"* — IMRAD synthesis with numbered figures + verified citations only.

The CLI is two commands by design:

| Command                              | What it does                              |
|--------------------------------------|-------------------------------------------|
| `research-os init [dir]`             | Scaffold a workspace.                     |
| `research-os start [--workspace .]`  | Run the MCP server (your IDE talks to it). |

Don't have a project yet? Paste
[`docs/SETUP_PROMPT.md`](docs/SETUP_PROMPT.md) into any AI chat — it walks
the install + IDE wiring without needing one.

---

## Why use it

| Pain | What Research OS does about it |
|---|---|
| AI hallucinates citations | `tool_synthesize` pulls every citation from real providers (Crossref / Semantic Scholar / PubMed / arXiv), drops unverified entries, and caps per-section (3 abstract / 6 poster / 12 dashboard / 25 report / 40 paper). |
| AI guesses methodology from training memory | `tool_research_method` mandates literature grounding before any choice; `mem_decision_log` records the rationale + citations. |
| AI writes 400-line one-shot scripts | `tool_plan_step` forces breakdown into atomic, versioned sub-tasks; protocol forbids mega-shots. |
| Researcher just wants to dump files and talk | `tool_intake_autofill` reads `inputs/`, classifies domain, extracts research question + hypotheses, fills `intake.md`. Every config field is optional. |
| Researcher mid-flow drops a new paper | `tool_context_intake` auto-routes the file into the right `inputs/` subfolder and re-runs intake autofill. |
| AI gets stuck / workspace looks broken | `tool_workspace_repair` heals missing dirs, regenerates manifest + mermaid, backs up corrupted state — **never deletes**. |
| Long jobs on shared HPC | `tool_task_run` (real `Popen`) backgrounds them; `tool_task_status` polls without blocking the chat. |
| Multi-language / notebook / Quarto workflows | First-class `.py`, `.R`, `.jl`, `.sh`, `.ipynb`, `.Rmd`, `.qmd`. |
| Custom analyses (not just off-the-shelf libs) | Protocols explicitly support custom methodology — `mem_methods_append implementation="custom"`. Use `workspace/scratch/` to prototype. |
| Iterating on direction (researcher wants AI to propose) | `guidance/iterative_planning` protocol reads state + searches literature/tools + proposes 2-3 options with rationale. |
| Multiple hypotheses to track | `mem_hypothesis_add` / `_update` / `_list` maintains a ledger across experiment steps. |
| Per-step literature | `tool_literature_download step_id=<NN_slug>` saves PDFs to `workspace/<step>/literature/`. Sidecar `.meta.yaml` lets synthesis cite them properly. |

---

## Workspace layout example

`research-os init` creates a clean skeleton. The AI fills the rest as you
work. **Real projects look like this after a few sessions** (the step
names below — `01_baseline_eda`, `02_data_preparation`,
`03_logistic_baseline`, `04_random_forest` — are **illustrative only**;
the AI derives each slug from the actual goal of the step it's creating,
following the naming rules in the `guidance/analysis_plan` protocol
(loaded contextually, not in `AGENTS.md`):

```text
my-project/
│
├── AGENTS.md                         # canonical AI rules (every IDE reads this)
├── GETTING_STARTED.md                # friendly intro for the researcher
├── CLAUDE.md  .windsurfrules  ...    # per-IDE shim rule files
├── README.md                         # project README (you write this)
├── .gitignore
│
├── inputs/                           # IMMUTABLE — researcher provides
│   ├── researcher_config.yaml        # source of truth for AI behaviour (gitignored)
│   ├── intake.md                     # auto-filled by tool_intake_autofill
│   ├── literature_index.yaml         # filename → citation_key mapping
│   ├── raw_data/
│   │   ├── cohort_2024.csv
│   │   ├── exposures.parquet
│   │   └── README.md                 # describes what's in this folder
│   ├── literature/                   # PROJECT-WIDE PDFs (anchor papers)
│   │   ├── vanderweele2020e_value.pdf
│   │   └── vanderweele2020e_value.pdf.meta.yaml
│   └── context/                      # notes, drafts, prior reports
│       ├── pi_briefing.md
│       └── prior_analysis_2022.pdf
│
├── docs/                             # human-readable
│   ├── research_question.md          # confirmed during project_startup
│   ├── domain_summary.md             # classified during domain_analysis
│   ├── research_design.md            # chosen during research_design
│   └── glossary.md                   # terms; extended by glossary_update
│
├── workspace/                        # ACTIVE — experiments live here
│   │
│   ├── methods.md                    # APPEND-ONLY method log (mem_methods_append)
│   ├── analysis.md                   # APPEND-ONLY narrative + workflow diagram
│   ├── citations.md                  # auto-generated bibliography
│   ├── workflow.mermaid              # auto-updated; rendered to .png if mmdc present
│   ├── workflow.png
│   │
│   ├── logs/
│   │   ├── searches.log              # every tool_search_* logged
│   │   ├── errors.log
│   │   ├── audit_report.md           # produced by audit_and_validation
│   │   └── context_intake_log.jsonl  # every file the AI auto-routed
│   │
│   ├── scratch/                      # AI sandbox (GITIGNORED)
│   │   ├── README.md                 # explains scratch policy
│   │   ├── try_groupby.py            # one-off tests live here, then get
│   │   └── sql_smoke.py              #   promoted into a numbered step or deleted
│   │
│   ├── 01_baseline_eda/              # ── EXPERIMENT STEP #1 ──
│   │   ├── README.md                 # goal, inputs, methods, outputs, decision
│   │   ├── conclusions.md            # findings + limitations + decision (proceed/branch/dead-end)
│   │   ├── scripts/
│   │   │   ├── 01_baseline_eda_v1.py    # first cut
│   │   │   ├── 01_baseline_eda_v2.py    # bumped after researcher asked for groupby by quarter
│   │   │   └── 01_baseline_eda_v3.py    # third version after audit flagged DPI
│   │   ├── literature/               # PDFs SCOPED to this step (canonical references)
│   │   │   ├── tukey1977eda.pdf
│   │   │   ├── tukey1977eda.pdf.meta.yaml
│   │   │   └── literature_index.yaml
│   │   ├── data/
│   │   │   ├── input/                # symlinked → ../../inputs/raw_data/
│   │   │   └── output/               # derived data (parquet, csv)
│   │   ├── outputs/
│   │   │   ├── reports/              # markdown summary WITH numbers + interpretation
│   │   │   │   └── distributions.md
│   │   │   ├── figures/              # PNG ≥150 DPI (300+ for publication)
│   │   │   │   ├── age_histogram.png
│   │   │   │   ├── age_histogram.caption.md
│   │   │   │   └── correlations_heatmap.png
│   │   │   └── tables/               # CSV / markdown
│   │   │       └── missingness_summary.csv
│   │   └── environment/
│   │       └── requirements.txt      # pip freeze at this step (per-step reproducibility)
│   │
│   ├── 02_data_preparation/          # ── EXPERIMENT STEP #2 ──
│   │   ├── README.md / conclusions.md
│   │   ├── scripts/
│   │   │   └── 02_data_preparation_v1.py
│   │   ├── data/
│   │   │   ├── input/                # symlinked → ../../01_baseline_eda/data/output/
│   │   │   └── output/
│   │   ├── outputs/{reports,figures,tables}/
│   │   └── environment/
│   │
│   ├── 03_logistic_baseline__DEAD_END/   # ── ABANDONED STEP (preserved, never deleted) ──
│   │   ├── README.md
│   │   ├── conclusions.md            # "## Why this path failed" section
│   │   ├── scripts/
│   │   │   ├── 03_logistic_baseline_v1.py
│   │   │   └── 03_logistic_baseline_v2.py
│   │   ├── literature/
│   │   ├── data/, outputs/, environment/
│   │   └── (renamed by sys_path_abandon — researcher can re-open at any time)
│   │
│   └── 04_random_forest/             # ── BRANCH PATH (parallel to abandoned 03) ──
│       ├── README.md / conclusions.md
│       ├── scripts/
│       │   ├── 04_random_forest_v1.py
│       │   ├── 04_random_forest_v2.py    # iterated after sub-task 3 failed
│       │   └── 04_random_forest_calibration_v1.py    # atomic sub-task
│       ├── literature/
│       │   ├── breiman2001rf.pdf
│       │   └── breiman2001rf.pdf.meta.yaml
│       ├── data/, outputs/, environment/
│
├── synthesis/                        # FINAL outputs (only created when you ask)
│   ├── paper.md                      # IMRAD with numbered figures, verified citations
│   ├── paper.tex                     # LaTeX with natbib + bibtex
│   ├── paper.pdf
│   ├── abstract.md                   # structured (journal) / unstructured (conference)
│   ├── poster.tex  /  poster.pdf     # tikzposter, audience-tailored
│   ├── dashboard.html                # single-file, sortable tables, light/dark
│   ├── references.bib                # BibTeX of every verified citation actually used
│   ├── figures/                      # numbered + copied (fig01_…, fig02_…)
│   ├── tables/                       # numbered + copied (tab01_…, tab02_…)
│   └── dashboard_figures/            # copies for offline dashboard
│
├── environment/                      # project-level baseline (per-step lives inside each step)
│   ├── requirements.txt
│   ├── Dockerfile                    # generated by sys_env_docker_generate
│   └── ...
│
└── .os_state/                        # internal — do not edit by hand
    ├── state_ledger.json             # primary state
    ├── state_ledger.yaml             # human-readable copy
    ├── manifest.json                 # workspace tree snapshot
    ├── os_state.md                   # human-readable status
    ├── protocol_execution_log.jsonl  # every protocol run
    ├── context_intake_log.jsonl
    ├── checkpoints/                  # hardlinked workspace snapshots
    ├── handoffs/                     # session handoff markdowns
    ├── cache/                        # API response cache
    └── tasks/                        # background subprocess registry
```

### Step naming — AI-derived, not hardcoded

**Nothing about the slug `baseline_eda` (or any other name) is special to
Research OS.** The AI picks every slug based on the goal of the step it's
about to create. The full rules live in the `guidance/analysis_plan`
protocol (the `create_step_folder` step) — short version:

* lowercase + underscores, ≤ 40 chars, descriptive
* mention the method when one is selected (`cox_ph_treatment_effect`, not generic `survival`)
* mention the sub-population if restricted (`logistic_under_65`)
* `NN_` prefix is auto-assigned by `sys_path_create` — don't pass it
* same goal, different parameters → bump `_v<n>` on the script
* different goal → new numbered step (different slug)

Plausible slugs the AI might pick (purely illustrative — different
projects look totally different):

```
01_baseline_eda           02_imputation_mice         03_cox_ph_full_cohort
01_distribution_scan      02_outlier_winsorise       03_ipw_treatment_effect
01_corpus_profile         02_bert_finetune_sentiment 03_attention_ablation
01_rna_seq_qc             02_deseq2_de               03_gsea_pathway
```

### How numbered steps grow over a session

*(Slugs below are made up to illustrate — your AI picks names from your
project's actual goals.)*

1. **AI creates the first step folder** via `sys_path_create name="<slug>"`,
   e.g. `name="baseline_eda"`. The server auto-prefixes `01_`. `data/input/`
   is symlinked to `inputs/raw_data/`.
2. **AI writes the main script** as `<NN>_<slug>_v1.<ext>` (atomic,
   single-purpose, RNG seeds set, library versions printed to stderr).
3. **Researcher pivots** ("group by quarter instead of month"). AI bumps
   to `<NN>_<slug>_v2.<ext>` (new version, not overwrite), re-runs,
   updates `conclusions.md`.
4. **AI creates the next step** with a slug describing its NEW goal. The
   server picks `02_`. Its `data/input/` symlinks to step 01's
   `data/output/`. Chain continues.
5. **A step fails** (e.g. assumption violated). AI calls
   `sys_path_abandon path_name="<NN>_<slug>" rationale="…"`. The folder
   is renamed `<NN>_<slug>__DEAD_END`. Files preserved. The
   `conclusions.md` gets a `## Why this path failed` section.
6. **AI creates an alternative step** — fresh slug describing the new
   approach. The server picks the next number. Its `data/input/` symlinks
   past the dead-end (to whichever earlier step produced its input).
   `tool_branch_recommendation` advises whether to branch or extend.
7. **Per-step literature** — AI downloads a canonical reference into the
   step's `literature/` with a `.meta.yaml` sidecar (instead of polluting
   project-wide `inputs/literature/`). Synthesis cites it correctly later.
8. **Scratch** — quick syntax checks live in `workspace/scratch/`
   (gitignored). Real work moves into a numbered step or gets deleted.

### Final outputs (synthesis is project-wide, not per-step)

`synthesis/` is built only when you ask ("write the paper" / "make a dashboard").
Per-step folders have `outputs/{reports,figures,tables}/` — **no dashboards**,
because dashboards are a project-level summary, not per-experiment.

### `.os_state/` is gitignored beyond the state ledger

`.gitignore` keeps `cache/`, `checkpoints/`, `handoffs/` out of git; the
ledger + manifest + protocol log are committed so collaborators can resume.

---

## Architecture (45 seconds)

```
AI IDE (Claude Code / OpenCode / Antigravity / Cursor / Claude / VS Code / Windsurf / Continue)
        │ MCP stdio
        ▼
research-os MCP server (Python)
        │
        ├── sys.*    workspace, state, paths, checkpoints, config, files, repair, env, scratch
        ├── tool.*   search, exec, audit, synthesis, tasks, research, intake, literature
        └── mem.*    append-only methods / analysis / citations / decisions / hypotheses
        │
        ▼
    Workspace files
    (immutable inputs · iterative workspace · final synthesis · gitignored .os_state)
```

The IDE plans and decides; Research OS executes and records. No autonomous
decisions in Research OS — your model stays in control.

---

## Documentation

| File | Read when |
|---|---|
| [`docs/QUICKSTART.md`](docs/QUICKSTART.md) | First time. 5-minute walkthrough. |
| [`docs/SETUP.md`](docs/SETUP.md) | Install + per-IDE MCP wiring + troubleshooting. |
| [`docs/SETUP_PROMPT.md`](docs/SETUP_PROMPT.md) | Paste-into-any-AI installer prompt (no project needed). |
| [`docs/RESEARCHER_GUIDE.md`](docs/RESEARCHER_GUIDE.md) | Non-technical walkthrough of the workflow. |
| [`docs/GUIDE.md`](docs/GUIDE.md) | Full technical reference: every tool + protocol + the pipeline. |
| [`docs/PROTOCOLS.md`](docs/PROTOCOLS.md) | Protocol catalog — when each fires, what it does, quality bars. |
| [`docs/TOOLS.md`](docs/TOOLS.md) | Tool catalog with example invocations. |
| [`docs/FAQ.md`](docs/FAQ.md) | Common questions. |
| [`templates/AGENTS.md`](templates/AGENTS.md) | The AI operating manual dropped into every workspace. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Adding tools, protocols, or fixing bugs. |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history. |

---

## What's in the box

* **~85 MCP tools** across `sys_*`, `tool_*`, `mem_*` namespaces. Dot
  notation (`sys.state.get`) and legacy names auto-rewrite. Run
  `python scripts/preflight.py` after install to verify everything is wired.
* **34 YAML protocols** — the AI loads the right one based on what you ask.
  Each declares an explicit `quality_bar` so output stays publication-grade
  even on smaller models.
* **5 domain presets** for `researcher_config.yaml`: RCTs, observational
  epidemiology, genomics, NLP benchmarks, economic panels.
* **8 IDE rule templates** auto-dropped on init.
* **Real, verified citations** — synthesis outputs cannot contain
  hallucinated references.
* **Per-step literature** — papers can be scoped to a specific experiment
  step with full metadata sidecars.
* **Workspace repair, scratch sandbox, mid-flow context intake, background
  tasks** — built-in robustness for shared servers and long-running work.

---

## Verify your install

```bash
python scripts/preflight.py
```

Runs ~11 checks in a few seconds (package imports, protocol loading,
tool/handler consistency, dispatcher aliases, workspace-scaffold smoke).
Exits non-zero on any failure with a clear detail dump.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues + PRs welcome at
<https://github.com/VibhavSetlur/Research-OS/issues>.
