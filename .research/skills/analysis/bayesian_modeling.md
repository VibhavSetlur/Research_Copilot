---
skill_id: "bayesian_modeling"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "pymc", "arviz"]
estimated_tokens: 4500
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/bayesian_results.json"]
---

# Skill: Bayesian Hierarchical Modeling (PyMC)

## Purpose
Specify, sample, and evaluate Bayesian hierarchical models using PyMC, enforcing MCMC convergence criteria.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to dataset |
| `formula` | Str | Yes | Statistical formula |
| `group_var` | Str | Yes | Grouping column name |

## Methodological Framework

### 1. Mathematical Formulations
- **Bayesian Hierarchical Model**:
  $$Y_{ij} \sim N(\mu_{ij}, \sigma^2), \quad \mu_{ij} = \alpha_j + \beta_j X_{ij}$$
  $$\alpha_j \sim N(\mu_\alpha, \sigma_\alpha^2), \quad \beta_j \sim N(\mu_\beta, \sigma_\beta^2)$$
- **Gelman-Rubin Diagnostic ($\hat{R}$)**:
  Compares variance between chains to variance within chains.
  $$\hat{R} = \sqrt{\frac{\text{Var}^+(\theta | y)}{W}}$$
  where $W$ is within-chain variance, and $\text{Var}^+$ is the marginal posterior variance estimate.

## Step-by-Step Analytical Protocol

### Step 1: Model Setup
Define priors (e.g. weakly informative normal and half-normal distributions) and structure random intercepts and slopes nested within groups.

### Step 2: Sampling
Execute PyMC sampling with NUTS. Set `target_accept=0.95` to handle funnel-shaped posteriors.

### Step 3: Convergence Checking
Verify that all parameters satisfy $\hat{R} < 1.05$ and Effective Sample Size ($ESS > 400$). Verify that divergent transitions equal zero.

## Diagnostics & Interpretation Guide (What to Look For)
- **Gelman-Rubin $\hat{R} \ge 1.05$**:
  - *Interpret*: Chain convergence failed. The chains have not explored the same posterior regions.
  - *Action*: Increase the number of tuning steps (`tune=2000`) or check if priors are too wide.
- **Divergent Transitions > 0**:
  - *Interpret*: Numerical instability during sampling. The sampler struggled with high curvature regions.
  - *Action*: Increase the NUTS target acceptance rate (`target_accept=0.99`) or re-parameterize the model using a non-centered parameterization.

## Writing & Reporting Standards
Report Bayesian statistics following this template:
> "We estimated a Bayesian hierarchical linear model using PyMC with 4 MCMC chains, 2,000 draws, and 1,000 tuning steps. Convergence was verified via the Gelman-Rubin diagnostic (all $\hat{R} < 1.01$) and absence of divergent transitions. Parameter estimates are reported as posterior means and 95% High Density Intervals (HDI). The group-level slope coefficient for X was $\beta = 1.84$ (95% HDI [1.21, 2.45]), indicating a positive relationship."

## Reference Python Implementation
```python
import pymc as pm
import arviz as az

def fit_bayesian(df, dep, indep, group_col):
    group_idx = pd.Categorical(df[group_col]).codes
    num_groups = len(df[group_col].unique())
    
    with pm.Model() as model:
        mu_a = pm.Normal('mu_a', mu=0, sigma=10)
        sigma_a = pm.HalfNormal('sigma_a', sigma=1)
        a = pm.Normal('a', mu=mu_a, sigma=sigma_a, shape=num_groups)
        
        sigma = pm.HalfNormal('sigma', sigma=1)
        mu = a[group_idx] + df[indep].values * 1.5
        
        y_obs = pm.Normal('y_obs', mu=mu, sigma=sigma, observed=df[dep].values)
        idata = pm.sample(2000, tune=1000, target_accept=0.95)
        
    return az.summary(idata), idata.sample_stats.diverging.sum().values
```

## Output Specification
Produces `bayesian_results.json` mapping posterior estimates, CIs, $\hat{R}$ and ESS.

## Validation Criteria
- [ ] $\hat{R} < 1.05$ for all parameters.
- [ ] Divergent transitions are zero.