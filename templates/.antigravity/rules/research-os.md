# Research OS workspace

This is a Research OS workspace. The full operating rules live in `AGENTS.md`
at the project root — read it first.

On every new session:

1. `sys_config_get` (in parallel with #2)
2. `sys_state_get`
3. `sys_protocol_next` → load the recommended protocol via `sys_protocol_get`
4. Run the protocol; finish with the injected `protocol_completion` step.

Tools use underscores: `sys_state_get`, `tool_data_profile`, `mem_analysis_log`.

Never write to `inputs/raw_data/` or `inputs/literature/` (immutable).
All workspace I/O goes through MCP tools.
