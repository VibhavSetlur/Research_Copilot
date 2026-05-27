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

## Every session — boot in ONE turn

```
1. sys_config_get        (in parallel)
2. sys_state_get         (in parallel)
3. sys_protocol_next  →  load that protocol with sys_protocol_get
```

Reply with one short summary, then run the protocol's first step.

If the researcher's message contains a specific ask ("write the methods
section", "make a dashboard"), load THAT protocol instead and tell them
you're skipping the default.

---

## How to operate, in one paragraph

Protocols are the source of truth for "what to do". Always
`sys_protocol_get` the relevant one and follow its numbered steps. Tool
names use underscores; dot notation and legacy names auto-rewrite.
`researcher_config.yaml` controls autonomy / model_profile / runtime —
respect them. When uncertain about a method or library, search literature
FIRST (`tool_research_method`, `tool_research_tool`). Log every
meaningful decision (`mem_decision_log`), method (`mem_methods_append`),
and hypothesis update (`mem_hypothesis_update`). Append-only files
(`methods.md`, `analysis.md`, `citations.md`) are never edited directly
— always via `mem_*`.

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
