---
skill_id: "descriptive_stats"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy", "scipy"]
estimated_tokens: 4000
depends_on: ["profile_tabular"]
produces: ["analysis/03_analytical/descriptive_results.json"]
---

# Skill: Descriptive Statistical Analysis

## Purpose
Perform robust descriptive statistical profiling to extract central tendency, dispersion, distribution shape, and uncertainty limits via bootstrapping.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to processed dataset |
| `variables` | List | Yes | Continuous and categorical variables to analyze |
| `weights` | Str | No | Column name for survey/sampling weights |

## Methodological Framework

### 1. Mathematical Formulations
- **Weighted Mean ($\mu_w$)**:
  $$\mu_w = \frac{\sum_{i=1}^{N} w_i x_i}{\sum_{i=1}^{N} w_i}$$
- **Weighted Variance ($\sigma^2_w$)**:
  $$\sigma^2_w = \frac{\sum_{i=1}^{N} w_i (x_i - \mu_w)^2}{\sum_{i=1}^{N} w_i - 1}$$
- **Fisher-Pearson Standardized Skewness ($G_1$)**:
  $$G_1 = \frac{n}{(n-1)(n-2)} \sum_{i=1}^{n} \left( \frac{x_i - \bar{x}}{s} \right)^3$$
- **Excess Kurtosis ($G_2$)**:
  $$G_2 = \frac{n(n+1)}{(n-1)(n-2)(n-3)} \sum_{i=1}^{n} \left( \frac{x_i - \bar{x}}{s} \right)^4 - \frac{3(n-1)^2}{(n-2)(n-3)}$$
- **Bias-Corrected and Accelerated (BCa) Bootstrap Confidence Interval**:
  Adjusts the endpoints of the bootstrap distribution to account for skewness and bias. The adjusted endpoints are $\alpha_1$ and $\alpha_2$:
  $$\alpha_1 = \Phi\left( z_0 + \frac{z_0 + z_{(\alpha/2)}}{1 - a(z_0 + z_{(\alpha/2)})} \right), \quad \alpha_2 = \Phi\left( z_0 + \frac{z_0 + z_{(1-\alpha/2)}}{1 - a(z_0 + z_{(1-\alpha/2)})} \right)$$
  where $z_0$ is the bias-correction parameter, $a$ is the acceleration parameter (estimated via jackknife), and $\Phi$ is the standard normal CDF.

## Step-by-Step Analytical Protocol

### Step 1: Weight and Missingness Filtering
Identify if the research brief specifies sampling weights. If yes, apply the weighted formulations. Drop missing cases row-wise per variable, and log the final valid sample size ($N$).

### Step 2: Distribution Shape Assessment
Compute Skewness and Kurtosis. If skewness is outside the range $[-1.0, 1.0]$ or kurtosis is outside $[-2.0, 2.0]$, flag the variable as highly skewed.

### Step 3: Bootstrapped Uncertainty Estimation
For all continuous variables, run $B = 10,000$ bootstrap iterations. Extract the 95% BCa confidence interval for the mean and median.

## Diagnostics & Interpretation Guide (What to Look For)
- **High Skewness (Skewness > 1.0 or < -1.0)**:
  - *Interpret*: The mean is pulled by extreme outliers. Do not rely solely on the mean; report the median and IQR.
  - *Action*: Inform the routing agent that parametric tests on this raw variable may violate normality assumptions.
- **Zero Variance (Standard Deviation = 0)**:
  - *Interpret*: The variable is constant across all observations.
  - *Action*: Flag and drop this variable from any subsequent regression modeling.
- **Outlier Density**: Compare the bootstrapped BCa confidence interval to the standard Student's $t$ interval. A wider BCa interval indicates heavy-tailed distributions and potential outlier influence.

## Writing & Reporting Standards
Report descriptive statistics in the text or Table 1 following this template:
> "Continuous variables were summarized using means and standard deviations (SD), or medians and interquartile ranges (IQR) for skewed distributions. Standard errors (SE) and 95% bootstrapped bias-corrected and accelerated (BCa) confidence intervals were calculated using 10,000 resamples. For example, age was normally distributed ($M = 45.32$, $SD = 12.11$, $95\%\text{ BCa CI } [44.18, 46.46]$, $N = 432$). Income was highly skewed ($M = 54,200$, $SD = 34,100$, $\text{Median } = 42,000$, $\text{IQR } [31,000, 68,000]$)."

## Reference Python Implementation
```python
import numpy as np
import pandas as pd
from scipy import stats

def run_descriptives(df, var, weight_col=None):
    x = df[var].dropna().values
    skew_val = stats.skew(x)
    kurt_val = stats.kurtosis(x)
    
    if weight_col:
        w = df.loc[df[var].notna(), weight_col].values
        mean_val = np.average(x, weights=w)
        var_val = np.average((x - mean_val)**2, weights=w) * (len(x) / (len(x) - 1))
        sd_val = np.sqrt(var_val)
    else:
        mean_val = np.mean(x)
        sd_val = np.std(x, ddof=1)
        
    boot_res = stats.bootstrap((x,), np.mean, confidence_level=0.95, method='BCa', n_resamples=10000)
    ci_low, ci_high = boot_res.confidence_interval.low, boot_res.confidence_interval.high
    
    return {
        "mean": float(mean_val),
        "sd": float(sd_val),
        "skewness": float(skew_val),
        "kurtosis": float(kurt_val),
        "ci_95": [float(ci_low), float(ci_high)],
        "n": int(len(x))
    }
```

## Output Specification
Produces a structured JSON file mapping variable names to calculated metrics.

## Validation Criteria
- [ ] Sample size (n) matches non-null count.
- [ ] Skewness and kurtosis calculations are present.
- [ ] Bootstrap intervals do not exceed the actual range of the variable.