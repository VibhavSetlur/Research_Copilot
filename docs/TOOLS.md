# Tool Catalog

~75 MCP tools under three namespaces. Names use underscores; dot notation
(`sys.state.get`) and legacy names (`sys_guidance_get`) auto-rewrite.

For most users this is a quick lookup. For *when* to use a tool, see
[PROTOCOLS.md](PROTOCOLS.md) — protocols string tools together to do real
work.

---

## `sys_*` — workspace, state, files, paths, checkpoints

| Tool | Purpose |
|---|---|
| `sys_protocol_get` | Load a protocol YAML by name. |
| `sys_protocol_list` | List every protocol + one-line summary. |
| `sys_protocol_next` | Recommend the next protocol from state + on-disk artifacts. |
| `sys_protocol_validate` | Check whether a protocol's expected_outputs exist. |
| `sys_protocol_log` | Record a protocol execution (started / completed / failed / skipped). |
| `sys_protocol_history` | Show recent execution log entries. |
| `sys_state_get` | Full / minimal / markdown state snapshot. |
| `sys_workspace_scaffold` | Re-create the directory tree. |
| `sys_workspace_tree` | Structured workspace listing. |
| `sys_file_read/_write/_list/_delete/_validate_md` | File I/O (writes to inputs/raw_data + inputs/literature blocked). |
| `sys_path_create` | Create the next numbered experiment folder. |
| `sys_path_abandon` | Mark a path as `__DEAD_END` (preserved, never deleted). |
| `sys_path_list` | List numbered experiment paths + status. |
| `sys_checkpoint_create/_rollback/_list` | Hardlinked workspace snapshots. |
| `sys_config_get/_set/_validate` | researcher_config.yaml. |
| `sys_notify` | Append to workspace/logs/notifications.log. |
| `sys_session_handoff` | Generate a markdown summary + resume prompt. |
| `sys_env_snapshot/_docker_generate` | Capture + containerise the environment. |

---

## `tool_*` — search, exec, audit, synthesis, research, intake, scratch, tasks, repair

### Search

| Tool | Purpose |
|---|---|
| `tool_search_semantic_scholar` | Semantic Scholar Graph API. |
| `tool_search_pubmed` | PubMed (NCBI eutils). |
| `tool_search_crossref` | Crossref. |
| `tool_search_arxiv` | arXiv (no key needed). |
| `tool_search_web` | Firecrawl → SerpAPI fallback. |
| `tool_web_scrape` | Scrape a URL to markdown. |
| `tool_literature_download` | Save a paper PDF into inputs/literature/. |

### Script execution

| Tool | File types |
|---|---|
| `tool_python_exec` | .py |
| `tool_r_exec` | .R |
| `tool_julia_exec` | .jl |
| `tool_bash_exec` | .sh |
| `tool_notebook_exec` | .ipynb (jupyter nbconvert --execute --inplace) |
| `tool_rmarkdown_render` | .Rmd / .qmd |
| `tool_package_install` | pip install + append to requirements |

### Data

| Tool | Purpose |
|---|---|
| `tool_data_sample` | Sample N rows from CSV / Parquet / Feather / Excel / JSON. |
| `tool_data_profile` | Schema + missingness + descriptive stats + suggestions. |
| `tool_data_convert` | CSV ↔ Parquet ↔ Feather ↔ RDS. |

### Audit

| Tool | Purpose |
|---|---|
| `tool_audit_synthesis` | Section coverage, causal-language hits, citation density. |
| `tool_audit_power` | Post-hoc statistical power (statsmodels). |
| `tool_audit_assumptions` | Re-run normality / homoscedasticity / etc. on residuals. |
| `tool_audit_figure` | DPI, size, format checks (Pillow). |
| `tool_audit_citations` | Verify every citation in workspace/citations.md online. |
| `tool_audit_reproducibility` | Re-run every script and hash-compare outputs. |

### Synthesis

| Tool | Purpose |
|---|---|
| `tool_synthesize_plan` | Show available sources + recommended ordering. |
| `tool_synthesize` | Build synthesis/<section>.md (or full paper). Output_type tunes citations cap. |
| `tool_latex_compile` | paper.tex → PDF. |
| `tool_poster_create` | tikzposter → PDF. |
| `tool_dashboard_create` | Single-file HTML dashboard (sortable, lightbox, light/dark, print-friendly). Audience: academic / executive / technical / teaching. |
| `tool_citations_verify` | Re-verify every citation_key in workspace/citations.md. |

