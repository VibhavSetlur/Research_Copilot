# Research OS — Guide

Research OS is an MCP server. The AI in your IDE plans and reasons;
Research OS executes, records state, enforces immutability, walks the AI
through the right protocol for the current pipeline stage.

> Research OS does NOT manage LLM provider keys. Your IDE owns model access.
> The credentials Research OS uses (Crossref / Semantic Scholar / PubMed /
> Firecrawl / SerpAPI) are for literature + web search only, all optional.

---

## 1. Install

```bash
pip install "research-os[all] @ git+https://github.com/VibhavSetlur/Research-OS.git"
```

Optional extras: `web`, `literature`, `viz`, `execution`, `r`, `julia`,
`audit`, `poster`, `ml`. The `all` extra is the easy default.

## 2. Scaffold

```bash
mkdir my-project && cd my-project
research-os init                                # uses cwd name
# or:
research-os init my-project --name "PM2.5 Study"
```

`init` drops:

* `AGENTS.md` — the AI operating manual.
* `inputs/researcher_config.yaml` — source of truth for behaviour (every
  field is optional).
* `.os_state/` + state ledger.
* `.cursor/`, `.claude/`, `.antigravity/`, `.vscode/`, `opencode.json` —
  pre-wired MCP configs for each IDE.

Drop your data into `inputs/raw_data/`, papers into `inputs/literature/`,
notes / drafts into `inputs/context/`. Open your IDE on the project. Say:

> "fill out the intake" → AI reads everything, fills `intake.md`, infers
>  question + domain + hypotheses, populates blank config fields.

> "start the project" / "run a baseline" → AI walks the pipeline.

> "what should I do next?" → iterative planning: literature + tool search +
>  2-3 concrete options + recommendation.

## 3. Start the server

```bash
research-os start --workspace .
```

The MCP configs dropped by `init` already point to this command, so most IDEs
auto-launch it. You rarely run `start` manually.

---

## 4. The pipeline (10 stages)

`sys_protocol_next` returns the first stage whose outputs (and execution log)
say "not done yet".

| # | Protocol                              | Done when... |
|---|---------------------------------------|---|
| 1 | `guidance/session_boot`               | first protocol logged in `protocol_execution_log.jsonl` |
| 2 | `guidance/project_startup`            | `intake.md` filled + research question confirmed |
| 3 | `domain/domain_analysis`              | `docs/domain_summary.md` exists |
| 4 | `domain/research_design`              | `docs/research_design.md` exists |
| 5 | `methodology/methodology_selection`   | `workspace/methods.md` substantive |
| 6 | `literature/literature_search`        | `inputs/literature_index.yaml` + `citations.md` exist |
| 7 | `guidance/analysis_plan`              | at least one `workspace/NN/conclusions.md` is non-empty |
| 8 | `reproducibility/reproducibility`     | `workspace/*/environment/requirements.txt` exists |
| 9 | `audit/audit_and_validation`          | `workspace/logs/audit_report.md` exists |
| 10| `synthesis/synthesis_paper`           | `synthesis/paper.md` exists |

### Side / on-demand protocols

* `guidance/iterative_planning` — for "what's next?" style work.
* `guidance/dead_end_routing` — abandon a failed path cleanly.
* `guidance/hypothesis_tracking` — register / update hypotheses.
* `guidance/glossary_update` / `guidance/writing_standards`.
* `methodology/{clinical_trials,machine_learning,meta_analysis,causal_inference_deep,survey_psychometrics,research_methods,tool_discovery}`.
* `literature/{systematic_review,evidence_synthesis}`.
* `synthesis/{synthesis_abstract,synthesis_poster,synthesis_dashboard}`.
* `writing/{writing_core,writing_methods,writing_citations,writing_conclusions,writing_analysis_log,writing_readme}`.
* `visualization/figure_guidelines`.

---

## 5. MCP tools (~75)

> All names use underscores. Dot notation + legacy names are auto-rewritten.

### `sys_*` — workspace, state, files, paths, checkpoints, repair

