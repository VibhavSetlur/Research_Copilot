---
skill_id: "dashboard_explorer"
version: "3.0.0"
category: "visualization"
type: "interactive_dashboard"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly", "pandas"]
estimated_tokens: 2500
depends_on: ["figure_descriptive"]
produces: ["reports/dashboards/explorer_dashboard.py"]
---

# Skill: Interactive Exploratory Dashboard (Plotly Dash)

## Purpose
Generate an interactive data exploration dashboard script for dynamic variable distribution mapping.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to processed dataset |

## Execution Protocol

### Step 1: Dropdown & Selection Layout
- Design a sidebar menu containing selectors:
  - X-axis variable (continuous).
  - Y-axis variable (continuous).
  - Grouping variable (categorical).
- Main content panel contains dynamic Plotly graphs.

### Step 2: Interactive Callbacks
- Construct callback functions mapping user dropdown selections to:
  - A scatter plot with marginal distribution histograms.
  - Box/violin plots stratified by the selected categorical group.
- Use `plotly.graph_objects` to handle updates. Apply marker transparency (`opacity=0.6`) and colorblind-friendly color themes.

### Step 3: High-Density Optimization
- If dataset size exceeds 10,000 observations:
  - Set `go.Scattergl` (WebGL rendering) instead of `go.Scatter` to ensure fast rendering.
  - Limit returned data points in callbacks using uniform downsampling to prevent browser crashes.

## Output Specification
Produces:
- `reports/dashboards/explorer_dashboard.py`

## Validation Criteria
- [ ] Callbacks execute without warnings or loop errors.
- [ ] WebGL rendering is configured for large datasets.