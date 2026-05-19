---
skill_id: "figure_inferential"
version: "3.0.0"
category: "visualization"
type: "static_figure"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "pandas", "numpy"]
estimated_tokens: 3000
depends_on: ["inferential_parametric", "inferential_nonparametric"]
produces: ["reports/figures/inferential_figures/"]
---

# Skill: Static Inferential Figures (Manuscript Quality)

## Purpose
Generate static figures presenting model estimates, confidence intervals, and hypothesis test results for scientific publication.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `results_path` | Path | Yes | Path to inferential test results JSON |
| `layout_type` | Str | No | Figure layout: 'single_column' (3.5 in) or 'double_column' (7.0 in). Default: 'single_column' |

## Execution Protocol

### Step 1: Styles Setup
- Load the global styling parameters (Helvetica/Arial, ticks-in, 6-7pt labels, 0.5pt line widths).
- Use `sns.despine()` to clear top and right spines.

### Step 2: Forest Plot Construction
- For model coefficients (Odds Ratios, Hazard Ratios, Beta weights):
  - Plot coefficients on the x-axis and variable labels on the y-axis.
  - Draw a reference dashed vertical line representing the null effect (e.g., x=1 for Ratios, x=0 for differences).
  - Draw symmetric horizontal error bars representing 95% Confidence Intervals.
  - Represent point estimates with solid squares.

### Step 3: Mean Comparisons & Bracket Annotation
- For pairwise comparisons (t-tests, ANOVA):
  - Plot group means as bars or point estimates with vertical 95% confidence interval error bars.
  - Annotate significant differences using brackets (`matplotlib.lines.Line2D`).
  - Label brackets with actual p-values formatted in APA/Nature style (italicized *p*, no leading zeros: e.g., "*p* = .021"). If *p* < .001, label as "*p* < .001".

### Step 4: Fit Diagnostics Panels
- Generate a 2x2 grid containing model diagnostics:
  - Residuals vs. Fitted plot.
  - Normal Q-Q plot.
  - Scale-Location plot.
  - Residuals vs. Leverage.

### Step 5: Exporting
- Save to vector formats **PDF** and **SVG** in `reports/figures/inferential_figures/`.
- Save a backup **PNG** at 600 DPI.
- Set `bbox_inches='tight'` and `dpi=600` inside `plt.savefig()`.

## Output Specification
Produces inside `reports/figures/inferential_figures/`:
- `model_coefficients.pdf`
- `group_comparisons.pdf`
- `model_diagnostics.pdf`
- Corresponding PNG formats.

## Validation Criteria
- [ ] Forest plot null line is present at the mathematically correct value.
- [ ] P-value text formatting uses italicized *p* and contains no leading zero before decimals (e.g., '.01' not '0.01').
- [ ] No text overlaps with grid lines or error bars.