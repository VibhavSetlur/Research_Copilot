---
skill_id: "generate_bibtex"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "bibtexparser|pybtex"]
depends_on: ["search_semantic_scholar", "extract_claims"]
produces: ["literature/references.bib"]
complexity: "basic"
---

# Skill: BibTeX Reference Generation

## Purpose
Generate a complete, validated BibTeX file from the literature corpus for use in manuscript writing.

## When to Use
- After literature search and claim extraction
- Before writing IMRAD manuscript
- Need formatted references for any output

## When NOT to Use
- Only in-text citations needed
- Reference manager (Zotero, EndNote) already has entries

## Execution Protocol

### Step 1: Entry Collection
- Gather all papers from corpus with: DOI, title, authors, year, journal, volume, pages
- For each paper: determine entry type (article, inproceedings, book, chapter, misc)

### Step 2: BibTeX Entry Generation
- Generate standard BibTeX entry per paper:
  - `@article`: journal articles (most common)
  - `@inproceedings`: conference papers
  - `@book`: books
  - `@incollection`: book chapters
  - `@misc`: preprints, reports
- Citation key: AuthorYearFirstWord (e.g., Smith2024Causal)
- Ensure all required fields present per entry type

### Step 3: Validation
- Check: all entries parse as valid BibTeX
- Check: no duplicate citation keys
- Check: all entries have DOI or URL
- Validate author names: "Last, First" format
- Validate year: 4-digit integer

### Step 4: Organization
- Sort entries alphabetically by citation key
- Add comments grouping by theme (optional)
- Generate entry count by type and year

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| All entries parse | Valid BibTeX | Fix formatting errors |
| No duplicate keys | Unique keys | Regenerate conflicting keys |
| DOI present | > 90% | Search for missing DOIs |
| Author format | "Last, First" | Reformat author strings |

## Output Specification
- `literature/references.bib`: complete BibTeX file with all corpus papers

## Validation Checks
- [ ] File parses as valid BibTeX
- [ ] Entry count matches corpus size
- [ ] No duplicate citation keys
- [ ] All entries have required fields for their type
