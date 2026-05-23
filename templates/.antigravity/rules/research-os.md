# Research OS Agent Guidelines

When interacting with Research OS workspaces, you must abide by the following operational constraints to ensure project integrity, provenance tracking, and data safety.

## 1. Golden Rule of Immutability
**Do not modify files in the `inputs/raw_data/` or `inputs/literature/` directories.**
Any data cleaning, transformation, or filtering must produce new files inside the current experiment step's `data/` directory (e.g., `workspace/01_experiment_baseline/data/`).

## 2. Mandatory State Logging
Log significant methodological decisions using `tool.log.decision` before proceeding.

## 3. Methodological Appends
Append analysis summaries to `workspace/methods.md` via `mem.methods.append`.

## 4. Analysis Checkpointing
Append findings to `workspace/analysis.md` via `mem.analysis.log`.

## 5. Experiment Paths
Experiments are numbered chronological steps (`01_experiment_baseline/`, `02_data_preparation/`). Use `sys.path.create` to create the next step. Use `sys.path.abandon` to mark dead ends.

## 6. Model-Size Awareness
Small models should load lightweight protocols first and use `sys.state.minimal_context`.

## 7. Mandatory Profiling Before Execution
Check `workspace/logs/data_inventory.json` for dataset size before executing Python scripts.

## 8. Citation and Fact-Checking Rule
Back every factual claim with a `tool.search.*` call and log the source. Every search result is automatically logged to `workspace/logs/searches.log`.
