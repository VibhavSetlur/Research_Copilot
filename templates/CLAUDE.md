# Research OS workspace — Claude Code

This is a Research OS workspace. **Read `AGENTS.md` at the project root
first** — it contains the canonical operating rules.

Every research action goes through the `research-os` MCP server:

1. `sys_config_get` + `sys_state_get` in parallel
2. `sys_protocol_next` → load the recommended protocol via `sys_protocol_get`
3. Follow the protocol; finish with the auto-injected `protocol_completion`.

Tools use underscores (`sys_state_get`, `tool_data_profile`,
`mem_analysis_log`). Dot notation and legacy names auto-rewrite.

Never write to `inputs/raw_data/` or `inputs/literature/` (immutable).
All workspace I/O goes through `sys_file_*` so provenance is captured.

Research OS does NOT manage LLM provider keys — Claude Code owns model
access. The only credentials Research OS uses are for literature / web
search providers (all optional).
