---
skill_id: "research_website"
version: "1.0.0"
category: "visualization"
depends_on: ["paper_compiler", "results_table_generator", "figure_descriptive", "figure_inferential"]
produces: ["03_synthesis/website/index.html"]
complexity: "standard"
---

# Skill: Research Website Generator

## Purpose
Generate a self-contained research website as a single `index.html` with embedded CSS/JS. No server needed — shareable via file link or static hosting.

---

## Protocol

### Step 1: Gather Inputs
Collect: `research_findings.md`, `key_findings.json`, all figures + `.interpret.md` files, analysis results JSONs, `global_methods.md`, `bibliography.bib`.

### Step 2: Build HTML Structure
Single `index.html` with sections: nav (sticky), abstract, methods (collapsible), results, interactive data explorer (Plotly CDN), data download, footer. Use Plotly CDN (`plotly-2.27.0.min.js`) for interactive figures.

### Step 3: Embedded CSS
Use CSS custom properties for theming (`--color-primary: #0072B2`, etc). Responsive nav, max-width 960px content, card styling with subtle shadows, figure panels with centered images, results tables with clean borders, collapsible sections with max-height transition. Mobile: nav wraps at 768px.

### Step 4: Section Content
- **Abstract**: Title, authors, structured abstract, key findings bullets
- **Methods** (collapsible, default closed): study design, sample, measures, analysis methods, assumption checks
- **Results**: per research question — question text, primary finding with effect size + CI, figures with `.interpret.md` content, results table
- **Data Explorer**: embed Plotly figures via `data-plotly` attributes. JS reads JSON and calls `Plotly.newPlot()`. Include: distributions, correlation heatmap, forest plot. Interactive: zoom, pan, hover.
- **Data Download**: links to raw data, processed data (CSV/Parquet), analysis scripts, manuscript PDF

### Step 5: Embedded JS
Collapsible sections (toggle `open` class on click). Smooth scroll for nav links. Plotly rendering: query `[data-plotly]`, parse JSON, call `Plotly.newPlot(el, data.data, data.layout, {responsive: true})`. Remove lasso/select tools via `modeBarButtonsToRemove`.

### Step 6: Figure Embedding
Option A: base64 encode PNG inline (`data:image/png;base64,...`). Option B (for large figures): copy to `03_synthesis/website/figures/` and reference by relative path. Each figure panel: image, caption from `.interpret.md`, download link.

---

## Output
- `03_synthesis/website/index.html` — self-contained website
- `03_synthesis/website/figures/` — copied figures (if not base64)
- `03_synthesis/website/data/` — downloadable data (optional)

## Validation
- [ ] Single HTML, no external deps except Plotly CDN
- [ ] All sections render
- [ ] Collapsible methods works
- [ ] Plotly figures interactive
- [ ] Download links functional
- [ ] Responsive at 375px
- [ ] All figures have alt text
- [ ] No broken links
