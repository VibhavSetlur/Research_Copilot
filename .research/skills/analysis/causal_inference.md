---
skill_id: "causal_inference"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "doubleml", "dowhy", "scikit-learn", "notebooklm-py"]
estimated_tokens: 4500
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/causal_results.json"]
---

# Skill: Causal Inference & Identification

## Purpose
Estimate structural causal effects (ATE and CATE) using double machine learning and validate causal DAG models with NotebookLM.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to dataset |
| `treatment` | Str | Yes | Treatment variable |
| `outcome` | Str | Yes | Outcome variable |
| `confounders` | List | Yes | Confounding variables |
| `notebook_id` | Str | No | NotebookLM ID for model auditing |

## Methodological Framework

### 1. Mathematical Formulations
- **Double Machine Learning (DML)**:
  Establishes orthogonalized score functions to estimate treatment effect $\theta_0$:
  1. $Y = g_0(X) + \theta_0 D + U, \quad E[U|D, X] = 0$
  2. $D = m_0(X) + V, \quad E[V|X] = 0$
  3. Run machine learning estimators to find predicted $\hat{g}_0(X)$ and $\hat{m}_0(X)$.
  4. Obtain residuals $\tilde{Y} = Y - \hat{g}_0(X)$ and $\tilde{D} = D - \hat{m}_0(X)$.
  5. Estimate $\theta_0$ via OLS of $\tilde{Y}$ on $\tilde{D}$.

## Step-by-Step Analytical Protocol

### Step 1: Causal DAG Audit via NotebookLM
Query NotebookLM to evaluate confounders:
```
Target Causal Setup: Treatment = [treatment], Outcome = [outcome], Controls = [confounders]. Are there any potential colliders or mediator variables in this control list?
```
Adjust lists based on returned literature findings.

### Step 2: DoubleML Execution
Configure DoubleML using Random Forest regressors as the nuisance parameter estimators. Fit the model to obtain the treatment effect.

### Step 3: Robustness and Refutation Testing
Run DoWhy refutation tests:
- Placebo Treatment: Replaces treatment with random noise. Causal effect should equal 0.
- Random Common Cause: Adds a random confounder. Estimate should remain stable.

## Diagnostics & Interpretation Guide (What to Look For)
- **Placebo Treatment Refutation p < .05**:
  - *Interpret*: Critical violation. The model finds a causal effect even when treatment is random. This indicates severe unobserved confounding or model overfitting.
  - *Action*: Re-evaluate confounders, review the causal DAG, and verify if the background ML models are overfitting.
- **Random Common Cause Estimate Shifts > 5%**:
  - *Interpret*: The model is highly sensitive to model specification variations, indicating instability.
  - *Action*: Increase regularization in the ML nuisance estimators or bootstrap the causal estimator.

## Writing & Reporting Standards
Report causal findings following this template:
> "We estimated the causal effect of treatment $D$ on outcome $Y$ using Double Machine Learning (DML) with Random Forest models to partial out the confounding effects of $X$. Causal assumptions were audited using literature queries. The estimated Average Treatment Effect (ATE) was significant ($ATE = 1.42$, $SE = 0.31$, $95\%\text{ CI } [0.81, 2.03]$, $p < .001$). Causal identification was validated using refutation tests; replacing the treatment with a placebo variable yielded no significant effect ($ATE_{\text{placebo}} = 0.02$, $p = .89$)."

## Reference Python Implementation
```python
import pandas as pd
from doubleml import DoubleMLData, DoubleMLPLR
from sklearn.ensemble import RandomForestRegressor

def run_dml(df, treatment, outcome, confounders):
    dml_data = DoubleMLData(df, y_col=outcome, d_cols=treatment, x_cols=confounders)
    ml_l = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    ml_m = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    
    dml_plr = DoubleMLPLR(dml_data, ml_l=ml_l, ml_m=ml_m, dml_procedure='dml2')
    dml_plr.fit()
    
    return dml_plr.summary
```

## Output Specification
Produces a JSON mapping estimated parameters and refutation checks.

## Validation Criteria
- [ ] Placebo refuter test p-value is > .05.
- [ ] Random common cause estimate changes by < 5%.