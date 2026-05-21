# Assumption Validator (Pre-Execution Gate)

## Purpose
Before any analysis script runs, this skill verifies its statistical assumptions against the data profile. If a required assumption fails, it blocks execution of the primary method, logs the failure to dead ends, and routes to a designated fallback method.

---

## Protocol

For each analytical task:
1. **Identify the Method**: Detect the method planned for the research question (e.g., OLS regression, t-test, ANOVA).
2. **Retrieve Stated Assumptions**: Read the planned assumptions from the methodology layout.
3. **Execute Statistical Assumption Tests**: Run specific validation checks on the actual input datasets.
4. **Determine Pass/Fail**: Evaluate the test statistics and p-values against standard criteria.
5. **Route Execution**:
   - **PASS**: Allow the primary script to execute.
   - **FAIL**: Block execution, log to dead ends, and trigger the fallback method (e.g., nonparametric alternative).

---

## Statistical Tests & Fallback Mapping

| Method | Assumption | Statistical Test | Criteria | Fallback Method |
|---|---|---|---|---|
| **t-test (independent)** | Normality of groups | Shapiro-Wilk test | $p \ge 0.05$ | Mann-Whitney U test |
| | Homogeneity of variance | Levene's test | $p \ge 0.05$ | Welch's t-test |
| **ANOVA (one-way)** | Normality of residuals | Shapiro-Wilk or Kolmogorov-Smirnov | $p \ge 0.05$ | Kruskal-Wallis test |
| | Homogeneity of variances | Levene's test | $p \ge 0.05$ | Welch's ANOVA |
| **OLS Regression** | Linearity | Harvey-Collier or Ramsey RESET | $p \ge 0.05$ | Generalized Additive Models (GAM) / Polynomial |
| | Homoscedasticity | Breusch-Pagan or White test | $p \ge 0.05$ | Weighted Least Squares (WLS) or robust errors |
| | Normality of residuals | Jarque-Bera or Shapiro-Wilk | $p \ge 0.05$ | Robust regression (RLM) or bootstrapping |
| | No Multicollinearity | Variance Inflation Factor (VIF) | $VIF < 5$ (or $< 10$) | Ridge/Lasso Regression or drop collinear feature |
| | Independence of residuals | Durbin-Watson test | $1.5 < DW < 2.5$ | Newey-West standard errors or ARMA modeling |
| **Time Series (ARIMA)** | Stationarity | Augmented Dickey-Fuller (ADF) | $p < 0.05$ | Differencing ($d \ge 1$) or detrending |

---

## Output Validation Report

The validator generates `reports/analysis/assumption_validation_{question_id}.json` with the following structure:

```json
{
  "question_id": "q1",
  "planned_method": "OLS",
  "timestamp": "2026-05-19T21:30:00Z",
  "verdict": "PASS | FAIL",
  "results": [
    {
      "assumption": "Normality of residuals",
      "test_name": "Shapiro-Wilk",
      "statistic": 0.985,
      "p_value": 0.123,
      "status": "PASS",
      "message": "Residuals are normally distributed."
    },
    {
      "assumption": "Homoscedasticity",
      "test_name": "Breusch-Pagan",
      "statistic": 12.4,
      "p_value": 0.002,
      "status": "FAIL",
      "message": "Heteroscedasticity detected (p < 0.05)."
    }
  ],
  "routing": {
    "action": "execute_fallback | execute_primary",
    "target_method": "Robust Regression (RLM)",
    "reason": "Failed Homoscedasticity assumption."
  }
}
```

---

## Sample-Size-Adaptive Normality Testing

The choice of normality test depends on sample size. Use this decision table before running any parametric test:

| Sample Size (N) | Normality Test | Rationale |
|-----------------|---------------|-----------|
| N < 30 | Exact tests (permutation / bootstrap) | Shapiro-Wilk unreliable at very small N; exact tests have correct Type I error |
| 30 ≤ N < 5000 | Shapiro-Wilk | Most powerful omnibus test for normality in this range |
| N ≥ 5000 | Kolmogorov-Smirnov (with Lilliefors correction) | Shapiro-Wilk becomes oversensitive at large N; KS is more stable |

### Implementation Note

For N ≥ 5000, supplement with visual diagnostics (Q-Q plot, histogram) because ANY formal test will reject trivial deviations. Use effect-size-based normality assessment: skewness |< 2| and kurtosis |< 7| as practical thresholds.

---

## Fallback Chain: OLS → Robust → Nonparametric

When OLS assumptions fail, follow this cascade. Each step has a 1-line rationale:

| Step | Method | Trigger | Rationale |
|------|--------|---------|-----------|
| 1 | **OLS** (baseline) | All assumptions pass | Most efficient estimator under Gauss-Markov conditions |
| 2 | **OLS + Robust SE** (HC3) | Heteroscedasticity only | Preserves coefficient estimates; corrects standard errors for unequal variance |
| 3 | **RLM** (Huber/bisquare) | Outliers or non-normal residuals | Down-weights influential observations; resistant to heavy-tailed errors |
| 4 | **Bootstrap** (percentile or BCa) | Non-normal residuals + small N | Distribution-free inference; valid for any sample size with 1000+ resamples |
| 5 | **Nonparametric** (rank-based / permutation) | Multiple assumption failures | Makes no distributional assumptions; valid under minimal conditions |

### Decision Rules

- If ONLY heteroscedasticity fails → Step 2 (Robust SE). Do NOT abandon OLS coefficients.
- If heteroscedasticity + non-normality → Step 3 (RLM).
- If multicollinearity (VIF > 10) → Ridge/Lasso BEFORE applying fallback chain.
- If N < 30 AND assumptions fail → Step 4 (Bootstrap) or Step 5 (Nonparametric).
- Document which step was used and why in the experiment `decisions.yaml`.

---

## Integration

- Run automatically prior to script execution.
- If a check fails, the orchestrator updates `.research/cache/state.json` with the fallback target and writes a dead end entry describing the violation to `docs/dead_ends/`.
- CLI Command: `python .research/scripts/utils/assumption_validator.py --data <path> --config <config_path>`
