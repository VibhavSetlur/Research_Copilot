# Skill: Shareable Dashboard

> Generates Quarto `.qmd` + standalone Plotly HTML dashboard with interactive figures.

## Purpose
Dual output: a Quarto source file (renderable to HTML/PDF/DOCX) and a standalone HTML dashboard using `plotly.offline` for zero-server interactivity.

---

## Protocol

### Step 1: Gather Content
Collect from experiment outputs: data table, all figures with `.interpret.md` files, results JSONs, key findings, and figure captions.

### Step 2: Generate Quarto `.qmd`
Create a `.qmd` with YAML front matter specifying `html`, `pdf`, and `docx` formats. Include sections: Summary, Data Overview (with `df.describe()` code block), Results (figures via `pio.show()`), Methods, and Data. Use `code-fold: true` for clean rendering.

### Step 3: Generate Standalone HTML
Build a single HTML file with these components:

**(a) Data table with filtering** — Paginated table (max 100 rows shown). Add text search input that filters rows via JS `textContent.toLowerCase().includes()`. Add column dropdown filter. Include Previous/Next pagination buttons.

**(b) Figure gallery** — CSS grid layout (`grid-template-columns: repeat(auto-fill, minmax(400px, 1fr))`). Each card: image, caption from `.interpret.md`, statistical annotation. Responsive: single column on mobile.

**(c) Results summary cards** — 3-card grid: Sample Size (N), Significant Findings (X of Y), Effect Size Range. Each card: large value, label, subtitle.

**(d) Download buttons** — Links for CSV data, PNG figures, LaTeX tables. Add `window.print()` button.

### Step 4: Embed Plotly Figures
Use `plotly.io.to_html(fig, include_plotlyjs='cdn', full_html=False)` for each figure. Embed in the HTML with Plotly CDN loaded in `<head>`.

### Step 5: Assemble
Combine all components into one HTML file with embedded CSS and JS. No external dependencies except Plotly CDN.

## Output
- `03_synthesis/dashboard/dashboard.qmd` — Quarto source
- `03_synthesis/dashboard/dashboard.html` — Standalone interactive HTML
- `03_synthesis/dashboard/figures/` — Copied figures
- `03_synthesis/dashboard/data/` — Downloadable data

## Render Commands
```
quarto render dashboard.qmd --to html
quarto render dashboard.qmd --to pdf
quarto render dashboard.qmd --to docx
```

## Validation
- [ ] `.qmd` renders without errors
- [ ] `.html` opens with no console errors
- [ ] Table filtering works
- [ ] Plotly figures interactive
- [ ] Download buttons functional
- [ ] Responsive on mobile
