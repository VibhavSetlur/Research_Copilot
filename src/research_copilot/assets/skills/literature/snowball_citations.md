---
skill_id: "snowball_citations"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "requests"]
depends_on: ["search_semantic_scholar"]
produces: ["literature/citation_graph.json", "literature/snowball_corpus.json"]
complexity: "intermediate"
---

# Skill: Snowball Citation Search

## Purpose
Expand a seed set of papers through forward chaining (papers that cite them) and backward chaining (papers they cite) to build a comprehensive literature corpus.

## When to Use
- After initial search has identified seed papers
- Need comprehensive coverage of a research area
- Building evidence matrix for systematic review

## When NOT to Use
- Only a few papers needed
- Seed papers are not well-chosen (garbage in, garbage out)
- API rate limits exhausted

## Execution Protocol

### Step 1: Seed Paper Selection
- Start with 5-20 highly-relevant papers from initial search
- Prioritize: high citation count, recent, review articles, seminal works
- Record: DOI, title, year for each seed

### Step 2: Backward Chaining (References)
- For each seed paper: fetch its reference list
- From Semantic Scholar: `paper/{id}/references`
- Filter references: keep those with abstracts and DOIs
- Add to corpus if not already present

### Step 3: Forward Chaining (Citations)
- For each seed paper: fetch papers that cite it
- From Semantic Scholar: `paper/{id}/citations`
- Filter: keep papers within research scope (year, field)
- Add to corpus if not already present

### Step 4: Recursive Expansion
- For each newly added paper: repeat backward and forward chaining
- Maximum depth: 2 (seed → references/citations → their references/citations)
- Stop when: no new papers found, depth limit reached, or corpus size limit

### Step 5: Deduplication & Ranking
- Deduplicate by DOI
- Rank by: citation count, recency, relevance to research question
- Compute: network centrality in citation graph (papers cited by many others are central)

### Step 6: Corpus Finalization
- Output: unified corpus with all papers
- Output: citation graph (nodes = papers, edges = citation relationships)
- Output: relevance scores for each paper

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Corpus growth | New papers found at each depth | Seed papers too narrow |
| Citation graph connected | Most papers connected | Disconnected subgraphs; add bridging seeds |
| Relevance maintained | > 70% papers relevant | Chaining drifted from topic; tighten filters |

### Red Flags
- **Corpus explodes (> 500 papers)**: topic too broad; narrow scope or reduce depth
- **No new papers at depth 1**: seed papers are very new or obscure
- **Citation graph has isolated nodes**: papers with no citation links in API data

## Output Specification
- `literature/citation_graph.json`: nodes (papers), edges (citation relationships)
- `literature/snowball_corpus.json`: deduplicated, ranked paper corpus with relevance scores

## Validation Checks
- [ ] No duplicate DOIs in corpus
- [ ] Citation graph edges reference valid nodes
- [ ] Depth limit respected
- [ ] All papers have DOI or arXiv ID
