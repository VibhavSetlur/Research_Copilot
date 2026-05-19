---
skill_id: "figure_descriptive"
version: "3.0.0"
category: "visualization"
type: "static_figure"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "pandas", "numpy"]
estimated_tokens: 3000
depends_on: ["descriptive_stats"]
produces: ["reports/figures/descriptive_figures/"]
---

# Skill: Static Descriptive Figures (Manuscript Quality)

## Purpose
Generate publication-ready, static descriptive figures for scientific manuscripts conforming to Nature/Science guidelines.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to processed dataset |
| `column_mapping` | Dict | No | Mapping of database column names to clean, publication labels |
| `layout_type` | Str | No | Figure layout: 'single_column' (89mm / 3.5 in) or 'double_column' (180mm / 7.0 in). Default: 'single_column' |

## Execution Protocol

### Step 1: Global Matplotlib Setting Synchronization
Initialize Matplotlib's `rcParams` to match top-tier journal guidelines:
- **Font**: Set `font.family` to `sans-serif` and `font.sans-serif` to `['Helvetica', 'Arial']`. Font size for labels: 6-7pt. Panel titles: 8pt bold.
- **Spines & Borders**: Spine line width: 0.5pt. Keep left and bottom spines only. Use `sns.despine(top=True, right=True)` to remove top and right spines.
- **Ticks**: `xtick.direction` and `ytick.direction` set to `in`. Tick length: 3pt, width: 0.5pt. Limit to 3-5 major ticks per axis to avoid clutter.
- **Resolution**: Force `savefig.dpi` to 600 DPI for raster fallbacks.

### Step 2: Dimension Setup
- Single-column figure: 3.5 inches width (89 mm). Set height using golden ratio (`width * 0.618`).
- Double-column figure: 7.0 inches width (180 mm). Set height to balance panel density (`width * 0.5` to `width * 0.7`).
- Always use `plt.subplots(..., constrained_layout=True)` or `GridSpec` to manage panel margins dynamically.

### Step 3: Multi-Panel Grid Construction (a, b, c)
- Group related univariate and bivariate plots into a unified composite figure.
- Add panel identifiers (lowercase bold letters **a**, **b**, **c**) at the top-left of each sub-axis. Place labels upright, 8pt bold, with a minor offset from the axis margin.
- If panels share the same axis metrics, enforce shared axes (`sharex=True` or `sharey=True`) and hide redundant tick labels.

### Step 4: Distribution Panels
- For continuous variables: Overlay a kernel density estimation (KDE) line on top of a rug plot of points. Avoid overlapping labels. Use desaturated, colorblind-friendly colors (e.g., Seaborn's `'colorblind'` or `'viridis'`).
- For categorical variables: Generate horizontal bar plots to prevent vertical label overlapping. Use `ax.bar_label` to print clean counts or percentages at the end of each bar using a small font (6pt).

### Step 5: Bivariate Relationship Panels
- Plot scatter plots with `alpha=0.4` for point transparency to represent density. If N > 10,000, set `rasterized=True` for the scatter points only (while keeping text/labels vector).
- Plot correlation heatmap of continuous features. Mask the redundant upper-triangular matrix using `np.triu`. Use a diverging colormap (`coolwarm` or `RdBu_r`). Annotate each cell with its correlation coefficient in 6pt font.

### Step 6: Vector Export
- Save final outputs in both **PDF** and **SVG** vector formats to preserve resolution independence.
- Save a **PNG** copy at 600 DPI for previewing.
- Save files using `plt.savefig(..., bbox_inches='tight', dpi=600)`.

## Output Specification
Produces inside `reports/figures/descriptive_figures/`:
- `descriptive_composite.pdf`
- `descriptive_composite.svg`
- `descriptive_composite.png`

## Validation Criteria
- [ ] Output includes both vector (PDF/SVG) and high-res raster (PNG) formats.
- [ ] Panel labels are lowercase bold letters (**a**, **b**, **c**) in the top-left margin.
- [ ] No font sizes are smaller than 5pt or larger than 10pt.
- [ ] Heatmap uses a masked upper triangle and diverging color scheme.