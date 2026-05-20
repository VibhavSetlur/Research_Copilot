# Skill: Preprint Submission Helper

> Prepares submission packages for arXiv, bioRxiv, medRxiv, and SSRN.

## Purpose
Generate ready-to-submit packages for preprint servers. Does NOT auto-submit — requires human approval.

---

## Protocol

### Step 1: Load Manuscript and Metadata
1. Read `reports/manuscript/research_findings.md`
2. Load project metadata from `docs/manifest.json`
3. Load literature corpus for reference validation

### Step 2: Determine Target Preprint Server
Based on domain and content:
- **arXiv**: Physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering, economics
- **bioRxiv**: Biological sciences
- **medRxiv**: Health sciences, clinical research
- **SSRN**: Social sciences, law, economics, humanities

### Step 3: Prepare arXiv Submission Package

#### 3.1 Generate Metadata JSON
Create `reports/manuscript/preprint/arxiv_metadata.json`:
```json
{
  "title": "Manuscript title",
  "authors": [
    {"name": "Author Name", "affiliation": "Institution", "orcid": "0000-0000-0000-0000"}
  ],
  "abstract": "Abstract text (max 1920 characters)",
  "categories": ["stat.AP", "cs.AI"],
  "comments": "X pages, Y figures",
  "doi": "",
  "journal_ref": "",
  "report_no": "",
  "msc_class": "",
  "acm_class": ""
}
```

#### 3.2 Validate PDF
1. Check PDF exists: `reports/manuscript/manuscript.pdf`
2. Validate PDF/A compliance (arXiv requirement)
3. Check font embedding (all fonts must be embedded)
4. Verify page size (letter or A4)
5. Check file size (< 10 MB recommended)

#### 3.3 Check Category
1. Suggest appropriate arXiv categories based on content
2. Primary category must be selected
3. Secondary categories optional (max 2)
4. Available categories:
   - `stat.AP` — Applications
   - `stat.ME` — Methodology
   - `stat.ML` — Machine Learning
   - `cs.AI` — Artificial Intelligence
   - `cs.LG` — Machine Learning
   - `q-bio.QM` — Quantitative Methods
   - `q-fin.ST` — Statistical Finance
   - `econ.EM` — Econometrics

#### 3.4 Generate Submission Checklist
Create `reports/manuscript/preprint/arxiv_checklist.md`:
- [ ] PDF validates (fonts embedded, PDF/A compliant)
- [ ] Abstract ≤ 1920 characters
- [ ] Categories selected
- [ ] Authors listed with affiliations
- [ ] No confidential information
- [ ] License selected (arXiv perpetual license or CC-BY)
- [ ] Endorsement obtained (if first-time submitter)

### Step 4: Prepare bioRxiv/medRxiv Submission Package

#### 4.1 Validate Format
1. Check manuscript format requirements:
   - Word or LaTeX source accepted
   - PDF generated from source
   - Figures embedded or separate
2. Verify abstract structure (bioRxiv: unstructured, ≤250 words)
3. Check for required statements:
   - Competing interests
   - Author contributions
   - Data availability
   - Ethics approval (if applicable)

#### 4.2 Generate Submission Checklist
Create `reports/manuscript/preprint/biorxiv_checklist.md`:
- [ ] Manuscript formatted per guidelines
- [ ] Abstract ≤ 250 words
- [ ] Competing interests declared
- [ ] Author contributions listed
- [ ] Data availability statement included
- [ ] Ethics approval statement (if applicable)
- [ ] All authors agree to submission
- [ ] Corresponding author designated

#### 4.3 medRxiv Specific
Additional requirements for medRxiv:
- [ ] Clinical trial registration number (if applicable)
- [ ] Funding statement
- [ ] Patient consent statement

### Step 5: Prepare SSRN Submission Package

#### 5.1 Format Abstract
1. SSRN abstract: ≤ 300 words
2. Include keywords (5-10)
3. Generate JEL classification codes (for economics)

#### 5.2 Generate Metadata
Create `reports/manuscript/preprint/ssrn_metadata.json`:
```json
{
  "title": "Manuscript title",
  "authors": ["Author Name"],
  "abstract": "Abstract text",
  "keywords": ["keyword1", "keyword2"],
  "jel_codes": ["C10", "C18"],
  "date": "YYYY-MM-DD"
}
```

#### 5.3 Generate Submission Checklist
Create `reports/manuscript/preprint/ssrn_checklist.md`:
- [ ] Abstract ≤ 300 words
- [ ] Keywords provided (5-10)
- [ ] JEL codes assigned (if economics)
- [ ] Author affiliations current
- [ ] No confidential information

### Step 6: Package Output
Create `reports/manuscript/preprint/` directory with:
- `arxiv_metadata.json` — arXiv metadata
- `arxiv_checklist.md` — arXiv submission checklist
- `biorxiv_checklist.md` — bioRxiv/medRxiv checklist
- `ssrn_metadata.json` — SSRN metadata
- `ssrn_checklist.md` — SSRN checklist
- `manuscript.pdf` — Ready-to-submit PDF
- `source/` — LaTeX source files (if applicable)

### Step 7: Human Approval Gate
1. Present submission package to user
2. User reviews all checklists
3. User confirms readiness
4. User manually submits to chosen preprint server
5. DO NOT auto-submit under any circumstances

---

## Integration
- Called by: `compile_outputs` agent or user request
- Requires: Complete manuscript, PDF generated
- Outputs to: `reports/manuscript/preprint/`
- Does NOT: Auto-submit to any server
