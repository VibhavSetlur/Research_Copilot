# Research OS — AI Operating Rules

You are connected to the **Research OS MCP server**. This file is loaded
every prompt — keep it short. Detailed step-by-step instructions live in
the **protocols** you load on demand.

---

## Mental model

* **You (the AI in the IDE)** plan and reason.
* **Research OS (MCP server)** executes, records, enforces immutability.
  Every research action goes through its tools.
* **The researcher** drops files into `inputs/`, talks to you in natural
  language, approves checkpoints.

If you can't see `sys_*` / `tool_*` / `mem_*` tools in this session, the
MCP server isn't connected. Tell the researcher to run `research-os start`
in a terminal at the project root, or restart their IDE so the MCP config
in the project loads.

---

## Every session — boot in TWO MCP calls (~1K tokens, not ~5K)

```
1. sys_boot                            (state + config + history + dep
                                        inventory + next protocol +
                                        pause classification + active plan)
2. (await researcher's message)
3. tool_route(prompt=<their message>)  (HIERARCHICAL pick — L1 → L2 → L3 —
                                        without loading every YAML)
4. If tool_route.ask_user is non-null → ASK the researcher that one
   sentence, then re-route. Do not guess.
5. If complexity="high":
     a. tool_plan_turn                 (batch the plan for this turn,
                                        respecting model_profile)
     b. Execute every entry in this_turn IN ORDER.
     c. After each entry, tool_plan_advance.
     d. If tool_plan_turn returned chat_split_recommended=true → run
        sys_session_handoff and tell the researcher to open a fresh chat
        with "pick up where we left off".
6. If complexity="low": call the shortcut_tool or load the primary
   protocol with sys_protocol_get format='summary' (≈300 tokens) then
   format='step' + step_id when ready to execute one step.
```

**Never** call `sys_state_get` + `sys_config_get` + `sys_protocol_history`
+ `sys_protocol_next` + `sys_dep_inventory` separately — `sys_boot`
returns the union in one shot. **Never** load a protocol at `format='full'`
just to learn what steps exist — `format='summary'` is what you want.

**Never one-shot complex prompts.** The router persists an `active_plan`
for high-complexity asks; walk it with `tool_plan_turn` + `tool_plan_advance`.
A small-model session executes 1 step/turn; medium 3; large 6. The router
decides for you — just respect it.

---

## How to operate, in one paragraph

Protocols are the source of truth for "what to do". Pick which one with
`tool_route`, load it lean with `sys_protocol_get format='summary'`,
drill into a single step with `format='step'` + `step_id=<id>` when
ready to execute. Tool names use underscores; dot notation and legacy
names auto-rewrite. `researcher_config.yaml` controls autonomy /
model_profile / runtime — respect them. When uncertain about a method
or library, search literature FIRST (`tool_research_method`,
`tool_research_tool`). Log every meaningful decision
(`mem_decision_log`), method (`mem_methods_append`), and hypothesis
update (`mem_hypothesis_update`). Append-only files (`methods.md`,
`analysis.md`, `citations.md`) are never edited directly — always via
`mem_*`. Need a tool you don't recognise? `sys_tool_describe(name)`
returns the full description without re-listing every tool.

---

## Where things live (so you stop asking)

| Need | Look in |
|---|---|
| Full tool list + signatures | `sys_protocol_list` then `sys_protocol_get` |
| Naming convention for experiment steps | `guidance/analysis_plan` protocol |
| Quality bars for paper / poster / dashboard | the `synthesis/*` protocol you're running |
| What to do mid-flow if a new file appears | `tool_context_intake` |
| Workspace looks broken | `tool_workspace_repair` |
| Quick scratch / smoke tests | `workspace/scratch/` + `tool_scratch_*` |
| Recovery from mistake | `sys_checkpoint_list` → `sys_checkpoint_rollback` |
| End-of-session | `sys_session_handoff` |
| Change autonomy mid-chat | `sys_config_set key=interaction.autonomy_level value=…` |

---

## Hard rules (only the things you must NEVER do)

1. Never write to `inputs/raw_data/` or `inputs/literature/` — immutable.
2. Never invent citations. All final-output citations come from
   `tool_synthesize` (verified online) or workspace literature sidecars.
3. Never use causal language ("causes", "proves") on observational data.
4. Never commit a method or library from training memory alone — run
   `tool_research_method` or `tool_research_tool` first.
5. Never delete anything in `workspace/`. To abandon, use
   `sys_path_abandon` (it renames to `__DEAD_END`, preserves files).
6. Never hold the conversation blocked on a long job — use `tool_task_run`.
7. Never pick experiment-step slugs from training memory — derive them
   from THIS step's actual goal (see `guidance/analysis_plan`).

Research OS does **not** manage LLM provider keys. Your IDE owns that.
The only credentials it uses are for literature / web search APIs.
