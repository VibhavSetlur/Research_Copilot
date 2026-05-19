---
agent_id: "literature_deep"
version: "1.0.0"
description: "Recursive literature discovery with multi-source search and citation snowballing."
domain_compatibility: ["all"]
depends_on:
  - "research_init"
composes:
  - "search_semantic_scholar"
  - "search_pubmed"
  - "search_arxiv"
  - "snowball_citations"
  - "extract_claims"
  - "synthesize_literature"
  - "generate_bibtex"
produces:
  - "reports/literature/literature_corpus.json"
  - "reports/literature/literature_citation_graph.json"
  - "reports/literature/evidence_table.csv"
  - "reports/literature/literature_synthesis.md"
  - "reports/literature/references.bib"
---

# Agent: Recursive Literature Review

## Purpose
Perform recursive, multi-source literature discovery with citation chaining, structured claim extraction, and synthesis.

## Inputs
- `docs_input/research_brief.md`
- `reports/baseline/initial_epistemic_baseline.md`
- `.research/config.yaml` (recursion limits)

## Execution Protocol
Execute the composed literature skills end-to-end. Respect recursion depth limits.
