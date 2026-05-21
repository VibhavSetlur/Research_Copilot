---
skill_id: "viz_design_system"
version: "2.0.0"
category: "visualization"
domain_compatibility: ["all"]
required_tools: ["python", "matplotlib", "seaborn", "plotly"]
depends_on: []
produces: ["scripts/utils/viz_theme.py"]
complexity: "intermediate"
---

# Skill: Visualization Design System

## Purpose
Unified visual language for ALL figures and dashboards. No ad-hoc styling. No inconsistent colors. No non-accessible palettes.

## Principles
Accessibility first, scientific integrity, consistency, reproducibility (theme is code), publication-ready, minimalist clarity.

---

## Minimalist Design
- Data-ink ratio: every pixel must serve the data
- Remove top/right spines, keep bottom/left thin (0.8pt)
- Subtle grid lines only (alpha ≤ 0.15), horizontal only
- 5-8 ticks per axis, round to meaningful values
- Direct labeling over legends
- No 3D, shadows, gradients on bars, pie charts, rainbow/jet colormaps
- Single focal point per figure

---

## Color System

### Okabe-Ito (categorical ONLY)
`#0072B2` blue, `#E69F00` orange, `#009E73` green, `#F0E442` yellow, `#56B4E9` sky_blue, `#D55E00` vermillion, `#CC79A7` red, `#000000` black

### Sequential
Default: `viridis`. Diverging: `RdBu_r` or `coolwarm`. Single hue: `Blues`, `Greens`.

### Semantic
Positive=`#009E73`, Negative=`#D55E00`, Null=`#999999`, Significant=`#0072B2`, Non-sig=`#999999`, Warning=`#E69F00`, Error=`#D55E00`

### NEVER Use
Rainbow/jet, default matplotlib colors, pure red/green combos, >8 categorical colors.

---

## Typography
Font stack: Inter → Source Sans 3 → Helvetica Neue → Arial. Sizes: title 14pt bold, axis labels 11pt, ticks 10pt, annotations 9pt, caption 10pt italic. Never below 8pt. Sentence case for titles. Proper statistical notation (italic *p*, *N*, Greek β).

---

## Spacing & Layout
Figure margins: left 0.12, right 0.05, bottom 0.12, top 0.08, wspace 0.25, hspace 0.30. Golden ratio (1.618) for aspect ratio. Dashboards: 12-column Bootstrap grid.

---

## Figure Size Presets

| Preset | Width | Height | Use |
|--------|-------|--------|-----|
| `single_column` | 3.35" | 2.07" | Most journal figures |
| `double_column` | 6.89" | 4.26" | Full-page figures |
| `square` | 3.35" | 3.35" | Heatmaps, scatter matrices |
| `wide` | 6.89" | 3.5" | Time series, horizontal layouts |
| `poster` | 12" | 8" | Conference posters |

Use `get_figsize(preset)` to retrieve. Raises ValueError on unknown preset.

## Font Embedding
Always set `plt.rcParams['pdf.fonttype'] = 42` and `plt.rcParams['ps.fonttype'] = 42` before saving. Journals reject Type 3 fonts. For SVG, set `svg.fonttype = "none"` to convert text to paths. Verify with `pdffonts` — all fonts must show "embedded: yes".

---

## Axis & Scale Rules
- Label axes with variable name AND units
- Bar charts: y-axis must start at zero
- Line charts: y-axis can start non-zero (clearly indicated)
- Log scale MUST be labeled
- Comma separators for numbers > 999
- Rotate x-axis labels if > 10 characters

---

## Statistical Annotations
Significance: ns (p>.05), * (p≤.05), ** (p≤.01), *** (p≤.001), **** (p≤.0001). Always show effect size with CI. Format: `β = 0.42 [0.18, 0.66]`. Never show p-value alone. Default 95% CI. Label confidence level. Never use SE bars without labeling.

---

## Chart Selection
Distribution→histogram/violin/raincloud (not pie). Comparison→sorted bar/dot plot (not 3D bar). Correlation→scatter+regression line. Time series→line+ribbon. Proportions→stacked bar/mosaic. Model results→forest plot/dot-and-whisker. Missing data→missingness matrix. Causal→DAG with annotations.

---

## Accessibility
Colorblind-safe (test with Coblis/Color Oracle). Color is never the only differentiator — use patterns, shapes, labels. Text contrast ≥4.5:1 (WCAG AA). All figures have alt text. Tables have proper headers. Interactive elements have ARIA labels.

---

## Theme Module
Create `scripts/utils/viz_theme.py` with: `OKABE_ITO` palette list, `SEMANTIC` color dict, `apply_matplotlib_theme()` (sets rcParams for fonts, colors, grid, spines, DPI=300, fonttype=42), `apply_plotly_theme()` (returns layout dict with font, colors, margins, grid). Apply theme module to every figure — no manual styling.

---

## Validation Checklist
- [ ] Okabe-Ito or approved sequential/diverging palette
- [ ] Colorblind-safe
- [ ] Axes labeled with units
- [ ] Font sizes ≥8pt print, ≥10pt web
- [ ] No chart junk
- [ ] Statistical annotations follow standard
- [ ] Effect sizes with CIs
- [ ] Alt text provided
- [ ] Figure size matches journal format
- [ ] DPI ≥300, fonts embedded (pdf.fonttype=42)
- [ ] Theme module applied
- [ ] Top/right spines removed
- [ ] Grid lines subtle (alpha ≤ 0.2)
- [ ] .interpret.md file generated
