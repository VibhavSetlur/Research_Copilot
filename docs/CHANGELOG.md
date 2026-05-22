# Changelog

All notable changes to this project will be documented in this file.

## [10.0.0] - 2026-05-22

### Added
- Pure MCP-Native architecture where the IDE does the thinking and the OS executes.
- `sys.*`, `mem.*`, `view.*`, and `tool.*` categories for 44+ MCP tools.
- Strict directory taxonomy with immutable `inputs/` and numbered `workspace/` experiments.
- Checkpoint and rollback tools to manage workspace state securely.
- Branch and merge tools to handle multiple analysis trajectories.
- Auto-updating Mermaid workflow diagrams in `analysis.md`.
- `CONTRIBUTING.md` and standard GitHub issue templates.

### Changed
- Refactored `SupervisorAgent` and `IntentRouter` to make the OS a purely stateless executor.
- Re-architected initialization sequence to provide seamless IDE integration snippets.
- Expanded documentation including `MCP_TOOLS_REFERENCE.md` and `SKILLS.md`.

### Removed
- Autonomous decision-making layers and planners inside the OS.
- Deprecated agent logic that overlapped with the IDE's cognitive process.
