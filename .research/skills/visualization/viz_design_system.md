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
Define a unified visual language for ALL figures and dashboards. Every plot, chart, and dashboard component MUST use this system. No ad-hoc styling. No inconsistent colors. No non-accessible palettes.

---

## Design Principles

1. **Accessibility first**: Colorblind-safe, sufficient contrast, readable at small sizes
2. **Scientific integrity**: No chart junk, no misleading axes, no decorative elements
3. **Consistency**: Same fonts, colors, spacing across ALL outputs
4. **Reproducibility**: Theme is code, not manual adjustments
5. **Publication-ready**: Meets journal requirements out of the box
6. **Minimalist clarity**: Strip all non-data ink; let the data speak

---

## Minimalist Design Manifesto

### The Data-Ink Ratio (Tufte, 1983)
Every pixel on a figure must serve the data. If removing an element doesn't change the message, remove it.

### Rules of Minimalist Figures
1. **No redundant grid lines**: Use only horizontal grid lines at meaningful intervals. Remove vertical grid lines entirely unless they encode specific values.
2. **Intentional whitespace**: Whitespace is not empty — it is breathing room. Use generous margins to separate panels. Never crowd subplots.
3. **Muted, accessible palettes**: Never use saturated default colors. Use Okabe-Ito for categorical, viridis for sequential. Saturation should be 70-85% of maximum.
4. **No decorative borders**: Remove top and right spines. Keep bottom and left spines thin (0.8pt).
5. **Sparse tick marks**: 5-8 ticks per axis. Never more. Round to meaningful values.
6. **Direct labeling over legends**: When possible, label data directly on the figure instead of using a separate legend box.
7. **No 3D, no shadows, no gradients on bars**: These distort perception and add zero information.
8. **Single focal point per figure**: Each figure should communicate ONE primary insight. Secondary insights go in subpanels.

### Implementation: Minimalist Theme
```python
def apply_minimalist_theme():
    """Apply minimalist design principles to matplotlib."""
    plt.rcParams.update({
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.alpha": 0.15,       # Subtle, not distracting
        "grid.color": "#E5E5E5",
        "xtick.bottom": True,
        "xtick.top": False,       # No top ticks
        "ytick.left": True,
        "ytick.right": False,     # No right ticks
        "figure.facecolor": "white",
        "axes.facecolor": "#FAFAFA",
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.1,  # Minimal padding
    })
```

### Anti-Patterns (NEVER do these)
- Default matplotlib blue/orange/green/red palette
- Dense grid lines on both axes
- Thick spines (≥1.5pt)
- Legends that obscure data
- Titles that repeat axis labels
- Pie charts (use stacked bars or dot plots)
- 3D anything
- Rainbow/jet colormaps
- Chartjunk: drop shadows, beveled edges, decorative backgrounds

---

## Color System

### Primary Palette (Colorblind-Safe)
Use Okabe-Ito palette as the default. This is the ONLY palette for categorical data.

```python
OKABE_ITO = {
    "blue":      "#0072B2",
    "orange":    "#E69F00",
    "green":     "#009E73",
    "yellow":    "#F0E442",
    "sky_blue":  "#56B4E9",
    "vermillion": "#D55E00",
    "red":       "#CC79A7",
    "black":     "#000000",
}
```

### Sequential Palettes
For continuous/ordinal data:
- **Default**: `viridis` (perceptually uniform, colorblind-safe)
- **Diverging**: `RdBu_r` or `coolwarm` (centered at zero)
- **Single hue**: `Blues`, `Greens` (for single-variable intensity)

### Semantic Colors
- **Positive effect**: `#009E73` (green)
- **Negative effect**: `#D55E00` (vermillion)
- **Null/reference**: `#999999` (gray)
- **Uncertainty**: `#CCCCCC` (light gray)
- **Significant**: `#0072B2` (blue)
- **Non-significant**: `#999999` (gray)
- **Warning/caution**: `#E69F00` (orange)
- **Error/fail**: `#D55E00` (vermillion)

