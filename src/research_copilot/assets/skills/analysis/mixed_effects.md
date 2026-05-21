---
skill_id: "mixed_effects"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "statsmodels", "linearmodels"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/mixed_effects_results.json"]
complexity: "advanced"
---

# Skill: Mixed-Effects (Multilevel) Modeling

## Purpose
Fit hierarchical models with fixed and random effects to account for nested or crossed data structures.

## When to Use
- Data has hierarchical structure (students in schools, patients in hospitals, repeated measures)
- Observations are not independent within groups
- Want to model both population-level and group-level effects
- Unbalanced designs (different group sizes)

## When NOT to Use
- No grouping structure in data
- Only a few groups (< 5): fixed effects more appropriate
- All groups have identical effects (no variation to model)

## Decision Protocol

### Model Selection
| Structure | Random Effects | Model |
|-----------|---------------|-------|
| Nested, intercepts vary | Random intercepts | LMM: y ~ X + (1 \| group) |
| Nested, slopes vary | Random intercepts + slopes | LMM: y ~ X + (1 + X \| group) |
| Crossed classification | Crossed random effects | LMM: y ~ X + (1 \| group1) + (1 \| group2) |
| Binary outcome | Random intercepts | GLMM: logit(y) ~ X + (1 \| group) |
| Count outcome | Random intercepts | GLMM: log(y) ~ X + (1 \| group) + offset |

## Execution Protocol

### Step 1: Data Structure Verification
- Identify grouping variables (cluster IDs)
- Compute: number of groups, group sizes, ICC (intraclass correlation)
- ICC > 0.05: multilevel modeling justified
- Check for crossed vs nested structure

### Step 2: Random Effects Specification
- Start with random intercepts only (simplest)
- Add random slopes if theory suggests effect varies by group
- Avoid: random slopes for variables with few levels within groups
- Check: sufficient observations per group for random slope estimation (≥ 10)

### Step 3: Model Fitting
- Estimator: REML (restricted maximum likelihood) for variance components
- For GLMM: Laplace approximation or adaptive Gaussian quadrature
- Convergence: check optimizer converged without warnings
- If convergence fails: simplify random effects structure, increase iterations

### Step 4: Model Comparison
- Compare nested models via likelihood ratio test (LRT)
- Compare non-nested models via AIC/BIC
- Test: random intercept vs random intercept+slope
- Test: varying covariance structures (compound symmetry, AR(1), unstructured)

### Step 5: Diagnostics
- Residual normality: Q-Q plot of level-1 residuals
- Random effects normality: Q-Q plot of BLUPs
- Homoscedasticity: residuals vs fitted plot
- Influence: Cook's D for groups (leave-one-group-out)

### Step 6: Inference
- Fixed effects: Wald tests with Satterthwaite or Kenward-Roger df approximation
- Random effects: variance components with 95% CI
- Compute ICC: proportion of variance at group level
- Compute marginal R² (fixed only) and conditional R² (fixed + random)

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| ICC > 0.05 | Multilevel structure | No group-level variation | Use single-level model |
| Convergence | Optimizer converged | Estimation failed | Simplify model, rescale predictors |
| Random effects normality | Approximately normal | Non-normal BLUPs | Check for outliers, consider robust |
| Residual homoscedasticity | Constant variance | Heteroscedasticity | Model variance structure |

### Red Flags
- **Random effect variance = 0**: no group-level variation; drop random effect
- **Singular fit**: random effects covariance matrix not full rank; simplify structure
- **ICC > 0.50**: most variation is between groups; few effective observations
- **Convergence warnings**: results may be unreliable; try different optimizer

## Reporting Template
> "A linear mixed-effects model was fitted with [fixed effects] as fixed effects and random intercepts for [grouping variable]. The ICC was [value], indicating [percentage]% of variance at the group level. The effect of [predictor] was significant, β = [value], SE = [value], t([df]) = [value], p = [value]. Conditional R² = [value], marginal R² = [value]."

## Output Specification
- `analysis/03_analytical/mixed_effects_results.json`: fixed effects, random effects variance components, ICC, model comparison, diagnostics

## Validation Checks
- [ ] Model converged without warnings
- [ ] ICC computed and reported
- [ ] Both marginal and conditional R² reported
- [ ] Random effects structure justified
