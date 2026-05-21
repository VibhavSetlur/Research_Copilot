---
agent_id: "literature_deep"
version: "9.0.0"
description: "Expand user's literature, build evidence matrix, identify gaps"
domain_compatibility: ["all"]
depends_on: ["research_init"]
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
  - "reports/literature/evidence_matrix.json"
  - "reports/literature/literature_synthesis.md"
  - "reports/literature/gap_analysis.md"
  - "reports/literature/references.bib"
max_iterations: 2
---

# Agent: Literature Deep

## Purpose
Start from the user's literature knowledge, expand with targeted search, and produce an evidence matrix mapped to the research question.

---

## Protocol

### Step 1: Load Research Map
Extract: research question, hypothesis, domain, user's stated literature findings, gap.

### Step 2: Ingest User's Papers
Scan `inputs/papers/`. For each: extract title, abstract, key findings. Map to the research question.

### Step 2.5: Semantic Clustering of Papers
After ingesting papers, cluster them by topic using TF-IDF cosine similarity on abstracts:
1. Vectorize all abstracts with `TfidfVectorizer(max_features=5000, stop_words='english')`
2. Compute pairwise cosine similarity matrix
3. Apply agglomerative clustering with threshold 0.7 (papers with similarity > 0.7 form a cluster)
4. Name each cluster by extracting top-3 TF-IDF terms (e.g., "RCT studies on X", "Observational studies on Y")
5. Save cluster assignments to `reports/literature/paper_clusters.json` with keys: cluster_id, cluster_name, paper_ids, top_terms
6. Update evidence matrix to include `cluster_id` per paper

This gives the evidence matrix a thematic structure instead of a flat list, enabling the `related_work_writer` skill to generate organized literature review sections.

### Step 3: Search (only if < 20 relevant papers)
Build queries from the research question. Run Semantic Scholar, PubMed (if biomedical), arXiv (if CS/math). Deduplicate against user's papers.

### Step 4: Snowball (only if < 20 papers after search)
From the top-10 most relevant papers, run `snowball_citations` depth 2.

### Step 5: Extract & Synthesize
Run `extract_claims` → build evidence matrix (papers × research question). Run `synthesize_literature` → consensus, contradictions, gaps. Generate BibTeX.

### Step 6: Update Research Map
Append: literature sufficiency, updated gap analysis, relevance scores.

### Step 7: Critic Review
- Trigger the `critic` agent to perform adversarial review of the literature corpus, evidence matrix, and gap analysis outputs.
- Verify that the synthesis is logically consistent and properly structured.
- If the critic verdict is FAIL, execute remediation steps via `research_iterate`.

---

## Validation

- [ ] User's papers ingested
- [ ] Evidence matrix covers the research question
- [ ] Gap analysis updated
- [ ] BibTeX generated
- [ ] Critic agent report generated with PASS verdict

