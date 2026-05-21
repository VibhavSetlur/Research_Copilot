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
Generate a publication-grade interactive dashboard integrating all research outputs. Component-based architecture, responsive design, accessibility.

## When to Use
- After all analysis completed
- Interactive exploration, sharing with collaborators, conference presentations

## When NOT to Use
- Only static reports needed, analysis incomplete, data under NDA

---

## Architecture

### File Structure
```
reports/dashboards/
  overview_dashboard.py       # Main app (≤200 lines)
  components/
    cards.py, charts.py, tables.py, filters.py, layout.py
  assets/custom.css
  data/dashboard_cache.parquet
```

### Design Rules
1. Main app ≤200 lines — all logic in component files
2. No raw data loading in callbacks — use pre-computed parquet cache
3. Every component is a function returning a Dash component
4. Theme applied globally via `viz_theme.py`
5. Bootstrap 12-column responsive grid
6. Loading spinners on every callback

---

## Tab Structure

### Tab 1: Overview
Metric cards (N obs, variables, results, significant findings, effect size range), main finding visualization, correlation heatmap of key variables, research questions summary table with status.

### Tab 2: Data Explorer
Dataset selector dropdown, variable selector, filter panel with live N counter, variable distribution plot, bivariate plot (X vs Y), paginated/sortable/filterable data table.

### Tab 3: Results
Question selector, method selector, forest plot (effect sizes + CIs), sortable results table with columns: Variable, Estimate, 95% CI, p, Adjusted p.

### Tab 4: Diagnostics
Model selector, 2×3 grid: Residuals vs Fitted, Q-Q Plot, Scale-Location, Cook's D, VIF Values, Missingness Pattern.

---

## Component Specifications

- **Metric card**: `create_metric_card(title, value, subtitle, color, icon, trend)` — standardized card with semantic color
- **Chart container**: `create_chart_container(figure, title, footer, height)` — wraps any Plotly figure in a card with loading state
- **Filter panel**: `create_filter_panel(filters, id_prefix)` — generates dropdown, range slider, date picker, checkbox controls

## Interactive Features
- Variable multi-select, subgroup filter, numeric range sliders, method selector, live N counter
- PNG export per figure, CSV export for tables, PDF report via WeasyPrint
- Tooltips for statistical terms, variable descriptions, method info

## Styling
Use Bootstrap FLATLY or LUX theme, Okabe-Ito palette, Inter font, 12-column grid, card shadows on hover. NEVER use default Plotly colors, inline CSS, hardcoded sizes, >8 colors per figure, 3D/pie charts.

## Accessibility
All figures have `aria-label`, color is never the only differentiator, keyboard navigation works, WCAG AA contrast (4.5:1 minimum), screen reader can navigate tabs.

---

## Generate Static Export

After building the Dash app, export each figure as standalone HTML and assemble into `dashboard_static.html`:

1. **Extract figures**: Call each component's figure-building function directly (bypass Dash callbacks). Use `plotly.io.to_html(fig, include_plotlyjs='cdn', full_html=False)` for each figure.

2. **Jinja2 template**: Create a template with sections for Overview (summary cards), Results (main_finding, correlation_heatmap, forest_plot), and Diagnostics (residuals_plot). Use `{{ fig_html | safe }}` to embed Plotly HTML. Include Plotly CDN in `<head>`.

3. **Assemble**: Render template with figures dict, summary_cards list, and timestamp. Write to `reports/dashboards/dashboard_static.html`.

4. **Usage**: `generate_static_export(app, data_cache_path, output_dir, summary_cards)` — call after Dash app is built. Output is shareable without Python, interactive via Plotly CDN.

---

## Validation
- [ ] Main app ≤200 lines
- [ ] All components are functions in separate files
- [ ] No raw data loading in callbacks
- [ ] Design system theme applied globally
- [ ] All 4 tabs render without errors
- [ ] Filters update figures correctly
- [ ] Download buttons functional
- [ ] Loading states shown during computation
- [ ] Accessibility: alt text, contrast, keyboard nav
- [ ] Static export generates valid HTML
