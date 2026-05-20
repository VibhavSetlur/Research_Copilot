# Skill: Audit Citations

> Audit #6: Three-pass citation verification as part of `audit_validate` pipeline.

## Purpose
Verify every citation in the manuscript through three passes: existence, content, and retraction. All three passes must pass for a PASS verdict.

---

## Protocol

### Step 1: Extract Citations from Manuscript
1. Read `reports/manuscript/research_findings.md`
2. Extract all DOIs, arXiv IDs, and PubMed IDs using regex
3. Cross-reference with `reports/literature/bibliography.bib`
4. Build citation list: `{doi, arxiv_id, pubmed_id, claim_text, location_in_manuscript}`

### Step 2: Pass 1 — Existence Check
For every citation:

#### DOI Verification
1. Call CrossRef API: `https://api.crossref.org/works/{doi}`
2. Verify: title, authors, year match claimed citation
3. Flag: any DOI returning 404 or metadata mismatch

#### arXiv Verification
1. Call arXiv API: `http://export.arxiv.org/api/query?id_list={arxiv_id}`
2. Verify: title, authors, year match claimed citation
3. Flag: any arXiv ID not found

#### PubMed Verification
1. Call NCBI E-utilities: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pubmed_id}`
2. Verify: title, authors, year match claimed citation
3. Flag: any PubMed ID not found

**Output:** `reports/literature/citation_verification_report.json` with `existence_check` status per citation

### Step 3: Pass 2 — Content Verification
For each citation used to support a claim:

1. Fetch abstract from Semantic Scholar API
2. Run validation: "Does this abstract support the claim '[claim text]'?"
3. Response options: YES / NO / PARTIAL with 1-sentence justification
4. Flag PARTIAL or NO responses for human review
5. Never use a citation that fails Pass 2 without explicit `[UNVERIFIED]` tag

**Output:** Update `citation_verification_report.json` with `content_check` status

### Step 4: Pass 3 — Retraction Check
For every cited paper:

1. Query Retraction Watch database API
2. Query CrossRef for retraction notices linked to DOI
3. **Hard block:** Retracted papers cannot appear as supporting evidence
4. **Warn:** Papers with expressions of concern

**Output:** Update `citation_verification_report.json` with `retraction_check` status

### Step 5: Generate Verification Report
Create `reports/literature/citation_verification_report.json`:

```json
{
  "schema_version": "1.0.0",
  "timestamp": "ISO 8601",
  "total_citations": 45,
  "summary": {
    "all_pass": 38,
    "existence_fail": 2,
    "content_fail": 3,
    "content_partial": 2,
    "retracted": 0,
    "expression_of_concern": 1
  },
  "citations": [
    {
      "doi": "10.xxxx/yyyy",
      "title": "Paper title",
      "existence_check": {"status": "PASS", "verified_title": "...", "verified_year": 2024},
      "content_check": {"status": "PASS", "supports_claim": true, "justification": "..."},
      "retraction_check": {"status": "PASS", "retracted": false},
      "overall_status": "VERIFIED",
      "location_in_manuscript": "Section 3.2, paragraph 2"
    }
  ],
  "failures": [
    {
      "doi": "10.xxxx/zzzz",
      "failure_type": "existence_fail",
      "reason": "DOI returns 404",
      "remediation": "Search CrossRef by title+author, find correct DOI"
    }
  ]
}
```

### Step 6: Verdict
- **PASS:** All citations verified (existence + content + retraction)
- **CONDITIONAL:** Some citations partial_match or expression_of_concern
- **FAIL:** Any citation retracted, or >10% unverified

### Step 7: Auto-Healing
If FAIL or CONDITIONAL:
1. For existence failures: Search CrossRef by title+author, find correct DOI
2. For content mismatches: Remove citation from claim, flag for manual replacement
3. For retractions: Remove citation from manuscript entirely, find replacement
4. Re-run verification after fixes

---

## Integration
- Called by: `audit_validate` agent as Audit #6
- Uses: `citation_verifier.py` script
- Outputs to: `reports/literature/citation_verification_report.json`
- Blocks manuscript if: FAIL verdict
