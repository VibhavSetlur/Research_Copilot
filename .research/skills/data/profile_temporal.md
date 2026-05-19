---
skill_id: "profile_temporal"
version: "3.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "statsmodels"]
estimated_tokens: 3000
depends_on: []
produces: ["data/01_ingested/profile_temporal.json"]
---

# Skill: Time Series Profiling

## Purpose
Analyze temporal data structures to identify frequency, gaps, stationarity, and seasonal components.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to dataset |
| `time_column` | Str | Yes | Column name containing date/time variables |
| `value_column` | Str | Yes | Continuous column for time-series diagnostics |

## Execution Protocol

### Step 1: Chronological Alignment
- Convert `time_column` to datetime objects. Sort rows chronologically.
- Infer temporal frequency (e.g., daily `D`, monthly `M`).

### Step 2: Gap & Discontinuity Analysis
- Check for missing intervals based on inferred frequency.
- Locate the longest continuous block of observations.
- Compute the proportion of missing time points.

### Step 3: Stationarity Diagnostics
- Execute Augmented Dickey-Fuller (ADF) test on `value_column`.
- Execute Kwiatkowski-Phillips-Schmidt-Shin (KPSS) test.
- Categorize series as stationary, trend-stationary, or non-stationary.

### Step 4: Seasonal Decomposition
- Run STL (Seasonal-Trend decomposition using Loess) to extract seasonal, trend, and residual components.
- Calculate strength of trend and strength of seasonality indices.

## Output Specification
Produces:
- `data/01_ingested/profile_temporal.json` containing stationarity parameters, gap lists, and decomposition metrics.

## Validation Criteria
- [ ] Time frequency is matching standard Pandas offset aliases.
- [ ] ADF and KPSS test statistics and p-values are valid numeric values.