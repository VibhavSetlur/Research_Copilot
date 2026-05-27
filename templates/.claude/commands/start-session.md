# /start-session

Run the mandatory Research OS session-start sequence:

1. `sys_config_get` and `sys_state_get` (in parallel)
2. `sys_protocol_next`
3. Load the returned protocol via `sys_protocol_get` and run its first step.

Reply with ONE short boot summary covering: project name, pipeline stage,
active path, autonomy mode, expertise, model profile, and the recommended
next protocol. Ask the researcher to confirm before proceeding.
