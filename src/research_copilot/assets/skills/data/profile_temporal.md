---
skill_id: "profile_temporal"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/temporal_profile.json"]
complexity: "intermediate"
---

# Skill: Temporal Data Profiling

## Purpose
Profile time-indexed data to understand temporal structure, frequency, seasonality, gaps, and stationarity properties.

## When to Use
- Dataset has datetime columns
- Data is time series or panel (longitudinal)
- Before time series analysis or forecasting

## When NOT to Use
- No temporal columns exist
- Time is not analytically relevant (e.g., timestamp is metadata only)

## Execution Protocol

### Step 1: Temporal Column Identification
- Identify all datetime columns
- Determine primary time index (most granular, most complete)
- Identify secondary time indices (e.g., event dates, cohort dates)

### Step 2: Temporal Range & Span
- Min/max dates, total span (days, months, years)
- Number of unique time points
- Time point frequency: infer from median interval (daily, weekly, monthly, quarterly, annual, irregular)

### Step 3: Gap Detection
- Compute intervals between consecutive time points
- Identify gaps: intervals > 2× median interval
- Classify gaps: expected (weekends, holidays) vs unexpected
- Report gap count, total gap duration, largest gap

### Step 4: Seasonality Assessment
- Decompose by time unit: day-of-week, month-of-year, quarter
- Compute mean value per time unit
- Visualize: seasonal plot, autocorrelation function (ACF)
- Flag strong seasonal patterns (coefficient of variation across seasons > 0.20)

### Step 5: Stationarity Screening
- Visual inspection: rolling mean and rolling SD plots
- Augmented Dickey-Fuller test: null = unit root (non-stationary)
- If non-stationary: determine differencing order (d) needed
- Check for structural breaks: Chow test or visual inspection

### Step 6: Panel Structure (if applicable)
- Identify cross-sectional units (e.g., firms, individuals, regions)
- Compute: N units, T time points, balanced vs unbalanced panel
- For unbalanced: entry/exit patterns, attrition rate
- Gap analysis per unit

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| ADF p < 0.05 | Stationary | Non-stationary series | Difference or use ARIMA/SARIMAX |
| Gap frequency | < 5% of intervals | Irregular sampling | Interpolate or use irregular-time models |
| Seasonality strength | CV < 0.20 across seasons | Strong seasonality | Include seasonal terms or use SARIMAX |
| Panel balance | Balanced or > 80% complete | High attrition | Use unbalanced panel methods |

### Red Flags
- **Non-chronological ordering**: sort by time index before any analysis
- **Multiple time zones**: standardize to single timezone (UTC preferred)
- **Future dates in historical data**: data entry error or projection; flag
- **Duplicate timestamps**: aggregate or investigate (multiple events at same time)

## Output Specification
- `data/01_ingested/temporal_profile.json`: time range, frequency, gaps, seasonality assessment, stationarity test results, panel structure (if applicable)

## Validation Checks
- [ ] Time index is monotonically non-decreasing
- [ ] Date range is plausible (no year 1900 or 2100 unless expected)
- [ ] Frequency is classified
- [ ] Stationarity test result recorded
