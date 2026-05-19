---
skill_id: "survival_analysis"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "lifelines"]
estimated_tokens: 3000
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/survival_results.json"]
---

# Skill: Survival Analysis (Cox Proportional Hazards)

## Purpose
Execute survival analysis and validate proportional hazard assumptions using Schoenfeld residual tests.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to dataset |
| `duration_col` | Str | Yes | Duration variable |
| `event_col` | Str | Yes | Event indicator (1 = event, 0 = censored) |
| `covariates` | List | Yes | Predictors |

## Methodological Framework
- **Cox Proportional Hazards**:
  $$h(t|X) = h_0(t) \exp(X\beta)$$
- **Proportional Hazards Assumption**:
  The ratio of hazard functions for any two individuals must remain constant over time. This is tested using Schoenfeld residuals.

## Step-by-Step Analytical Protocol
1. Fit Kaplan-Meier survival curves.
2. Fit Cox proportional hazards model.
3. Check assumptions via Schoenfeld residual testing.

## Diagnostics & Interpretation Guide (What to Look For)
- **Schoenfeld Residual Test p < .05**:
  - *Interpret*: Proportional hazard assumption violated. The effect of the covariate changes over time.
  - *Action*: Add an interaction term between the covariate and time (time-varying covariate), or perform stratified Cox regression.

## Writing & Reporting Standards
> "We fitted a Cox proportional hazards model to estimate event risk. The proportional hazards assumption was verified using Schoenfeld residuals (all $p > .10$). Predictors are reported as Hazard Ratios (HR): $HR = 1.65, 95\%\text{ CI } [1.21, 2.24], p = .002$."

## Reference Python Implementation
```python
from lifelines import CoxPHFitter

def fit_cox(df, duration_col, event_col, covariates):
    cph = CoxPHFitter()
    df_clean = df[[duration_col, event_col] + covariates].dropna()
    cph.fit(df_clean, duration_col, event_col=event_col)
    cph.check_assumptions(df_clean, p_value_threshold=0.05)
    return cph.summary
```

## Validation Criteria
- [ ] Proportional hazards check is run.