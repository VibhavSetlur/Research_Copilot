# Research OS — Agent Operating Protocol

## 1. MANDATORY SESSION START (Run before ANYTHING else)
1. Call `sys.config.profile` to get your behavioral profile.
2. Call `sys.config.get` to read the full researcher_config.yaml.
3. Call `sys.state.get` to understand current project phase.
4. Call `sys.path.list` to know which experiment paths exist.
5. Load and follow `guidance/session_boot` protocol.
6. DO NOT start working until these 5 steps are complete.

## 2. PROCESSING ANY REQUEST
For every researcher message:
a. Classify intent: NEW research task, CONTINUATION, QUESTION, or CORRECTION.
b. Before acting, call `sys.state.health` if more than 4 turns have elapsed.
c. Load the relevant protocol via `sys.guidance.get` before executing any multi-step workflow.
d. Break multi-step work into STAGES. After each stage, report what was done and ASK before the next stage.
e. NEVER stuff more than one logical step into one response.

## 3. AFTER COMPLETING ANY STEP
Always do ALL of the following in order:
1. `mem.analysis.log` — append a timestamped entry to workspace/analysis.md
2. `mem.methods.append` — append any new method used to workspace/methods.md
3. Update `workspace/workflow.mermaid` via `sys.file.write` — mark completed nodes green
4. Call `sys.state.get` to verify the ledger updated
5. Ask the researcher: "Step complete. Want me to [describe next logical step]?"

## 4. TOOL USAGE RULES
- NEVER read or process `inputs/raw_data/` files directly — use `tool.data.sample` for all data exploration.
- NEVER write to `inputs/` — use `workspace/<path>/data/` for all derived data.
- ALWAYS call `sys.checkpoint.pending` before running scripts that generate output.
- Use `sys.file.list` before `sys.file.read` to confirm a file exists.
- For literature: search → download → add to `workspace/citations.md` (in that order).

## 5. PROTOCOL COMPLIANCE
Every research phase has a YAML protocol. You MUST load and follow it:
| Phase               | Protocol to Load           |
|---------------------|---------------------------|
| Session start       | guidance/session_boot      |
| First analysis      | guidance/project_startup   |
| Domain check        | domain/domain_analysis     |
| Method selection    | methodology/methodology_selection |
| Literature          | literature/literature_search |
| Writing methods     | writing/writing_methods    |
| Writing conclusions | writing/writing_conclusions|
| Synthesis           | synthesis/synthesis_paper  |

## 6. MULTI-SESSION RULES
- If `sys.state.health` recommends handoff, call `sys.session.handoff` before ending.
- End every session with a brief "Session Summary" listing what was done and the exact first message for the next session.
- NEVER assume the next session will remember anything — always write state to files.

## 7. FORBIDDEN ACTIONS
- Do NOT create synthesis/ files until ALL experiments are complete.
- Do NOT use causal language ("causes", "proves") for observational data.
- Do NOT call more than 3 tools consecutively without reporting to the researcher.
- Do NOT create a new experiment path without telling the researcher why.
