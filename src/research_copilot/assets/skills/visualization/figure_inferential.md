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
Publication-quality figures for inferential test results: effect sizes, CIs, model diagnostics, p-value functions.

---

## Effect Size Figures

### Forest Plot
Point estimates with CI error bars, null reference line (dashed), sorted by effect size or p-value. Color: significant (blue), non-significant (gray). Optional diamond for pooled estimate.

### Dot-and-Whisker Plot
Coefficients sorted by absolute magnitude. Dot = point estimate, whisker = CI. Grouped by model if multiple models. Null reference line.

### Caterpillar Plot
Ranked effect sizes (largest first) with CI bars. Color by significance. Best for many estimates (meta-analysis, multilevel).

---

## Model Diagnostic Plots

### Four-Panel Diagnostic
(1) Residuals vs Fitted — check homoscedasticity, LOWESS smooth. (2) Q-Q Plot — check normality, reference line. (3) Scale-Location — sqrt(|std residuals|) vs fitted, LOWESS smooth. (4) Residuals vs Leverage — Cook's D contours (0.5, 1.0), label high-leverage points.

### Six-Panel Regression Diagnostics Grid (Publication Standard)
Extends four-panel with two partial regression plots. Panels 1-4 same as above. Panel 5: partial regression for top predictor by |t-statistic| — shows relationship after controlling for all other variables, OLS line with 95% CI. Panel 6: same for second-top predictor. Use `statsmodels.graphics.regressionplots.plot_partreg2`. Label observations exceeding Cook's D threshold (4/n). Use for final manuscript; four-panel is sufficient for exploratory checks.

---

## Group Comparison Figures

### Mean Comparison Plot
Group means with 95% CI error bars. Optional raw data points (jittered). Sorted by mean descending. Significance brackets between groups.

### Raincloud Plot (Inferential)
Half-violin + box + raw data. Statistical test result annotation. Effect size with CI. Significance marker.

---

## P-value Visualization

### P-value Function Plot (Confidence Curve)
X-axis: effect size values. Y-axis: p-value for each hypothesized value. Horizontal line at alpha threshold. Shaded region = CI. Shows full p-value curve, not just threshold.

### Volcano Plot
X-axis: effect size. Y-axis: -log10(p-value). Color: significant vs non-significant. Label top significant results. Threshold lines for p-value and effect size.

---

## Statistical Annotation

Significance markers: ns (p>.05), * (p≤.05), ** (p≤.01), *** (p≤.001), **** (p≤.0001). Always show estimate + 95% CI. Format: `β = 0.42 [0.18, 0.66]`. Never show p-value alone. Report exact p-values.

Significance brackets: horizontal line connecting groups with *, **, ***, or ns label. Proper vertical offset.

---

## Output Standards

### File Naming
`fig_inf_001_forest_[question].png`, `fig_inf_002_diagnostics_[model].png`, `fig_inf_003_volcano_[analysis].png`

### Format
Primary: PNG at 300 DPI. Editable: SVG for line art. Size: single column (3.35") or double column (6.89").

---

## Validation
- [ ] Effect sizes match computed values exactly
- [ ] CIs correctly plotted
- [ ] Null line clearly marked
- [ ] Diagnostic plots include reference lines
- [ ] Significance markers follow standard
- [ ] P-values reported exactly
- [ ] Design system theme applied
- [ ] Colorblind-safe palettes
- [ ] All axes labeled with units
