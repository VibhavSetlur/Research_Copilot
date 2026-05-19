---
skill_id: "search_arxiv"
version: "2.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "urllib", "xml.etree.ElementTree"]
estimated_tokens: 2500
depends_on: []
produces: ["arxiv_results.json"]
---

# Skill: arXiv API Search

## Purpose
Query arXiv for preprints in CS, Math, Physics, and Quant Bio.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | Str | Yes | Search query |
| `limit` | Int | No | Max results (default: 50) |

## Execution Protocol

### Step 1: Query Formulation
- Construct arXiv API URL using `search_query=all:<query>`

### Step 2: API Request
- Execute GET request to `http://export.arxiv.org/api/query`

### Step 3: Parsing
- Parse Atom XML response
- Extract id (arXiv ID), published date, title, summary, authors
- Convert arXiv ID to DOI format if registered, else use arXiv URL as identifier

## Output Specification
- `arxiv_results.json`: Array of paper objects

## Validation Criteria
- [ ] XML parsing must handle missing fields gracefully
- [ ] Abstracts must be stripped of newline characters
