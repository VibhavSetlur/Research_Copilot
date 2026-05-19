---
skill_id: "dashboard_overview"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly", "dash-bootstrap-components", "pandas"]
depends_on: ["viz_design_system", "viz_code_standards", "figure_descriptive", "figure_inferential"]
produces:
  - "reports/dashboards/overview_dashboard.py"
  - "reports/dashboards/components/"
  - "reports/dashboards/assets/custom.css"
complexity: "advanced"
---

# Skill: Interactive Overview Dashboard

## Purpose
Generate a professional, publication-grade interactive dashboard integrating all research outputs. Built with component-based architecture, responsive design, and accessibility.

## When to Use
- After all analysis completed
- For interactive exploration of results
- Sharing with collaborators
- Conference presentations

## When NOT to Use
- Only static reports needed
- Analysis not yet complete
- Data under NDA with no sharing allowed

---

## Architecture

### File Structure
```
reports/dashboards/
  overview_dashboard.py       # Main app (≤200 lines)
  components/
    __init__.py               # Component exports
    cards.py                  # Metric card components
    charts.py                 # Reusable chart components
    tables.py                 # Data table components
    filters.py                # Filter/control components
    layout.py                 # Page layout templates
  assets/
    custom.css                # Custom styles (design system)
  data/
    dashboard_cache.parquet   # Pre-computed analysis data
```

### Design Rules
1. **Main app ≤200 lines** — All logic in components
2. **No raw data loading in callbacks** — Use pre-computed cache
3. **Every component is a function** — Returns Dash component
4. **Theme applied globally** — Via viz_theme.py
5. **Responsive grid** — Bootstrap 12-column system
6. **Loading states** — Every callback shows spinner

---

## Tab Structure

### Tab 1: Overview
**Purpose**: Key findings at a glance

**Layout**:
```
┌─────────────────────────────────────────────────┐
│  [Project Title]              [Last Updated]    │
│  Research Dashboard                              │
├─────────────────────────────────────────────────┤
│  [Card: N Obs] [Card: Variables] [Card: Results]│
│  [Card: Significant] [Card: Effect Size Range]  │
├─────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────────┐  │
│  │  Main Finding   │  │  Correlation Heatmap  │  │
│  │  Visualization  │  │  (key variables)      │  │
│  │                 │  │                       │  │
│  └─────────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────┤
│  Research Questions Summary                      │
│  ┌───────────────────────────────────────────┐  │
│  │ Q1: [text] → [result summary] [status]    │  │
│  │ Q2: [text] → [result summary] [status]    │  │
│  │ Q3: [text] → [result summary] [status]    │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Components**:
- `create_metric_card(title, value, subtitle, color, icon)` — Standardized metric cards
- `create_question_summary(questions, results)` — Question status table
- `create_correlation_heatmap(df, vars)` — Top correlations
- `create_main_finding_figure(results)` — Primary result visualization

### Tab 2: Data Explorer
**Purpose**: Interactive data inspection

**Layout**:
```
┌─────────────────────────────────────────────────┐
│  Data Explorer                                   │
├─────────────────────────────────────────────────┤
│  [Dropdown: Dataset] [Dropdown: Variable]       │
│  [Filter Panel] [N = XXXX]                      │
├─────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────────┐  │
│  │  Variable       │  │  Bivariate Plot      │  │
│  │  Distribution   │  │  (X vs Y)            │  │
│  └─────────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────┤
│  Data Table (paginated, sortable, filterable)   │
└─────────────────────────────────────────────────┘
```

### Tab 3: Results
**Purpose**: Statistical results exploration

**Layout**:
```
┌─────────────────────────────────────────────────┐
│  Results                                         │
├─────────────────────────────────────────────────┤
│  [Dropdown: Question] [Dropdown: Method]        │
├─────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐   │
│  │  Forest Plot (effect sizes + CIs)        │   │
│  └──────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  Results Table (sortable, with significance)    │
│  Variable | Estimate | 95% CI | p | Adjusted p  │
└─────────────────────────────────────────────────┘
```

### Tab 4: Diagnostics
**Purpose**: Model diagnostics and assumption checks

**Layout**:
```
┌─────────────────────────────────────────────────┐
│  Diagnostics                                     │
├─────────────────────────────────────────────────┤
│  [Dropdown: Model]                               │
├──────────────┬──────────────┬───────────────────┤
│ Residuals    │ Q-Q Plot     │ Scale-Location    │
│ vs Fitted    │              │                   │
├──────────────┼──────────────┼───────────────────┤
│ Cook's D     │ VIF Values   │ Missingness       │
│ Plot         │              │ Pattern           │
└──────────────┴──────────────┴───────────────────┘
```

---

## Component Specifications

### Metric Card
```python
def create_metric_card(title, value, subtitle=None, color=None, icon=None, trend=None):
    """Standardized metric card.
    
    Args:
        title: Label (e.g., "Observations")
        value: Main number (formatted with commas)
        subtitle: Context (e.g., "after filtering")
        color: Semantic color from design system
        icon: Bootstrap icon name
        trend: Optional trend indicator ("up", "down", "flat")
    """
