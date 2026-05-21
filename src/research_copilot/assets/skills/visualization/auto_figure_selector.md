---
skill_id: "auto_figure_selector"
version: "1.0.0"
category: "visualization"
depends_on: ["viz_design_system", "profile_tabular"]
produces: ["02_experiments/<exp>/outputs/figures/auto_selected_figure.png"]
complexity: "quick"
---

# Skill: Auto Figure Selector

## Purpose
Takes variable types, N, and question type → returns optimal figure type with rationale.

---

## Protocol

### Step 1: Input Analysis
Gather from data profile: variable types (continuous, categorical, binary, ordinal, time), sample size N, research question type, number of variables.

### Step 2: Decision Table

| X | Y | N | Question | Figure |
|---|---|---|----------|--------|
| continuous | continuous | any | association | Scatter + regression + CI band |
| continuous | continuous | >5000 | association | Hexbin / 2D density |
| categorical (2 levels) | continuous | any | comparison | Raincloud plot |
| categorical (2 levels) | continuous | <200 | comparison | Strip + boxplot overlay |
| categorical (3+ levels) | continuous | >200 | comparison | Violin plot |
| categorical (3+ levels) | continuous | <200 | comparison | Strip + boxplot overlay |
| time | continuous | any | trend | Line + confidence ribbon |
| categorical | categorical | any | association | Mosaic plot / grouped bar |
| multiple (regression) | continuous | any | prediction | Coefficient forest plot |
| continuous (5+ vars) | continuous (5+ vars) | any | correlation | Clustered heatmap |
| continuous | binary | any | classification | ROC curve |
| time | event | any | survival | Kaplan-Meier curve |
| any | any | <30 | exploratory | Raw data + summary |

### Step 3: Generate Figure
Write the appropriate plotting function using design system theme. Use `get_figsize()` for dimensions. Apply Okabe-Ito palette. Label axes with variable names.

### Step 4: Output
Return: figure type, rationale, figure size preset, estimated runtime. Save figure to experiment outputs. Generate `.interpret.md` alongside.

---

## Validation
- [ ] Figure type matches decision table
- [ ] Design system theme applied
- [ ] Colorblind-safe palette
- [ ] Axes labeled
- [ ] `.interpret.md` generated
