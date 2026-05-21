# Citation Verification — Three-Pass Anti-Hallucination Pipeline

## Purpose
Every citation must be triple-verified before appearing in any output. This skill is invoked by the `audit_validate` agent and the `citation_verifier.py` script.

## Protocol

### Pass 1 — Existence Check

For every citation in the bibliography or manuscript:

1. **DOI citations:** Call CrossRef API (`api.crossref.org/works/{doi}`)
   - Confirm title, authors, year match the claimed citation
   - Flag: 404 response or metadata mismatch

2. **arXiv IDs:** Call arXiv API (`export.arxiv.org/api/query?id_list={id}`)
   - Confirm title, authors, year match
   - Flag: not found or metadata mismatch

3. **PubMed IDs:** Call NCBI E-utilities (`eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=text&rettype=abstract`)
   - Confirm title, authors, year match
   - Flag: not found or metadata mismatch

4. **ISBN/Book citations:** Flag for manual review (no automated existence check)

**Output per citation:**
```json
{
  "citation": "Author et al., Year",
  "identifier": "10.xxxx/yyyy",
  "identifier_type": "doi",
  "pass_1": {
    "status": "verified|mismatch|not_found|skipped",
    "title": "Actual title from API",
    "authors": ["Author1", "Author2"],
    "year": 2024,
    "claimed_title": "Title as cited in manuscript",
    "claimed_year": 2024,
    "title_match": true,
    "year_match": true,
    "error": null
  }
}
```

### Pass 2 — Content Verification

For each citation used to support a specific claim:

1. Fetch abstract from Semantic Scholar API (`api.semanticscholar.org/graph/v1/paper/{identifier}`)
2. Evaluate: "Does this abstract support the claim '[claim text]'?"
3. Response: YES / NO / PARTIAL with 1-sentence justification
4. Flag PARTIAL or NO for human review
5. Never use a citation that fails Pass 2 without explicit `[UNVERIFIED]` tag

**Output per citation:**
```json
{
  "citation": "Author et al., Year",
  "claim": "The specific claim this citation supports",
  "pass_2": {
    "status": "supported|unsupported|partial|no_abstract",
    "justification": "The abstract reports X which supports/contradicts the claim because...",
    "abstract_snippet": "First 200 chars of abstract"
  }
}
```

### Pass 3 — Retraction Check

1. Query Retraction Watch database for the paper
2. Query CrossRef for retraction notices linked to DOI
3. **Hard block:** retracted papers cannot appear as supporting evidence
4. **Warn:** papers with expressions of concern

**Output per citation:**
```json
{
  "citation": "Author et al., Year",
  "pass_3": {
    "status": "clear|retracted|expression_of_concern|unknown",
    "retraction_date": null,
    "retraction_reason": null,
    "source": "crossref|retraction_watch|none"
  }
}
```

## Final Verification Report

Output: `reports/literature/citation_verification_report.json`

```json
{
  "schema_version": "1.0.0",
  "generated_at": "ISO 8601 timestamp",
  "total_citations": 42,
  "summary": {
    "fully_verified": 38,
    "unverified": 2,
    "retracted": 0,
    "partial_match": 2,
    "not_found": 0
  },
  "verdict": "PASS|FAIL",
  "citations": [
    {
      "citation": "...",
      "identifier": "...",
      "pass_1": {...},
      "pass_2": {...},
      "pass_3": {...},
      "overall_status": "verified|unverified|retracted|partial"
    }
  ]
}
```

**Verdict Rules:**
- PASS: all citations verified (pass 1 + pass 2 + pass 3 clear)
- FAIL: any citation is retracted, or >10% are unverified
- CONDITIONAL: some citations are partial_match or not_found but <10%

## Integration

- `audit_validate` agent runs this as Audit #6
- Any UNVERIFIED citation = gate FAIL
- Retracted paper = immediate FAIL, remove from manuscript
- Run via: `python .research/scripts/utils/citation_verifier.py --bibliography reports/literature/bibliography.bib`
