---
skill_id: "figure_descriptive"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "plotly"]
depends_on: ["viz_design_system", "viz_code_standards", "descriptive_stats"]
produces: ["reports/figures/descriptive/"]
complexity: "basic"
---

# Skill: Descriptive Statistics Figures

## Purpose
Generate publication-quality figures summarizing descriptive statistics. Every figure uses the design system theme, proper sizing, and accessibility standards.

## When to Use
- After descriptive statistics computed
- For Table 1 visualizations
- Exploratory data analysis

---

## Figure Specifications

### Distribution Plots

#### Histogram + KDE
```python
def plot_distribution(df, column, ax=None, bins=30, add_stats=True):
    """Histogram with KDE overlay and statistics.
    
    Features:
    - Density histogram (area = 1)
    - KDE curve overlay
    - Mean (solid line) and median (dashed line)
    - Statistics box: mean, median, SD, skewness, N
    - Proper axis labels with units
    """
```

#### Violin Plot (Grouped)
```python
def plot_violin_grouped(df, value_col, group_col, ax=None):
    """Violin plot comparing distributions across groups.
    
    Features:
    - Violin shape (distribution density)
    - Box plot inside (median, IQR)
    - Individual data points (jittered, if N < 200)
    - Color: Okabe-Ito palette
    - Sorted by median (descending)
    """
```

#### Raincloud Plot
```python
def plot_raincloud(df, value_col, group_col, ax=None):
    """Raincloud plot: half-violin + box + raw data.
    
    Features:
    - Half-violin (distribution shape)
    - Box plot (median, IQR, whiskers)
    - Jittered raw data points
    - Best for: group comparisons with moderate N
    """
```

### Categorical Plots

#### Bar Chart (Sorted)
```python
def plot_categorical_bar(df, column, ax=None, normalize=True):
    """Bar chart of category frequencies, sorted descending.
    
    Features:
    - Sorted by frequency (highest first)
    - Proportion labels on bars
    - Count labels below bars
    - Color: single hue (Blues)
    - Horizontal orientation (better for long labels)
    """
```

#### Stacked Bar (Cross-tabulation)
```python
def plot_stacked_bar(df, row_col, col_col, ax=None, normalize="row"):
    """Stacked bar chart for cross-tabulation.
    
    Features:
    - Proportional stacking
    - Legend with category labels
    - Color: Okabe-Ito palette
    - Normalize by row, column, or total
    """
```

### Multivariate Plots

#### Correlation Heatmap
```python
def plot_correlation_heatmap(df, columns=None, ax=None, 
                              method="pearson", annot=True):
    """Correlation matrix heatmap.
    
    Features:
    - Diverging colormap (RdBu_r, centered at 0)
    - Annotated with r values (2 decimal places)
    - Sorted by hierarchical clustering
    - Square cells
    - Colorbar with labeled scale
    """
```

#### Pairplot (Subset)
```python
def plot_pairplot(df, columns=None, max_vars=6, hue=None):
    """Pairplot for key variables (max 6×6).
    
    Features:
    - Diagonal: histogram + KDE
    - Off-diagonal: scatter + regression line
    - Color by hue variable if specified
    - Size: 3" × 3" per panel
    """
```

---

## Output Standards

### File Naming
```
fig_desc_001_distribution_[variable].png
fig_desc_002_violin_[value]_by_[group].png
fig_desc_003_correlation_heatmap.png
fig_desc_004_pairplot_[vars].png
```

### Format
- **Primary**: PNG at 300 DPI
- **Editable**: SVG (for line art)
- **Size**: Single column (3.35" wide) or double column (6.89" wide)

---

## Validation Checks
- [ ] All figures have axis labels with units
- [ ] Colorblind-safe palettes used
- [ ] No overlapping text or labels
- [ ] Figures match descriptive statistics values
- [ ] Font sizes meet minimum (10pt)
- [ ] Design system theme applied
- [ ] Statistical annotations follow standards
