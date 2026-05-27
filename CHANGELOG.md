# Changelog

All notable changes to Research OS are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) ·
versioning: [SemVer](https://semver.org).

## [1.2.0] - 2026-05-27

### Removed
- `.env.example`, `Dockerfile`, `docker-compose.yml`. `research-os init`
  drops a fully-functioning MCP config for every supported IDE; nothing else
  is needed to start the server. researcher_config holds any optional keys.

### Added — reasoning + iteration
- `tool_plan_next_step` — surveys state + paths + hypotheses, pulls fresh
  literature on the open question, searches the web for relevant tools,
  proposes 2-3 prioritised next-step options, writes the plan markdown.
- `tool_branch_recommendation` — branch into a parallel experiment vs
  extend the current one; returns a guidance string.
- `guidance/iterative_planning` — new protocol for the "what's next?"
  workflow. Walks the AI through assess → propose → recommend → run.

### Added — scratch sandbox
- `workspace/scratch/` is auto-scaffolded and gitignored.
- `tool_scratch_write/_run/_list/_clear` — AI playground for syntax checks,
  smoke tests, parameter sweeps. Anything important moves OUT into a proper
  numbered experiment.

### Added — workspace healing
- `tool_workspace_repair` — detects missing dirs, corrupted state ledgers,
  stale path entries, broken symlinks; heals them and regenerates manifest +
  workflow.mermaid. NEVER deletes — corrupted ledgers are backed up before
  being reseeded.

### Added — mid-flow context injection
- `tool_context_intake` — researcher drops a new paper / dataset / note
  anywhere in the project; auto-routes each to the right `inputs/` subfolder
  (PDFs → literature, tabular → raw_data, prose → context), logs every move
  to `.os_state/context_intake_log.jsonl` + `analysis.md`, optionally re-runs
  `tool_intake_autofill` so the AI's view stays current. Never overwrites
  (conflicts get `_imported_N` suffix).

### Added — verified citations + condensed synthesis
- `src/research_os/tools/actions/synthesis/citations.py`:
  `collect_for_section` (pull k verified hits per section, dedupe by DOI),
  `verify_all_in_workspace` / `verify_citation_key` (re-verify online),
  `format_bib/_apa/_vancouver`, `write_references_bib`, `cap_for`.
- `tool_synthesize` rewritten: every output (`paper`, `poster`, `abstract`,
  `dashboard`, `report`) gets a citation cap (3 for abstracts, 6 posters,
  12 dashboards, 25 reports, 40 papers). Citations are pulled from real
  providers and dropped if unverified — no hallucinations leak through.
  Writes `synthesis/references.bib` alongside `paper.md`.
- `tool_citations_verify` exposes the verifier as a standalone audit.

### Changed — tools/actions/ layout
Reorganised into eight domain subfolders. Back-compat shim modules at the
old flat paths keep every existing import working.

```
tools/actions/
├── protocol.py                    # top-level — the loader
├── state/                         # config, path, checkpoint, interaction, scratch, repair
├── data/                          # data, profiling, intake, context_intake
├── exec/                          # scripts, notebook, tasks, environment
├── search/                        # search, literature
├── research/                      # research_*, planning
├── audit/                         # audit, md_audit
├── synthesis/                     # synthesize, latex, citations
└── memory/                        # hypotheses, decision/methods/citations logs
```

### Changed — tests layout
Three subfolders: `tests/unit/`, `tests/integration/`, `tests/tools/`. Added
`test_planning.py`, `test_scratch.py`, `test_repair.py`,
`test_context_intake.py`, `test_citations.py`, `test_reorganized_imports.py`.

### Changed — scaffold
`workspace/scratch/` is now part of `TOP_LEVEL_DIRS` and created on init
with its own `.gitignore` (contents ignored; folder + README tracked).

### Changed — AGENTS.md
Expanded to 18 rules including:
- explicit custom/novel methodology support (Rule 6),
- iterative planning (Rule 7),
- scratch sandbox (Rule 11),
- mid-flow context injection (Rule 12),
- workspace repair (Rule 13),
- verified citations + per-output_type caps (Rule 16).

### Changed — docs
README + GUIDE rewritten end-to-end. New "FAQ for power users" covers custom
analyses, branching, scratch, context injection, repair, iterative planning,
and hallucination-proof citations.

## [1.1.0] - 2026-05-27

### Removed
- All LLM provider key management (openai/anthropic). Research OS does not
  call any model — your IDE owns LLM access. `_inject_api_keys` now only
  exports literature / search credentials (Semantic Scholar, PubMed,
  Crossref, Firecrawl, SerpAPI).

### Added — reasoning + research
- `tool_research_method` — deep-dives a method by hitting 3-4 academic
  providers + web, dedupes by DOI, writes a structured report into the
  current step's `outputs/reports/`.
- `tool_research_tool` — finds candidate libraries / CLIs / websites for a
  task and tags each as `installable_via_package_manager` |
  `api_available` | `external_tool` | `paid_or_licensed`.
- `tool_external_tool_instructions` — when the chosen tool is external,
  writes a `WORKSHEET.md` telling the researcher exactly what to do
  (open URL X, upload Y, drop output back into `data/output/`).
- `tool_plan_step` — forces complex steps to be broken into atomic
  sub-tasks BEFORE coding; writes a plan markdown the AI executes piecewise.

### Added — intake autofill
- `tool_intake_autofill` — reads inputs/raw_data + inputs/literature +
  inputs/context, classifies domain, extracts research question + H1/H2/H3
  from context notes, fills BLANK fields in `researcher_config.yaml`,
  registers hypotheses in state, rewrites `inputs/intake.md` and
  `docs/research_question.md`.

### Added — real background tasks
- `tool_task_run` (real `subprocess.Popen`, returns task_id immediately),
  `tool_task_status` (tail of log + live PID check),
  `tool_task_list`, `tool_task_kill`. Designed for shared-server / HPC
  workflows. Replaces the previous fake `task.py`.

### Added — multi-language scripts
- `tool_notebook_exec` — `jupyter nbconvert --execute --inplace` for .ipynb.
- `tool_rmarkdown_render` — `rmarkdown::render` (.Rmd) or `quarto render` (.qmd).
- Documented in AGENTS.md + analysis_plan: every script naming convention
  applies across .py / .R / .jl / .sh / .ipynb / .Rmd / .qmd.

### Added — multi-hypothesis tracking
- `mem_hypothesis_add`, `mem_hypothesis_update`, `mem_hypothesis_list` —
  track multiple hypotheses across experiment steps with status (testing |
  supported | refuted | inconclusive) and evidence-with-step references.

### Added — config defaults
- `runtime.shared_server`, `runtime.long_running_threshold_seconds`,
  `runtime.default_n_for_sampling` — used by session_boot and analysis_plan.
- `hypotheses: []` top-level field — list of free-form hypotheses, auto-
  registered into state by intake autofill.
- Every researcher_config field is now optional. session_boot applies
  silent defaults so researchers can dump files and just say
  "fill out the intake".

### Changed — init flow
- Scaffold no longer pre-creates `synthesis/paper.md`, `synthesis/abstract.md`,
  `docs/research_overview.md`, or any other output. Protocols own their
  outputs and write them only when they actually run.
- `docs/research_question.md` is a one-line placeholder; intake autofill
  rewrites it once it has real material.

### Changed — protocols
- `guidance/session_boot` v5: blank-field defaults; runtime awareness; routing
  override when the researcher has a specific ask.
- `guidance/project_startup` v5: mandatory `tool_intake_autofill` step before
  any coding.
- `guidance/analysis_plan` v5: enforces literature grounding BEFORE method
  choice; forbids one-shot mega-scripts; mandates `tool_plan_step` when scope
  is non-trivial; documents all 7 script-language tools; backgrounds long
  jobs on shared servers.
- `methodology/methodology_selection` v5: mandatory `tool_research_method`
  for each candidate; mandatory `tool_research_tool` for library choice.
- `AGENTS.md` rewritten with explicit runtime / reasoning / autonomy gates.

### Changed — tools/actions/ layout
- `web_search.py` + `literature_retrieval.py` collapsed into one
  `search.py` (back-compat shims kept). All providers now share a single
  cache + error-log path.

### Fixed
- `_resolve_root(root)` no longer ignored its `root` argument.
- `get_next_protocol` now considers the protocol execution log AS WELL as
  on-disk artifacts so projects migrated from outside Research OS resume
  cleanly.
- Audit-stub `_log_search` and other helpers can be called even when
  `.os_state/` doesn't exist (gracefully no-op).

### Tests
- `test_research.py`, `test_tasks.py`, `test_intake.py`, `test_hypotheses.py`,
  `test_notebook.py`, `test_pipeline.py`, `test_all_protocols_load.py`
  cover every new tool + pipeline walk.

## [1.0.0] - 2026-05-27

### Highlights
End-to-end overhaul. The CLI surface is two commands. Protocols are one
source-of-truth file each. The tool dispatcher accepts both underscore and
dot notation. The pipeline actually flows from session_boot through synthesis
without dead ends.

### Added
- `tool_data_profile` — schema, missingness, descriptive stats, suggested next steps.
- `tool_audit_citations` — verify every citation in workspace/citations.md against Crossref.
- `tool_audit_reproducibility` — re-run every script and hash-compare outputs.
- `tool_dashboard_create` — single-file HTML dashboard summarising all experiments.
- `tool_search_arxiv` — arXiv API (no key required).
- `mem_decision_log` — structured decision append to analysis.md.
- `sys_file_validate_md` — markdown linter against a writing protocol.
- API-key aliases — `SEMANTIC_SCHOLAR_API_KEY` / `S2_API_KEY`, `FIRECRAWL_API_KEY`,
  `SERPAPI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` all auto-injected from
  `inputs/researcher_config.yaml`.

### Changed
- **Dispatcher**: tool names now accept dot notation (`sys.state.get`) and
  legacy aliases (`sys_guidance_get` → `sys_protocol_get`).
- **Single state schema** — `default_state` and `_default_state` reconciled.
- **Single experiment-creation path** — `sys_path_create` delegates to
  `project_ops.create_numbered_experiment` so state is always updated.
- **Single checkpoint system** — hardlinked snapshots via `ResearchLedger`.
- **CLI** — only `init` and `start`. Removed `doctor`, `pull`, `env`, `status`.
- **Protocols** — 33 files (down from 66). Light mode is derived in-process
  by trimming verbose keys; no separate `light/` folder.
- **`PIPELINE`** in `protocol.py` now uses predicate functions instead of
  brittle hardcoded file lists.
- **`protocol_completion`** step injected by the loader — no longer copy-pasted
  into 30 protocols.
- **Researcher config path** — server now reads `inputs/researcher_config.yaml`
  (was reading the wrong root-level path).
- **Search & scrape** — Firecrawl + SerpAPI fallback no longer crashes on
  missing `urllib.parse` import.
- **`docs/GUIDE.md`** rewritten; complete tool table, pipeline table,
  natural-language workflow, troubleshooting.
- **`templates/AGENTS.md`** rewritten as the single source of truth for AI
  behaviour. IDE rule files are tiny shims that defer to it.
- **`templates/researcher_config.yaml`** restructured around what actually
  drives behaviour (autonomy, model_profile, output_types, citation style).
- **Domain templates** (`templates/configs/*.yaml`) — meaningful per-domain
  hints (expected columns, biases to monitor, reporting standards).

### Fixed
- 275 broken dot-notation tool calls across protocols (e.g. `sys_file.read`)
  now resolve.
- Pipeline no longer dead-ends: `project_startup` → `domain_analysis` →
  `research_design` → `methodology_selection` → `literature_search` →
  `analysis_plan` → `reproducibility` → `audit_and_validation` →
  `synthesis_paper`.
- `tool_data_sample` no longer crashes on missing `n_rows` in the handler.
- `audit_*` tools return real diagnostics instead of hardcoded "passed".
- `task.py` (fake background tasks), `scrape.py` (dead), `external_mcp.py`
  (vestigial), `capability_registry.py` and `models.py` (unused) — removed.
- `state/__init__.py` now exports `ResearchLedger` so
  `from research_os.state import ResearchLedger` works.

### Removed
- CLI: `doctor`, `pull`, `env`, `status`.
- Protocol `light/` folder.
- Tools: `view_workspace_tree`, `tool_env_freeze` (deprecated alias),
  `sys_external_mcp_discover`, `sys_tool_info`, `sys_tool_search`,
  `sys_task_create/monitor/kill`, `sys_state_summary{,_md,_health,_minimal_context}`
  (all collapsed into `sys_state_get` with a `format` argument).
- Misc dead modules (`models.py`, `capability_registry.py`, `scrape.py`,
  `checkpoint_manager.py`).

## [0.1.0] - 2026-05-23

Initial MCP-native release.
