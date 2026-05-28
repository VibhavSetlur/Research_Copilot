# Changelog

All notable changes to Research OS are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) ·
versioning: [SemVer](https://semver.org).

## [1.0.0] — Stable release

### Operational safety + ergonomics (post-routing finalization)

* **`tool_route` returns `active_tools`** — a tight 10-15 tool shortlist
  (essentials + the chosen protocol's decomposition tools) so the AI
  focuses its working set instead of triaging all 98 tools every turn.
  `sys_active_tools(protocol_name)` queries the same scope directly.
* **`tool_workflow_dag`** — walks each numbered step's `data/input`
  symlink, derives cross-step dependencies, writes
  `docs/workflow_dag.mermaid` (+ PNG via `mmdc` if available).
  Auto-refreshed on every `sys_path_create` / `sys_path_abandon`.
* **`tool_step_env_lock`** — pins `requirements.txt` +
  `python_version.txt` (+ optional `conda.yaml` + per-step `Dockerfile`)
  inside `workspace/<NN>/environment/`. Each step becomes
  self-contained and reproducible years later even if the global env
  drifts.
* **`tool_task_run` security** — argv[0] validated against
  `runtime.command_allowlist` (default = common interpreters + benign
  coreutils; bypass with `runtime.allow_arbitrary`); shell
  metacharacters refused unless `runtime.allow_shell_meta`; per-task
  CPU / RSS / file-size limits via `setrlimit`; every accepted task
  audited to `workspace/logs/task_audit.log`.
* **Search caching with TTL + 429 backoff** — file cache moved to
  `.os_state/cache/search/<provider>/<hash>.json` with timestamped
  envelopes; 24h default TTL (`runtime.cache_ttl_seconds` to override).
  All literature providers now use a shared `_fetch_json_with_backoff`
  helper that retries on 429 / 5xx and honours `Retry-After`.
  `tool_cache_clear` wipes per-provider or older-than-N-days.
* **Preflight protocol freshness check** — warns when a protocol
  hasn't been touched in 180+ days (uses explicit `last_reviewed` field
  or git mtime). Surfaces the 47-protocol maintenance burden early.

### Routing layer (token-efficient + anti-one-shot)

* **`sys_boot`** — one MCP call returns project state + researcher
  config + protocol history tail + dep inventory + recommended next
  protocol + pause classification + any active plan. Replaces 4-5
  separate calls per session boot; cuts a typical boot from ~5K tokens
  to ~1K.
* **`tool_route(prompt)`** — hierarchical L1 → L2 → L3 picker.
  L1 = `intent_class` (session / discover / plan / execute /
  methodology / literature / synthesize / audit_wrap / memory / review).
  L2 = `sub_intent` within class. L3 = specific protocol. Returns
  ambiguity-aware: if two L3 candidates tie, returns `resolved_level=2`
  + an `ask_user` line for the AI to disambiguate with one researcher
  follow-up.
* **`tool_plan_turn`** — slices the active plan into a `this_turn`
  batch + `next_turn` queue, sized to the researcher's `model_profile`
  (small: 1 step/turn, medium: 3, large: 6, weighted for heavy tools
  like `tool_synthesize` or `tool_audit_reproducibility`). Returns
  `chat_split_recommended` when the remaining plan exceeds what one
  chat should hold; AI then hands off + asks for a fresh chat.
* **`tool_plan_advance` / `tool_plan_clear`** — walk or discard the
  persistent active plan written to `.os_state/active_plan.json`.
* **`sys_tool_describe`** — full description of one tool on demand
  (paired with trimmed `list_tools` defaults, saving ~2K tokens
  permanently per message).
* **`sys_dep_inventory`** — reports which optional extras failed to
  import so the AI knows which tools will work this session.
* **`sys_protocol_get`** now supports `format='summary'` (~300 tokens,
  step headings only), `format='step' step_id='<id>'` (one step body),
  or `format='full'` (whole YAML, ~2-3K tokens).
* **`_router_index.yaml`** — single source of truth for trigger
  phrases, decompositions, intent classes, and sub-intents. Preflight
  validates every entry resolves.

### Resume / handoff / progress / quick review

* **`tool_session_resume`** — reconstructs intent + status after any
  pause (different chat, different AI model, next day) in one call.
* **`tool_progress_digest`** — one-page summary of experiments,
  hypotheses, outputs, citations.
* **`tool_dead_end_lessons`** — pulls reusable lessons from every
  `__DEAD_END` folder so future steps don't repeat past mistakes.
* **`tool_quick_review`** — stages the critical-appraisal skeleton for
  reviewing someone else's paper (orthogonal to the main project).
* **`sys_session_handoff`** now snapshots a checkpoint, captures
  running background tasks + open hypotheses + methods tail + dead-end
  lessons + a "Notes for the next AI" addendum. Fresh AI can pick up
  with just the handoff + AGENTS.md.

### Protocols (47 total)

10-stage main pipeline (`session_boot → project_startup →
domain_analysis → research_design → methodology_selection →
literature_search → analysis_plan → reproducibility →
audit_and_validation → synthesis_paper`) plus 37 on-demand protocols:

* **Guidance**: session_boot, session_resume, project_startup,
  analysis_plan, iterative_planning, dead_end_routing,
  hypothesis_tracking, writing_standards, glossary_update,
  casual_exploration, autopilot, chat_handoff, quick_paper_review.
* **Domain**: domain_analysis, research_design.
* **Methodology**: methodology_selection, research_methods,
  causal_inference_deep, machine_learning, clinical_trials,
  meta_analysis, survey_psychometrics, qualitative_research,
  simulation_studies, replication_study, ablation_study, pilot_study,
  mixed_methods, tool_discovery.
* **Literature**: literature_search, systematic_review,
  evidence_synthesis.
* **Synthesis**: synthesis_paper, synthesis_abstract, synthesis_poster,
  synthesis_dashboard, synthesis_grant, synthesis_report.
* **Writing**: writing_core, writing_methods, writing_citations,
  writing_analysis_log, writing_conclusions, writing_readme.
* **Visualization**: figure_guidelines.
* **Audit + reproducibility**: audit_and_validation, reproducibility.

Every protocol declares `quality_bar`, `expected_outputs`,
`next_protocol`, `on_failure`; ends with the auto-injected
`protocol_completion` step (logs + checkpoints + routes). All have
matching entries in `_router_index.yaml` for hierarchical routing.

### Domain presets (10)

`rct_config`, `epidemiology_observational`, `genomics`, `nlp_benchmark`,
`economic_panel`, `qualitative_research`, `geospatial`, `time_series`,
`survival_analysis`, `psychometric`. Each defines expected columns,
expected file extensions, biases to monitor, suggested protocols, and
reporting standard.

### Tools (94 total)

Three namespaces:

* `sys_*` — workspace, state, paths, checkpoints, config, files, env,
  notifications, session handoff, scratch sandbox, workspace repair,
  boot, dep inventory, tool describe.
* `tool_*` — routing (route, plan_turn, plan_advance, plan_clear),
  search (Crossref / Semantic Scholar / PubMed / arXiv / web),
  literature download, multi-language execution (py / R / julia / bash
  / ipynb / Rmd / qmd), background tasks (real `subprocess.Popen` for
  shared servers), data sample / profile / convert, audits, research
  grounding, intake autofill, mid-flow context injection, synthesis
  (paper / abstract / poster / dashboard / grant / report), citation
  verification, session resume, progress digest, dead-end lessons,
  quick review.
* `mem_*` — append-only methods / analysis / citations / decision /
  hypothesis ledgers (multi-hypothesis tracking).

Dot notation (`sys.state.get`) and legacy tool names auto-rewrite.

### Synthesis quality bars (no hallucinations)

* Every citation in every final output is pulled from real providers,
  verified online, and dropped if unverified.
* Per-output_type caps: abstract 3, poster 6, dashboard 12, report 25,
  paper 40.
* `synthesis_paper` / `_abstract` / `_poster` / `_dashboard` / `_grant` /
  `_report` each have venue-tailored quality minimums.
* `tool_citations_verify` re-verifies a workspace's bibliography on
  demand.

### Auto-intake + mid-flow context

* `tool_intake_autofill` classifies domain, extracts research question
  + hypotheses, rewrites `inputs/intake.md`, fills blank config fields,
  registers hypotheses.
* `tool_context_intake` routes mid-flow file drops into the right
  `inputs/` subfolder; skips scaffold files (AGENTS.md, CLAUDE.md,
  opencode.json, etc.) to avoid noise.

### Robustness

* `tool_workspace_repair` heals missing dirs / corrupted state —
  NEVER deletes.
* Background tasks survive zombies via `waitpid(WNOHANG)` +
  `/proc/<pid>/status` fallback.
* `execute_bash_script` / `_r` / `_julia` propagate non-zero exit
  codes (previously claimed success on every completed run).
* `scratch_list` excludes `.gitkeep` (previously over-counted).
* Scaffold prunes stale `.gitkeep` after populating dirs.

### Runtime awareness

* `runtime.shared_server` + `runtime.long_running_threshold_seconds`
  in `researcher_config`: protocols background long jobs via
  `tool_task_run`, poll with `tool_task_status`, warn before heavy
  compute.

### Multi-language scripts

`.py`, `.R`, `.jl`, `.sh`, `.ipynb`, `.Rmd`, `.qmd` — first-class.

### Codebase organisation

`src/research_os/tools/actions/` has eight domain subpackages
(`state/`, `data/`, `exec/`, `search/`, `research/`, `audit/`,
`synthesis/`, `memory/`) plus two cross-cutting modules flat at the
top (`protocol.py` — YAML loader; `router.py` — sys_boot + tool_route
+ plan_turn + active plan).

Tests live in `tests/{unit,integration,tools}/` — ~180 tests, ~3s
to run. Preflight at `scripts/preflight.py` runs 12 wiring checks
in ~2s.

### CI

GitHub Actions workflow runs ruff + preflight + unit tests on Python
3.11 (fast path), then integration + tools tests on Python 3.10 /
3.11 / 3.12. Lean `[ci]` extras keep installs fast; the build job
validates the wheel ships all 47 protocols + the router index.

### Docs

* `README.md` — 60-second pitch + cheat sheet.
* `docs/WALKTHROUGH.md` — exhaustive 10-day simulated project with
  messy/ranting researcher prompts, every protocol exercised.
* `docs/GUIDE.md` — full reference: routing, tools, protocols.
* `docs/QUICKSTART.md` — 5-minute walkthrough.
* `docs/SETUP.md` — install + per-IDE MCP wiring.
* `docs/RESEARCHER_GUIDE.md` — non-technical user guide.
* `docs/PROTOCOLS.md` — protocol catalog with trigger phrases.
* `docs/TOOLS.md` — tool catalog with example invocations.
* `docs/FAQ.md` — common questions.
* `docs/SETUP_PROMPT.md` — paste-into-any-AI installer prompt.
