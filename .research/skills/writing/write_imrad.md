---
skill_id: "write_imrad"
version: "3.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic"]
estimated_tokens: 4000
depends_on: ["write_methods_section", "write_results_narrative", "generate_bibtex"]
produces: ["reports/research_findings.md"]
---

# Skill: Write IMRAD Paper

## Purpose
Assemble and write the complete IMRAD format academic manuscript ready for submission.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parsed_brief` | Path | Yes | Path to parsed_research_brief.json |
| `methods_section` | Path | Yes | Path to methods_section.md |
| `results_section` | Path | Yes | Path to results_section.md |
| `bibtex_file` | Path | Yes | Path to references.bib |

## Execution Protocol

### Step 1: Introduction Integration
- Draft the Introduction detailing:
  - Context and setting.
  - Literature gap identified during search.
  - Statement of objectives, research questions, and hypotheses.

### Step 2: Assembly
- Append the Introduction, the Methods section (`methods_section.md`), and the Results section (`results_section.md`) into a single markdown manuscript.

### Step 3: Discussion Drafting
- Interpret findings directly in relation to the original hypotheses.
- Compare results with literature references present in the BibTeX manifest.
- Define a dedicated "Limitations" sub-section identifying statistical caveats (e.g., missingness adjustments, observational design limits, sample size restrictions).
- Propose future research paths based on the gaps.

### Step 4: Reference Formatting
- Append a "References" section at the end. Use a formatting engine (e.g., `pandoc-citeproc` or similar) to generate styled references from the `.bib` file.

## Output Specification
Produces:
- `reports/research_findings.md`

## Validation Criteria
- [ ] Section headers match IMRAD standard (Introduction, Methods, Results, Discussion).
- [ ] References section is populated and matches in-text citations.