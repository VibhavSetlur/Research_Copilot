# Web Search Grounding — Anti-Hallucination Fact Verification

## Purpose
For any factual claim an agent makes that is NOT derived from an uploaded paper or computed from data, this skill must be invoked. Prevents agents from inventing statistics, facts, or references.

## When to Invoke

Invoke this skill whenever:
- Making a numeric claim (percentages, counts, statistics) not computed from project data
- Stating a fact about the real world not sourced from the literature corpus
- Referencing library/framework documentation or API behavior
- Making claims about current events, policies, or standards

## Search Sources (in priority order)

### 1. Context7 (`/context7`)
For library/framework documentation claims:
- Use `context7_resolve-library-id` to get the library ID
- Use `context7_query-docs` to fetch current documentation
- Mandatory for: scipy, statsmodels, pandas, sklearn, lifelines, pymc, networkx, geopandas, altair, bokeh, panel, holoviews, dash, plotly

### 2. Semantic Scholar API
For academic claims:
- `https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=10&fields=title,abstract,authors,year,citationCount`
- Use to verify academic statistics, effect sizes, methodological claims

### 3. CrossRef API
For publication metadata:
- `https://api.crossref.org/works?query={query}&select=title,author,published,DOI`
- Use to verify publication dates, author lists, journal names

### 4. NCBI E-utilities (PubMed)
For biomedical facts:
- `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax=10`
- Use to verify biomedical statistics, prevalence rates, clinical findings

## Protocol

### Step 1: Identify the Claim
Extract the specific factual claim that needs grounding:
```
Claim: "X affects Y by approximately Z%"
Source type needed: empirical_study | documentation | statistic | policy
```

### Step 2: Select Search Source
Based on claim type:
- Library API → Context7
- Academic finding → Semantic Scholar
- Publication fact → CrossRef
- Biomedical fact → PubMed
- General fact → Semantic Scholar (broadest coverage)

### Step 3: Execute Search
- Formulate a precise search query
- Include year constraints if the claim is time-sensitive
- Execute the search via the appropriate API

### Step 4: Record Search
Store every search in `reports/literature/search_log.json`:
```json
{
  "timestamp": "ISO 8601",
  "claim": "The claim being verified",
  "query": "The exact search query",
  "source": "semantic_scholar|crossref|pubmed|context7",
  "results_count": 5,
  "top_result": {
    "title": "...",
    "url": "...",
    "snippet": "..."
  },
  "verified": true,
  "evidence": "Brief summary of supporting evidence"
}
```

### Step 5: Tag the Claim
In any output, tag claims based on verification status:
- `[VERIFIED: source]` — Confirmed by web search
- `[DATA: file_path]` — Computed from project data
- `[LITERATURE: DOI]` — From verified literature corpus
- `[UNVERIFIED]` — Could not be verified — requires human review

## Enforcement Rules

1. **No naked numbers:** No numeric claim may appear in manuscript without a trace to either computed data or a verified web source
2. **No invented APIs:** Library function calls must be verified via Context7
3. **No assumed facts:** If a fact cannot be verified, state uncertainty explicitly
4. **Log everything:** Every search is recorded with query, source, results, and timestamp
5. **Cache results:** Store verified facts in the research cache to avoid re-searching

## CLI Reference
```bash
# Search log is at: reports/literature/search_log.json
# Each entry is append-only — never modify previous entries
```
