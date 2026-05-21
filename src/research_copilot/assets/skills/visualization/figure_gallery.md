---
skill_id: "figure_gallery"
version: "1.0.0"
category: "visualization"
depends_on: ["viz_design_system", "figure_descriptive", "figure_inferential"]
produces: ["03_synthesis/figure_gallery.html"]
complexity: "quick"
---

# Skill: Figure Gallery Generator

## Purpose
Static HTML gallery where each figure panel shows the image, `.interpret.md` content, statistical annotation, and download link. Clean grid with lightbox. Pure HTML/CSS/vanilla JS.

---

## Protocol

### Step 1: Scan for Figures
Find all `.png` files in `outputs/figures/` that have sibling `.interpret.md` files. Also check for `.meta.yaml` sidecars.

### Step 2: Parse Interpretation Files
Extract sections from each `.interpret.md`: Visual Description, Statistical Interpretation (test, effect size, CI, p-value, N), Key Takeaway, Caveats.

### Step 3: Generate HTML
Single `index.html` with: header (project title, date), CSS grid gallery (`grid-template-columns: repeat(auto-fill, minmax(500px, 1fr))`), lightbox overlay.

**CSS**: responsive grid, card styling with shadow, figure images at 100% width with hover opacity transition, stat annotation box with left accent border, caveats section with muted text. Lightbox: fixed overlay, 90% max image size, close on click outside or Escape key. Mobile: single column at 768px.

**JS**: lightbox open on image click (set `src` and `alt`), close on overlay click or X button or Escape key.

### Step 4: Generate Figure Cards
Each card: image (clickable for lightbox), figure number + title from `.meta.yaml`, stat annotation box (test, effect size, CI, p-value, N), key takeaway paragraph, caveats paragraph, download link to PNG.

### Step 5: Copy Figures
Copy all figures to `03_synthesis/figure_gallery_files/figures/`. Reference by relative path in HTML.

---

## Output
- `03_synthesis/figure_gallery.html` — static HTML gallery
- `03_synthesis/figure_gallery_files/figures/` — copied figures

## Validation
- [ ] All figures with `.interpret.md` included
- [ ] Lightbox opens on click, closes on Escape/X/overlay
- [ ] Download links work
- [ ] Responsive grid (single column mobile)
- [ ] Statistical annotations on every figure
- [ ] No external JS dependencies