| Tool | Purpose |
|---|---|
| `sys_protocol_get/_list/_next/_validate/_log/_history` | Protocol discovery + execution log. |
| `sys_state_get`        | Full / minimal / markdown state. |
| `sys_workspace_scaffold/_tree` | Re-create / inspect the workspace tree. |
| `sys_file_read/_write/_list/_delete/_validate_md` | File I/O (writes blocked in `inputs/raw_data` + `inputs/literature`). |
| `sys_path_create/_abandon/_list` | Numbered experiment folders. |
| `sys_checkpoint_create/_rollback/_list` | Hardlinked workspace snapshots. |
| `sys_config_get/_set/_validate` | researcher_config.yaml. |
| `sys_notify`           | Append to `workspace/logs/notifications.log`. |
| `sys_session_handoff`  | Markdown handoff + resume prompt. |
| `sys_env_snapshot/_docker_generate` | Capture + containerise the env. |

### `tool_*` — search, exec, audit, synthesis, research, intake, scratch, tasks, repair

| Tool | Purpose |
|---|---|
| `tool_search_semantic_scholar/_pubmed/_crossref/_arxiv/_web` | Literature + web search. |
| `tool_web_scrape` / `tool_literature_download` | Scrape a URL / save a PDF into `inputs/literature/`. |
| `tool_python_exec` / `tool_r_exec` / `tool_julia_exec` / `tool_bash_exec` / `tool_notebook_exec` / `tool_rmarkdown_render` | Run scripts / notebooks. |
| `tool_package_install` | `pip install` + update requirements. |
| `tool_data_sample` / `tool_data_profile` / `tool_data_convert` | Sample, profile, convert tabular data. |
| `tool_audit_synthesis/_power/_assumptions/_figure/_citations/_reproducibility` | Real audits — citation lookups, statistical power, assumption tests, figure DPI, full re-runs. |
| `tool_synthesize_plan` / `tool_synthesize` | Plan section order; build paper / abstract / etc. with verified citations. |
| `tool_latex_compile` / `tool_poster_create` / `tool_dashboard_create` | PDF + tikzposter + single-file HTML dashboard. |
| `tool_research_method` / `tool_research_tool` / `tool_external_tool_instructions` / `tool_plan_step` | Reasoning helpers. |
| `tool_plan_next_step` / `tool_branch_recommendation` | Iterative planning. |
| `tool_intake_autofill` / `tool_context_intake` | Auto-fill + mid-flow context injection. |
| `tool_task_run/_status/_list/_kill` | Real background subprocesses for shared servers. |
| `tool_scratch_write/_run/_list/_clear` | Workspace sandbox. |
| `tool_workspace_repair` | Heal a broken workspace; never deletes. |
| `tool_citations_verify` | Re-verify every citation_key in `workspace/citations.md` online. |

### `mem_*` — append-only logs, decisions, hypotheses

| Tool | Purpose |
|---|---|
| `mem_analysis_log` / `mem_methods_append` / `mem_citations_generate` / `mem_intake_regenerate` / `mem_decision_log` | Append to the canonical workspace logs. |
| `mem_hypothesis_add/_update/_list` | Multi-hypothesis ledger. |

---

## 6. Codebase layout

After v1.2.0 the action modules live in eight subfolders, grouped by domain:

```
src/research_os/
├── server.py                         # MCP server + dispatcher
├── cli.py                            # `init` + `start`
├── project_ops.py                    # scaffolding, state, mermaid, intake regen
├── config.py / errors.py / __init__.py
├── protocols/                        # 34 YAML protocols
├── state/                            # ResearchLedger
├── utils/                            # asset manager, common helpers
└── tools/
    ├── capability_registry.py
    └── actions/
        ├── protocol.py               # the loader (top-level — fundamental)
        ├── state/                    # config, path, checkpoint, interaction,
        │                             # scratch, repair
        ├── data/                     # data, profiling, intake, context_intake
        ├── exec/                     # scripts, notebook, tasks, environment
        ├── search/                   # search providers, literature download
        ├── research/                 # research_method/tool/plan, planning
        ├── audit/                    # audit, md_audit
        ├── synthesis/                # synthesize, latex, citations
        └── memory/                   # hypotheses, append-only helpers
```

Back-compat shim modules (`tools/actions/config.py`, `data.py`, …) re-export
from the subfolders so any older import paths keep working.

---

## 7. Tests

```
tests/
├── conftest.py                       # isolates each test on tmp_path
├── unit/                             # pure-function tests, fast
├── integration/                      # workspace + pipeline + reorganization-aware
└── tools/                            # one file per new MCP tool group
```

Run all:
```bash
pytest -q
```

Run a slice:
```bash
pytest tests/unit -q
pytest tests/integration -q
pytest tests/tools/test_planning.py -q
```

---

## 8. Configuration

