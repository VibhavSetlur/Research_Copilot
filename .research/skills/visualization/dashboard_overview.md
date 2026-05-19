---
skill_id: "dashboard_overview"
version: "3.0.0"
category: "visualization"
type: "interactive_dashboard"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly"]
estimated_tokens: 2500
depends_on: ["figure_descriptive", "figure_inferential"]
produces: ["reports/dashboards/overview_dashboard.py"]
---

# Skill: Interactive Overview Dashboard (Plotly Dash)

## Purpose
Generate the master interactive Plotly Dash script summarizing descriptive and inferential research outputs.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_dir` | Path | Yes | Path to project root folder |

## Execution Protocol

### Step 1: Layout Grid Design
- Implement a responsive layout utilizing `dash-bootstrap-components` (e.g., `FLATLY` or `MINTY` stylesheet).
- Use a 12-column grid system (`dbc.Col` and `dbc.Row`) to ensure proper display across standard screen resolutions.
- Enforce global sans-serif typography.

### Step 2: Theme Setup
- Use HSL-tailored schemes for visuals:
  - Dark Navy primary: `#2c3e50`
  - Teal secondary: `#18bc9c`
- Apply the `plotly_white` template globally to all Plotly figures to maintain clean, white backgrounds.

### Step 3: Integration of Sub-Dashboards
- Setup tabbed interface (`dbc.Tabs`):
  - Tab 1: Project Overview & KPIs.
  - Tab 2: Interactive Data Explorer.
  - Tab 3: Model Results & Diagnostics.
- Load descriptive and inferential figures dynamically into `dcc.Graph` containers.

### Step 4: Export Utilities
- Add a download action to export static PDF figures.
- Include a CSV export button for analytical tables using `dcc.Download`.

## Output Specification
Produces:
- `reports/dashboards/overview_dashboard.py`

## Validation Criteria
- [ ] Script compiles and runs without syntax errors.
- [ ] Dash components use unique IDs.
- [ ] Default port is 8050.