### Background Colors
- **Figure background**: `#FFFFFF` (white)
- **Plot background**: `#FAFAFA` (near-white)
- **Grid lines**: `#E5E5E5` (light gray, subtle)
- **Dashboard background**: `#F8F9FA` (Bootstrap light gray)
- **Card background**: `#FFFFFF` (white)

### NEVER Use
- Rainbow/jet colormaps (misleading, not perceptually uniform)
- Default matplotlib colors (not colorblind-safe)
- Pure red/green combinations (colorblind indistinguishable)
- More than 8 categorical colors (use grouping instead)

---

## Typography System

### Font Stack
```python
FONT_FAMILY = "sans-serif"
FONT_SANS = ["Inter", "Source Sans 3", "Helvetica Neue", "Arial", "sans-serif"]
FONT_MONO = ["JetBrains Mono", "Fira Code", "Consolas", "monospace"]
```

### Font Sizes (Publication Standard)
| Element | Size (pt) | Weight |
|---------|-----------|--------|
| Figure title | 14 | bold |
| Axis labels | 11 | normal |
| Tick labels | 10 | normal |
| Legend title | 11 | bold |
| Legend items | 10 | normal |
| Annotations | 9 | normal |
| Caption | 10 | italic |
| Dashboard title | 24 | bold |
| Dashboard subtitle | 16 | normal |
| Card metric | 32 | bold |
| Card label | 14 | normal |
| Table header | 11 | bold |
| Table body | 10 | normal |

### Text Rules
- NEVER use Comic Sans, Papyrus, or decorative fonts
- NEVER use font size below 8pt (unreadable in print)
- Always use sentence case for titles (not ALL CAPS)
- Always use proper statistical notation (italic *p*, italic *N*, Greek β)

---

## Spacing & Layout System

### Figure Margins
```python
FIGURE_MARGINS = {
    "left": 0.12,    # Space for y-axis labels
    "right": 0.05,   # Minimal right margin
    "bottom": 0.12,  # Space for x-axis labels
    "top": 0.08,     # Space for title
    "wspace": 0.25,  # Between subplots (horizontal)
    "hspace": 0.30,  # Between subplots (vertical)
}
```

### Dashboard Spacing
```python
DASHBOARD_SPACING = {
    "page_padding": "24px",
    "card_padding": "16px",
    "card_margin": "12px",
    "element_gap": "8px",
    "section_gap": "24px",
}
```

### Grid System
- **Dashboards**: 12-column responsive grid (Bootstrap)
- **Figures**: Golden ratio (1.618) for aspect ratio when possible
- **Multi-panel**: Align axes, share scales where comparable

---

## Figure Sizing Standards

