---
skill_id: "dashboard_executive"
version: "3.0.0"
category: "visualization"
type: "interactive_dashboard"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly"]
estimated_tokens: 2500
depends_on: ["dashboard_results"]
produces: ["reports/dashboards/executive_dashboard.py"]
---

# Skill: Interactive Executive Dashboard (Plotly Dash)

## Purpose
Generate a high-level executive KPI dashboard script for research summaries and stakeholder presentation.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `results_path` | Path | Yes | Path to results JSON |

## Execution Protocol

### Step 1: KPI Summary Layout
- Define grid-based panels presenting primary outcomes:
  - Primary Hypothesis status (e.g., green card for "Supported", red card for "Rejected").
  - Primary Effect Size value (with confidence intervals).
  - Study Sample Size.
- Design layout with a soft background color (`#f8f9fa`) and clean borders (`border: 1px solid #e3e6f0`).

### Step 2: Graphic Integration
- Display the main causal DAG or forest plot in a card container.
- Integrate an interactive markdown panel (`dcc.Markdown`) displaying the executive summary text from `executive_summary.md`.

## Output Specification
Produces:
- `reports/dashboards/executive_dashboard.py`

## Validation Criteria
- [ ] Key metrics render dynamically from the JSON payload.
- [ ] Layout is clean and fits standard screen widths without horizontal scrolling.