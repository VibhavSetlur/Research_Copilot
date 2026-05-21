# Research Overview: Policy Impact Synthesis

## Context
This project examines the impact of a recent policy change on localized outcomes across multiple regions. Because the true model specification is unknown, we need to test several approaches (linear, interaction terms, and site-level adjustments) to see which model is most robust, and synthesize the findings.

## Research Intent
"Run predictive and robustness analyses across alternative model specifications (linear, interaction, site-adjusted) to identify the true effect of the treatment policy, and select the winning specification based on model fit and p-values."

## Data Dictionary
- `treatment`: Binary indicator (0 or 1) of policy application.
- `baseline`: The baseline metric value prior to the policy.
- `age`: Demographic age of the cohort.
- `site`: Categorical region identifier (north, south, east, west).
- `outcome`: The final continuous metric being measured post-policy.
