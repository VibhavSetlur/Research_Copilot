# Skill: Journal Formatter

> Reformats assembled manuscript for a specific journal's requirements.

## Purpose
Take the assembled manuscript and adapt it to meet a specific journal's submission guidelines.

---

## Protocol

### Step 1: Load Manuscript and Target Journal
1. Read `reports/manuscript/research_findings.md`
2. Load target journal specification (from user input or domain config)
3. Load journal requirements from internal database

### Step 2: Check Word Count Compliance
1. Count words in each section:
   - Abstract
   - Main text (Introduction through Discussion)
   - References
2. Compare against journal limits:
   - **Nature family**: Abstract ≤150 words, Main text ≤3000 words
   - **Lancet family**: Abstract ≤300 words, Main text ≤3500 words
   - **PLOS family**: No strict limit, but ≤6000 recommended
   - **APA journals**: Abstract ≤250 words, varies by journal
   - **AEA journals**: Abstract ≤150 words, varies by journal
   - **Elsevier general**: Varies by journal, check specific guidelines
3. If over limit:
   - Flag sections needing compression
   - Suggest specific cuts (redundant text, verbose explanations)
   - Do NOT auto-truncate without user approval

### Step 3: Format Abstract
1. Check abstract structure requirements:
   - **Structured** (Background, Methods, Results, Conclusion): Nature, Lancet, PLOS
   - **Unstructured** (single paragraph): APA, many Elsevier journals
2. Reformat abstract to match target structure
3. Verify abstract word limit compliance

### Step 4: Convert Reference Format
1. Load bibliography from `reports/literature/bibliography.bib`
2. Convert to target citation style:
   - **Vancouver**: Numbered, author-title-journal-year-volume-pages
   - **APA**: Author-date, italicized journal and volume
   - **AMA**: Superscript numbers, specific punctuation
   - **Nature**: Superscript numbers, abbreviated journal names
   - **ACS**: Varied (superscript, numbered, or author-year)
3. Use Pandoc or CSL processor for conversion:
   ```bash
   pandoc manuscript.md -o manuscript_formatted.md \
     --citeproc \
     --csl=<journal_csl_style.csl>
   ```
4. Verify all references are present and correctly formatted

### Step 5: Format Figure Numbering and Captions
1. Check journal figure requirements:
   - Numbering style (Figure 1, Fig. 1, Figure 1.)
   - Caption placement (below figure, separate file)
   - Caption format (legend style, bold labels)
   - Resolution requirements (typically 300+ DPI)
2. Reformat all figure references and captions
3. Generate figure submission checklist

### Step 6: Organize Supplementary Materials
1. Identify content that should move to supplementary:
   - Additional analyses
   - Robustness checks
   - Extended tables
   - Additional figures
2. Create `reports/manuscript/supplementary/` directory
3. Generate supplementary material document

### Step 7: Generate Cover Letter
Create `reports/manuscript/cover_letter.md`:
1. Address to journal editor
2. Include:
   - Manuscript title
   - Brief summary of findings
   - Statement of novelty and significance
   - Confirmation of originality (not under consideration elsewhere)
   - Suggested reviewers (if requested)
   - Conflict of interest statement
3. Use journal-appropriate tone and format

### Step 8: Generate Submission Checklist
Create `reports/manuscript/submission_checklist.md`:

| Item | Status |
|------|--------|
| Word count within limits | ✓/✗ |
| Abstract formatted correctly | ✓/✗ |
| References in correct style | ✓/✗ |
| Figures meet resolution requirements | ✓/✗ |
| Figure captions formatted | ✓/✗ |
| Tables formatted | ✓/✗ |
| Supplementary materials organized | ✓/✗ |
| Cover letter drafted | ✓/✗ |
| Conflict of interest statement | ✓/✗ |
| Data availability statement | ✓/✗ |
| Ethics approval statement | ✓/✗ |
| Author contributions statement | ✓/✗ |

### Step 9: Output
Files produced:
- `reports/manuscript/manuscript_<journal>.md` — Formatted manuscript
- `reports/manuscript/cover_letter.md` — Cover letter
- `reports/manuscript/submission_checklist.md` — Submission checklist
- `reports/manuscript/supplementary/` — Supplementary materials directory
- `reports/manuscript/references_<journal>.md` — Formatted references

---

## Supported Journals

### Nature Family
- Nature, Nature Medicine, Nature Genetics, etc.
- Abstract: ≤150 words, unstructured
- Main text: ≤3000 words
- References: Numbered superscript
- Figures: Separate files, 300+ DPI

### Lancet Family
- The Lancet, Lancet Global Health, etc.
- Abstract: ≤300 words, structured
- Main text: ≤3500 words
- References: Vancouver style

### PLOS Family
- PLOS ONE, PLOS Biology, PLOS Medicine
- Abstract: ≤300 words, structured
- No strict word limit
- References: Author-year

### APA Journals
- Psychological Science, Journal of Applied Psychology, etc.
- Abstract: ≤250 words
- References: APA 7th edition
- Tables: APA format

### AEA Journals
- American Economic Review, Journal of Political Economy, etc.
- Abstract: ≤150 words
- References: Author-year
- Tables: Economics format

### Elsevier General
- Varies by journal, check specific guidelines
- Common: numbered references, structured abstracts

---

## Integration
- Called by: `compile_outputs` agent or `export --format <journal>` CLI
- Requires: Manuscript complete, bibliography available
- Outputs to: `reports/manuscript/`
