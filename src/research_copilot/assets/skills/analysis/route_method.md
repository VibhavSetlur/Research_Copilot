---
skill_id: "route_method"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "pyyaml"]
depends_on: ["classify_domain", "profile_tabular", "detect_missingness"]
produces: ["analysis/methods_routing.json"]
complexity: "advanced"
---

# Skill: Analytical Method Routing

## Purpose
Route data profiles to appropriate analysis skills based on data characteristics, research question, and domain conventions.

## When to Use
- After profiling and domain classification
- Before executing any analysis
- To generate an analysis plan from data characteristics

## When NOT to Use
- Analysis method already specified by researcher
- Only one analysis method is applicable

## Decision Protocol

### Routing Tree
```
1. What is the research question type?
   ├── "Describe" → descriptive_stats
   ├── "Compare groups" → go to 2
   ├── "Test association" → go to 3
   ├── "Predict" → go to 4
   ├── "Causal effect" → causal_inference
   ├── "Discover structure" → clustering or dimensionality_reduction
   └── "Model time" → time_series_analysis

2. Compare groups:
   ├── 2 groups, continuous DV → check normality
   │   ├── Normal → inferential_parametric (t-test)
   │   └── Non-normal → inferential_nonparametric (Mann-Whitney)
   ├── 3+ groups, continuous DV → inferential_parametric (ANOVA) or inferential_nonparametric (Kruskal-Wallis)
   ├── Binary DV → logistic regression
   ├── Time-to-event DV → survival_analysis
   └── Repeated measures → mixed_effects

3. Test association:
   ├── Both continuous → inferential_parametric (Pearson) or inferential_nonparametric (Spearman)
   ├── Both categorical → chi-square
   ├── One continuous, one categorical → point-biserial
   └── Spatial data → spatial_analysis

4. Predict:
   ├── Continuous outcome → multiple regression
   ├── Binary outcome → logistic regression
   ├── Count outcome → Poisson/negative binomial regression
   ├── Time-to-event → survival_analysis
   └── High-dimensional predictors → dimensionality_reduction + regression
```

## Execution Protocol

### Step 1: Input Assembly
- Load: research brief (question type, variables of interest)
- Load: data profile (variable types, distributions, missingness)
- Load: domain classification (domain, reporting standard)

### Step 2: Variable Role Assignment
- Identify: outcome variable(s), predictor variable(s), covariates
- Map each variable to its role based on research brief
- If ambiguous: present options to researcher

### Step 3: Method Selection
- Apply routing tree based on: question type, DV type, IV type
- Check assumptions for selected method
- If assumptions violated: route to alternative method
- If multiple methods applicable: rank by appropriateness

### Step 4: Dependency Resolution
- For each selected method, check depends_on skills
- Build execution order: skills with no dependencies first
- Flag circular dependencies (should not occur)

### Step 5: Output Routing Plan
- List skills in execution order
- For each skill: inputs required, outputs produced, assumptions to check
- Include fallback methods if primary method fails

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Question type identified | Clear routing | Ask researcher to clarify |
| Variables mapped to roles | Complete | Flag unmapped variables |
| Assumptions checkable | Data supports method | Route to alternative |
| Dependencies satisfiable | All prerequisites met | Run missing prerequisite skills |

### Red Flags
- **No method matches**: research question may not be answerable with available data
- **Multiple equally valid methods**: present both, compare results
- **Routing suggests causal method but data is cross-sectional**: warn about causal limitations
- **Domain-specific method not available**: use general method with domain-appropriate reporting

## Complexity Budget

Every method is tagged with a runtime complexity tier. The intent router uses these tags to enforce depth constraints — exploratory queries MUST NOT invoke `intensive` methods.

### Complexity Tiers

| Tier | Runtime | When to Use | Examples |
|------|---------|-------------|----------|
| **quick** | <2 min | Exploratory queries, "show me the data", quick look, sanity checks | descriptive_stats, profile_tabular, correlation_matrix, histogram, scatter_plot, chi-square, t-test |
| **standard** | 5–15 min | Planned analysis, hypothesis testing, publication methods | multiple_regression, logistic_regression, ANOVA, factor_analysis, mediation_analysis, bootstrap CI |
| **intensive** | >15 min | Publication-only, final validation, complex models | MCMC/Bayesian, mixed_effects, structural_equation_model, permutation_tests (10k+), cross-validated ML, survival_analysis, time_series_ARIMA |

### Depth Enforcement Rules

- `depth: exploratory` → ONLY `quick` methods allowed. Block any `standard` or `intensive` method.
- `depth: standard` → `quick` + `standard` allowed. `intensive` requires explicit user approval.
- `depth: publication` → all tiers allowed. No restrictions.

### Intent Router Integration

When the intent router classifies a query as `exploratory`:
1. Filter out all methods tagged `intensive`
2. Filter out all methods tagged `standard` unless explicitly requested
3. Select the simplest `quick` method that answers the question
4. If no `quick` method is appropriate, ask: "This requires a more complex analysis. Proceed?"

### Method Complexity Tags

```
descriptive_stats          → quick
profile_tabular            → quick
correlation_matrix         → quick
t_test                     → quick
chi_square                 → quick
histogram                  → quick
scatter_plot               → quick
multiple_regression        → standard
logistic_regression        → standard
ANOVA                      → standard
factor_analysis            → standard
mediation_analysis         → standard
bootstrap_ci               → standard
mixed_effects              → intensive
bayesian_mcmc              → intensive
structural_equation_model  → intensive
survival_analysis          → intensive
time_series_arima          → intensive
permutation_test           → intensive
cross_validated_ml         → intensive
```

## Output Specification
- `analysis/methods_routing.json`: ordered skill list, variable role assignments, assumption checks, fallback methods, execution dependencies

## Validation Checks
- [ ] At least one analysis method selected
- [ ] Execution order respects dependencies
- [ ] Each method's assumptions are checkable with available data
- [ ] Fallback methods specified for each primary method
