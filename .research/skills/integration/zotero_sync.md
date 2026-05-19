---
skill_id: "zotero_sync"
version: "2.0.0"
category: "integration"
domain_compatibility: ["all"]
required_tools: ["python", "pyzotero"]
estimated_tokens: 2500
depends_on: ["generate_bibtex"]
produces: ["zotero_sync_log.json"]
---

# Skill: Zotero Sync

## Purpose
Push the generated BibTeX references to a Zotero collection via the Zotero API.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `bibtex_path` | Path | Yes | Path to references.bib |
| `zotero_api_key` | Str | Yes | Zotero API key |

## Execution Protocol

### Step 1: Parsing
- Parse the BibTeX file into python dictionaries

### Step 2: API Push
- Format items to Zotero API JSON schema
- POST items to the specified Zotero collection

## Output Specification
- Log of successful and failed sync items

## Validation Criteria
- [ ] API response must be 200 OK for all items
