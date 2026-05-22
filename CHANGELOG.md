# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Protocols (v2.0.0)**: Upgraded 10 protocols (`domain_analysis`, `research_design`, `methodology_selection`, `literature_search`, `evidence_synthesis`, `analysis_plan`, `figure_guidelines`, `writing_standards`, `reproducibility`, `audit_and_validation`). All protocols now explicitly list expected outputs and are dynamically verifiable.
- **Protocols (`light` variants)**: Added `protocols/light/` versions for `small` LLM profiles to save token space.
- **Tool: `sys.guidance.validate`**: Dynamically verifies the current workspace state against protocol requirements.
- **Tool: `sys.state.minimal_context`**: Provides a ≤500-token summary tailored for small models.
- **Execution Profiles**: Added `model_profile` to `researcher_config.yaml` to govern tool verbosity and protocol detail level.

### Changed
- **Tool: `sys.file.write`**: Enhanced immutability guard. It now explicitly rejects overwrites in `synthesis/` unless forced via the `--force` flag.
- **Tool: `sys.file.read`**: Added a 50MB file size read limit to avoid breaking the MCP agent context window.
- **Tool: `tool.python.exec`**: Now parses `data_inventory.json` for safety, and fully logs output/stderr to `workspace/logs/`.
- **Tool: `tool.search.web`**: Upgraded Firecrawl calls with `tenacity` exponential backoff and implemented a SerpAPI fallback.
- **Tool: `tool.search.semantic_scholar`**: Implemented real API bindings, strict rate limiting handling, and file-based caching.
- **Tool: `tool.search.pubmed`**: Improved fallback handling for zero-result queries by warning agents to broaden MeSH parameters.
- **Tool: `tool.literature.download`**: Added an Unpaywall API pre-check layer.
- **Tool: `sys.branch.switch`**: Refactored symlink moving logic to cleanly transition `workspace/.os_state` directories.
- **Tool: `sys.branch.merge`**: Integrated automated 3-way merge conflict blocks for text log files like `analysis.md`.