### Journal Formats
| Format | Width | Height | Use |
|--------|-------|--------|-----|
| Single column | 8.5 cm (3.35") | varies | Most journals |
| 1.5 column | 12 cm (4.72") | varies | Some journals |
| Double column | 17.5 cm (6.89") | varies | Full-page figures |
| Square | 8.5 cm × 8.5 cm | 8.5 cm × 8.5 cm | Heatmaps, scatter matrices |

### DPI Requirements
- **Print**: 300 DPI minimum
- **Web**: 150 DPI minimum
- **Vector**: SVG/PDF (preferred for line art)

---

## Axis & Scale Rules

### Axis Standards
- Always label axes with variable name AND units
- Never truncate y-axis for bar charts (must start at zero)
- Y-axis CAN start non-zero for line charts (if clearly indicated)
- Use scientific notation for very large/small numbers
- Log scale MUST be labeled as such
- Always show grid lines for quantitative axes (subtle)

### Tick Rules
- 5-8 ticks per axis (not too many, not too few)
- Round tick values to meaningful numbers
- Rotate x-axis labels if > 10 characters
- Use comma separators for numbers > 999

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
- Always show effect size with confidence interval
- Format: `β = 0.42 [0.18, 0.66]` or `OR = 2.1 [1.4, 3.2]`
- Never show p-value alone without effect size
- Report exact p-values (not just "p < 0.05") unless p < 0.001

### Confidence Intervals
- Default: 95% CI
- Show as error bars, ribbons, or forest plot bars
- Label the confidence level
- Never use standard error bars without labeling them as such

---

## Chart Type Selection Guide

| Data Type | Best Chart | Avoid |
|-----------|-----------|-------|
| Distribution | Histogram, violin, raincloud | Pie chart |
| Comparison | Bar (sorted), dot plot | 3D bar |
| Correlation | Scatter + regression line | Bubble with >3 dimensions |
| Time series | Line plot with ribbon | Area chart with overlap |
| Proportions | Stacked bar, mosaic | Pie chart |
| Model results | Forest plot, dot-and-whisker | Table without visualization |
| Missing data | Missingness matrix, bar | Heatmap without sorting |
| Causal | DAG with annotations | Network without direction |

---

## Accessibility Requirements

### Colorblind Safety
- All figures MUST be interpretable without color
- Use patterns, shapes, or labels in addition to color
- Test with colorblind simulator (Coblis, Color Oracle)

### Contrast
- Text on background: minimum 4.5:1 contrast ratio (WCAG AA)
- Data elements on background: minimum 3:1
- Never use light text on light background

### Screen Reader
- All dashboard figures MUST have alt text
- Tables MUST have proper headers
- Interactive elements MUST have ARIA labels

---

## Implementation: Theme Module

Create `scripts/utils/viz_theme.py` with:

```python
"""Visualization theme — apply to ALL figures and dashboards."""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# Color palettes
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#F0E442",
             "#56B4E9", "#D55E00", "#CC79A7", "#000000"]
SEMANTIC = {
    "positive": "#009E73", "negative": "#D55E00",
    "null": "#999999", "significant": "#0072B2",
    "warning": "#E69F00", "error": "#D55E00",
}

def apply_matplotlib_theme():
    """Apply publication theme to matplotlib/seaborn."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Source Sans 3", "Helvetica Neue", "Arial"],
        "font.size": 10,
        "axes.titlesize": 14,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 14,
        "figure.facecolor": "white",
        "axes.facecolor": "#FAFAFA",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.color": "#E5E5E5",
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.transparent": False,
    })
    sns.set_theme(
        context="paper", style="whitegrid",
        palette=OKABE_ITO, font="sans-serif",
        rc={"axes.grid": True, "grid.alpha": 0.3}
    )

def apply_plotly_theme():
    """Return Plotly template dict for dashboards."""
    return {
        "layout": {
            "font": {"family": "Inter, sans-serif", "size": 12, "color": "#333333"},
            "title": {"font": {"size": 16, "color": "#111111"}},
            "plot_bgcolor": "#FAFAFA",
            "paper_bgcolor": "#FFFFFF",
            "colorway": OKABE_ITO,
            "margin": {"l": 60, "r": 20, "t": 50, "b": 60},
            "xaxis": {
                "gridcolor": "#E5E5E5", "gridwidth": 0.5,
                "zerolinecolor": "#999999", "zerolinewidth": 1,
            },
            "yaxis": {
                "gridcolor": "#E5E5E5", "gridwidth": 0.5,
                "zerolinecolor": "#999999", "zerolinewidth": 1,
            },
            "legend": {"bgcolor": "rgba(0,0,0,0)", "bordercolor": "rgba(0,0,0,0)"},
            "hoverlabel": {"font": {"family": "JetBrains Mono, monospace", "size": 11}},
        }
    }
```

---

## Validation Checklist

Every figure and dashboard MUST pass:
- [ ] Uses Okabe-Ito or approved sequential/diverging palette
- [ ] Colorblind-safe (test with simulator)
- [ ] All axes labeled with units
- [ ] Font sizes meet minimum (8pt print, 10pt web)
- [ ] No chart junk (no 3D, no shadows, no decorative elements)
- [ ] Statistical annotations follow standard (*, **, ***)
- [ ] Effect sizes with CIs shown (not just p-values)
- [ ] Alt text provided for accessibility
- [ ] Figure size matches journal format
- [ ] DPI meets publication standard (300 for print)
- [ ] Theme module applied (not manual styling)
- [ ] Top and right spines removed
- [ ] Grid lines are subtle (alpha ≤ 0.2)
- [ ] No redundant vertical grid lines
- [ ] Direct labeling used instead of legend when possible
- [ ] Single focal point per figure
- [ ] Accompanying .interpret.md file generated in docs/decisions/
