---
skill_id: "figure_inferential"
version: "8.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "plotly", "statsmodels"]
depends_on: ["viz_design_system", "viz_code_standards", "inferential_parametric", "inferential_nonparametric"]
produces: ["reports/figures/inferential/"]
complexity: "intermediate"
---

# Skill: Inferential Statistics Figures

## Purpose
Generate publication-quality figures visualizing inferential test results: effect sizes, confidence intervals, model diagnostics, and p-value functions. Every figure meets journal standards.

## When to Use
- After inferential tests completed
- For results section figures
- Model diagnostic checking

---

## Figure Specifications

### Effect Size Figures

#### Forest Plot
```python
def plot_forest(results_df, ax=None, sort_by="estimate",
                show_null=True, color_by_sig=True):
    """Forest plot: effect sizes with 95% CIs.
    
    Features:
    - Point estimate with CI error bars
    - Null reference line (dashed)
    - Sorted by effect size or p-value
    - Color: significant (blue), non-significant (gray)
    - Y-axis: variable names
    - X-axis: effect size metric with label
    - Optional: diamond for pooled estimate
    """
```

#### Dot-and-Whisker Plot
```python
def plot_dotwhisker(results_df, ax=None, sort_by="magnitude",
                    group_by=None):
    """Dot-and-whisker: coefficients sorted by magnitude.
    
    Features:
    - Dot: point estimate
    - Whisker: confidence interval
    - Sorted by absolute effect size
    - Grouped by model if multiple models
    - Null reference line
    """
```

#### Caterpillar Plot
```python
def plot_caterpillar(results_df, ax=None):
    """Caterpillar plot: ranked effect sizes.
    
    Features:
    - Ranked by effect size (largest first)
    - CI bars
    - Color by significance
    - Best for: many estimates (meta-analysis, multilevel)
    """
```

### Model Diagnostic Plots

#### Four-Panel Diagnostic
```python
def plot_model_diagnostics(model, fig=None):
    """Four-panel model diagnostic plot.
    
    Panel 1: Residuals vs Fitted
    - Check homoscedasticity
    - Red line: LOWESS smooth
    - Should show random scatter
    
    Panel 2: Q-Q Plot
    - Check residual normality
    - Reference line: theoretical quantiles
    - Deviations indicate non-normality
    
    Panel 3: Scale-Location
    - Check variance homogeneity
    - sqrt(|standardized residuals|) vs fitted
    - Red line: LOWESS smooth
    
    Panel 4: Residuals vs Leverage
    - Identify influential points
    - Cook's D contours (0.5, 1.0)
    - Label points with high leverage
    """
```

### Group Comparison Figures

#### Mean Comparison Plot
```python
def plot_mean_comparison(df, value_col, group_col, ax=None,
                          ci=0.95, show_raw=False):
    """Group means with 95% CI error bars.
    
    Features:
    - Point: group mean
    - Error bar: 95% CI
    - Optional: raw data points (jittered)
    - Sorted by mean (descending)
    - Significance brackets between groups
    """
```

#### Raincloud Plot (Inferential)
```python
def plot_raincloud_inferential(df, value_col, group_col, ax=None,
                                show_test=True, test="t-test"):
    """Raincloud plot with statistical test annotation.
    
    Features:
    - Half-violin + box + raw data
    - Statistical test result annotation
    - Effect size with CI
    - Significance marker
    """
```

### P-value Visualization

#### P-value Function Plot
```python
def plot_pvalue_function(estimate, se, ax=None, 
                          alpha=0.05, show_ci=True):
    """P-value function (confidence curve).
    
    Features:
    - X-axis: effect size values
    - Y-axis: p-value for each hypothesized value
    - Horizontal line: alpha threshold
    - Shaded region: confidence interval
    - Shows full p-value curve, not just threshold
    """
```

#### Volcano Plot
```python
def plot_volcano(results_df, ax=None, 
                  sig_threshold=0.05, effect_threshold=0):
    """Volcano plot: effect size vs -log10(p).
    
    Features:
    - X-axis: effect size
    - Y-axis: -log10(p-value)
    - Color: significant vs non-significant
    - Label: top significant results
    - Threshold lines: p-value and effect size
    """
```

---

## Statistical Annotation Standards

### Significance Markers
```
ns    p > 0.05
*     p ≤ 0.05
**    p ≤ 0.01
***   p ≤ 0.001
****  p ≤ 0.0001
```

### Effect Size Display
- Always show: estimate + 95% CI
- Format: `β = 0.42 [0.18, 0.66]`
- Never show p-value alone
- Report exact p-values (not just "p < 0.05")

### Significance Brackets
```python
def add_significance_bracket(ax, x1, x2, y, label, offset=0.1):
    """Add significance bracket between two groups.
    
    Features:
    - Horizontal line connecting groups
    - Label: *, **, ***, or ns
    - Proper vertical offset
    """
```

---

## Output Standards

### File Naming
```
fig_inf_001_forest_[question].png
fig_inf_002_diagnostics_[model].png
fig_inf_003_volcano_[analysis].png
fig_inf_004_pvalue_function_[variable].png
```

### Format
- **Primary**: PNG at 300 DPI
- **Editable**: SVG (for line art)
- **Size**: Single column (3.35") or double column (6.89")

---

## Validation Checks
- [ ] Effect sizes match computed values exactly
- [ ] CIs correctly plotted
- [ ] Null line clearly marked
- [ ] Diagnostic plots include reference lines
- [ ] Significance markers follow standard
- [ ] P-values reported exactly (not thresholded)
- [ ] Design system theme applied
- [ ] Colorblind-safe palettes
- [ ] All axes labeled with units
