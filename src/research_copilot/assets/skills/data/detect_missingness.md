---
skill_id: "detect_missingness"
version: "7.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "pandas", "numpy", "scipy"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/missingness_report.json"]
complexity: "intermediate"
---

# Skill: Missing Data Mechanism Detection & Strategy Selection

## Purpose
Diagnose the mechanism of missingness (MCAR, MAR, MNAR) and recommend appropriate handling strategies based on pattern, proportion, and mechanism.

## When to Use
- After profiling reveals missing data
- Before any analysis that requires complete cases
- When > 5% of any analysis variable is missing

## When NOT to Use
- Dataset has zero missing values
- Missingness is by design (e.g., skip patterns in surveys)

## Decision Protocol

### Missingness Mechanism
```
IF Little's MCAR test p > 0.05 → MCAR (missing completely at random)
ELIF missingness predictable from observed data → MAR (missing at random)
ELIF missingness depends on the missing value itself → MNAR (missing not at random)
ELSE → Assume MAR (conservative default)
```

### Strategy Selection by Mechanism
| Mechanism | Missing < 5% | Missing 5-20% | Missing > 20% |
|-----------|-------------|---------------|---------------|
| MCAR | Complete-case | Multiple imputation | Multiple imputation + sensitivity |
| MAR | Complete-case | Multiple imputation (MICE) | Multiple imputation + pattern-mixture |
| MNAR | Complete-case | Selection models | Pattern-mixture + sensitivity analysis |

## Execution Protocol

### Step 1: Missingness Pattern Mapping
- Compute missingness matrix: binary indicator per cell
- Visualize: heatmap or `missingno` matrix plot
- Compute pairwise missingness: which variables are missing together
- Identify monotone patterns (if A missing → B also missing)

### Step 2: Quantify Missingness
- Per-variable: count, proportion, 95% CI for proportion
- Overall: total missing cells / total cells
- By subgroup: missing rate stratified by each categorical variable
- Flag variables exceeding 20% missing

### Step 3: Mechanism Testing
**Little's MCAR Test** (N < 5000):
- Null hypothesis: data is MCAR
- If p < 0.05: reject MCAR → data is MAR or MNAR

**Missingness Correlation:**
- For each pair of variables, correlate missingness indicators
- Significant correlations suggest MAR (missingness in A depends on observed B)

**Pattern Analysis:**
- Compare distributions of observed vs missing cases for each variable
- If distributions differ systematically → MAR or MNAR

### Step 4: Strategy Recommendation
Based on mechanism + proportion, recommend:
1. **Complete-case analysis**: only if MCAR and < 5% missing
2. **Single imputation** (median/mode): only for descriptive stats, never for inference
3. **Multiple imputation (MICE)**: default for MAR, 5-20 imputations
4. **Maximum likelihood**: if using SEM or mixed models
5. **Inverse probability weighting**: if missingness mechanism is well-modeled
6. **Sensitivity analysis**: always for MNAR or > 20% missing

### Step 5: Imputation Quality Checks (if imputing)
- Compare distributions of observed vs imputed values
- Check that imputed values are plausible (within observed range for bounded variables)
- Verify between-imputation variance is reasonable
- Run analysis on each imputed dataset; check result consistency

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Little's MCAR p > 0.05 | MCAR plausible | Data not MCAR | Use MAR/MNAR methods |
| Missingness correlation | No strong correlations | MAR likely | Include predictors in imputation model |
| Imputed vs observed | Similar distributions | Imputation model misspecified | Add more predictors, change method |
| Between-imputation variance | Reasonable | Too few imputations | Increase m to 20-50 |

### Red Flags
- **> 40% missing on key outcome**: results will be highly uncertain; consider alternative data source
- **Missingness differs by treatment group**: threatens internal validity; must model missingness mechanism
- **MNAR suspected**: any imputation assumes untestable assumptions; report sensitivity bounds
- **Monotone missingness**: dropout pattern; use mixed models or pattern-mixture models

## Domain Conventions

| Domain | Common Missingness Pattern | Preferred Method |
|--------|--------------------------|-----------------|
| Clinical trials | Dropout (MNAR) | Mixed models, pattern-mixture |
| Survey research | Item nonresponse (MAR) | MICE with auxiliary variables |
| Longitudinal | Attrition (MAR/MNAR) | FIML, multiple imputation |
| EHR data | Informative missingness (MNAR) | Selection models, sensitivity analysis |

## Reporting Template
> "Missing data was assessed across [N] variables. Overall missingness was [percentage]%. Little's MCAR test [was/was not] significant (p = [value]), suggesting data were [MCAR/MAR]. Missingness was handled using [method] with [details]. Sensitivity analysis using [alternative method] yielded [consistent/divergent] results."

## Output Specification
- `data/01_ingested/missingness_report.json`: mechanism classification, per-variable missingness, pattern matrix, recommended strategy, imputation parameters

## Validation Checks
- [ ] Mechanism classified (MCAR/MAR/MNAR with rationale)
- [ ] Strategy recommended matching mechanism and proportion
- [ ] No variable with > 20% missing left unaddressed
- [ ] If imputed: quality checks performed and logged
