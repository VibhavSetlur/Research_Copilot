---
skill_id: "dashboard_results"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly", "dash-bootstrap-components", "statsmodels"]
depends_on: ["viz_design_system", "viz_code_standards", "inferential_parametric", "inferential_nonparametric"]
produces:
  - "reports/dashboards/results_dashboard.py"
  - "reports/dashboards/components/results/"
complexity: "advanced"
---

# Skill: Results Dashboard

## Purpose
Build an interactive dashboard for exploring statistical analysis results: effect sizes, model coefficients, diagnostics, and model comparisons. Built with component architecture, proper statistical visualization, and reproducibility.

## When to Use
- After inferential analysis completed
- For results review and sensitivity analysis
- Comparing multiple model specifications
- Peer review preparation

---

## Architecture

### File Structure
```
reports/dashboards/
  results_dashboard.py
  components/
    results/
      __init__.py
      forest_plot.py          # Interactive forest plot component
      coefficient_table.py    # Sortable results table
      model_comparison.py     # Side-by-side model comparison
      sensitivity.py          # Sensitivity analysis controls
      diagnostics.py          # Model diagnostic plots
```

---

## Layout

### Tab 1: Effect Sizes
```
┌─────────────────────────────────────────────────┐
│  Effect Sizes                                    │
├─────────────────────────────────────────────────┤
│  [Dropdown: Question] [Dropdown: Method]        │
│  [Checkbox: Show non-significant]               │
├─────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐   │
│  │  Forest Plot                             │   │
│  │  • Effect sizes with 95% CI bars        │   │
│  │  • Color: significant vs non-significant │   │
│  │  • Null reference line                   │   │
│  │  • Hover: full statistics                │   │
│  └──────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  Results Table                                   │
│  Variable | Estimate | 95% CI | SE | p | adj. p │
│  [Sortable] [Filterable] [Exportable]           │
└─────────────────────────────────────────────────┘
```

### Tab 2: Model Comparison
```
┌─────────────────────────────────────────────────┐
│  Model Comparison                                │
├─────────────────────────────────────────────────┤
│  [Multi-select: Models to compare]              │
├─────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐   │
│  │  Coefficient Comparison Plot             │   │
│  │  • Dot-and-whisker for each model        │   │
│  │  • Color by model                        │   │
│  │  • Highlight unstable coefficients       │   │
│  └──────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  Model Fit Table                                 │
│  Model | AIC | BIC | R² | Log-Likelihood | N   │
└─────────────────────────────────────────────────┘
```

### Tab 3: Sensitivity Analysis
```
┌─────────────────────────────────────────────────┐
│  Sensitivity Analysis                            │
├─────────────────────────────────────────────────┤
│  Controls:                                       │
│  [ ] Exclude outliers                           │
│  [ ] Remove covariate: [dropdown]               │
│  [ ] Subgroup: [dropdown]                       │
│  [ ] Alternative method: [dropdown]             │
├─────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐   │
│  │  Sensitivity Plot                        │   │
│  │  • Base estimate (bold line)             │   │
│  │  • Sensitivity estimates (lighter lines) │   │
│  │  • Color: changes conclusion vs not      │   │
│  └──────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  Sensitivity Summary                             │
│  Specification | Estimate | 95% CI | Conclusion │
│  [Highlight: specifications that change result] │
└─────────────────────────────────────────────────┘
```

---

## Component Specifications

### Forest Plot
```python
def create_forest_plot(
    results_df,
    title="Effect Sizes",
    show_null_line=True,
    color_by_significance=True,
    sort_by="estimate",
    sort_order="descending",
):
    """Publication-quality forest plot.
    
    Features:
    - Sorted by effect size or p-value
    - Color-coded by significance
    - Null reference line
    - Hover with full statistics
    - Proper CI error bars
    """
```

