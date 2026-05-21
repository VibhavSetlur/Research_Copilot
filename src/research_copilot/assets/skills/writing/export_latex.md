# Skill: Export LaTeX

> Converts `research_findings.md` to publication-ready LaTeX manuscript.

## Purpose
Transform the assembled markdown manuscript into a LaTeX document formatted for academic publication.

---

## Protocol

### Step 1: Load Manuscript and Configuration
1. Read `reports/manuscript/research_findings.md`
2. Load domain config from `.research/domains/<domain>.yaml`
3. Determine target template based on domain:
   - Default: `article`
   - Physics/Astronomy: `revtex4-2`
   - Elsevier journals: `elsarticle`
   - Astronomy: `aastex`
   - PNAS: `pnas-new`

### Step 2: Select LaTeX Template
Available templates:
- `article` — Standard LaTeX article (default)
- `revtex4-2` — APS/AIP journals
- `elsarticle` — Elsevier journals
- `aastex` — AAS journals
- `pnas-new` — PNAS
- `apa7` — APA journals

Template selection priority:
1. User-specified in intake
2. Domain config default
3. Fall back to `article`

### Step 3: Convert Manuscript Structure
Using Pandoc with custom Lua filters:

```bash
pandoc reports/manuscript/research_findings.md \
  -o reports/manuscript/manuscript.tex \
  --template=<selected_template> \
  --lua-filter=.research/skills/writing/pandoc_filters/latex_filter.lua \
  --bibliography=reports/literature/bibliography.bib \
  --citeproc \
  --mathjax \
  --standalone
```

### Step 4: Handle Figures
1. Scan `reports/figures/` for all figure files
2. For each figure referenced in manuscript:
   - Insert `\includegraphics` with proper sizing
   - Add figure environment with caption
   - Use domain-appropriate numbering style
3. Generate figure placement hints:
   - Single column: `\includegraphics[width=\linewidth]{path}`
   - Double column: `\includegraphics[width=\textwidth]{path}`
   - Two-panel: use `subfigure` or `subcaption` package

### Step 5: Handle Tables
1. Convert markdown tables to LaTeX `booktabs` format:
   - Replace `|---|` with `\toprule`, `\midrule`, `\bottomrule`
   - Remove vertical lines (publication standard)
   - Add `tabular` or `table` environment
2. For complex tables, use `longtable` or `threeparttable`

### Step 6: Handle Bibliography
1. Convert citations to `\cite{}` commands
2. Generate `.bib` file from literature corpus:
   - Extract DOI, authors, title, year, journal from `literature_corpus.json`
   - Format as BibTeX entries
3. Use domain-appropriate bibliography style:
   - APA: `apalike`
   - Nature: `nature`
   - ACS: `achemso`
   - Default: `plainnat`

### Step 7: Handle Math Notation
1. Preserve all math notation from markdown
2. Convert inline `$...$` to proper LaTeX math mode
3. Convert display math `$$...$$` to `equation` or `align` environments
4. Verify all math compiles correctly

### Step 8: Add Preamble
Generate LaTeX preamble with:
- Document class and options
- Required packages (graphicx, booktabs, amssymb, hyperref, etc.)
- Domain-specific packages
- Custom commands and definitions
- Bibliography style

### Step 9: Validate Output
1. Run `pdflatex` on generated `.tex` file (if available)
2. Check for compilation errors
3. If errors occur:
   - Log error to `docs/dead_ends/latex_compilation_error.md`
   - Attempt auto-fix (escape special characters, fix encoding)
   - Re-run compilation
4. Max 3 compilation attempts

### Step 10: Output
Files produced:
- `reports/manuscript/manuscript.tex` — Main LaTeX file
- `reports/manuscript/manuscript.bib` — Bibliography file
- `reports/manuscript/manuscript.pdf` — Compiled PDF (if pdflatex available)
- `reports/manuscript/figures/` — Copied figure files for LaTeX

---

## Pandoc Lua Filter

Create `.research/skills/writing/pandoc_filters/latex_filter.lua`:

```lua
-- Custom LaTeX filters for Pandoc
function Math(elem)
  if elem.mathtype == "DisplayMath" then
    return pandoc.RawBlock('latex', '\\begin{equation}\n' .. elem.text .. '\n\\end{equation}')
  end
  return elem
end

function Table(elem)
  -- Convert to booktabs format
  -- Implementation handles header, body, footer rows
  return elem
end

function Image(elem)
  -- Wrap in figure environment
  local caption = elem.caption and pandoc.utils.stringify(elem.caption) or ''
  local label = elem.identifier or ''
  return pandoc.RawBlock('latex',
    '\\begin{figure}[htbp]\n' ..
    '\\centering\n' ..
    '\\includegraphics[width=\\linewidth]{' .. elem.src .. '}\n' ..
    '\\caption{' .. caption .. '}\n' ..
    '\\label{fig:' .. label .. '}\n' ..
    '\\end{figure}'
  )
end
```

---

## Integration
- Called by: `compile_outputs` agent or `export --format latex` CLI
- Requires: Pandoc installed, LaTeX distribution (optional for PDF)
- Outputs to: `reports/manuscript/manuscript.tex`
