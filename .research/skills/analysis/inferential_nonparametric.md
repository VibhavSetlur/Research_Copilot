---
skill_id: "inferential_nonparametric"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "scipy", "numpy"]
estimated_tokens: 3500
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/nonparametric_results.json"]
---

# Skill: Non-Parametric Inferential Analysis

## Purpose
Execute non-parametric statistical tests (Mann-Whitney, Wilcoxon, Kruskal-Wallis) and permutation inference when data violates parametric assumptions.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to dataset |
| `group_column` | Str | Yes | Categorical grouping variable |
| `value_column` | Str | Yes | Continuous dependent variable |

## Methodological Framework

### 1. Mathematical Formulations
- **Mann-Whitney U Test**:
  Ranks all combined observations. Compute $U$:
  $$U_1 = n_1 n_2 + \frac{n_1(n_1+1)}{2} - R_1, \quad U_2 = n_1 n_2 - U_1$$
  where $R_1$ is the rank sum of group 1. Test statistic $U = \min(U_1, U_2)$.
- **Empirical Permutation Test**:
  Shuffles group labels to construct the empirical null distribution.
  $$\text{Empirical } p = \frac{1 + \sum_{m=1}^{M} I(|\Delta^*_m| \ge |\Delta_{\text{obs}}|)}{M + 1}$$
  where $\Delta_{\text{obs}}$ is the observed median difference and $\Delta^*_m$ are permuted differences.

## Step-by-Step Analytical Protocol

### Step 1: Normality Screening
Run Shapiro-Wilk test on `value_column` for each group. If p < .05, group distributions are non-normal. Proceed with non-parametric tests.

### Step 2: Test Selection & Execution
- If 2 independent groups -> Mann-Whitney U.
- If 2 paired groups -> Wilcoxon signed-rank.
- If > 2 independent groups -> Kruskal-Wallis H test, followed by post-hoc Dunn's tests with Bonferroni correction.

### Step 3: Permutation Testing
Execute a 10,000 iteration permutation test to compute empirical p-values for difference in medians.

## Diagnostics & Interpretation Guide (What to Look For)
- **Shapiro-Wilk W p < .05**:
  - *Interpret*: The data violates the assumption of normality. A t-test would be invalid.
  - *Action*: Continue with the non-parametric Mann-Whitney U or Wilcoxon test.
- **Discrepancy Between Mann-Whitney p and Permutation p**:
  - *Interpret*: Mann-Whitney assumes similar distribution shapes. If shapes differ greatly, Mann-Whitney tests differences in distributions, not medians.
  - *Action*: Rely on the empirical permutation test p-value, which is robust to shape differences.

## Writing & Reporting Standards
Report findings following this template:
> "Because the Shapiro-Wilk test indicated that the dependent variable was non-normally distributed ($W = \text{value}, p < .001$), we conducted a Mann-Whitney U test to compare groups. A permutation test with 10,000 shuffles was run to calculate empirical p-values for differences in medians. Group A ($Mdn = 12.0$) significantly differed from Group B ($Mdn = 8.5$), $U = \text{value}$, $p_{\text{asymp}} = .002$, $p_{\text{perm}} = .003$."

## Reference Python Implementation
```python
import numpy as np
from scipy import stats

def run_nonparametric(df, group_col, val_col):
    grp_names = df[group_col].unique()
    g1 = df[df[group_col] == grp_names[0]][val_col].values
    g2 = df[df[group_col] == grp_names[1]][val_col].values
    
    # Shapiro-Wilk
    _, p_w1 = stats.shapiro(g1)
    _, p_w2 = stats.shapiro(g2)
    
    # Mann-Whitney
    u_stat, mwu_p = stats.mannwhitneyu(g1, g2, alternative='two-sided')
    
    # Permutation
    obs_diff = np.median(g1) - np.median(g2)
    combined = np.concatenate([g1, g2])
    n1 = len(g1)
    
    perm_diffs = []
    for _ in range(10000):
        shuffled = np.random.permutation(combined)
        perm_diffs.append(np.median(shuffled[:n1]) - np.median(shuffled[n1:]))
        
    emp_p = (1 + np.sum(np.abs(perm_diffs) >= np.abs(obs_diff))) / 10001
    
    return {
        "normality_p": [p_w1, p_w2],
        "mwu_p": mwu_p,
        "permutation_p": emp_p,
        "median_diff": obs_diff
    }
```

## Output Specification
Produces a JSON detailing normality p-values, test statistics, and empirical p-values.

## Validation Criteria
- [ ] Post-hoc testing applies Bonferroni correction.
- [ ] Permutation count is at least 10,000.