### Coefficient Table
```python
def create_coefficient_table(
    results_df,
    columns=None,
    sort_by="p_value",
    sort_order="ascending",
    highlight_significant=True,
    show_adjusted_p=True,
):
    """Interactive dash-table for results.
    
    Features:
    - Sortable by any column
    - Color-coded significance
    - Export to CSV
    - Conditional formatting
    """
```

### Model Comparison Plot
```python
def create_model_comparison(
    models_dict,  # {model_name: results_df}
    highlight_unstable=True,
    threshold=0.1,  # Coefficient change threshold
):
    """Side-by-side coefficient comparison.
    
    Features:
    - Dot-and-whisker for each model
    - Highlight coefficients that change > threshold
    - Model fit statistics table
    """
```

### Sensitivity Analysis
```python
def create_sensitivity_plot(
    base_estimate,
    sensitivity_results,  # List of (spec_name, estimate, ci_lower, ci_upper)
    highlight_conclusion_changes=True,
):
    """Sensitivity analysis visualization.
    
    Features:
    - Base estimate as reference
    - All sensitivity specs overlaid
    - Color: changes conclusion vs doesn't
    - Summary table with all specs
    """
```

---

## Statistical Visualization Standards

### Forest Plot Rules
- Sort by effect size (largest first) or p-value (smallest first)
- Null line clearly visible (dashed, gray)
- Significant results in blue, non-significant in gray
- Hover shows: estimate, CI, p-value, adjusted p-value, N
- Y-axis labels: variable names (not codes)
- X-axis: labeled with effect size metric (β, OR, RR, etc.)

### Coefficient Table Rules
- Show: estimate, SE, 95% CI, p-value, adjusted p-value
- Sort by p-value by default
- Highlight significant rows (subtle background color)
- Show N for each estimate
- Format numbers: 3 decimal places for estimates, 4 for p-values
- Scientific notation for very small p-values (p < 0.001)

### Model Comparison Rules
- Show coefficients for ALL models side by side
- Highlight coefficients that change > 10% across models
- Include model fit statistics (AIC, BIC, R², log-likelihood)
- Order models: simplest to most complex
- Use consistent color per model

### Sensitivity Analysis Rules
- Base estimate clearly marked
- Show ALL sensitivity specifications
- Color-code: specifications that change the conclusion
- Report: which specifications alter the conclusion
- Never hide sensitivity results that contradict main finding

---

## Interactive Features

### Filters
- **Question selector**: Filter results by research question
- **Method selector**: Choose analysis method
- **Significance filter**: Show/hide non-significant results
- **Variable filter**: Select specific variables
- **Model selector**: Choose which models to compare

### Downloads
- **Forest plot PNG**: High-resolution export
- **Results CSV**: Full results table
- **Model comparison CSV**: All model coefficients
- **Sensitivity report**: Full sensitivity analysis summary

### Tooltips
- **Statistical terms**: Explain estimate, CI, p-value
- **Variable names**: Show variable definition
- **Method descriptions**: Explain analysis approach

---

## Implementation Steps

1. **Create result components** — forest_plot.py, coefficient_table.py, model_comparison.py, sensitivity.py
2. **Load pre-computed results** — From analysis output files
3. **Build main app** — Import components, define layout
4. **Implement callbacks** — Filter updates, comparison toggles
5. **Add download handlers** — PNG, CSV exports
6. **Test** — Verify all tabs, filters, downloads
7. **Validate** — All figures pass design system checks

---

## Output Specification
- `reports/dashboards/results_dashboard.py`: Runnable Dash app
- `reports/dashboards/components/results/`: Result components

## Validation Checks
- [ ] Forest plot correctly shows effect sizes and CIs
- [ ] Coefficient table matches analysis output
- [ ] Model comparison highlights unstable coefficients
- [ ] Sensitivity analysis shows all specifications
- [ ] Filters correctly subset results
- [ ] Downloads produce correct files
- [ ] No hardcoded colors or sizes
- [ ] All figures pass design system validation
- [ ] Runs on port 8050 without errors
- [ ] Statistical values match computed results exactly
