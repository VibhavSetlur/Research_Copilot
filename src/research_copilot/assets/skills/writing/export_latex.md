# Skill: Export LaTeX

> Converts `research_findings.md` to publication-ready LaTeX manuscript.

## Purpose
Transform the assembled markdown manuscript into a LaTeX document formatted for academic publication.

---

## Protocol

### Step 1: Select Template
Load domain config from `.research/domains/<domain>.yaml`. Priority: user-specified → domain default → `article`.

| Domain | Template |
|--------|----------|
| Default | `article` |
| Physics/Astronomy | `revtex4-2` |
| Elsevier | `elsarticle` |
| APA | `apa7` |
| PNAS | `pnas-new` |

### Step 2: Convert with Pandoc
Run pandoc with `--citeproc --bibliography=<bib_path> --standalone`. Use a Lua filter to wrap images in figure environments and convert tables to booktabs format.

### Step 3: Handle Figures
- Single column: `\includegraphics[width=\linewidth]{path}`
- Double column (width > `\columnwidth`): use `\begin{figure*}...\end{figure*}` (starred, floats to next page top)
- Multi-panel: use `subcaption` package, each subfigure gets its own `\label{}`, main caption references "(A) ... (B) ..."
- Wide tables exceeding page width: use `sidewaystable` from `rotating` package
- Supplementary items: place after `\appendix`, label as S1, S2, etc.

### Step 4: Handle Tables
Convert to booktabs: `\toprule`, `\midrule`, `\bottomrule`. No vertical lines. For number formatting, use `siunitx` with `S` column type and `{}` wrapped headers.

### Step 5: Handle Bibliography
Convert citations to `\cite{}`. Generate `.bib` from `literature_corpus.json`. Styles: APA→`apalike`, Nature→`nature`, ACS→`achemso`, default→`plainnat`.

### Step 6: Preamble
Include: `graphicx`, `subcaption`, `booktabs`, `rotating`, `threeparttable`, `siunitx`, `longtable`, `appendix`, `float`, `amssymb`, `hyperref`. Set `pdf.fonttype = 42` for font embedding.

### Step 7: Compile
Run `pdflatex` → `bibtex` → `pdflatex` → `pdflatex` (3 passes for cross-refs). Max 3 attempts. Log errors to `docs/dead_ends/`.

## Output
- `reports/manuscript/manuscript.tex`
- `reports/manuscript/manuscript.bib`
- `reports/manuscript/manuscript.pdf` (if pdflatex available)

## Validation
- [ ] All `\cite{}` resolved (no `??`)
- [ ] All `\ref{}` resolved
- [ ] No vertical lines in tables
- [ ] Figures use booktabs
- [ ] PDF compiles without errors
