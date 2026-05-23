# Research OS Agent Guidelines

When interacting with Research OS workspaces, you must abide by the following operational constraints to ensure project integrity, provenance tracking, and data safety.

## 1. Golden Rule of Immutability
**Do not modify files in the `inputs/raw_data/` or `inputs/literature/` directories.**
These files form the immutable basis of the research.
Any data cleaning, transformation, or filtering must produce new files inside the current experiment step's `data/` directory (e.g., `workspace/01_experiment_baseline/data/`).
The ONLY exception is the `inputs/literature_index.yaml` file.

## 2. Mandatory State Logging
Whenever you make a significant methodological decision, log it using the `tool.log.decision` MCP tool before proceeding with major analysis steps.

## 3. Methodological Appends
After executing a new analysis script or applying a new technique, append a one-line summary to `workspace/methods.md` using the `mem.methods.append` tool.

## 4. Analysis Checkpointing
Append chronological findings, results, and interim thoughts to `workspace/analysis.md` using the `mem.analysis.log` tool.

## 5. Experiment Paths
Experiments follow numbered chronological steps (`01_experiment_baseline/`, `02_data_preparation/`). Use `sys.path.create` to create the next step. If a path reaches a dead end, use `sys.path.abandon` to rename it — files are preserved, not deleted.

## 6. Model-Size Awareness
If you are a small model, always load the light protocol first. Rely on `sys.state.minimal_context` to stay oriented.

## 7. Mandatory Profiling Before Execution
Before any Python execution, check `workspace/logs/data_inventory.json` for dataset size. Use `tool.data.sample` for large datasets.

## 8. Citation and Fact-Checking Rule
Every factual claim must be backed by a `tool.search.*` call. Log the retrieved citation alongside your claim. Every search result is automatically logged to `workspace/logs/searches.log`.
