---
skill_id: "longitudinal_analysis"
version: "1.0.0"
category: "analysis"
depends_on: ["profile_tabular", "assumption_validator"]
produces: ["02_experiments/<exp>/outputs/analysis/longitudinal_results.json"]
complexity: "intensive"
---

# Skill: Longitudinal Analysis

## Purpose
Analyze repeated-measures and panel data. Covers paired t-tests, repeated measures ANOVA, linear mixed effects (LME), and latent growth curve (LGC) models.

---

## Protocol

### Step 1: Detect Data Structure
Identify:
- **Subject ID column**: unique identifier for each participant/unit
- **Time column**: measurement occasion (numeric or ordered categorical)
- **Outcome variable(s)**: repeated measurements
- **Covariates**: time-invariant (e.g., gender) and time-varying (e.g., treatment status)

Count: number of subjects (N), number of time points (T), balance (balanced vs unbalanced).

### Step 2: Select Method by Decision Table

| Time Points | Trend | Individual Differences | Method |
|-------------|-------|----------------------|--------|
| 2 | Any | Not needed | Paired t-test |
| 2 | Any | Need to adjust for covariates | ANCOVA on change score |
| 3+ | Linear | Not needed | Repeated measures ANOVA |
| 3+ | Linear | Yes (random slopes) | LME: `outcome ~ time + (1 + time \| subject)` |
| 3+ | Nonlinear | Yes | LME with polynomial time or splines |
| 3+ | Any | Latent trajectory classes | Latent Growth Curve (SEM) |
| Irregular spacing | Any | Yes | LME with continuous time |
| Unbalanced | Any | Yes | LME (handles missing time points) |

### Step 3: Paired t-Test (2 Time Points)
`scipy.stats.ttest_rel(time1, time2)`. Report: mean difference, 95% CI, t(df), p-value, Cohen's d_z = mean_diff / SD_diff.

### Step 4: Repeated Measures ANOVA (3+ Time Points, Balanced)
`pingouin.rm_anova(dv, subject, within, data)`. Check sphericity with Mauchly's test. If violated, apply Greenhouse-Geisser correction. Report: F(df_num, df_den), p, η²_p (partial eta-squared).

### Step 5: Linear Mixed Effects Model
Use `statsmodels.MixedLM` or `statsmodels` formula API:
```python
import statsmodels.formula.api as smf
model = smf.mixedlm("outcome ~ time + treatment + time:treatment",
                    data=df, groups=df["subject_id"],
                    re_formula="~time")
result = model.fit(reml=True)
```
Report: fixed effects (β, SE, 95% CI, p), random effects variance components, ICC, AIC/BIC.

### Step 6: Nonlinear Trends
Add polynomial terms: `time + time² + time³`, or use splines:
```python
from patsy import dmatrix
spline_basis = dmatrix("bs(time, df=4, degree=3)", {"time": df["time"]})
```
Compare models with likelihood ratio test or AIC.

### Step 7: Latent Growth Curve Model (SEM)
Use `semopy` or manual specification:
- Intercept factor: loadings fixed to 1 at all time points
- Slope factor: loadings fixed to 0, 1, 2, ... (linear) or time values
- Estimate: mean and variance of intercept and slope factors
- Fit indices: CFI, TLI, RMSEA, SRMR

### Step 8: Diagnostics
- Residual plots: residuals vs fitted, residuals vs time
- Random effects: check normality of BLUPs
- Influence: Cook's D for mixed models
- Missing data: verify MAR assumption, compare completers vs dropouts

### Step 9: Output
Save to `02_experiments/<exp>/outputs/analysis/longitudinal_results.json`:
- Method used with rationale
- Fixed effects table (β, SE, CI, p)
- Random effects variance components
- Model fit indices (AIC, BIC, ICC)
- Diagnostics results
- Predicted trajectories plot data

---

## Validation
- [ ] Data structure identified (N subjects, T time points, balanced/unbalanced)
- [ ] Method selected per decision table
- [ ] Sphericity checked (if RM ANOVA)
- [ ] Random effects structure justified
- [ ] Model fit indices reported
- [ ] Diagnostics: residuals, random effects normality
- [ ] Results saved to JSON
