# Research OS Agent Guidelines

1. **Immutability**: Do not modify `inputs/raw_data/` or `inputs/literature/`. Write new data to the current experiment step's `data/` directory.
2. **State Logging**: Log significant methodological decisions using `tool.log.decision`.
3. **Methodological Appends**: Append new analysis steps to `workspace/methods.md` using `mem.methods.append`.
4. **Analysis Checkpointing**: Append chronologically to `workspace/analysis.md` using `mem.analysis.log`.
5. **Experiment Paths**: Use `sys.path.create` for new steps. Use `sys.path.abandon` for dead ends (preserves files).
6. **Execution Estimation**: Before running heavy scripts, check `data_inventory.json` and use `tool.data.sample` to test logic first.
7. **Approval Gates**: In `supervised` mode, use `sys.checkpoint.pending` for major milestones.
8. **Checkpointing**: Use `sys.checkpoint.create` before massive refactoring.
9. **Model-Size Awareness**: Small models MUST use protocols from `protocols/light/` and `sys.state.minimal_context`.
10. **Fact-Checking**: Cite sources via `tool.search.*` calls.
11. **Autonomy Modes**:
    - **manual**: Propose actions and wait for PI approval.
    - **supervised**: Auto-execute routines; pause at key decisions.
    - **autopilot**: Execute one numbered task per response, end with "Type continue". After 4+ continues, call `sys.session.handoff`.
12. **Output-Driven Workflow**:
    - **exploratory/dashboard**: Build interactive dashboards/summaries.
    - **abstract**: 250-word abstract + key figure.
    - **poster**: Call `tool.poster.create`.
    - **paper**: Full IMRAD (section-by-section for complex work via `tool.synthesize section=...`).
