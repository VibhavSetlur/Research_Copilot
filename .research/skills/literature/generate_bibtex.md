---
skill_id: "generate_bibtex"
version: "2.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "bibtexparser"]
estimated_tokens: 2500
depends_on: []
produces: ["references.bib"]
---

# Skill: BibTeX Generation

## Purpose
Convert the finalized literature corpus into a standard BibTeX file.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `corpus_path` | Path | Yes | Path to paper JSON corpus |

## Execution Protocol

### Step 1: Metadata Mapping
- Map custom JSON fields to BibTeX standard fields (author, title, year, journal, volume, doi)

### Step 2: Key Generation
- Generate citation keys in format `AuthorYearWord` (e.g., `Smith2023Analysis`)

### Step 3: Formatting
- Serialize to `.bib` format

## Output Specification
- `references.bib`: Standard BibTeX file

## Validation Criteria
- [ ] Generated `.bib` file must pass standard LaTeX BibTeX parsing
- [ ] All citation keys must be strictly unique
