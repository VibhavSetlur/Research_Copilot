---
skill_id: "inferential_parametric"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scipy", "statsmodels", "pandas"]
depends_on: ["descriptive_stats", "detect_outliers"]
produces: ["analysis/03_analytical/parametric_results.json"]
complexity: "intermediate"
---

# Skill: Parametric Inferential Testing

## Purpose
Conduct parametric hypothesis tests (t-tests, ANOVA, regression) with assumption verification and effect size reporting.

## When to Use
- Research question involves comparing groups or testing associations
- Data meets parametric assumptions (normality, homoscedasticity, independence)
- Sample size adequate for asymptotic approximations (N ≥ 30 per group)

## When NOT to Use
- Assumptions severely violated → use inferential_nonparametric
- Sample size too small → use exact tests
- Data is dependent/paired → use paired tests or mixed_effects

## Decision Protocol

### Test Selection
| Design | DV Type | IV Type | Test |
|--------|---------|---------|------|
| 2 independent groups | Continuous | Binary (2 levels) | Independent t-test (Welch) |
| 2 paired groups | Continuous | Binary (2 levels, repeated) | Paired t-test |
| 3+ independent groups | Continuous | Categorical (3+ levels) | One-way ANOVA |
| 3+ paired groups | Continuous | Categorical (repeated) | Repeated measures ANOVA |
| 2×2 design | Continuous | 2 categorical factors | Two-way ANOVA |
| Continuous association | Continuous | Continuous | Pearson correlation / Linear regression |
| Continuous outcome, multiple predictors | Continuous | Mixed | Multiple regression (OLS) |

## Execution Protocol

### Step 1: Assumption Verification
**Normality:**
- Shapiro-Wilk (N < 5000) or Kolmogorov-Smirnov (N ≥ 5000)
- Visual: Q-Q plot
- If violated but N > 30 per group: CLT applies, proceed with caution

**Homoscedasticity (equal variances):**
- Levene's test (robust to non-normality) or Brown-Forsythe
- If p < 0.05: use Welch correction (unequal variance t-test, Welch ANOVA)

**Independence:**
- Study design check: are observations independent?
- If repeated measures: use paired tests or mixed_effects skill
- If clustered: use cluster-robust SEs

**Linearity (regression):**
- Residual vs fitted plot: check for patterns
- If non-linear: add polynomial terms or use GAM

### Step 2: Test Execution
- Run selected test
- Report: test statistic, degrees of freedom, p-value, exact p (not just < 0.05)
- Compute effect size: Cohen's d (t-test), η² (ANOVA), R² (regression)
- Compute 95% CI for effect size and mean differences

### Step 3: Multiple Comparison Correction
- If > 1 hypothesis tested: apply correction
- Default: Bonferroni (conservative) or Holm-Bonferroni (step-down, less conservative)
- For exploratory analyses: Benjamini-Hochberg FDR control
- Report both raw and adjusted p-values

### Step 4: Regression Diagnostics (if regression)
- Multicollinearity: VIF > 10 indicates problematic collinearity
- Residual normality: Shapiro-Wilk on residuals
- Residual homoscedasticity: Breusch-Pagan test
- Influential points: Cook's D > 4/n
- If diagnostics fail: report robust SEs (HC3) or use robust regression

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Normality | p > 0.05 or N > 30 | Non-normal | Non-parametric or transform |
| Homoscedasticity | Levene p > 0.05 | Unequal variances | Welch correction |
| VIF | < 10 | Multicollinearity | Remove correlated predictor |
| Cook's D | < 4/n | Influential observation | Report sensitivity analysis |

### Red Flags
- **p = 0.000**: report as p < 0.001, never p = 0.000
- **Effect size trivial (d < 0.10) but p < 0.05**: large sample driving significance; report effect size prominently
- **Significant but CI includes null**: check computation; this is impossible
- **VIF > 100**: perfect collinearity; one predictor is linear combination of others

## Domain Conventions

| Domain | Effect Size | Small | Medium | Large |
|--------|------------|-------|--------|-------|
| Psychology | Cohen's d | 0.20 | 0.50 | 0.80 |
| Medicine | Cohen's d | 0.20 | 0.50 | 0.80 |
| Education | Cohen's d | 0.20 | 0.50 | 0.80 |
| Economics | Standardized β | 0.10 | 0.30 | 0.50 |

## Reporting Template
> "An independent-samples Welch t-test indicated that [Group A] (M = [value], SD = [value], N = [value]) scored significantly [higher/lower] than [Group B] (M = [value], SD = [value], N = [value]), t([df]) = [value], p = [value], d = [value], 95% CI [lower, upper]. Levene's test indicated [equal/unequal] variances, F([df]) = [value], p = [value]."

## Output Specification
- `analysis/03_analytical/parametric_results.json`: test results, effect sizes, CIs, assumption test results, multiple comparison adjustments

## Validation Checks
- [ ] Test statistic matches formula
- [ ] p-value in [0, 1]
- [ ] Effect size in plausible range
- [ ] CI direction consistent with test statistic sign
- [ ] All assumptions tested and reported
