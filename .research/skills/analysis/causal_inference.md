---
skill_id: "causal_inference"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "dowhy", "econml|doubleml", "scikit-learn"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/causal_results.json"]
complexity: "advanced"
---

# Skill: Causal Inference & Identification

## Purpose
Estimate causal effects (ATE, CATE) using structural causal models, double machine learning, and refutation testing.

## When to Use
- Research question is causal ("does X cause Y?") not associational
- Observational data with potential confounding
- RCT data (use simple difference-in-means, but validate randomization)

## When NOT to Use
- Only associational question asked
- No plausible identification strategy
- Treatment and outcome measured simultaneously with no temporal ordering

## Decision Protocol

### Method Selection
| Design | Data Type | Method |
|--------|-----------|--------|
| RCT | Any | Difference-in-means (validate randomization) |
| Observational, measured confounders | Any | Propensity score matching / weighting |
| Observational, high-dimensional confounders | Any | Double Machine Learning (DML) |
| Natural experiment | Binary treatment | Instrumental Variables (2SLS) |
| Policy intervention, panel data | Panel | Difference-in-Differences (DiD) |
| Threshold-based assignment | Continuous running variable | Regression Discontinuity (RDD) |
| Time-varying treatment | Longitudinal | Marginal Structural Models (MSM) |

## Execution Protocol

### Step 1: Causal Model Specification
- Define: treatment (D), outcome (Y), confounders (X), instruments (Z), mediators (M)
- Draw causal DAG: nodes = variables, edges = causal relationships
- Identify backdoor paths: all non-causal paths from D to Y
- Determine identification strategy: backdoor criterion, frontdoor criterion, or IV

### Step 2: Confounder Selection
- Include pre-treatment variables that affect both D and Y
- Exclude: mediators (on causal path D → M → Y), colliders (D → C ← Y), instruments (Z → D, Z ⊥ Y)
- Validate confounder list against domain literature

### Step 3: Effect Estimation
**Propensity Score Methods:**
- Estimate propensity: P(D=1|X) using logistic regression or ML
- Check overlap: propensity distributions should overlap between treated and control
- Match: nearest neighbor (1:1 or 1:k), caliper = 0.2 × SD of logit
- Weight: IPTW (inverse probability of treatment weighting)
- Check balance: standardized mean differences < 0.10 after matching/weighting

**Double Machine Learning:**
- Nuisance models: ML for Y|X and D|X (Random Forest, Lasso, or gradient boosting)
- Cross-fitting: split data into K folds, estimate nuisances on K-1 folds
- Orthogonalized residuals: Ỹ = Y - Ê[Y|X], D̃ = D - Ê[D|X]
- Final estimate: OLS of Ỹ on D̃
- Report: ATE, SE, 95% CI

### Step 4: Refutation Testing (DoWhy)
- **Placebo treatment**: replace D with random noise → effect should be 0
- **Random common cause**: add random confounder → estimate should be stable
- **Data subset**: remove 50% of data → estimate should be stable
- **Unobserved confounder**: simulate hidden confounder → sensitivity bound

### Step 5: Heterogeneous Treatment Effects (CATE)
- If treatment effect varies by subgroup: estimate CATE
- Methods: causal forest, meta-learners (T-learner, S-learner, X-learner)
- Report: which subgroups benefit most/least

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| Propensity overlap | Distributions overlap | No common support | Trim to overlap region |
| Balance | SMD < 0.10 | Residual confounding | Add interaction terms, re-match |
| Placebo refuter | p > 0.05 | Unobserved confounding | Reconsider identification strategy |
| Common cause stability | Estimate change < 5% | Model unstable | Increase regularization |

### Red Flags
- **No overlap in propensity scores**: treated and control are fundamentally different; cannot estimate causal effect
- **Placebo refuter significant**: model finds effect in random noise → severe misspecification
- **CATE varies wildly**: treatment effect highly heterogeneous; report subgroup-specific effects
- **IV weak (F-stat < 10)**: instrument too weak; biased 2SLS estimates

## Reporting Template
> "We estimated the causal effect of [treatment] on [outcome] using [method]. The ATE was [value] (SE = [value], 95% CI [lower, upper], p = [value]). Causal identification was validated through [refutation tests]. Placebo treatment refutation yielded ATE = [value] (p = [value]), supporting the validity of our identification strategy."

## Output Specification
- `analysis/03_analytical/causal_results.json`: ATE, CATE, SEs, CIs, refutation results, propensity diagnostics, causal DAG

## Validation Checks
- [ ] Causal DAG specified and justified
- [ ] Confounders pre-treatment only
- [ ] Propensity overlap verified
- [ ] At least 2 refutation tests passed
- [ ] Effect size plausible given domain knowledge
