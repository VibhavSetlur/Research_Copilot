# Example 2: Policy Impact Synthesis

This directory is a **fully populated Research Copilot workspace** demonstrating a complex, multi-branch analysis with automated synthesis.

It represents the end-state of a project where a researcher has:
1. Initialized the workspace (`rcp init`).
2. Placed raw data in `00_inputs/raw_data/policy_panel.csv`.
3. Ingested the data for vector search (`rcp ingest`).
4. Used the `ResearchEngine` to explore the intent: *"Run predictive and robustness analyses across alternative model specifications."*
5. Branched the workspace to test three separate models:
   - `branch_linear`: standard OLS.
   - `branch_interaction`: OLS with treatment-baseline interaction.
   - `branch_site_adjusted`: OLS controlling for categorical site biases.
6. Synthesized the findings across all three branches to select the winning specification.

## Exploring the Workspace

- **`00_inputs/`**: Contains the raw policy panel dataset.
- **`01_workspace/`**: Contains routing decisions and cache.
- **`02_experiments/`**: Contains the standard execution node logs and base outputs.
- **`03_synthesis/`**: This is the core of this example.
  - Explore the `expert_outputs/` folder to see the parallel branches (`branch_linear`, `branch_interaction`, `branch_site_adjusted`).
  - View `parallel_results.json` to see how the system tracked branch execution status.
  - Review `state_ledger.json` to see how the system recorded the `winning_branch_name` and promoted its artifact data path back to the main trunk.
- **`RESEARCH_OVERVIEW.md`**: The initial problem statement and data dictionary.

*Note: This is not a "runnable script" example, but a pristine example of the artifact structure produced by the Research Copilot system operating at production quality.*
