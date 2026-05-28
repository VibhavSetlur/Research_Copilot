# Migrating to Research OS 2.0

Most v1.x projects continue to work without changes — the state schema
auto-migrates on first load. This page lists the few things that
genuinely changed so you can update any scripts / CI / wrappers that
referenced the old surface.

## Things that DID change

### Renamed tools (with alias compat)
* `tool_audit_figure_quality` → **`tool_audit_figure_full`**
  (the legacy name still resolves via the alias table for the 2.0
  cycle; will be removed in 3.0).

### Dropped aliases (no longer resolve)
These pointed at functions no real caller used. Use the canonical
names directly:

| Old alias | Canonical |
|---|---|
| `sys_guidance_get` | `sys_protocol_get` |
| `sys_guidance_list` | `sys_protocol_list` |
| `sys_guidance_validate` | `sys_protocol_validate` |
| `sys_md_validate` | `sys_file_validate_md` |
| `tool_audit_md_consistency` | `sys_file_validate_md` |
| `tool_env_freeze` | `sys_env_snapshot` |
| `tool_env_restore` | `sys_env_snapshot` |
| `tool_audit_reproducibility_full` | `tool_audit_reproducibility` |
| `sys_state_summary_md` | `sys_state_get` |
| `sys_state_health` | `sys_state_get` |
| `sys_state_minimal_context` | `sys_state_get` |
| `sys_config_profile` / `_init` / `_explain` | `sys_config_get` (or `sys_workspace_scaffold` for init) |
| `sys_tool_info` | `sys_protocol_get` |
| `sys_tool_search` | `sys_protocol_list` |

The five aliases that are kept (because they're plausibly still typed
at the prompt): `tool_audit_figure_quality`,
`tool_audit_statistical_power`, `sys_state_summary`, `tool_log_decision`,
`view_workspace_tree`.

### State schema v4.0
Legacy fields are auto-migrated on first load — no manual action needed.
The migrator drops:

* `phase` → renamed to `pipeline_stage`.
* `project` → renamed to `project_name`.
* `run_id` → renamed to `project_id`.
* `token_budget` — vestigial; removed.
* `knowledge_graph_path` — never used; removed.
* `data_scale_profile` — never used; removed.
* `execution_dag_path` — fixed path (`.os_state/execution_dag.json`); removed.
* Per-path `input_data_hashes` mirrors — `compute_input_hashes()` returns
  the live view; removed.
* `context_transfer_memos` (inline blobs) — externalised to
  `.os_state/context_transfer_memos/<id>.json`; in-state list now
  carries 3-field stubs only.

### Protocols moved or merged
* **Merged** `guidance/writing_standards` → `writing/writing_core`
  (single source of style truth).
* **Merged** `methodology/research_methods` →
  `methodology/methodology_selection` (lookup-mode absorbed).
* **Added** `methodology/preregistration`, `methodology/bayesian_analysis`,
  `methodology/timeseries_analysis`, `synthesis/synthesis_null_findings`,
  `guidance/code_review`, `guidance/peer_review_response`,
  `guidance/collaboration_handoff`.

If any of your scripts hit one of the merged-away protocols directly,
update to the new canonical name above.

## Things you should DO (recommended, not required)

* **Convert multi-script steps to `pipeline.yaml`.**
  `tool_audit_step_completeness` will start flagging multi-script steps
  (>2) that don't have a pipeline declaration. Run `tool_step_pipeline_define`
  to seed one from the 7-node template.
* **Backfill provenance sidecars on existing outputs.** New outputs get
  them automatically via `tool_figure_create` / `tool_step_pipeline_run`.
  Old outputs without `.prov.json` will show up in the audit gate.
* **Tag exploratory hypotheses.** Pass `kind='exploratory'` to
  `mem_hypothesis_add` for anything added post-hoc; everything else is
  assumed confirmatory.
* **Run `tool_audit_quality_full` before any final synthesis.** It's the
  one-call gate that surfaces every blocker (completeness, code, prose,
  claim grounding, pre-registration drift).

## Nothing-to-do paths

These v1.x workflows continue unchanged:
* `research-os init` scaffolding.
* `tool_route` → `tool_plan_turn` → `tool_plan_advance` planning loop.
* `tool_synthesize` paper builder.
* All `mem_*` append-only logs.
* All `tool_search_*` literature providers.
* Per-step folder layout (`workspace/NN_<slug>/`).
