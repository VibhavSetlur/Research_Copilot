---
skill_id: "search_semantic_scholar"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "requests"]
depends_on: []
produces: ["literature/semantic_scholar_results.json"]
complexity: "basic"
---

# Skill: Semantic Scholar API Search

## Purpose
Query the Semantic Scholar Graph API to retrieve academic papers with citation metadata, abstracts, and influence metrics.

## When to Use
- Initial literature search for any research topic
- Finding highly-cited papers in a domain
- Building a seed corpus for snowball citation search

## When NOT to Use
- Need biomedical-specific search (use search_pubmed)
- Need preprint-only search (use search_arxiv)
- API rate limit exhausted (cache results first)

## Execution Protocol

### Step 1: Query Construction
- Extract key terms from research brief
- Construct query: combine terms with AND/OR operators
- Use field-specific search: `title:term`, `abstract:term`
- Limit query length to avoid API truncation

### Step 2: API Request
- Endpoint: `https://api.semanticscholar.org/graph/v1/paper/search`
- Fields: title, abstract, year, authors, citationCount, referenceCount, influentialCitationCount, externalIds (DOI), publicationVenue, fieldsOfStudy
- Parameters: limit (default 50, max 100), offset (pagination), year range, fieldsOfStudy filter
- Handle rate limiting: 100 requests/5 minutes without API key, exponential backoff on HTTP 429

### Step 3: Result Processing
- Filter: remove papers without abstracts (unless seminal)
- Filter: remove papers outside year range (if specified)
- Deduplicate: by DOI
- Sort: by citationCount (default) or relevance
- Score: compute relevance score based on query term overlap in title + abstract

### Step 4: Quality Assessment
- Flag papers with: citationCount = 0 (may be very new or low quality)
- Flag predatory journals (check publication venue)
- Prioritize: papers in top-tier venues, high citation counts, recent publications

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Results returned | ≥ 10 papers | Broaden query or check API |
| Abstracts present | > 80% have abstracts | Accept without abstracts for seminal papers |
| Year distribution | Spans relevant period | Adjust year filter |
| Citation distribution | Mix of highly-cited and recent | Query may be too narrow |

## Output Specification
- `literature/semantic_scholar_results.json`: paper objects with title, authors, year, abstract, DOI, citationCount, relevance score, fieldsOfStudy

## Validation Checks
- [ ] All papers have valid DOI or externalId
- [ ] Results ≤ limit parameter
- [ ] No duplicate DOIs
- [ ] Relevance scores computed
