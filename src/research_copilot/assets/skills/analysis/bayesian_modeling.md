---
skill_id: "bayesian_modeling"
version: "7.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "pymc", "arviz"]
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/bayesian_results.json"]
complexity: "advanced"
---

# Skill: Bayesian Hierarchical Modeling

## Purpose
Specify, sample, and evaluate Bayesian models with proper prior specification, MCMC convergence diagnostics, and posterior predictive checks.

## When to Use
- Prior information available and should be incorporated
- Hierarchical/multilevel data structure
- Small sample sizes where frequentist estimates are unstable
- Need full posterior distributions (not just point estimates)
- Model comparison via Bayes factors or LOO-CV

## When NOT to Use
- No prior information and non-informative priors would be used anyway
- Computational resources insufficient for MCMC
- Simple descriptive question only

## Execution Protocol

### Step 1: Prior Specification
**Principles:**
- Use weakly informative priors by default (regularize, don't dominate)
- Prior predictive check: simulate from prior alone; are predictions plausible?
- Domain-informed priors: use literature to set prior means and SDs

**Default priors:**
- Intercept: Normal(0, 10) on standardized outcome
- Slopes: Normal(0, 2.5) on standardized predictors
- Group-level SDs: HalfNormal(0, 1) or HalfStudentT(3, 1)
- Residual SD: HalfNormal(0, 1)
- Correlation parameters: LKJ(η=2)

### Step 2: Model Specification
- Define likelihood: distribution of Y given parameters
- Define linear predictor: link function and predictors
- For hierarchical models: random intercepts and/or slopes
- Non-centered parameterization for group-level effects (avoids funnel problem)

### Step 3: MCMC Sampling
- Sampler: NUTS (No-U-Turn Sampler)
- Chains: 4 (minimum), draws: 2000 per chain, tuning: 1000
- Target acceptance: 0.95 (increase to 0.99 if divergences)
- Initialize: adapt_diag or jitter+adapt_diag
- Random seed: set for reproducibility

### Step 4: Convergence Diagnostics
**Required checks (ALL must pass):**
- R-hat (R̂) < 1.05 for all parameters (ideally < 1.01)
- Effective sample size (ESS) > 400 for all parameters
- Divergent transitions = 0
- No max-tree-depth hits
- Trace plots: chains mix well, no trends

**If diagnostics fail:**
- Divergences > 0: increase target_accept to 0.99, reparameterize
- R̂ > 1.05: increase tuning steps, check priors
- Low ESS: increase draws, check for high autocorrelation

### Step 5: Posterior Summarization
- Point estimates: posterior mean or median
- Uncertainty: 95% HDI (Highest Density Interval)
- Probability of direction: P(β > 0) or P(β < 0)
- ROPE (Region of Practical Equivalence): proportion of posterior within [-0.1, 0.1] of null

### Step 6: Posterior Predictive Checks
- Simulate replicated data from posterior predictive distribution
- Compare replicated data to observed: do they look similar?
- Test statistic: mean, SD, max, min of replicated vs observed
- If replicated data systematically differs: model misspecified

### Step 7: Model Comparison
- LOO-CV (Leave-One-Out Cross-Validation): expected log predictive density
- WAIC: Watanabe-Akaike Information Criterion
- Bayes factors: for nested models (use bridge sampling)
- Prefer: LOO-CV for predictive accuracy, Bayes factors for hypothesis testing

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| R̂ < 1.05 | Chains converged | Non-convergence | Increase tuning, check priors |
| ESS > 400 | Adequate sampling | Poor mixing | Increase draws, reparameterize |
| Divergences = 0 | Stable sampling | Numerical instability | Increase target_accept, non-centered param |
| PPC passes | Model fits data | Model misspecified | Add predictors, change likelihood |

### Red Flags
- **R̂ > 1.1**: chains haven't mixed; results unreliable
- **All posterior mass on one side of zero**: strong effect, but check prior influence
- **PPC fails dramatically**: model doesn't capture key data features
- **Prior dominates posterior**: prior too informative relative to data

## Reporting Template
> "We estimated a Bayesian [model type] using PyMC with 4 MCMC chains, 2,000 draws, and 1,000 tuning steps. Weakly informative priors were used throughout. Convergence was confirmed (all R̂ < 1.01, ESS > 400, zero divergences). The posterior mean for [parameter] was [value] (95% HDI [lower, upper]), with P(β > 0) = [probability]. Posterior predictive checks confirmed adequate model fit."

## Output Specification
- `analysis/03_analytical/bayesian_results.json`: posterior summaries, HDIs, convergence diagnostics, PPC results, model comparison metrics

## Validation Checks
- [ ] All R̂ < 1.05
- [ ] All ESS > 400
- [ ] Zero divergent transitions
- [ ] PPC passes visual inspection
- [ ] Prior predictive check shows plausible predictions
