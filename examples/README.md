# Research Copilot Examples

This directory contains two pre-populated, production-quality **Research Copilot Workspaces**. 

Unlike simple "run scripts," these examples are fully hydrated workspaces that show what the end-state of a successful research project looks like when using the Research Copilot CLI and SDK.

## Example 1: `01_sleep_quality_analysis`
A clean, single-path statistical analysis. It demonstrates the standard `rcp` pipeline:
1. Workspace initialization and dataset ingestion.
2. Standard execution routing (data profiling, EDA, reporting).
3. A custom node calculating t-statistics, Cohen's d, and generating figures.
4. Finalizing outputs into `02_experiments`.

## Example 2: `02_policy_impact_synthesis`
A complex, multi-branch analysis with final synthesis. It demonstrates the engine's capacity for robustness checks:
1. Workspace initialization and dataset ingestion.
2. Publication-depth routing.
3. Branching the workspace to run three concurrent analytical specifications (linear, interaction, and site-adjusted models).
4. Synthesizing the branches, determining a winning specification based on fit metrics (R-squared and p-values), and updating the core state ledger (`03_synthesis/state_ledger.json`).

## How to Explore

You do **not** need to run any scripts to generate these examples. They are ready to inspect.

1. **`00_inputs/`**: Check the raw data and vector search artifacts.
2. **`01_workspace/`**: Look at the engine's routing scratchpads.
3. **`02_experiments/`**: View the direct analysis outputs, CSVs, and figures.
4. **`03_synthesis/`**: Examine the ledger to see how the system tracks branches and the overall state of the research project.

If you wish to try the system yourself, you can run `python -m research_copilot.cli init my_workspace` from the repository root to start your own blank canvas!
