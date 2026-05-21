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
Professional code quality for ALL visualization and dashboard code. No spaghetti plots. No hardcoded values. No untested rendering.

---

## Architecture Rules

1. **Modular design**: Main entry point (`03_figures.py`) imports from `utils/viz_theme.py`, `utils/viz_helpers.py`, `utils/viz_validation.py`.
2. **Function-based plotting**: NEVER inline plotting code. Every plot type is a function.
3. **Configuration over hardcoding**: Use theme constants for colors, sizes, paths. Never `color="#FF0000"` or `dpi=150`.
4. **Data validation before plotting**: Check required columns exist, min rows ≥3, not all null.
5. **Error handling**: All plotting functions return `{"status": "success/error", "path": ...}` dicts.

---

## Dashboard Architecture

Component-based structure: main app (≤200 lines) imports from `components/cards.py`, `components/charts.py`, `components/tables.py`, `components/filters.py`, `components/layout.py`. Assets in `assets/custom.css`. Data pre-computed to `data/dashboard_cache.parquet` — never load raw data in callbacks.

Every component is a function returning a Dash component. Use `@lru_cache` for data loading. Callbacks show loading spinners. Use `dash.no_update` when input hasn't changed.

---

## Plotly Figure Standards

Build figures with `go.Figure()`, add traces, set layout. Use `template=plotly_template` from theme. Sort data before plotting. Add null reference lines with `fig.add_vline()`. Use `customdata` for hover templates. Responsive sizing: `autosize=True, height=400` for dashboards. Fixed sizing: `width=689, height=430` for static journal figures.

---

## CSS Standards

Import Inter font. Card styling: border, border-radius 8px, hover shadow. Tables: 12px font, bold headers. Tabs: active tab has 3px bottom border in accent color. Loading states: accent color. Print styles: hide non-print elements, remove shadows.

---

## Performance

Cache data with `@lru_cache(maxsize=32)`. Load pre-computed parquet, not raw data. Only recompute when callback input changes (`if not ctx.triggered: return dash.no_update`).

---

## Accessibility Annotation

**Every figure MUST have screen reader metadata.**

### Plotly
Set `fig.update_layout(meta={'alt_text': '...'})`. Add `aria-label` on the containing `html.Div`. Make focusable with `tabIndex=0`.

### matplotlib
Pass `metadata={'Title': '...', 'Description': '...'}` to `fig.savefig()`. Set figure title.

### Alt Text Template
`[Figure type] of [N] observations showing [relationship]. [Key finding with statistics]. [Visual encoding note].`

Examples:
- "Scatter plot of 1,234 observations showing positive association between income and life satisfaction. β = 0.34, 95% CI [0.21, 0.47], p < .001."
- "Forest plot of 5 coefficients. Three significant (blue), two non-significant (gray). Effects range 0.12 to 0.67."

### Dashboard ARIA
Wrap figures in `html.Div(dcc.Graph(figure=fig), role="img", aria-label=alt_text, tabIndex=0)`. Tables: `role="table", aria-label="..."`.

### Validation
`check_figure_accessibility(fig)` — checks for alt_text in Plotly meta or title in matplotlib axes. Returns `{"accessible": bool, "issues": [...]}`.

---

## Anti-Patterns (NEVER)
1. Inline plotting — all plots must be functions
2. Hardcoded colors — use theme constants
3. No error handling — every function catches errors
4. No validation — validate data before plotting
5. No alt text — every figure needs accessibility metadata
6. Spaghetti callbacks — use component pattern
7. Raw data in dashboard — use pre-computed cache
8. No loading states — show spinners
9. Inconsistent sizing — use theme constants
10. No testing — validate figures and test dashboards

---

## Validation Checklist
- [ ] Uses theme module (viz_theme.py)
- [ ] All plots are functions
- [ ] Data validated before plotting
- [ ] Error handling in all functions
- [ ] No hardcoded colors, sizes, or paths
- [ ] Component-based dashboard architecture
- [ ] CSS follows design system
- [ ] Proper labels and titles
- [ ] Alt text on every figure
- [ ] Cached data, lazy loading
- [ ] Validation functions pass

---

## Dashboard Smoke Test

**Requires:** `pip install dash[testing]`

Do NOT call `app.layout` directly — this does not trigger callbacks. Use one of these approaches:

### Option 1: Layout value (quick check)
```python
from app import app
layout = app._layout_value()  # Returns the resolved layout tree
assert layout is not None
```

### Option 2: Dash testing (full callback test)
```python
from dash.testing.application_runners import DashRunner
from app import app

runner = DashRunner()
with runner(app) as drv:
    drv.wait_for_element("#main-content")
    assert drv.find_element("#main-content").is_displayed()
```

### Option 3: pytest-dash (CI-friendly)
```python
def test_dashboard_loads(dash_duo):
    from app import app
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#main-content")
    assert dash_duo.find_element("#main-content").is_displayed()
```
