# Iteration

At any point during the research pipeline, you can request iteration to investigate, refine, or challenge findings.

## How Iteration Works

1. You ask a follow-up question in plain English
2. The intent router classifies the iteration type
3. A new experiment branch is created under `02_experiments/`
4. Results are documented — previous iterations are never deleted
5. The state ledger and manifest are updated

Each iteration gets a unique ID (001, 002, 003...) and is fully documented in the experiment's `decisions.yaml`.

## Iteration Types

| Type | You Say | What Happens |
|------|---------|-------------|
| `investigate` | "Why did we get this result?" | Deep dive into existing results, check assumptions, examine outliers |
| `method_switch` | "Try a different method" | Replace current method with alternative (e.g., OLS → quantile regression) |
| `variable_change` | "What if we control for X?" | Add or remove variables, re-run analysis |
| `robustness` | "Check if this holds up" | Sensitivity analysis: different specifications, subsamples, alternative measures |
| `literature_compare` | "How does this compare to literature?" | Compare findings to prior studies from evidence matrix |
| `explore` | "What else is in the data?" | Exploratory analysis: new variables, interactions, subgroups |
| `optimize` | "Find a better approach" | Method optimization: hyperparameter tuning, feature selection |
| `validate` | "Double-check this" | Replicate with different approach, cross-validation |

## Example Iterations

### Investigate a Result

> "Why is the coefficient for income so large?"

The system:
1. Checks for multicollinearity (VIF)
2. Examines influential points (Cook's D)
3. Tests for nonlinearity (polynomial terms)
4. Reports findings in a new experiment branch

### Switch Methods

> "Try a Bayesian approach instead."

The system:
1. Creates `exp_002_bayesian/` branch
2. Re-runs analysis with Bayesian method
3. Compares results to frequentist baseline
4. Documents differences in `decisions.yaml`

### Add Controls

> "What if we control for age and education?"

The system:
1. Adds specified variables to the model
2. Re-runs analysis
3. Reports coefficient changes (confounding assessment)
4. Updates the evidence matrix

### Robustness Check

> "Check if this holds up with a different specification."

The system:
1. Runs alternative specifications (e.g., log-transform, winsorize, different fixed effects)
2. Reports coefficient stability across specifications
3. Flags results that are specification-sensitive

## Viewing Iteration History

```bash
rcp iterations
```

Shows all iterations with their type, status, and key decisions.

## Branch Management

Iterations create experiment branches. Manage them with:

```bash
rcp branches                    # List all branches
rcp switch exp_002_bayesian     # Switch to a branch
rcp merge exp_002_bayesian      # Merge findings to main
rcp abandon exp_002_bayesian    # Abandon an exploratory branch
```

## Documentation

Every iteration is documented in:
- `02_experiments/<exp>/decisions.yaml` — Local decision ledger
- `01_workspace/lab_notebook.md` — Append-only chronological log
- `03_synthesis/manifest.json` — Global project manifest

Iterations are never deleted. Dead ends are valuable — they document what doesn't work.
