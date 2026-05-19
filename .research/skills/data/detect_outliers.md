---
skill_id: "detect_outliers"
version: "3.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy", "scikit-learn", "scipy"]
estimated_tokens: 3000
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/outliers_report.json", "data/02_processed/data_flagged.csv"]
---

# Skill: Outlier & Anomaly Detection

## Purpose
Identify univariate and multivariate outliers using robust statistical methods and evaluate their influence on data summaries.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to dataset |
| `numeric_columns` | List | Yes | Numeric columns to scan |

## Execution Protocol

### Step 1: Univariate Outlier Scanning
- Calculate Tukey's IQR boundaries (1.5 * IQR and 3.0 * IQR).
- Calculate Modified Z-scores using Median Absolute Deviation (MAD) to handle non-normal distributions:
  - `MAD = median(|x - median(x)|)`
  - `Z = 0.6745 * (x - median(x)) / MAD`
  - Flag values where `|Z| > 3.5`.

### Step 2: Multivariate Anomaly Detection
- Apply Isolation Forest: Scale variables using `RobustScaler`, fit model with contamination set to 0.05.
- Compute Mahalanobis Distance for multivariate normal assumptions. Compare to Chi-Square distribution threshold.

### Step 3: Outlier Influence Assessment (Sensitivity Analysis)
- Calculate the difference in mean and variance for each column when flagged outliers are removed.
- If variance shifts > 20%, log the column as "outlier-sensitive".

### Step 4: Data Export
- Append binary flag column `outlier_flag` (1 if outlier in univariate or multivariate, 0 otherwise) to data.

## Output Specification
Produces:
- `data/01_ingested/outliers_report.json` mapping flags and sensitivity scores.
- `data/02_processed/data_flagged.csv` containing outlier flag columns.

## Validation Criteria
- [ ] Sensitivity score is calculated for all targeted numeric columns.
- [ ] Outlier flags are binary (0/1).