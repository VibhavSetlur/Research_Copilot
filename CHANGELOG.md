# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-05-26

### Added
- **73 MCP tools** (up from 40+) across `sys.*`, `tool.*`, `mem.*`, and `view.*` categories.
- **66 protocol YAML files** (33 full + 33 light) with mandatory `protocol_completion` step and `next_protocol` routing.
- **Pipeline discovery** via `sys.protocol.next` with `PIPELINE_ORDER` — 10-stage recommended protocol sequence.
- **Protocol logging** via `sys.protocol.log` and `sys.protocol.history` — execution log in `.os_state/protocol_execution_log.jsonl`.
- **Synthesis planning** via `tool.synthesize.plan` — section-by-section status with plan-first workflow.
- **Workspace tree** via `sys.workspace.tree` with depth control; included in `sys.state.health`.
- **State summary** via `sys.state.summary_md` — `.os_state/os_state.md` auto-generated after every `save_state()`.
- **Config profile & explain** via `sys.config.profile` (<100 token behavioral profile) and `sys.config.explain` (key documentation).
- **Rich methods schema** for `mem.methods.append` — step_number, dataset_name, dataset_hash, implementation, parameters, justification, assumptions.
- **Task management** via `sys.task.create`, `sys.task.monitor`, `sys.task.kill` with PID-based tracking.
- **Turn structure** in `project_startup`, `synthesis_paper`, `domain_analysis` protocols — `steps_per_turn` and `approval_required_before` per autonomy level.
- **Model adaptations** — protocols have `small`/`medium`/`large` variants injected by `_handle_sys_guidance_get`.
- **3 new guidance protocols**: `glossary_update`, `hypothesis_tracking`, `dead_end_routing` (full + light).
- **CLI: `research-os pull <ide>`** — add IDE config (cursor/claude/opencode/vscode/antigravity) to existing workspace.
- **CLI: `research-os status --json`** — machine-readable JSON output with pipeline stage, experiments, key files.
- **CLI: `research-os status`** rewritten with pipeline progress bar, experiment path icons, next suggested action.
- **API key injection** — `api_keys` from `researcher_config.yaml` injected into `os.environ` at server start.
- **Manifest sync** — `.os_state/manifest.json` auto-synced with workspace directory structure on every path/file change.
- **Mermaid auto-update** — `_update_workflow_mermaid` called from `create_path`, `abandon_path`, `mem.analysis.log`.
- **Session handoff** rewritten to read real project state (paths, analysis tail, pending scripts).
- **Session boot protocol** (`guidance/session_boot`) with 7 mandatory steps including protocol history read.
- **`.os_state/os_state.md`** — human-readable project status snapshot with phase, active paths, key file health.
- **AGENTS.md** 8-section operating protocol with turn structure, synthesis workflow, protocol compliance table.
- **IDE rule templates** — `.cursor/rules/research-os.mdc`, `.claude/rules/research-os.md`, `.antigravity/rules/research-os.md`.
- **`project_startup.yaml` v2.0.0** — 11-step True North Star protocol with turn_structure and model_adaptations.
- **Protocol validation script** — `scripts/validate_protocols.py` validates all 66 YAML files for completeness.
- **Template system** — `templates/` with AGENTS.md, mcp_config.json, researcher_config.yaml, IDE rules.
- **Comprehensive tests** — 194 integration tests across all 10 phases.

### Changed
- **Tool count**: Expanded from ~44 to 73 tools.
- **Stub behavior**: Unknown tool calls now return `_error_envelope` instead of `_success_envelope` — no more silent failures.
- **`sys.state.health`**: Now returns `current_path`, `pipeline_stage`, `active_paths`, `pending_approval`, `handoff_reason`, `estimated_context_used_pct`, `next_suggested_action`, `workspace_tree`.
- **`sys.guidance.get`**: Injects `model_adaptations` based on `model_profile` from config.
- **Config template**: Uncommented active defaults for all behavioral fields; `api_keys` annotated with env injection note.
- **`init`**: Creates `docs/research_question.md` (single-file simplified template) instead of multiple doc files.
- **`init`**: Auto-runs `research-os doctor --quiet` at end.
- **Config keys**: `explain_config` now documents `api_keys.firecrawl` and `api_keys.semantic_scholar` with env injection info.
- **Documentation**: Updated README.md workspace tree, MCP tools reference (73 tools), architecture diagrams, guidance system protocol listing.

