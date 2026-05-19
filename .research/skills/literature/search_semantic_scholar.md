---
skill_id: "search_semantic_scholar"
version: "2.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "requests"]
estimated_tokens: 2500
depends_on: []
produces: ["semantic_scholar_results.json"]
---

# Skill: Semantic Scholar API Search

## Purpose
Query Semantic Scholar Graph API to retrieve highly relevant academic papers.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | Str | Yes | Search query |
| `limit` | Int | No | Max results (default: 50) |

## Execution Protocol

### Step 1: Query Construction
- Format URL encoding for query parameters
- Specify requested fields: title, abstract, year, authors, citationCount, externalIds (DOI)

### Step 2: API Request
- Execute GET request to `https://api.semanticscholar.org/graph/v1/paper/search`
- Handle rate limiting (HTTP 429) with exponential backoff

### Step 3: Parsing
- Filter out papers missing abstracts or DOIs
- Sort by citationCount descending

## Output Specification
- `semantic_scholar_results.json`: Array of paper objects

## Validation Criteria
- [ ] All returned papers must have a valid DOI
- [ ] Results must not exceed the `limit` parameter
