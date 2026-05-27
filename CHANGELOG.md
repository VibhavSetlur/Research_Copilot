# Changelog

All notable changes to Research OS are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) ·
versioning: [SemVer](https://semver.org).

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
