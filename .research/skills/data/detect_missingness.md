---
skill_id: "detect_missingness"
version: "3.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "scipy", "statsmodels"]
estimated_tokens: 3000
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/missingness_report.json"]
---

# Skill: Missing Data Mechanism Analysis

## Purpose
Analyze missing data properties to classify missingness mechanisms (MCAR, MAR, MNAR) and select statistical imputation adjustments.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to dataset |
| `profile_path` | Path | Yes | Path to data profile JSON |

## Execution Protocol

### Step 1: Missingness Matrix Mapping
- Binarize dataset to indicate null values (1 if missing, 0 if present).
- Compute correlation matrix of missingness indicators.

### Step 2: Little's MCAR Test
- Run Little's MCAR (Missing Completely at Random) test.
- If N > 10,000, perform test on a random sample of 5,000 rows to prevent execution timeouts.

### Step 3: Missingness Association Check (MAR vs MCAR)
- For variables with missing values, construct binary indicators.
- Fit logistic regression models using other complete variables as predictors for the binary indicators.
- Significant predictors indicate MAR (Missing at Random) patterns.

### Step 4: Decision Tree Imputation Routing
- Route to appropriate strategies:
  - If missingness < 5%: Recommend complete case analysis (listwise deletion).
  - If MCAR: Recommend simple imputation (mean/mode/median) or random draw.
  - If MAR: Recommend Multiple Imputation by Chained Equations (MICE) or FIML (Full Information Maximum Likelihood).
  - If MNAR: Add warnings advising pattern-mixture modeling.

## Output Specification
Produces:
- `data/01_ingested/missingness_report.json` mapping test results and adjustments.

## Validation Criteria
- [ ] Imputation recommendation matches the output category of the decision route.
- [ ] P-values are valid decimals.