```

### Chart Component
```python
def create_chart_container(figure, title=None, footer=None, height=400):
    """Wrap any Plotly figure in a standardized card.
    
    Includes: title, figure, optional footer, loading state.
    """
```

### Filter Panel
```python
def create_filter_panel(filters, id_prefix="filter"):
    """Generate filter controls from filter spec.
    
    Supports: dropdown, range slider, date picker, checkbox.
    """
```

---

## Interactive Features

### Filters
- **Variable selector**: Multi-select dropdown for variables
- **Subgroup filter**: Filter by categorical variable levels
- **Range filter**: Numeric range sliders
- **Method selector**: Choose analysis method/specification
- **Live N counter**: Shows sample size after filtering

### Downloads
- **PNG export**: Each figure has download button
- **CSV export**: Tables exportable as CSV
- **Report export**: Generate PDF summary (via WeasyPrint)

### Tooltips
- **Statistical terms**: Hover explains p-value, CI, effect size
- **Variable descriptions**: Hover shows variable definition
- **Method info**: Hover explains analysis method

---

## Styling Requirements

### Must Use
- Bootstrap FLATLY or LUX theme
- Design system colors (Okabe-Ito palette)
- Inter font family
- 12-column responsive grid
- Card shadows on hover
- Loading spinners for all async operations

### Must NOT Use
- Default Plotly colors
- Inline CSS (use assets/custom.css)
- Hardcoded sizes (use design system constants)
- More than 8 colors in any single figure
- 3D charts, pie charts, or decorative elements

---

## Accessibility

- All figures have `aria-label` with description
- Color is NEVER the only differentiator (use labels, patterns)
- Keyboard navigation works for all interactive elements
- Contrast ratios meet WCAG AA (4.5:1 minimum)
- Screen reader can navigate tab structure

---

## Implementation Steps

1. **Create component files** — cards.py, charts.py, tables.py, filters.py, layout.py
2. **Create assets/custom.css** — Design system styles
3. **Build main app** — Import components, define layout, wire callbacks
4. **Pre-compute data** — Save analysis results to dashboard_cache.parquet
5. **Implement callbacks** — One per interactive element, with loading states
6. **Test** — Verify all tabs render, filters work, downloads function
7. **Validate** — Run figure validation on all embedded plots

---

## Output Specification
- `reports/dashboards/overview_dashboard.py`: Runnable Dash app
- `reports/dashboards/components/`: Component modules
- `reports/dashboards/assets/custom.css`: Custom styles
- `reports/dashboards/data/dashboard_cache.parquet`: Pre-computed data

## Validation Checks
- [ ] Main app ≤200 lines
- [ ] All components are functions in separate files
- [ ] No raw data loading in callbacks
- [ ] Design system theme applied globally
- [ ] All 4 tabs render without errors
- [ ] Filters update figures correctly
- [ ] Download buttons functional
- [ ] Loading states shown during computation
- [ ] No hardcoded colors or sizes
- [ ] All figures pass validation checklist
- [ ] Accessibility: alt text, contrast, keyboard nav
- [ ] Runs on port 8050 without errors