### Research / reasoning

| Tool | Purpose |
|---|---|
| `tool_research_method` | Deep-dive a method via 3-4 academic providers + web. |
| `tool_research_tool` | Find candidate libraries / CLIs / websites, tag each: installable / api / external / paid. |
| `tool_external_tool_instructions` | Write a WORKSHEET.md when the chosen tool is non-AI-executable. |
| `tool_plan_step` | Force a complex step into atomic sub-tasks BEFORE coding. |
| `tool_plan_next_step` | Single-turn next-step recommendation. |
| `tool_branch_recommendation` | Branch into parallel experiment vs extend current. |

### Intake

| Tool | Purpose |
|---|---|
| `tool_intake_autofill` | Read inputs/, classify domain, extract question + hypotheses, fill blanks in config. |
| `tool_context_intake` | Route mid-flow file drops into the right inputs/ subfolder. |

### Background tasks (real `subprocess.Popen`)

| Tool | Purpose |
|---|---|
| `tool_task_run` | Spawn a background process; returns task_id immediately. |
| `tool_task_status` | Live PID check + tail of log. |
| `tool_task_list` | List all known tasks. |
| `tool_task_kill` | Terminate a task (TERM by default). |

### Scratch

| Tool | Purpose |
|---|---|
| `tool_scratch_write` | Write a quick-test file to workspace/scratch/. |
| `tool_scratch_run` | Execute it (language by extension). |
| `tool_scratch_list` / `tool_scratch_clear` | Inspect / wipe scratch. |

### Repair

| Tool | Purpose |
|---|---|
| `tool_workspace_repair` | Detect + heal missing dirs / corrupted state / stale paths. NEVER deletes. |

---

## `mem_*` — append-only logs, decisions, hypotheses

| Tool | Purpose |
|---|---|
| `mem_analysis_log` | Append a line to workspace/analysis.md. |
| `mem_methods_append` | Append a structured method entry (step, dataset, implementation, parameters, justification, assumptions). |
| `mem_citations_generate` | Regenerate workspace/citations.md from inputs/literature_index.yaml. |
| `mem_intake_regenerate` | Refresh inputs/intake.md (recompute file hashes). |
| `mem_decision_log` | Append a structured decision (context / selected / rationale). |
| `mem_hypothesis_add/_update/_list` | Multi-hypothesis ledger. |

---

## Tool naming compatibility

Three accepted forms:

| Form | Example | Notes |
|---|---|---|
| canonical underscore | `sys_state_get` | Preferred. |
| dot notation | `sys.state.get` | Auto-rewritten by the dispatcher. |
| legacy aliases | `sys_guidance_get` | Mapped to `sys_protocol_get`. |

The full alias table lives in `src/research_os/server.py::_ALIASES`. The AI
should default to canonical underscore form in new code.

---

## Example invocations (raw MCP)

> You rarely call these by hand. The AI handles them for you. These examples
> are for power users who want to debug a single tool.

### `sys_state_get` (full state)
```json
{"name": "sys_state_get", "arguments": {}}
```

### `sys_state_get` (markdown summary)
```json
{"name": "sys_state_get", "arguments": {"format": "markdown"}}
```

### `tool_data_profile`
```json
{"name": "tool_data_profile",
 "arguments": {"filepath": "inputs/raw_data/cohort.csv"}}
```

### `tool_research_method`
```json
{"name": "tool_research_method",
 "arguments": {"query": "logistic regression with imbalanced classes",
               "limit": 5}}
```

### `tool_synthesize` — abstract section, conference venue
```json
{"name": "tool_synthesize",
 "arguments": {"section": "abstract", "output_type": "abstract"}}
```

### `tool_dashboard_create` — executive audience
```json
{"name": "tool_dashboard_create",
 "arguments": {"title": "Cohort 2024 — Q4 update", "audience": "executive"}}
```

### `tool_task_run` — background long job
```json
{"name": "tool_task_run",
 "arguments": {"command": "python workspace/03_train/scripts/train_v1.py",
               "description": "GPU training run"}}
```
