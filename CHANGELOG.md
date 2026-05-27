# Changelog

All notable changes to Research OS are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) ·
versioning: [SemVer](https://semver.org).

## [1.0.0] — Initial release

Research OS 1.0.0 is the first stable release. Headline features:

### Surface

* Two-command CLI: `research-os init` (scaffold a workspace) and
  `research-os start` (run the MCP server). No `doctor`, `pull`, `env`.
* **Research OS does NOT manage LLM providers.** Your AI client (Claude Code,
  OpenCode, Antigravity, Cursor, Claude, VS Code, Windsurf, Continue, Aider,
  ...) owns model access. The only credentials Research OS uses are for
  literature / web search providers, all optional.
* `inputs/researcher_config.yaml` is auto-created on init. Every field is
  optional — session_boot applies silent defaults.

### Tools (~75 MCP tools)

Grouped under three namespaces:

* `sys_*` — workspace, state, paths, checkpoints, config, files, env,
  notifications, session handoff, workspace repair, scratch sandbox.
* `tool_*` — search (Crossref / Semantic Scholar / PubMed / arXiv / web),
  literature download, multi-language execution (py / R / julia / bash /
  ipynb / Rmd / qmd), background tasks (real subprocess.Popen for shared
  servers), data sample / profile / convert, audits (synthesis, power,
  assumptions, figures, citations, reproducibility), research
  (research_method / research_tool / external_tool_instructions / plan_step /
  plan_next_step / branch_recommendation), intake autofill, mid-flow
  context injection, synthesis (paper / abstract / poster / dashboard / grant
  / report — all with verified citations), citation verification.
* `mem_*` — append-only methods / analysis / citations / decision / hypothesis
  ledgers (multi-hypothesis tracking).

Dot notation (`sys.state.get`) and legacy tool names auto-rewrite to the
underscore form.

### Protocols (34 YAML)

10-stage pipeline (`session_boot → project_startup → domain_analysis →
research_design → methodology_selection → literature_search → analysis_plan →
reproducibility → audit_and_validation → synthesis_paper`) plus on-demand
side protocols (iterative_planning, dead_end_routing, systematic_review,
methodology specialisations, writing helpers, visualization, all six
synthesis variants).

Every protocol:
* uses underscore tool names (dot form auto-rewritten),
* declares `expected_outputs`, `next_protocol`, `on_failure`,
* is shaped by `model_profile` (small / medium / large) at load time,
* ends with the auto-injected `protocol_completion` step (logs +
  checkpoints + routes).

The pipeline's `sys_protocol_next` consults BOTH the execution log AND
on-disk artifacts so migrated projects resume cleanly.

### Synthesis quality bars (no hallucinations)

* Every citation in every final output is pulled from real providers,
  verified online, and dropped if unverified.
* Per-output_type caps: abstract 3, poster 6, dashboard 12, report 25,
  paper 40. No literature-dump writing.
* `synthesis_paper` / `_abstract` / `_poster` / `_dashboard` / `_grant` /
  `_report` each have venue-tailored quality minimums (word counts,
  section structure, figure standards).
* `tool_citations_verify` re-verifies a workspace's bibliography on demand.

### Auto-intake from researcher dumps

Drop files into `inputs/raw_data` + `inputs/literature` + `inputs/context`,
say "fill out the intake" — `tool_intake_autofill` classifies the domain,
extracts the research question and hypotheses, rewrites `inputs/intake.md`,
populates the blank fields in `researcher_config.yaml`, registers each
inferred hypothesis in state.

### Reasoning + iteration

* `tool_research_method` deep-dives a method via 3-4 academic providers + web.
* `tool_research_tool` finds candidate libraries / CLIs / websites, tagged
  as installable / api / external / paid.
* `tool_external_tool_instructions` writes a WORKSHEET.md when the chosen
  tool isn't AI-executable.
* `tool_plan_step` forces non-trivial steps into atomic sub-tasks BEFORE coding.
* `tool_plan_next_step` + `guidance/iterative_planning` for "what's next?"
  workflows.
* `tool_branch_recommendation` for branch-vs-extend decisions.

### Robustness

* `tool_workspace_repair` heals missing dirs, corrupted state, stale
  paths — NEVER deletes.
* `tool_context_intake` routes mid-flow file drops into the right inputs/
  subfolder, never overwriting.
* `workspace/scratch/` AI sandbox with `tool_scratch_*` (write/run/list/clear).

### Runtime awareness

* `runtime.shared_server` + `runtime.long_running_threshold_seconds` in
  researcher_config: protocols background long jobs via `tool_task_run`
  (real `subprocess.Popen`), poll with `tool_task_status`, warn before
  heavy compute.

### Multi-language scripts

`.py`, `.R`, `.jl`, `.sh`, `.ipynb`, `.Rmd`, `.qmd` — first-class.

### Codebase organisation

`src/research_os/tools/actions/` is laid out in eight domain subfolders
(`state/`, `data/`, `exec/`, `search/`, `research/`, `audit/`, `synthesis/`,
`memory/`) with `protocol.py` at the top. Back-compat shim modules at the
old flat paths.

Tests live in `tests/{unit,integration,tools}/`.

### Docs

* `README.md` — 60-second pitch.
* `docs/GUIDE.md` — full tool + protocol reference.
* `docs/QUICKSTART.md` — 5-minute walkthrough.
* `docs/SETUP.md` — install + MCP wiring deep dive.
* `docs/RESEARCHER_GUIDE.md` — non-technical user guide.
* `docs/PROTOCOLS.md` — protocol catalog.
* `docs/TOOLS.md` — tool catalog with examples.
* `docs/FAQ.md` — frequently asked questions.
* `docs/SETUP_PROMPT.md` — paste-into-any-AI installer prompt.
