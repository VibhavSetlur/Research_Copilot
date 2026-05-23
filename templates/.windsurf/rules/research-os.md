# Research OS Agent Guidelines

When interacting with Research OS workspaces, you must abide by the following operational constraints to ensure project integrity, provenance tracking, and data safety.

## 1. Golden Rule of Immutability
**Never modify `inputs/raw_data/` or `inputs/literature/`. The OS will block you.**
These files form the immutable basis of the research.
Any data cleaning, transformation, or filtering must produce new files in `workspace/data/derived/`.
The ONLY exception is the `inputs/literature_index.yaml` file.

## 2. Mandatory State Logging
Whenever you make a significant methodological decision (e.g., choosing a statistical test, dropping an outlier, selecting a hyperparameter), you MUST log it using the `tool.log.decision` MCP tool.
Do not proceed with major analysis steps without logging the decision first.

## 3. Methodological Appends
If you execute a new analysis script or apply a new technique, you MUST append a one-line summary to `workspace/methods.md` using the `mem.methods.append` tool.
Example: `Applied SMOTE to balance the training dataset prior to Random Forest training.`

## 4. Analysis Checkpointing
Append your chronological findings, results, and interim thoughts to `workspace/analysis.md` using the `mem.analysis.log` tool.

## 5. Experiment Branching
If you are about to try a risky, alternative, or exploratory analysis path, use `sys.branch.create` to spin up a new experiment workspace. Do not overwrite the main workspace for speculative testing.
Once the experiment is proven successful, you may use `sys.branch.merge` to bring the findings back to the main branch.

## 6. Model-Size Awareness
If you are a small model, always load the light protocol first.
Rely on `sys.state.minimal_context` to stay oriented without blowing out your context window.

## 7. Mandatory Profiling Before Execution
Before any Python execution, check `workspace/logs/data_inventory.json` for dataset size.
If the runtime is expected to be long or the file is large, always use `tool.data.sample` to develop and verify your logic on a subset of the data first.
