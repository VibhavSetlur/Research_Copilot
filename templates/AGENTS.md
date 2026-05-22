# Research OS Agent Guidelines

When interacting with Research OS workspaces, LLM-based agents (e.g., Cursor, Windsurf, generic MCP clients) must abide by the following operational constraints to ensure project integrity, provenance tracking, and data safety.

## 1. Golden Rule of Immutability
**Do not modify files in the `inputs/raw_data/` or `inputs/literature/` directories.**
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
This creates a continuous, readable narrative of the research process.

## 5. Experiment Branching
If you are about to try a risky, alternative, or exploratory analysis path, use `sys.branch.create` to spin up a new experiment workspace. Do not overwrite the main workspace for speculative testing.
Once the experiment is proven successful, you may use `sys.branch.merge` to bring the findings back to the main branch.

## 6. Execution Estimation
Before executing Python scripts (`tool.python.exec`) that process large datasets (e.g., >1GB), check the `workspace/logs/data_inventory.json` file. If the estimated processing time is high, consider using `tool.data.sample` to run a smaller test first.

## 7. Approval Gates
If the configuration specifies `supervised` autonomy, you must use `sys.checkpoint.pending` to request approval from the human researcher before executing long-running scripts, modifying core hypotheses, or completing major milestones.

## 8. Checkpoint Usage
Always create a checkpoint (`sys.checkpoint.create`) before undertaking massive refactoring of scripts or data pipelines. This allows the researcher to rollback (`sys.checkpoint.rollback`) if the analysis goes awry.

## 9. Model-Size Awareness
If you are operating as a small model (e.g. indicated by `model_profile: small` in the configuration), you MUST load the lightweight protocols from the `protocols/light/` directory. Rely on `sys.state.minimal_context` to stay oriented without blowing out your context window.

## 10. Mandatory Profiling Before Execution
Never execute a data processing script (`tool.python.exec`) without first checking `workspace/logs/data_inventory.json` for dataset size and estimated runtime. If the runtime is expected to be long or the file is large, always use `tool.data.sample` to develop and verify your logic on a subset of the data first.

## 11. Citation and Fact-Checking Rule
Every factual claim, literature reference, or established methodology you cite MUST be backed by a `tool.search.*` call (e.g., `tool.search.pubmed`, `tool.search.semantic_scholar`). You must log the retrieved citation or result alongside your claim to ensure provenance.
