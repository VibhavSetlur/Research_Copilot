---
agent_id: "literature_pipeline"
version: "1.0.0"
description: "Automated literature search across multiple sources, deduplication, and PRISMA flow"
domain_compatibility: ["all"]
depends_on: ["research_init"]
composes:
  - "search_arxiv"
  - "search_pubmed"
  - "search_semantic_scholar"
  - "synthesize_literature"
  - "generate_bibtex"
  - "extract_claims"
produces:
  - "reports/literature/literature_corpus.json"
  - "reports/literature/evidence_matrix.md"
  - "reports/literature/gap_analysis.md"
  - "reports/literature/prisma_flow.md"
  - "reports/literature/bibliography.bib"
  - "reports/figures/prisma_diagram.png"
max_iterations: 3
---

# Agent: Literature Pipeline

## Purpose
Automate the entire literature search process: search multiple sources, deduplicate results, screen for relevance, extract claims, build evidence matrix, generate bibliography, and create PRISMA flow diagram. One agent replaces hours of manual searching.

---

## Protocol

### Step 1: Build Search Strategy
From the research map, extract:
- **Keywords**: from research questions, variables, and domain
- **Date range**: from intake constraints or default (last 10 years)
- **Inclusion criteria**: study types, populations, outcomes
- **Exclusion criteria**: non-peer-reviewed, wrong language, etc.

### Step 2: Search All Sources
Run searches in parallel across available sources:

| Source | Skill | Search Strategy |
|--------|-------|----------------|
| Semantic Scholar | `search_semantic_scholar` | Keywords + field filters |
| arXiv | `search_arxiv` | Keywords + category filters |
| PubMed | `search_pubmed` | MeSH terms + keywords (if biomedical) |
| CrossRef | `generate_bibtex` | DOI-based search for known papers |
| User-provided | — | Papers in `inputs/papers/` |

### Step 3: Deduplicate
Merge results from all sources and remove duplicates:
1. **DOI match**: Same DOI = same paper
2. **Title similarity**: Levenshtein distance < 0.1 on normalized titles
3. **Author + year + title**: Fuzzy match on all three fields
4. Keep the most complete record (most metadata fields filled)

### Step 4: Screen for Relevance
Apply inclusion/exclusion criteria:
1. **Title screening**: Does title contain keywords or related terms?
2. **Abstract screening**: Does abstract mention key variables or outcomes?
3. **Full-text screening** (for user-provided PDFs): Does content address research question?

Classify each paper:
- **Included**: Directly relevant to research question
- **Maybe**: Potentially relevant, needs manual review
- **Excluded**: Not relevant (with reason)

### Step 5: Extract Claims
For each included paper, use `extract_claims`:
- Main findings related to our research question
- Effect sizes and confidence intervals
- Sample size and population
- Methods used
- Limitations noted
- How findings support or contradict our hypothesis

### Step 6: Build Evidence Matrix
Create `reports/literature/evidence_matrix.md`:
- Rows: included papers
- Columns: research questions
- Cells: what each paper found for each question
- Summary: consensus, contradictions, gaps

### Step 7: Gap Analysis
Create `reports/literature/gap_analysis.md`:
- What questions have strong evidence?
- What questions have weak or conflicting evidence?
- What methods are underused in the literature?
- Where does our study fit?
- What would strengthen the evidence base?

### Step 8: Generate Bibliography
Create `reports/literature/bibliography.bib`:
- All included papers in BibTeX format
- Complete citation information
- Sorted by year or relevance

### Step 9: Create PRISMA Flow
Create `reports/figures/prisma_diagram.png` and `reports/literature/prisma_flow.md`:
- Records identified from each source
- Duplicates removed
- Records screened
- Records excluded (with reasons)
- Full-text articles assessed
- Studies included in synthesis

### Step 10: Update Research Map
Update `reports/baseline/research_map.json`:
- Literature section: paper count, key findings, gaps
- Update feasibility if literature reveals new constraints

### Step 11: Document in Research Log
Append to `docs/research_log.md`:
```markdown
### [Date] — Literature Pipeline
- **Sources searched**: [list]
- **Total records found**: [count]
- **After deduplication**: [count]
- **Included**: [count]
- **Maybe**: [count]
- **Excluded**: [count]
- **Key findings**: [summary]
- **Gaps identified**: [summary]
```

---

## Search Strategy Builder

```python
def build_search_strategy(research_map, intake):
    """Build search queries from research questions."""
    queries = []
    
    for q in research_map["questions"]:
        # Extract keywords from question text
        keywords = extract_keywords(q["text"])
        
        # Add variable names
        variables = [q.get("outcome", ""), q.get("predictor", "")]
        
        # Add domain-specific terms
        domain_terms = get_domain_terms(research_map["domain"]["name"])
        
        queries.append({
            "question": q["text"],
            "keywords": keywords + variables + domain_terms,
            "date_range": intake.get("date_range", "2016-2026"),
            "filters": get_domain_filters(research_map["domain"]["name"]),
        })
    
    return queries
```

---

## Deduplication Algorithm

```python
def deduplicate_papers(papers):
    """Remove duplicate papers from merged search results."""
    unique = []
    seen_dois = set()
    seen_titles = set()
    
    for paper in sorted(papers, key=lambda p: -completeness_score(p)):
        # DOI match
        if paper.get("doi") and paper["doi"] in seen_dois:
            continue
        
        # Title fuzzy match
        normalized_title = normalize_title(paper.get("title", ""))
        if any(levenshtein(normalized_title, t) < 0.1 for t in seen_titles):
            continue
        
        seen_dois.add(paper.get("doi", ""))
        seen_titles.add(normalized_title)
        unique.append(paper)
    
    return unique
```

---

## PRISMA Flow Data

```json
{
  "identified": {
    "semantic_scholar": 234,
    "arxiv": 45,
    "pubmed": 156,
    "user_provided": 12,
    "other_sources": 23,
    "total": 470
  },
  "deduplicated": 389,
  "duplicates_removed": 81,
  "screened": 389,
  "excluded_title_abstract": 267,
  "full_text_assessed": 122,
  "excluded_full_text": {
    "wrong_population": 15,
    "wrong_outcome": 23,
    "wrong_study_design": 18,
    "insufficient_data": 12,
    "not_peer_reviewed": 8,
    "total_excluded": 76
  },
  "included_in_synthesis": 46,
  "included_in_meta_analysis": 28
}
```

---

## Output Specification
- `reports/literature/literature_corpus.json`: Structured literature database
- `reports/literature/evidence_matrix.md`: Findings mapped to questions
- `reports/literature/gap_analysis.md`: Where our work fits
- `reports/literature/prisma_flow.md`: PRISMA flow data
- `reports/literature/bibliography.bib`: BibTeX bibliography
- `reports/figures/prisma_diagram.png`: PRISMA flow diagram

## Validation Checks
- [ ] All configured sources searched
- [ ] Deduplication reduces count by at least 5%
- [ ] Each included paper has complete citation info
- [ ] Evidence matrix covers all research questions
- [ ] Gap analysis identifies at least 2 gaps
- [ ] Bibliography is valid BibTeX
- [ ] PRISMA flow numbers are consistent (total = identified - duplicates = screened = excluded + assessed = excluded + included)
- [ ] Research log updated
