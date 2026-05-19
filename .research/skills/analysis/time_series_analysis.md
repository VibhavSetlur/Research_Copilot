---
skill_id: "time_series_analysis"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["finance", "econometrics", "ecology"]
required_tools: ["python", "statsmodels", "scipy"]
depends_on: ["descriptive_stats", "profile_temporal"]
produces: ["analysis/03_analytical/time_series_results.json"]
complexity: "advanced"
---

# Skill: Time Series Analysis

## Purpose
Model temporal dependencies using ARIMA/SARIMAX, test for stationarity, and diagnose residual autocorrelation.

## When to Use
- Data is a single time series or panel with temporal structure
- Goal is forecasting, trend detection, or intervention analysis
- Temporal autocorrelation is present

## When NOT to Use
- Data is cross-sectional (no time ordering)
- Time series is too short (N < 30 for ARIMA)
- Only descriptive trend needed (plot and summarize)

## Decision Protocol

### Method Selection
| Pattern | Method |
|---------|--------|
| Stationary, no seasonality | ARMA(p, q) |
| Non-stationary, no seasonality | ARIMA(p, d, q) |
| Seasonal pattern | SARIMAX(p, d, q)(P, D, Q, s) |
| With exogenous predictors | SARIMAX with exog |
| Structural break | Interrupted time series |
| Volatility clustering | GARCH |
| Multiple series | VAR (Vector Autoregression) |

## Execution Protocol

### Step 1: Stationarity Assessment
- Visual: plot series, rolling mean, rolling SD
- ADF test: null = unit root (non-stationary); reject if p < 0.05
- KPSS test: null = stationary; reject if p < 0.05
- If non-stationary: difference (d = 1) and retest
- If seasonal non-stationary: seasonal difference (D = 1)

### Step 2: Model Identification
- ACF plot: identify MA order (q) from significant lags
- PACF plot: identify AR order (p) from significant lags
- Auto-ARIMA: search (p, d, q) grid, minimize AIC
- Seasonal: identify (P, D, Q) from seasonal ACF/PACF

### Step 3: Model Fitting
- Fit SARIMAX via maximum likelihood
- Check: optimizer converged, no singularities
- For SARIMAX: specify seasonal period (s = 12 for monthly, s = 4 for quarterly, s = 7 for daily)

### Step 4: Residual Diagnostics
- Ljung-Box test: null = residuals are white noise; p > 0.05 = pass
- Residual ACF: no significant autocorrelation
- Residual normality: Jarque-Bera test, Q-Q plot
- Residual homoscedasticity: plot residuals vs fitted

### Step 5: Model Selection
- Compare candidate models via AIC, BIC
- Prefer: lowest AIC (predictive accuracy) or BIC (parsimony)
- Out-of-sample validation: hold out last 20% of series, forecast, compare to actual

### Step 6: Forecasting
- Generate point forecasts and prediction intervals
- Forecast horizon: ≤ 1/3 of series length (beyond that, uncertainty explodes)
- Report: forecast values, 95% prediction intervals, fan chart

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| ADF p < 0.05 | Stationary | Non-stationary | Difference series |
| Ljung-Box p > 0.05 | White noise residuals | Residual autocorrelation | Increase p or q |
| Residual normality | Approximately normal | Non-normal | Check for outliers, use robust |
| Forecast accuracy | MAPE < 20% | Poor forecasts | Try alternative model |

### Red Flags
- **ACF decays very slowly**: long memory process; consider ARFIMA
- **Seasonal pattern not captured**: increase seasonal order or use STL decomposition
- **Forecast intervals too wide**: high uncertainty; report with appropriate caution
- **Structural break detected**: pre-break and post-break dynamics differ; model separately

## Reporting Template
> "The time series was modeled using a SARIMAX([p,d,q])([P,D,Q],[s]) model selected by minimizing AIC. The series was [stationary/differenced once]. Residual diagnostics confirmed no remaining autocorrelation (Ljung-Box Q = [value], p = [value]). The model explained [percentage]% of variance (R² = [value])."

## Output Specification
- `analysis/03_analytical/time_series_results.json`: model order, coefficients, diagnostics, forecast values, prediction intervals

## Validation Checks
- [ ] Stationarity tested and addressed
- [ ] Model order justified (AIC/PACF/ACF)
- [ ] Ljung-Box test reported
- [ ] Forecast horizon ≤ 1/3 of series length
