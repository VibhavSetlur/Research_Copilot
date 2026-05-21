---
skill_id: "report_compiler"
version: "1.0.0"
category: "writing"
depends_on: ["paper_compiler", "results_table_generator", "captions_and_legends"]
produces: ["03_synthesis/report/report.pdf", "03_synthesis/report/report.docx", "03_synthesis/report/report.html"]
complexity: "standard"
---

# Skill: Report Compiler

## Purpose
Generates a formatted research report (not journal article) in 3 formats: PDF via WeasyPrint, DOCX via python-docx, HTML. Used when `target_output` is "report" not "journal_article".

---

## Protocol

### Step 1: Gather Content
Collect: `key_findings.json`, `global_methods.md`, all figures with `.interpret.md` files, results tables, analysis JSONs, `figure_captions.json`.

### Step 2: Structure Report
Five sections in order:

1. **Executive Summary** (1 page): headline finding, key results with effect sizes, bottom-line recommendation
2. **Key Findings** (2-3 pages): one subsection per research question, each with finding statement, effect size + CI + p-value, associated figure with caption, comparison to prior work
3. **Methods** (1-2 pages): study design, sample, measures, analysis methods (from `global_methods.md`), assumption checks
4. **Full Results** (variable length): detailed results per question, all tables (from results_table_generator), diagnostic figures, robustness checks
5. **Appendix**: supplementary tables, full model outputs, sensitivity analyses, data dictionary

### Step 3: Generate PDF (WeasyPrint)
Build HTML with embedded CSS (page breaks, headers, footers, page numbers). Render with WeasyPrint: `HTML(string=html).write_pdf(output_path)`. Use `@page` rules for margins, headers, footers. Insert page breaks before each major section.

### Step 4: Generate DOCX (python-docx)
Create document with styles: Heading 1 (sections), Heading 2 (subsections), Normal (body), Caption (figures/tables). Insert figures as images with captions. Build tables from results data. Set page margins to 1 inch.

### Step 5: Generate HTML
Single-page HTML with anchor navigation, embedded CSS, all figures inline. Responsive layout. Print-friendly via `@media print`.

### Step 6: Auto-Include Figures
For each figure in experiment outputs, insert into appropriate section with caption from `figure_captions.json`. Place in Results or Appendix based on importance (primary findings in Results, diagnostics in Appendix).

---

## Output
- `03_synthesis/report/report.pdf` — WeasyPrint PDF
- `03_synthesis/report/report.docx` — python-docx document
- `03_synthesis/report/report.html` — Single-page HTML

## Validation
- [ ] All 5 sections present and in order
- [ ] All figures included with captions
- [ ] Effect sizes with CIs in Key Findings
- [ ] Page numbers in PDF
- [ ] DOCX opens without errors
- [ ] HTML responsive on mobile
- [ ] Print layout clean
