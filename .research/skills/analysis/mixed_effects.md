---
skill_id: "mixed_effects"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "statsmodels", "scipy"]
estimated_tokens: 3000
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/mixed_effects_results.json"]
---

# Skill: Mixed Effects Modeling

## Purpose
Fit Linear Mixed Models (LMM) and calculate ICC to evaluate nested data structures.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to dataset |
| `formula` | Str | Yes | Model formula |
| `groups` | Str | Yes | Grouping variable |

## Methodological Framework

### 1. Intraclass Correlation Coefficient (ICC)
$$\text{ICC} = \frac{\sigma^2_{u0}}{\sigma^2_{u0} + \sigma^2_{\epsilon}}$$
Measures the proportion of total variance explained by grouping differences.

## Step-by-Step Analytical Protocol
1. **Unconditional Model**: Fit empty model (no predictors) to calculate base ICC.
2. **Conditional Model**: Fit full model with fixed and random parameters using REML.

## Diagnostics & Interpretation Guide (What to Look For)
- **ICC < 0.05**:
  - *Interpret*: Very little variance is explained by grouping. Clustered modeling might be unnecessary.
  - *Action*: Run standard OLS with cluster-robust standard errors and compare fit.
- **Singular Fit Warnings**:
  - *Interpret*: Random effect variance is estimated at zero, meaning the model is overparameterized.
  - *Action*: Simplify the random effects structure (e.g. drop random slopes, keep only random intercepts).

## Writing & Reporting Standards
> "To adjust for nesting within groups, we fitted a Linear Mixed Model using REML. An initial unconditional model indicated an Intraclass Correlation Coefficient (ICC) of .18, justifying mixed effects modeling. Fixed effect coefficients are reported with standard errors: $b = 3.42, SE = 0.54, p < .001$."

## Reference Python Implementation
```python
import statsmodels.formula.api as smf

def fit_lmm(df, formula, group_col):
    model = smf.mixedlm(formula, df, groups=df[group_col])
    results = model.fit()
    return results.summary()
```

## Validation Criteria
- [ ] ICC is computed.
- [ ] Singular fit warnings are handled.