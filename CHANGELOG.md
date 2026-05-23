# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-23

### Added
- **MCP-native research OS**: Model Context Protocol server with 40+ tools for reproducible academic workflows.
- **10 Guidance Protocols**: `domain_analysis`, `research_design`, `methodology_selection`, `literature_search`, `evidence_synthesis`, `analysis_plan`, `figure_guidelines`, `writing_standards`, `reproducibility`, `audit_and_validation` with both full and `light` variants.
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
