---
skill_id: "paper_compiler"
version: "1.0.0"
category: "writing"
depends_on: ["export_latex", "write_imrad", "generate_apa_tables"]
produces: ["03_synthesis/manuscript/paper.pdf"]
complexity: "standard"
---

# Skill: Paper Compiler

## Purpose
Takes assembled manuscript, figure metadata, and bibliography, then compiles a submission-ready PDF.

---

## Protocol

### Step 1: Validate Figures
Check all expected figures exist at 300 DPI. Use PIL to open PNG/JPG and check `dpi` info (must be ≥300). PDF figures are vector — skip DPI check. Missing figures = halt compilation. Low DPI = warning but proceed.

### Step 2: Assemble Manuscript
Collect from `03_synthesis/manuscript/`: `research_findings.md` (main body), each figure's `.meta.yaml` (captions), `bibliography.bib`, `global_methods.md`.

### Step 3: Convert to LaTeX
Run pandoc: `--standalone --citeproc --bibliography=<bib> --cite-method=biblatex --lua-filter=latex_filter.lua`. The Lua filter wraps images in figure environments and converts tables to booktabs.

### Step 4: Insert Figure Environments
For each figure, insert `\begin{figure}[htbp]` with `\includegraphics`, caption from `.meta.yaml` or `.interpret.md`, and `\label{}`. Caption priority: `.interpret.md` > `.meta.yaml` > auto-generated.

### Step 5: Compile PDF
Run: `pdflatex` → `bibtex` → `pdflatex` → `pdflatex` (3 passes for cross-references). Use `-interaction=nonstopmode`.

### Step 6: Validate
Check PDF exists and is non-empty. Verify no `??` unresolved references. Check `.log` for overfull/underfull hbox warnings.

---

## Output
- `03_synthesis/manuscript/paper.pdf`
- `03_synthesis/manuscript/manuscript.tex`
- `03_synthesis/manuscript/compilation_report.json`

## Validation
- [ ] All figures at 300 DPI or vector PDF
- [ ] Bibliography resolves all citations
- [ ] No `??` in output
- [ ] PDF compiles without errors (max 3 attempts)
- [ ] Figure captions include statistical annotations
- [ ] Tables use booktabs (no vertical lines)

## Error Handling
Missing figure → halt and report. Low DPI → compile with warning. BibTeX error → fix common issues (missing braces). pdflatex not found → output `.tex` only. Unresolved refs → run third pass, report remaining.
