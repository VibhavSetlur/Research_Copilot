---
skill_id: "viz_code_standards"
version: "1.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "plotly", "dash"]
depends_on: ["viz_design_system"]
produces: ["scripts/utils/viz_helpers.py"]
complexity: "intermediate"
---

# Skill: Visualization Code Standards

## Purpose
Enforce professional code quality for ALL visualization and dashboard code. No spaghetti plots. No hardcoded values. No untested rendering.

---

## Architecture Rules

### 1. Modular Design
Every visualization script MUST follow this structure:
```
scripts/
  03_figures.py          # Main entry point
  utils/
    viz_theme.py         # Theme, colors, typography
    viz_helpers.py       # Reusable plot functions
    viz_validation.py    # Figure quality checks
```

### 2. Function-Based Plotting
NEVER write plotting code inline. Every plot type gets a function:

```python
# BAD — inline plotting
fig, ax = plt.subplots()
ax.scatter(x, y)
ax.set_title("My Plot")

# GOOD — function-based
from utils.viz_helpers import scatter_with_regression
fig = scatter_with_regression(df, x="predictor", y="outcome", 
                               title="Predictor vs Outcome")
```

### 3. Configuration Over Hardcoding
NEVER hardcode colors, sizes, or paths:

```python
# BAD
ax.plot(x, y, color="#FF0000", linewidth=2)
fig.savefig("my_plot.png", dpi=150)

# GOOD
from utils.viz_theme import SEMANTIC, FIGURE_MARGINS
ax.plot(x, y, color=SEMANTIC["error"], linewidth=1.5)
fig.savefig(output_path, dpi=300, bbox_inches="tight")
```

### 4. Data Validation Before Plotting
ALWAYS validate data before creating figures:

```python
def validate_for_plot(df, required_cols, min_rows=3):
    """Validate data before plotting."""
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if len(df) < min_rows:
        raise ValueError(f"Need at least {min_rows} rows, got {len(df)}")
    if df[required_cols].isnull().all().any():
        raise ValueError("All values null in required column(s)")
    return True
```

### 5. Error Handling
ALL plotting functions MUST handle errors gracefully:

```python
def create_figure(data, output_path, **kwargs):
    try:
        validate_for_plot(data, kwargs.get("required_cols", []))
        fig = build_figure(data, **kwargs)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return {"status": "success", "path": str(output_path)}
    except Exception as e:
        return {"status": "error", "message": str(e), "path": None}
```

---

## Dashboard Architecture

### Component-Based Structure
Every dashboard MUST use this architecture:

```
reports/dashboards/
  overview_dashboard.py     # Main app
  components/
    __init__.py
    cards.py                # Metric card components
    charts.py               # Reusable chart components
    tables.py               # Data table components
    filters.py              # Filter/control components
    layout.py               # Page layout templates
  assets/
    custom.css              # Custom styles
    logo.png                # Project logo
  utils/
    data_loader.py          # Data loading + caching
    callbacks.py            # Dashboard callbacks
```

### Dashboard App Template
```python
"""Overview Dashboard — [Project Title]
Run: python overview_dashboard.py
Port: 8050
"""
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from utils.viz_theme import apply_plotly_theme, OKABE_ITO

# ── Configuration ──
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    title="[Project Title] — Research Dashboard",
    update_title="Loading...",
    suppress_callback_exceptions=True,
)

# Apply theme
plotly_template = apply_plotly_theme()

# ── Layout ──
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("[Project Title]", className="mb-1"),
            html.P("Research Dashboard — [Date]", className="text-muted"),
        ], width=12)
    ], className="mb-4"),

    # Navigation tabs
    dbc.Tabs([
        dbc.Tab(label="Overview", tab_id="tab-overview"),
        dbc.Tab(label="Data", tab_id="tab-data"),
        dbc.Tab(label="Results", tab_id="tab-results"),
        dbc.Tab(label="Diagnostics", tab_id="tab-diagnostics"),
    ], id="dashboard-tabs", active_tab="tab-overview", className="mb-4"),

    # Tab content
    html.Div(id="tab-content"),
], fluid=True, className="px-4 py-3")

# ── Callbacks ──
@callback(Output("tab-content", "children"), Input("dashboard-tabs", "active_tab"))
def render_tab(active_tab):
    """Render tab content based on active tab."""
    tab_map = {
        "tab-overview": render_overview,
        "tab-data": render_data,
        "tab-results": render_results,
        "tab-diagnostics": render_diagnostics,
    }
    return tab_map.get(active_tab, render_overview)()

def render_overview():
    """Overview tab: key findings, summary cards, main figures."""
    return dbc.Row([
        # Summary cards row
        dbc.Col(create_metric_card("N", str(n_obs), "Observations"), width=3),
        dbc.Col(create_metric_card("Variables", str(n_vars), "Total"), width=3),
        dbc.Col(create_metric_card("Questions", str(n_questions), "Analyzed"), width=3),
        dbc.Col(create_metric_card("Significant", str(n_sig), f"of {n_tests} tests"), width=3),
    ])

# ── Run ──
if __name__ == "__main__":
    app.run(debug=False, port=8050)
```

