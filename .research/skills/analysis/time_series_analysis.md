---
skill_id: "time_series_analysis"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "statsmodels", "scipy"]
estimated_tokens: 3500
depends_on: ["descriptive_stats", "profile_temporal"]
produces: ["analysis/03_analytical/time_series_results.json"]
---

# Skill: Advanced Time Series Analysis

## Purpose
Estimate temporal models (SARIMAX) while testing for residual autocorrelation using Ljung-Box tests.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to series data |
| `value_col` | Str | Yes | Target series |

## Methodological Framework
- **Ljung-Box Test**:
  Checks if autocorrelations of residuals are non-zero:
  $$Q = n(n+2) \sum_{k=1}^{h} \frac{\hat{\rho}^2_k}{n-k}$$
  where $\hat{\rho}_k$ is the residual autocorrelation at lag $k$.

## Step-by-Step Analytical Protocol
1. Verify stationarity (differencing if needed).
2. Fit SARIMAX. Iterate models to minimize AIC.
3. Check residuals for white noise using Ljung-Box.

## Diagnostics & Interpretation Guide (What to Look For)
- **Ljung-Box Test p < .05**:
  - *Interpret*: Residuals are autocorrelated. The model has omitted temporal structures.
  - *Action*: Increase autoregressive (p) or moving average (q) terms.

## Writing & Reporting Standards
> "We modeled the time series using a SARIMAX(1,1,1) model. Residual diagnostics verified no remaining autocorrelation via the Ljung-Box test at lag 10 ($Q = \text{value}, p = .34$)."

## Reference Python Implementation
```python
import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX

def fit_sarimax(series, order):
    model = SARIMAX(series, order=order)
    results = model.fit(disp=False)
    lb_test = sm.stats.acorr_ljungbox(results.resid, lags=[10], return_df=True)
    return results.summary(), lb_test['lb_pvalue'].values[0]
```

## Validation Criteria
- [ ] Residual Ljung-Box p-value is > .05.