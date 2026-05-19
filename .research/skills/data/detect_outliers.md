---
skill_id: "detect_outliers"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy", "scipy"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/outlier_report.json"]
complexity: "intermediate"
---

# Skill: Outlier Detection & Characterization

## Purpose
Identify, classify, and characterize outliers using multiple complementary methods to distinguish data errors from legitimate extreme values.

## When to Use
- After profiling, before any modeling
- When descriptive stats show extreme skewness or kurtosis
- When domain knowledge suggests plausible value bounds

## When NOT to Use
- Data is already cleaned and validated
- Sample size < 20 (outlier tests unreliable)
- All values are categorical/nominal

## Decision Protocol

### Method Selection
| Data Distribution | Primary Method | Secondary Method |
|-------------------|---------------|-------------------|
| Approximately normal | Z-score (|z| > 3) | Grubbs' test |
| Skewed or unknown | IQR fence (1.5× or 3×) | Modified Z-score (MAD) |
| Multivariate | Mahalanobis distance | Isolation Forest |
| Time series | Rolling IQR | STL decomposition residuals |
| Small sample (N < 30) | Dixon's Q test | Visual inspection only |

## Execution Protocol

### Step 1: Univariate Detection
**IQR Method (default, robust to non-normality):**
- Q1, Q3 = 25th, 75th percentiles
- IQR = Q3 - Q1
- Lower fence = Q1 - 1.5×IQR (mild), Q1 - 3×IQR (extreme)
- Upper fence = Q3 + 1.5×IQR (mild), Q3 + 3×IQR (extreme)
- Flag values beyond fences; classify as mild or extreme

**Modified Z-Score (MAD-based, more robust):**
- MAD = median(|Xi - median(X)|)
- Mi = 0.6745 × (Xi - median) / MAD
- Flag |Mi| > 3.5

**Z-Score (only if approximately normal):**
- Flag |z| > 3 for outliers, |z| > 4 for extreme
- Verify normality first (Shapiro-Wilk or visual Q-Q)

### Step 2: Multivariate Detection
- Compute Mahalanobis distance: D² = (x - μ)' Σ⁻¹ (x - μ)
- Compare to χ²(p) critical value at α = 0.001
- Flag observations exceeding critical value
- Alternative: Isolation Forest with contamination=0.05

### Step 3: Contextual Classification
For each flagged outlier, classify:
- **Data error**: impossible value (negative age, BMI > 100), typo (decimal shift), duplicate entry
- **Legitimate extreme**: plausible but rare (income > $1M, age > 90)
- **Novel observation**: represents a distinct subpopulation
- **Measurement artifact**: instrument saturation, detection limit

### Step 4: Impact Assessment
- Compute statistics with and without outliers
- Compare: mean shift %, SD change %, correlation changes
- If outlier removal changes conclusions → report both versions
- Never silently drop outliers; always document

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Outlier proportion | < 5% of observations | Systematic issue | Investigate data collection process |
| Single-method flag | Flagged by ≥ 2 methods | Confirmed outlier | Classify and document |
| Influence check | Cook's D < 4/n | Influential point | Report sensitivity analysis |

### Red Flags
- **> 10% flagged as outliers**: method too sensitive or data fundamentally non-standard; widen thresholds
- **All outliers in one subgroup**: subgroup may have different data-generating process; stratify analysis
- **Outliers drive the entire effect**: effect disappears without them → report as exploratory only
- **Impossible values**: data error → correct if source available, otherwise exclude with documentation

## Domain Conventions

| Domain | Plausible Bounds | Common Outlier Sources |
|--------|-----------------|----------------------|
| Clinical | HR: 20-300, BP: 40-300, Temp: 30-45°C | Unit errors (lb vs kg), decimal shifts |
| Finance | Returns: -100% to +1000%, Volume > 0 | Flash crashes, data feed errors |
| Survey | Likert: 1-5, Age: 0-120 | Straight-lining, satisficing responses |
| Genomics | Expression: ≥ 0, p-value: [0,1] | Batch effects, probe failures |

## Reporting Template
> "Outlier detection was performed using [method] on [N] variables. [Count] observations ([percentage]%) were flagged as outliers, of which [count] were classified as data errors and [count] as legitimate extreme values. Sensitivity analysis showed that excluding outliers changed the mean of [variable] by [percentage]% but did not alter the direction of [key finding]."

## Output Specification
- `data/01_ingested/outlier_report.json`: per-variable outlier counts, flagged row indices, classification, impact assessment

## Validation Checks
- [ ] At least two detection methods applied
- [ ] Each outlier classified (error/legitimate/novel/artifact)
- [ ] Impact assessment computed
- [ ] No outliers silently dropped
