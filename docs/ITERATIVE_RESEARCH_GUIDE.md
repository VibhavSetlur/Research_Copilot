# Iterative Research Guide

Research is non-linear. You will hit dead ends, make mistakes, and need to change methodologies. Research OS uses Git-like branching and checkpointing to let you explore safely.

---

## 1. Using Branches

Branches let you test a new hypothesis or analysis method without touching your main `analysis.md` or data pipelines.

- **Create a Branch**: `sys.branch.create(name="bayesian_model")`
  This clones the current state, so you can freely modify `workspace/` files. The new state is isolated.
  
- **Switch Branches**: `sys.branch.switch(name="main")`
  This restores the workspace to the `main` branch.

- **Merge Branches**: `sys.branch.merge(target="main")`
  Once you are happy with a branch, merge it. Research OS handles conflict resolution for log files like `analysis.md`.

## 2. Checkpoints and Rollbacks

Think of checkpoints as commits.

- **Create Checkpoint**: `sys.checkpoint.create(message="Cleaned missing data")`
  This saves a snapshot.
  
- **Rollback**: `sys.checkpoint.rollback(checkpoint_id="...")`
  If you break something, you can revert the state to a previous snapshot.

## 3. Workflow Diagrams

Research OS profiles your pipeline and logs dependencies to `.os_state/execution_dag.json`. This generates a `workflow.png` visualizing the data transformations.

- **How to read it**: The DAG shows raw inputs pointing to derived outputs, with the scripts that generated them acting as edges.
- **Why it matters**: It verifies methodological provenance, ensuring that every result in `synthesis/` is fully reproducible from `inputs/`.
