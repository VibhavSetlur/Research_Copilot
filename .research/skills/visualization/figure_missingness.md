---
skill_id: "figure_missingness"
version: "3.0.0"
category: "visualization"
type: "static_figure"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "pandas"]
estimated_tokens: 2000
depends_on: ["detect_missingness"]
produces: ["reports/figures/missingness_figures/"]
---

# Skill: Static Missingness Figures (Manuscript Quality)

## Purpose
Generate static figures mapping missing data density and patterns for publication.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_path` | Path | Yes | Path to processed dataset |

## Execution Protocol

### Step 1: Matplotlib Configuration
- Load standard formatting (Helvetica/Arial, ticks-in, 6-7pt text labels, 0.5pt spines).
- Define binary colormap: White (1) for present values, Dark Indigo/Slate (`#2b2b2b`) (0) for missing values.

### Step 2: Density Map
- Draw binary missingness matrix.
- Sort columns by missingness rate (descending) to group gaps.
- Remove row index labels. Add y-axis label showing observation scale (e.g., "Observations (N=1500)").
- Add x-axis labels rotated at 45 degrees.

### Step 3: Nullity Correlation
- Calculate correlation matrix of missingness indicators.
- Plot heatmap using diverging color scheme (`RdBu_r` or `coolwarm`).
- Mask upper triangle to avoid redundancy.

### Step 4: Export
- Save to `reports/figures/missingness_figures/` as vector **PDF**, **SVG**, and 600 DPI **PNG**.
- Use `bbox_inches='tight'` and `dpi=600` on save.

## Output Specification
Produces inside `reports/figures/missingness_figures/`:
- `missingness_density.pdf`
- `missingness_correlation.pdf`
- Corresponding PNG formats.

## Validation Criteria
- [ ] Heatmap colormap is binary and clearly labeled.
- [ ] Row numbers are hidden.
- [ ] Labels do not overlap.