`inputs/researcher_config.yaml` is auto-created on `init`. Every field is
optional. Set only what you care about — the rest gets sensible defaults
applied silently by `session_boot`.

```yaml
project_name: ""                  # blank → uses directory name
research_question: ""             # blank → tool_intake_autofill proposes
domain: ""                        # blank → AI classifies from inputs
hypotheses: []                    # AI tracks via mem_hypothesis_*

researcher:
  name: ""
  field: ""
  expertise_level: ""             # beginner | intermediate | advanced | pi

interaction:
  autonomy_level: "supervised"    # manual | supervised | autopilot

model_profile: "medium"           # small | medium | large

runtime:
  shared_server: false
  long_running_threshold_seconds: 60
  default_n_for_sampling: 1000

research_goal:
  output_types: []                # paper | abstract | poster | dashboard | report | exploratory
  target_venue: ""
  reporting_standard: ""
  poster_dimensions: "36x48"

writing_preferences:
  citation_style: "apa"
  language: "en-US"

api_keys:                         # all optional — NO LLM provider keys
  semantic_scholar: ""
  pubmed: ""
  crossref: ""
  firecrawl: ""
  serpapi: ""
```

### Domain presets

Copy any of these into `inputs/researcher_config.yaml`:

* `templates/configs/rct_config.yaml` — RCT (CONSORT).
* `templates/configs/epidemiology_observational.yaml` — STROBE.
* `templates/configs/genomics.yaml` — MINSEQE / MIAME.
* `templates/configs/nlp_benchmark.yaml` — Model Cards.
* `templates/configs/economic_panel.yaml` — AEA.

---

## 9. FAQ for power users

**Custom / novel methodology** — Skip `tool_research_tool` (or run it just
to confirm no library fits). Run `tool_research_method` for published
precedent. Document with `mem_methods_append implementation="custom"` and
`mem_decision_log` explaining why off-the-shelf was inadequate. Prototype
in `workspace/scratch/`.

**Branching** — When an alternative methodology deserves its own thread,
create a parallel numbered path. Use `tool_branch_recommendation` if
uncertain whether to branch or extend.

**Multiple hypotheses** — `mem_hypothesis_add` for each; every experiment
step declares which hypothesis IDs it touches via `mem_hypothesis_update`.

**Mid-flow context** — Researcher dropped a new paper / dataset?
`tool_context_intake also_autofill=true` routes the file and re-runs intake.

**Workspace looks broken** — `tool_workspace_repair`. Heals missing
directories, regenerates manifest + mermaid, backs up corrupted state
ledgers. Never deletes.

**Long-running jobs** — `tool_task_run` for real background subprocesses;
poll with `tool_task_status`. Especially important on shared HPC.

**Iterative ("what's next?") workflow** — Load `guidance/iterative_planning`
or call `tool_plan_next_step` for a single-turn recommendation.

**Hallucinated citations** — Cannot happen for synthesis outputs.
`tool_synthesize` pulls every citation from Crossref / Semantic Scholar /
PubMed / arXiv and drops anything unverified. Confirm with
`tool_citations_verify`.

---

## 10. Migrating an existing project into Research OS

```bash
cd my-existing-project
research-os init . --force                  # safe — keeps your existing files
mv my_data*.csv inputs/raw_data/
mv references/*.pdf inputs/literature/
research-os start --workspace .
```

In your IDE:

> "I have an existing project — fill out the intake, then propose how to continue."

`tool_intake_autofill` reads everything, classifies, proposes, and the
pipeline picks up from whichever stage already has outputs on disk.

---

## 11. Troubleshooting

| Problem | Fix |
|---|---|
| `research-os: command not found` | Add `~/.local/bin` to `PATH`. |
| `Not a Research OS workspace` | `research-os init .` or pass `--workspace`. |
| `WriteProtectedError` | You tried to write into `inputs/raw_data/` or `inputs/literature/`. Write to `workspace/` instead. |
| `Protocol not found` | `sys_protocol_list`. |
| Tools missing in IDE | Restart IDE; check its MCP panel for stderr. |
| `No web-search provider configured` | Set `firecrawl` or `serpapi` in researcher_config. |
| Mermaid PNG not rendering | `npm install -g @mermaid-js/mermaid-cli`. |
| `pdflatex not found` | Install TeX Live for PDF compile. |
| `tool_audit_reproducibility` slow | It re-runs every script. Skip in autopilot unless explicitly asked. |
| State / dir looks broken | `tool_workspace_repair`. |
