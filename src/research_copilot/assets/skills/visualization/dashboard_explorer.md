---
skill_id: "dashboard_explorer"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "dash", "plotly", "dash-bootstrap-components", "pandas"]
depends_on: ["viz_design_system", "viz_code_standards", "profile_tabular"]
produces:
  - "reports/dashboards/data_explorer.py"
  - "reports/dashboards/components/explorer/"
complexity: "intermediate"
---

# Skill: Interactive Data Explorer Dashboard

## Purpose
Build an interactive dashboard for exploring raw and processed data: filtering, sorting, visualizing distributions, and profiling variables. Built with component architecture and automatic plot type selection.

## When to Use
- After data profiling
- For exploratory data analysis
- Collaborative data review
- Data quality assessment

---

## Architecture

### File Structure
```
reports/dashboards/
  data_explorer.py
  components/
    explorer/
      __init__.py
      data_table.py           # Paginated, filterable table
      variable_profile.py     # Auto-type-aware variable plots
      bivariate.py            # Auto-type-aware bivariate plots
      filters.py              # Filter panel
      summary_cards.py        # Data summary metrics
```

---

## Layout

```
┌─────────────────────────────────────────────────┐
│  Data Explorer — [Dataset Name]                  │
├─────────────────────────────────────────────────┤
│  [Dropdown: Dataset]  [N = XXXX]  [p = XX vars] │
├─────────────────────────────────────────────────┤
│  Summary Cards                                   │
│  [Rows] [Columns] [Missing %] [Duplicates]       │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────────────────┐  │
│  │ Variable    │  │  Variable Distribution    │  │
│  │ Selector    │  │  (auto-type plot)         │  │
│  │             │  │                           │  │
│  │ [Search]    │  │                           │  │
│  │ [Type filt] │  │                           │  │
│  └─────────────┘  └──────────────────────────┘  │
├─────────────────────────────────────────────────┤
│  Bivariate Explorer                              │
│  X: [Dropdown]  Y: [Dropdown]  Color: [Dropdown]│
│  ┌──────────────────────────────────────────┐   │
│  │  Auto-type bivariate plot                │   │
│  └──────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  Filter Panel                                    │
│  [Condition builder] [Apply] [Reset] [Export]   │
├─────────────────────────────────────────────────┤
│  Data Table (paginated, sortable, filterable)   │
└─────────────────────────────────────────────────┘
```

---

## Auto-Type Plot Selection

### Univariate (Single Variable)
| Variable Type | Plot Type | Features |
|--------------|-----------|----------|
| Continuous | Histogram + KDE + rug | Density overlay, mean/median lines |
| Categorical | Bar chart | Sorted by frequency, proportions on hover |
| Ordinal | Bar chart | Preserves order, frequency labels |
| Temporal | Line plot | Time axis, trend line, seasonality |
| Binary | Donut chart | Proportions, counts |
| Text | Length histogram | Word count distribution |

### Bivariate (Two Variables)
| X Type | Y Type | Plot Type | Features |
|--------|--------|-----------|----------|
| Continuous | Continuous | Scatter + regression line | Confidence band, correlation |
| Continuous | Categorical | Violin plot | Distribution per category |
| Categorical | Continuous | Box plot | Median, IQR, outliers |
| Categorical | Categorical | Stacked bar | Proportions, counts |
| Temporal | Continuous | Line plot | Time series, trend |
| Continuous | Temporal | Line plot | Time on x-axis |

---

## Component Specifications

### Variable Profile Plot
```python
def create_variable_profile(df, column):
    """Auto-generate appropriate plot based on variable type.
    
    Returns:
        go.Figure with appropriate plot type
    """
    col_type = infer_column_type(df[column])
    plot_funcs = {
        "continuous": histogram_with_kde,
        "categorical": bar_chart_proportions,
        "ordinal": ordered_bar_chart,
        "temporal": time_series_plot,
        "binary": donut_chart,
    }
    return plot_funcs[col_type](df, column)
```

### Bivariate Plot
```python
def create_bivariate_plot(df, x_col, y_col, color_col=None):
    """Auto-generate bivariate plot based on variable types.
    
    Returns:
        go.Figure with appropriate plot type
    """
    x_type = infer_column_type(df[x_col])
    y_type = infer_column_type(df[y_col])
    # Dispatch to appropriate plot function
```

### Filter Panel
```python
def create_filter_panel(df):
    """Generate filter controls for each variable type.
    
    Continuous: Range slider
    Categorical: Multi-select dropdown
    Temporal: Date range picker
    Binary: Toggle switch
    """
```

---

## Data Table Features

- **Pagination**: 50 rows per page (configurable)
- **Sorting**: Click column header to sort
- **Filtering**: Per-column filter controls
- **Conditional formatting**:
  - Missing values: highlighted in orange
  - Outliers: highlighted in red
  - Duplicate rows: highlighted in yellow
- **Export**: Filtered subset as CSV
- **Column types**: Color-coded header by semantic type

---

## Filter System

### Filter Types
- **Range**: Min/max slider for continuous variables
- **Category**: Multi-select checkbox for categorical
- **Date**: Date range picker for temporal
- **Text**: Contains/starts with/equals for text
- **Missing**: Show/hide missing values

### Filter Logic
- Multiple filters combine with AND
- Live N counter shows filtered sample size
- Reset button clears all filters
- Export button downloads filtered data

---

## Performance

- **DataTable**: Virtualized rendering (only visible rows)
- **Plots**: Cached per variable (don't recompute on tab switch)
- **Filters**: Debounced (wait 300ms after last input)
- **Large datasets**: Sample to 10,000 rows for plots, show full in table

---

## Implementation Steps

1. **Create explorer components** — data_table.py, variable_profile.py, bivariate.py, filters.py
2. **Build main app** — Import components, define layout
3. **Implement type inference** — Auto-detect variable types
4. **Wire callbacks** — Variable selector → plot, filters → table
5. **Add export** — CSV download of filtered data
6. **Test** — Verify all plot types, filters, table features

---

## Output Specification
- `reports/dashboards/data_explorer.py`: Runnable Dash app
- `reports/dashboards/components/explorer/`: Explorer components

## Validation Checks
- [ ] DataTable loads without error
- [ ] Variable plots render correctly for ALL types
- [ ] Bivariate plots dispatch to correct type combination
- [ ] Filters correctly subset data
- [ ] Live N counter updates with filters
- [ ] Export produces valid CSV with filtered data
- [ ] Conditional formatting works (missing, outliers, duplicates)
- [ ] No hardcoded colors or sizes
- [ ] All figures pass design system validation
- [ ] Runs on port 8050 without errors