### Component Pattern
Every reusable component follows this pattern:

```python
def create_metric_card(title, value, subtitle=None, color=None, icon=None):
    """Create a standardized metric card.
    
    Args:
        title: Card label (e.g., "Observations")
        value: Main metric value (e.g., "1,234")
        subtitle: Optional context (e.g., "after filtering")
        color: Semantic color key or hex
        icon: Optional icon name (Bootstrap Icons)
    
    Returns:
        dbc.Card component
    """
    card_color = color or "#0072B2"
    card = dbc.Card([
        dbc.CardBody([
            html.H4(title, className="card-title text-muted mb-1",
                    style={"fontSize": "14px", "fontWeight": "400"}),
            html.H2(value, className="mb-1",
                    style={"fontSize": "32px", "fontWeight": "700", "color": card_color}),
            html.Small(subtitle or "", className="text-muted",
                      style={"fontSize": "12px"}) if subtitle else html.Div(),
        ])
    ], className="h-100 shadow-sm")
    return card
```

---

## Plotly Figure Standards

### Figure Construction Pattern
```python
def create_forest_plot(results_df, title="Effect Sizes"):
    """Create a publication-quality forest plot.
    
    Args:
        results_df: DataFrame with columns [variable, estimate, ci_lower, ci_upper, p_value]
        title: Plot title
    
    Returns:
        go.Figure
    """
    fig = go.Figure()
    
    # Sort by estimate
    df = results_df.sort_values("estimate").reset_index(drop=True)
    
    # Add confidence interval bars
    fig.add_trace(go.Scatter(
        x=df["estimate"], y=df["variable"],
        error_x=dict(type="data", array=df["ci_upper"] - df["estimate"],
                     arrayminus=df["estimate"] - df["ci_lower"],
                     visible=True, color="#999999", thickness=1.5, width=3),
        mode="markers", marker=dict(
            size=8,
            color=[SEMANTIC["significant"] if p < 0.05 else SEMANTIC["null"]
                   for p in df["p_value"]],
        ),
        name="Effect Size",
        hovertemplate="<b>%{y}</b><br>Estimate: %{x:.3f}<br>"
                      "95% CI: [%{customdata[0]:.3f}, %{customdata[1]:.3f}]<br>"
                      "p = %{customdata[2]:.4f}<extra></extra>",
        customdata=df[["ci_lower", "ci_upper", "p_value"]].values,
    ))
    
    # Add null line
    fig.add_vline(x=0, line_dash="dash", line_color="#999999", line_width=1,
                  annotation_text="Null")
    
    # Layout
    fig.update_layout(
        template=plotly_template,
        title={"text": title, "x": 0.5, "xanchor": "center"},
        xaxis_title="Effect Size (95% CI)",
        yaxis_title="",
        yaxis={"autorange": "reversed"},
        height=max(300, len(df) * 35),
        showlegend=False,
        margin={"l": 150, "r": 20, "t": 50, "b": 50},
    )
    
    return fig
```

