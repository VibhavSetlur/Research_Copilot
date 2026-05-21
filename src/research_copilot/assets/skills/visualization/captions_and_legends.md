---
skill_id: "captions_and_legends"
version: "1.0.0"
category: "visualization"
depends_on: ["execute_analysis", "viz_design_system"]
produces: ["03_synthesis/figure_captions.json"]
complexity: "quick"
---

# Skill: Captions and Legends

## Purpose
Generate publication-quality figure captions grounded in analysis results. Used by `paper_compiler` and `research_website`.

---

## Protocol

### Step 1: Gather Data
For each figure: read `.meta.yaml` (source info), `.interpret.md` (statistical interpretation), analysis results JSON (effect sizes, CIs, p-values).

### Step 2: Generate Caption
Format: **Figure N.** _Title._ Description. Statistical annotation (test, effect size, 95% CI, N, significance). Notes on color/symbols.

Components:
- **Figure N.**: sequential number
- _Title._: concise relationship description (from `.meta.yaml` or auto-generated)
- Description: what the figure shows visually (from `.interpret.md`)
- Statistical annotation: test name, effect size, 95% CI, p-value, N
- Notes: color coding, symbols, significance markers

### Step 3: Save Captions
Output `03_synthesis/figure_captions.json` keyed by figure filename. Each entry: `figure_number`, `title`, `caption_markdown`, `caption_latex`, `caption_plain`, `statistical_annotation` (test, effect_size, ci_lower, ci_upper, p_value, n), `source_files`.

### Step 4: Format Variants
- **Markdown**: `**Figure 1.** _Title._ Description. Annotation. Notes.`
- **LaTeX**: `\textbf{Figure 1.} \textit{Title.} Description. Annotation. Notes.`
- **Plain**: `Figure 1. Title. Description. Annotation. Notes.`

### Step 5: Significance Legend
Standard: `*p < .05, **p < .01, ***p < .001`. Include in captions, table footnotes, dashboard tooltips.

---

## Validation
- [ ] Every figure has a caption
- [ ] Each caption includes effect size + CI + p-value + N
- [ ] Captions grounded in analysis results (no hallucination)
- [ ] Sequential figure numbers
- [ ] Three format variants generated
- [ ] Source files traced for every claim