### Fixed
- **VSCode init crash** — `NameError` on bare `ide` variable (now uses `ide_flags` list).
- **Scaffold kwargs** — `_handle_sys_workspace_scaffold` passes correct args to `scaffold_minimal_workspace`.
- **`save_artifact`** — no longer calls non-existent `get_current_path` method.
- **`researcher_config.yaml`** — blank after init; now properly populated with answers via `init_config(overrides=)`.
- **`--name` flag** — ambiguous behavior resolved; tree print suppressed for large projects.
- **MCP doctor** — now actually tests server start via subprocess + `list_tools` (not just file existence).
- **Protocol inconsistencies** — all 62+ light/full protocols now have consistent name, description, schema_version fields.
- **Protocol descriptions** — truncated descriptions in 28+ files fixed.
- **Syntax error** — pre-existing invalid multiline f-strings in `project_ops.py` fixed.
- **Session handoff** — placeholder content replaced with real project state reading.
- **Stale references** — old `.research/` directory references, stale tool counts, contradictory documentation.

## [0.1.0] - 2026-05-23

### Added
- **MCP-native research OS**: Model Context Protocol server with 40+ tools for reproducible academic workflows.
- **20+ Guidance Protocols** organized into subdirectories (`guidance`, `domain`, `methodology`, `literature`, `writing`, `synthesis`, `visualization`, `audit`, `reproducibility`) with both full and `light` variants for every protocol.
- **Tool: `sys.guidance.validate`**: Dynamically verifies workspace state against protocol requirements.
- **Tool: `sys.state.minimal_context`**: Provides a ≤500-token summary tailored for small models.
- **Tool: `tool.synthesize`**: Gathers workspace findings and compiles `synthesis/paper.md`.
- **Execution Profiles**: `model_profile` in `researcher_config.yaml` governs tool verbosity and protocol depth.
- **Task Management**: `sys.task.create`, `sys.task.monitor`, `sys.task.kill` with PID-based tracking.
- **Template System**: `templates/` with `AGENTS.md`, `mcp_config.json`, `researcher_config.yaml`, Cursor rules.
- **Comprehensive Tests**: 100+ tests covering state, config, protocols, server, actions, and integration.

### Changed
- **Renamed to Research OS**: Removed all "Agentic" branding. Package name changed to `research-os`.
- **Version**: Reset from `9.0.0` to `0.1.0` to reflect true project maturity.
- **Documentation**: Rewrote README.md, fixed stale architecture diagrams, removed contradictory content.
- **Tool: `sys.file.write`**: Immutability guard rejects overwrites in `synthesis/` unless forced via `--force`.
- **Tool: `sys.file.read`**: Added 50MB file size limit to protect agent context windows.
- **Tool: `tool.python.exec`**: Parses `data_inventory.json` for safety, logs output/stderr to `workspace/logs/`.
- **Tool: `tool.search.web`**: Upgraded with `tenacity` exponential backoff and SerpAPI fallback.
- **Tool: `tool.search.semantic_scholar`**: Real API bindings, rate limiting, file-based caching.
- **Tool: `tool.latex.compile`**: Fixed `_project_root()` bug that would crash at runtime.
- **CLI**: Fixed stale directory paths (`.research/` → `.os_state/`, `00_inputs/` → `inputs/`).
- **State System**: Unified `.os_state/state_ledger.json` location across all components.
- **Templates**: AGENTS.md with 11 rules including lazy protocol loading and data inventory checks.

### Fixed
- Server `_project_root()` NameError in `tool.latex.compile` handler.
- Stale `.research/` directory references in CLI commands.
- Contradictory architecture documentation referencing non-existent tools.
- Duplicate documentation files in `docs/` root vs `docs/architecture/`.
- `safety.py` autonomous-agent remnants contradicting MCP-native philosophy.
- Fixed duplicate `workspace/` prefixes in fallback paths within `save_artifact`.
- Updated `_setup_mcp_configs` to accept an optional `ide` parameter.
- Removed legacy autonomous-agent pipeline phases (`method_route`, `execute_analysis`, etc.) from `registry.json`.
- Fixed broken Quickstart links in `README.md`.
