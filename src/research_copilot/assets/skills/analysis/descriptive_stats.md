---
skill_id: "descriptive_stats"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy", "scipy"]
depends_on: ["profile_tabular"]
produces: ["analysis/03_analytical/descriptive_results.json"]
complexity: "basic"
---

# Skill: Descriptive Statistical Analysis

## Purpose
Compute robust descriptive statistics with bootstrapped uncertainty estimates for all analysis variables.

## When to Use
- After profiling, before any inferential testing
- For Table 1 / baseline characteristics
- To understand variable distributions before model selection

## When NOT to Use
- Data not yet profiled
- Only inferential results needed (descriptive is still recommended)

## Execution Protocol

### Step 1: Weight Application
- If sampling weights specified: compute weighted mean, weighted variance
- Weighted mean: μ_w = Σ(w_i × x_i) / Σ(w_i)
- Weighted variance: σ²_w = Σ[w_i × (x_i - μ_w)²] / (Σw_i - 1)
- Log effective sample size after weighting

### Step 2: Continuous Variable Summaries
Per variable compute: N, mean, SD, median, IQR, skewness (G1), kurtosis (G2), min, max, SE of mean, SE of median
- If |G1| > 1.0: report median/IQR as primary, mean/SD as secondary
- If |G1| ≤ 1.0: report mean/SD as primary

### Step 3: Categorical Variable Summaries
Per variable: N, category frequencies, proportions, mode, Shannon entropy
- Present as count (percentage) format

### Step 4: Bootstrapped Uncertainty
- B = 10,000 bootstrap resamples
- Compute BCa (bias-corrected and accelerated) 95% CI for mean and median
- BCa adjusts for skewness in bootstrap distribution
- If bootstrap CI much wider than parametric CI: heavy-tailed distribution

### Step 5: Grouped Descriptives
- If grouping variable specified (e.g., treatment vs control):
  - Compute descriptives per group
  - Compute standardized mean difference (Cohen's d) between groups
  - Flag variables with |d| > 0.25 (potential imbalance)

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Skewness | |G1| < 1.0 | Non-normal; median preferred | Use non-parametric tests |
| Bootstrap CI width | Similar to parametric CI | Heavy tails / outliers | Report bootstrap CI, not parametric |
| Group balance | |d| < 0.25 | Covariate imbalance | Adjust in model or match |

### Red Flags
- **Mean and median differ by > 1 SD**: distribution heavily skewed; do not use mean for inference
- **SD > mean for positive-only variable**: extreme skew or outliers; consider log transform
- **Bootstrap failed to converge**: increase B or check for degenerate distribution

## Reporting Template
> "Continuous variables are reported as mean (SD) or median [IQR] based on distributional symmetry. Categorical variables are reported as n (%). Bootstrapped 95% BCa confidence intervals (10,000 resamples) are provided for all estimates."

## Output Specification
- `analysis/03_analytical/descriptive_results.json`: per-variable statistics, bootstrap CIs, group comparisons, effect sizes

## Validation Checks
- [ ] N matches non-null count for each variable
- [ ] Bootstrap CIs within variable range
- [ ] Proportions sum to 1.0 per categorical variable
- [ ] Cohen's d correctly signed