### Responsive Sizing
```python
# Dashboard figures: responsive
fig.update_layout(
    autosize=True,
    height=400,  # Base height, scales with container
)

# Static figures: fixed journal size
fig.update_layout(
    width=689,   # 17.5cm at 300 DPI (double column)
    height=430,  # Golden ratio
)
```

---

## CSS Standards for Dashboards

### assets/custom.css
```css
/* ── Typography ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
    color: #333333;
    background-color: #F8F9FA;
}

/* ── Cards ── */
.card {
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    transition: box-shadow 0.2s ease;
}

.card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

/* ── Tables ── */
.dash-table-container {
    font-size: 12px !important;
}

.dash-header {
    background-color: #F8F9FA !important;
    font-weight: 600 !important;
}

/* ── Tabs ── */
.nav-tabs .nav-link.active {
    font-weight: 600;
    border-bottom: 3px solid #0072B2;
}

/* ── Loading States ── */
.dash-loading {
    color: #0072B2;
}

/* ── Print Styles ── */
@media print {
    .no-print { display: none !important; }
    .card { box-shadow: none !important; border: 1px solid #ccc !important; }
}
```

---

## Performance Standards

### Data Loading
```python
from functools import lru_cache

@lru_cache(maxsize=32)
def load_analysis_data():
    """Cache analysis results to avoid recomputation."""
    # Load from pre-computed files, not raw data
    return pd.read_parquet("data/03_analytical/analysis_results.parquet")
```

### Figure Caching
```python
from dash import ctx

@callback(
    Output("forest-plot", "figure"),
    Input("method-selector", "value"),
    prevent_initial_call=False,
)
def update_forest_plot(method):
    """Only recompute when input changes."""
    if not ctx.triggered:
        return dash.no_update
    return create_forest_plot(filtered_results(method))
```

---

## Testing Standards

### Figure Validation
```python
def validate_figure(fig, expected_traces=None, min_height=200):
    """Validate a Plotly figure meets standards."""
    errors = []
    
    if not hasattr(fig, 'data') or len(fig.data) == 0:
        errors.append("Figure has no traces")
    
    if expected_traces and len(fig.data) != expected_traces:
        errors.append(f"Expected {expected_traces} traces, got {len(fig.data)}")
    
    if fig.layout.height < min_height:
        errors.append(f"Figure height {fig.layout.height} below minimum {min_height}")
    
    # Check for axis labels
    if not fig.layout.xaxis.title:
        errors.append("Missing x-axis label")
    if not fig.layout.yaxis.title:
        errors.append("Missing y-axis label")
    
    return {"valid": len(errors) == 0, "errors": errors}
```

### Dashboard Smoke Test
```python
def test_dashboard_loads():
    """Verify dashboard starts without errors."""
    from overview_dashboard import app
    assert app.layout is not None
    # Test each tab renders
    for tab_id in ["tab-overview", "tab-data", "tab-results"]:
        content = app.layout  # Simplified — use dash.testing in production
        assert content is not None
```

---

## Anti-Patterns (NEVER Do These)

1. **Inline plotting** — All plots must be functions
2. **Hardcoded colors** — Use theme constants
3. **No error handling** — Every function must catch and report errors
4. **No validation** — Validate data before plotting
5. **No alt text** — Every figure needs accessibility text
6. **Spaghetti callbacks** — Use component pattern, not monolithic callbacks
7. **Raw data in dashboard** — Load pre-computed analysis results
8. **No loading states** — Show spinners during computation
9. **Inconsistent sizing** — Use theme constants for all sizes
10. **No testing** — Validate figures and test dashboards

---

## Validation Checklist

Every visualization script and dashboard MUST pass:
- [ ] Uses theme module (viz_theme.py)
- [ ] All plots are functions, not inline code
- [ ] Data validated before plotting
- [ ] Error handling in all functions
- [ ] No hardcoded colors, sizes, or paths
- [ ] Dashboard uses component-based architecture
- [ ] CSS follows design system
- [ ] Figures have proper labels and titles
- [ ] Alt text provided for accessibility
- [ ] Performance: cached data, lazy loading
- [ ] Tested: validation functions pass
