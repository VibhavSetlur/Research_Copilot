---
skill_id: "inferential_parametric"
version: "5.0.0"
category: "analysis"
domain_compatibility: ["all"]
required_tools: ["python", "statsmodels", "scipy", "notebooklm-py"]
estimated_tokens: 4500
depends_on: ["descriptive_stats"]
produces: ["analysis/03_analytical/parametric_results.json"]
---

# Skill: Parametric Inferential Modeling (OLS/GLM)

## Purpose
Fit parametric regression models (OLS, GLM) while auditing assumptions (linearity, normality, homoscedasticity, collinearity) and verifying covariate selections using NotebookLM.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to dataset |
| `dependent` | Str | Yes | Dependent variable name |
| `independent` | List | Yes | List of independent variables |
| `notebook_id` | Str | No | NotebookLM ID for literature verification |

## Methodological Framework

### 1. Mathematical Formulations
- **Multiple Linear Regression (OLS)**:
  $$Y = X\beta + \epsilon, \quad \epsilon \sim N(0, \sigma^2 I)$$
- **Variance Inflation Factor (VIF)**:
  $$\text{VIF}_j = \frac{1}{1 - R_j^2}$$
  where $R_j^2$ is the coefficient of determination when regressing $X_j$ on all other predictors.
- **Breusch-Pagan Test**:
  Regresses squared residuals $e_i^2$ on the independent variables:
  $$e^2 = X\gamma + \nu, \quad H_0: \gamma_1 = \gamma_2 = ... = 0 \text{ (Homoscedasticity)}$$
- **HC3 Covariance Estimator**:
  Corrects for heteroscedasticity by dividing squared residuals by the square of $(1 - h_{ii})$, where $h_{ii}$ are the hat matrix diagonal values:
  $$\Sigma_{\text{HC3}} = (X^T X)^{-1} X^T \text{diag}\left( \frac{e_i^2}{(1 - h_{ii})^2} \right) X (X^T X)^{-1}$$

## Step-by-Step Analytical Protocol

### Step 1: Pre-estimation Check & NotebookLM Literature Search
Query NotebookLM using the provided `notebook_id`:
```
Identify standard covariates for a model predicting [dependent] using [independent]. Are there known mediators or colliders in this set?
```
Ensure the predictor list is updated based on literature.

### Step 2: Model Ingestion and Fitting
Fit the baseline model using Ordinary Least Squares (OLS) or GLM depending on the dependent variable scale (e.g. continuous -> OLS, binary -> Logistic).

### Step 3: Run Diagnostic Tests
1. **Multicollinearity**: Calculate VIF for each predictor.
2. **Heteroscedasticity**: Run the Breusch-Pagan test.
3. **Residual Normality**: Run the Jarque-Bera and Omnibus tests.

### Step 4: Robust Adjustments
If the Breusch-Pagan test rejects homoscedasticity ($p < .05$), re-fit the model applying the **HC3 robust covariance estimator**.

## Diagnostics & Interpretation Guide (What to Look For)
- **VIF > 5.0**:
  - *Interpret*: High multicollinearity. Standard errors of coefficients are inflated, making them unstable.
  - *Action*: If the collinear variable is a control, keep it but warn. If it is a primary variable, consider dropping it, combining variables, or using Ridge regression.
- **Breusch-Pagan test p < .05**:
  - *Interpret*: Heteroscedasticity is present. Standard OLS errors are biased.
  - *Action*: Enforce **HC3 standard errors**. Note this choice in the manuscript.
- **Jarque-Bera/Omnibus test p < .05**:
  - *Interpret*: Non-normal residuals. Hypothesis tests (t/F) may be inaccurate in small samples.
  - *Action*: If sample size $N < 100$, consider log-transforming $Y$, utilizing a GLM (e.g., Gamma), or switching to a non-parametric alternative.

## Writing & Reporting Standards
Report coefficients and diagnostics following this template:
> "We fitted a multiple linear regression model predicting $Y$. The Breusch-Pagan test indicated significant heteroscedasticity ($\chi^2(df) = \text{value}, p = \text{val}$), prompting the use of heteroscedasticity-robust standard errors (HC3). Multicollinearity was ruled out as all VIF values were below 2.1. The model explained [adjusted $R^2$]% of the variance ($F(df_1, df_2) = \text{value}, p < .001$). The primary predictor was significantly associated with $Y$ ($b = 2.45$, $95\%\text{ CI } [1.12, 3.78]$, $t(df) = 3.65$, $p < .001$)."

## Reference Python Implementation
```python
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan

def analyze_parametric(df, dep, indeps):
    X = sm.add_constant(df[indeps])
    y = df[dep]
    
    # Collinearity
    vifs = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    
    model = sm.OLS(y, X)
    results = model.fit()
    
    # Breusch-Pagan
    _, bp_p, _, _ = het_breuschpagan(results.resid, X)
    
    if bp_p < 0.05:
        results = model.fit(cov_type='HC3')
        cov_type = "HC3"
    else:
        cov_type = "nonrobust"
        
    return results, vifs, cov_type
```

## Output Specification
Produces a detailed JSON of coefficients, standard errors, p-values, 95% CIs, VIF, and diagnostic test parameters.

## Validation Criteria
- [ ] Robust standard errors (HC3) are applied if Breusch-Pagan p < .05.
- [ ] VIF scores are calculated for all non-constant columns.