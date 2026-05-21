---
skill_id: "smart_imputer"
version: "1.0.0"
category: "data"
depends_on: ["detect_missingness", "profile_tabular"]
produces: ["02_experiments/<exp>/outputs/analysis/imputation_diagnostics.json"]
complexity: "standard"
---

# Skill: Smart Imputer

## Purpose
Handle missing data with mechanism-appropriate imputation. Replaces generic missingness handling with targeted strategies.

---

## Protocol

### Step 1: Diagnose Mechanism
Use `detect_missingness` output. Classify each variable's missingness as MCAR, MAR, or MNAR. If unknown, default to MAR (conservative).

### Step 2: Select Strategy by Mechanism × Proportion

| Mechanism | < 5% missing | 5-20% missing | > 20% missing |
|-----------|-------------|---------------|---------------|
| **MCAR** | Median/mode fill for descriptive; listwise deletion for analysis | MICE with 5 imputations | MICE with 20 imputations + sensitivity analysis |
| **MAR** | MICE with 5 imputations | MICE with 10-20 imputations | MICE + pattern-mixture model + sensitivity bounds |
| **MNAR** | Listwise deletion + sensitivity bounds | Selection model or pattern-mixture | Pattern-mixture + wide sensitivity bounds; flag results as highly uncertain |

### Step 3: MCAR — Simple Imputation
For <5% missing: median (continuous) or mode (categorical). Use `sklearn.impute.SimpleImputer(strategy='median')`. Only for descriptive stats — never for inference. For analysis: listwise deletion.

### Step 4: MAR — MICE (Multiple Imputation by Chained Equations)
Use `sklearn.impute.IterativeImputer` or `statsmodels` MICE. Steps:
1. Build imputation model for each variable with missing values, using all other variables as predictors
2. Run 5-20 imputations (more for higher missingness)
3. Analyze each imputed dataset separately
4. Combine results using Rubin's rules: pooled estimate = mean of estimates, pooled SE = sqrt(mean(SE²) + (1+1/m)×between-imputation variance)

Include auxiliary variables (variables correlated with missingness) in the imputation model even if not in the analysis model.

### Step 5: MNAR — Pattern Mixture / Sensitivity Bounds
MNAR requires untestable assumptions. Use:
- **Pattern mixture model**: stratify by missingness pattern, estimate within each stratum, combine with weights
- **Sensitivity bounds**: compute best-case and worst-case scenarios by imputing at extreme values (e.g., min and max for continuous)
- **Selection model**: jointly model outcome and missingness mechanism (requires strong assumptions)

Always report sensitivity bounds alongside point estimates.

### Step 6: Diagnostics
After imputation, validate:
1. Compare distributions of observed vs imputed values (should be similar but not identical)
2. Check imputed values are plausible (within observed range for bounded variables)
3. Verify between-imputation variance is reasonable (too low = model overconfident; too high = too few imputations)
4. Run analysis on each imputed dataset; check result consistency

### Step 7: Output
Save to `02_experiments/<exp>/outputs/analysis/imputation_diagnostics.json`:
- Mechanism classification per variable
- Imputation method used, number of imputations
- Before/after missingness proportions
- Distribution comparison (observed vs imputed)
- Rubin's rules pooled estimates (if MICE)
- Sensitivity bounds (if MNAR)

---

## Validation
- [ ] Mechanism classified before imputation
- [ ] Strategy matches mechanism × proportion table
- [ ] MICE uses ≥5 imputations
- [ ] Rubin's rules applied for pooled estimates
- [ ] Diagnostics: observed vs imputed distributions compared
- [ ] MNAR: sensitivity bounds reported
- [ ] Imputation diagnostics JSON saved
