---
skill_id: "search_arxiv"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "requests", "feedparser"]
depends_on: []
produces: ["literature/arxiv_results.json"]
complexity: "basic"
---

# Skill: arXiv Preprint Search

## Purpose
Search arXiv for preprints in physics, mathematics, computer science, quantitative biology, and related fields.

## When to Use
- Need latest preprints not yet peer-reviewed
- CS, physics, math, statistics, or quantitative biology research
- Tracking cutting-edge developments

## When NOT to Use
- Need peer-reviewed literature only
- Non-quantitative fields (humanities, social sciences)

## Execution Protocol

### Step 1: Query Construction
- Use arXiv API query syntax: `ti:"term"` (title), `au:"name"` (author), `abs:"term"` (abstract)
- Category filters: cs.AI, cs.LG, stat.ML, q-bio, physics, math, etc.
- Combine with AND (`AND`), OR (`OR`), NOT (`ANDNOT`)

### Step 2: API Request
- Endpoint: `http://export.arxiv.org/api/query`
- Parameters: search_query, max_results (default 10, max 30000), sortBy (relevance/lastUpdatedDate/submittedDate), sortOrder
- Parse Atom XML response using feedparser

### Step 3: Result Processing
- Extract: arXiv ID, title, authors, abstract, categories, published date, updated date, DOI (if available)
- Filter: by category, date range
- Deduplicate: by arXiv ID
- Note: preprints may have multiple versions; use latest version

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Results returned | ≥ 5 papers | Broaden category filter |
| Recent papers | Within last 2 years | Adjust date filter |
| Abstracts present | 100% | Always available on arXiv |

## Output Specification
- `literature/arxiv_results.json`: paper objects with arXiv ID, title, abstract, authors, categories, dates, DOI

## Validation Checks
- [ ] All papers have valid arXiv ID
- [ ] Categories are valid arXiv categories
- [ ] Results sorted by specified criterion
