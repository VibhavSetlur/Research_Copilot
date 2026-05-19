---
skill_id: "search_pubmed"
version: "2.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "requests", "xml.etree.ElementTree"]
estimated_tokens: 2500
depends_on: []
produces: ["pubmed_results.json"]
---

# Skill: PubMed E-Utilities Search

## Purpose
Query NCBI PubMed for biomedical literature.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | Str | Yes | Search query |
| `limit` | Int | No | Max results (default: 50) |

## Execution Protocol

### Step 1: ESearch
- Query `esearch.fcgi` to get a list of PMIDs matching the query

### Step 2: ESummary
- Query `esummary.fcgi` with retrieved PMIDs to fetch metadata (Title, Source, PubDate, DOI)

### Step 3: Parsing
- Extract DOI and Abstract (if available via EFetch)
- Format into standard paper JSON format

## Output Specification
- `pubmed_results.json`: Array of paper objects

## Validation Criteria
- [ ] Output JSON schema must exactly match the internal paper schema
- [ ] Must respect NCBI rate limits (3 requests/second)
