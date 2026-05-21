---
skill_id: "figure_missingness"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "missingno"]
depends_on: ["viz_design_system", "viz_code_standards", "detect_missingness"]
produces: ["reports/figures/missingness/"]
complexity: "basic"
---

# Skill: Missingness Visualization

## Purpose
Generate figures showing missing data patterns, mechanisms, and impact on analysis.

## When to Use
- After missingness analysis
- For methods section (missing data handling)
- Diagnosing missingness mechanisms

---

## Figure Specifications

### Missingness Matrix
```python
def plot_missingness_matrix(df, max_rows=1000, ax=None):
    """Heatmap of missing data pattern.
    
    Features:
    - Rows: observations (sampled if N > max_rows)
    - Columns: variables (sorted by missingness)
    - Missing: dark color, Present: light color
    - Sparkline on right: missingness per row
    - Bar chart on bottom: missingness per column
    """
```

### Missingness Bar Chart
```python
def plot_missingness_bars(df, ax=None, sort=True):
    """Horizontal bar chart of missing proportions.
    
    Features:
    - Sorted: highest missingness at top
    - Annotated: exact percentage on each bar
    - Color gradient: green (0%) → yellow (20%) → red (50%+)
    - Threshold line: warning level (20%)
    """
```

### Missingness Correlation
```python
def plot_missingness_correlation(df, ax=None):
    """Heatmap of pairwise missingness correlations.
    
    Features:
    - Binary indicators: 1 if missing, 0 if present
    - Phi coefficient (for binary-binary correlation)
    - Diverging colormap
    - Only show variables with > 5% missingness
    """
```

### Missingness by Subgroup
```python
def plot_missingness_by_subgroup(df, group_col, ax=None):
    """Missing rate in other variables by subgroup.
    
    Features:
    - Grouped bar chart
    - One bar per variable, grouped by category
    - Identifies MAR mechanism
    """
```

---

## Output Standards

### File Naming
```
fig_miss_001_matrix.png
fig_miss_002_bars.png
fig_miss_003_correlation.png
fig_miss_004_by_subgroup.png
```

## Validation Checks
- [ ] Matrix shows correct missing pattern
- [ ] Bar chart percentages match computed values
- [ ] Correlation matrix is symmetric
- [ ] Subgroup analysis includes all categories
- [ ] Design system theme applied
