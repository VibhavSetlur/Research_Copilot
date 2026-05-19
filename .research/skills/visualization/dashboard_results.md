---
skill_id: "dashboard_results"
version: "3.0.0"
category: "visualization"
type: "interactive_dashboard"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly", "pandas"]
estimated_tokens: 2500
depends_on: ["figure_inferential"]
produces: ["reports/dashboards/results_dashboard.py"]
---

# Skill: Interactive Results Dashboard (Plotly Dash)

## Purpose
Generate an interactive dashboard script presenting analytical models, fit indices, and parameter estimates.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `results_path` | Path | Yes | Path to inferential results JSON |

## Execution Protocol

### Step 1: Layout & Dropdown
- Layout is split:
  - Model selector dropdown (loads specific fit configurations).
  - Model KPI indicators (R-squared, Adjusted R-squared, AIC, BIC, Degrees of Freedom).

### Step 2: Interactive Coefficient Forest Plot
- Code a reactive callback that draws a horizontal forest plot of coefficients with confidence intervals when a model is selected.
- Highlight statistically significant parameters (*p* < .05) in teal, and non-significant parameters in gray.
- Enable custom tooltips on hover displaying: Estimate, 95% CI Limits, and Exact p-value.

### Step 3: Interactive Diagnostics Panel
- Plot interactive diagnostic plots:
  - Residuals vs Fitted values.
  - Normal Q-Q plot.
- Allow users to click data points on the diagnostic scatter plots to view corresponding database row records in a Dash DataTable.

## Output Specification
Produces:
- `reports/dashboards/results_dashboard.py`

## Validation Criteria
- [ ] Hover tooltips show formatted stats (decimals rounded to 3 digits).
- [ ] DataTable renders with correct page limits (e.g., 10 rows per page).