# Contributing to Research OS

Thanks for being interested. Research OS is small on purpose — only contribute
changes that keep the surface small and the protocols sharp.

## Architecture in one paragraph

The AI IDE is the brain (Cursor / Claude / Antigravity / OpenCode / VS Code).
Research OS is the body: it exposes ~50 MCP tools and 33 YAML protocols, and
it enforces immutability (`inputs/raw_data/`, `inputs/literature/`) and
provenance (`workspace/methods.md`, `workspace/analysis.md`,
`.os_state/protocol_execution_log.jsonl`). It never calls an LLM itself.

## Development setup

```bash
git clone https://github.com/VibhavSetlur/Research-OS.git
cd Research-OS
pip install -e ".[all,dev]"
pytest                           # run the test suite
ruff check . && ruff format .    # lint + format
```

## Adding or modifying a protocol

Each protocol lives at `src/research_os/protocols/<category>/<name>.yaml`.
Keep the schema tight:

```yaml
id: <protocol_id>
name: <Human Name>
version: '4.0.0'
schema_version: '2.0'
description: One-line summary.
trigger: When the AI should run this.
prerequisites:
  - state field or file
steps:
  - id: step_id
    name: Step Name
    description: |
      Concrete tool calls (underscore form), one numbered action per step.
expected_outputs:
  - path/to/file
next_protocol: category/next_one     # null if terminal
on_failure: guidance/dead_end_routing # null if no fallback
```

* The loader injects the standard `protocol_completion` step — do NOT add it.
* `next_protocol` must point at a real protocol or `null`. Verify the chain
  doesn't cycle.
* Add the protocol's `expected_outputs` to `PIPELINE` in
  `src/research_os/tools/actions/protocol.py` only if it's part of the main
  pipeline.

## Adding a new tool

1. Implement the action in `src/research_os/tools/actions/<file>.py`. Return a
   dict with `status="success"|"error"` and either `data` or `message`.
2. Add a JSON schema entry in `TOOL_DEFINITIONS` in `src/research_os/server.py`.
   Use underscore naming (`sys_X_Y`, `tool_X_Y`, `mem_X_Y`).
3. Add a handler `_handle_<name>(name, arguments, root)` and register it in
   the `_HANDLERS` dict at the bottom of `server.py`.
4. If you're replacing an old tool name, add it to `_ALIASES` so older
   protocols keep working.
5. Reference the tool from at least one protocol — orphaned tools become dead
   code and will be removed in the next cleanup.

## Testing

Tests live in `tests/`. Run a focused subset with:

```bash
pytest tests/test_protocols.py -k literature_search -v
```

## Style

* Black / Ruff defaults; line length 100.
* Type hints required on new functions.
* One short module docstring at the top of every new file.
* No emojis in source or markdown unless an existing convention requires it.

## Reporting issues

Use the GitHub issue templates. Include the version (`research-os start --help`
or `pip show research-os`), the OS, the steps to reproduce, and the full
traceback or relevant log excerpt from `workspace/logs/`.
