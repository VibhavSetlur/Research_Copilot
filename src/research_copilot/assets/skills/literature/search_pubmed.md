---
skill_id: "search_pubmed"
version: "7.0.0"
category: "literature"
domain_compatibility: ["epidemiology", "medicine", "biology"]
required_tools: ["python", "requests", "BeautifulSoup"]
depends_on: []
produces: ["literature/pubmed_results.json"]
complexity: "basic"
---

# Skill: PubMed/MEDLINE Search

## Purpose
Search PubMed for biomedical literature using E-utilities API with MeSH term support and systematic review filtering.

## When to Use
- Biomedical, clinical, or public health research
- Need MeSH (Medical Subject Headings) indexing
- Systematic review or meta-analysis literature search

## When NOT to Use
- Non-biomedical topic (use search_semantic_scholar)
- Need preprints (use search_arxiv or bioRxiv)

## Execution Protocol

### Step 1: Query Construction
- Translate research question to PICO format (Population, Intervention, Comparison, Outcome)
- Map terms to MeSH headings using MeSH database
- Construct E-utilities query with MeSH terms and free-text keywords
- Use Boolean operators: AND (intersection), OR (synonyms), NOT (exclusion)

### Step 2: API Request
- E-utilities endpoint: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- Step 1: `esearch.fcgi` to get PMIDs
- Step 2: `efetch.fcgi` to get full records (abstract, authors, MeSH terms)
- Rate limit: 10 requests/second without API key
- Filters: publication type (clinical trial, review, meta-analysis), species, language, date range

### Step 3: Result Processing
- Extract: PMID, title, abstract, authors, journal, year, MeSH terms, publication types
- Deduplicate: by PMID
- Score: relevance based on MeSH term match and abstract keyword overlap
- Flag: retracted publications (check PMID against retraction database)

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Results returned | ≥ 10 papers | Broaden MeSH terms |
| MeSH terms assigned | > 70% | Include free-text search |
| Abstracts present | > 90% | Accept older papers without abstracts |

## Output Specification
- `literature/pubmed_results.json`: paper objects with PMID, title, abstract, authors, year, MeSH terms, publication types, relevance score

## Validation Checks
- [ ] All papers have valid PMID
- [ ] No duplicate PMIDs
- [ ] MeSH terms validated against MeSH database
- [ ] Results sorted by relevance
