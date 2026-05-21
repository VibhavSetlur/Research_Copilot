---
skill_id: "related_work_writer"
version: "1.0.0"
category: "literature"
depends_on: ["literature_deep", "extract_claims"]
produces: ["03_synthesis/manuscript/related_work.md"]
complexity: "standard"
---

# Skill: Related Work Writer

## Purpose
Generate the Related Work / Literature Review section from the evidence matrix and paper clusters. Produces 3-5 themed paragraphs grounded strictly in cited papers.

---

## Protocol

### Step 1: Load Evidence Matrix & Clusters
Read `reports/literature/evidence_matrix.json` and `reports/literature/paper_clusters.json`. If no clusters exist, create them by grouping papers by methodology (RCT, observational, review, meta-analysis).

### Step 2: Select Themes
Choose 3-5 clusters to cover, prioritized by:
1. Relevance to the research question (highest first)
2. Recency (last 5 years preferred)
3. Methodological rigor (RCTs > longitudinal > cross-sectional)
4. Citation count (proxy for influence)

Skip clusters with < 2 papers or relevance score < 0.3.

### Step 3: Write Theme Paragraphs
For each selected cluster, write one paragraph:
1. **Opening sentence**: Introduce the theme (e.g., "Several randomized trials have examined the effect of X on Y...")
2. **Evidence summary**: Cite 3-5 papers with findings (e.g., "Smith et al. (2021) found a 15% reduction (95% CI: 8-22%, p<0.01), consistent with Jones et al. (2022)...")
3. **Consensus**: Note where papers agree
4. **Contradictions**: Note where papers disagree and possible reasons (different populations, methods, sample sizes)
5. **Gap**: End with what this cluster leaves unanswered

### Step 4: Write Positioning Paragraph
Final paragraph positions the present study:
1. Summarize the overall state of the literature in 1 sentence
2. Identify the specific gap the present study addresses
3. State how the present study fills this gap (method, population, analysis)
4. Template: "The present study addresses gap X by [method] in [population], extending prior work by [novel contribution]."

### Step 5: Grounding Check
Every claim must be traceable to a paper in the evidence matrix. For each sentence:
- Verify the cited paper exists in the corpus
- Verify the claim matches the paper's extracted findings
- If a claim cannot be grounded, remove it or mark as "author interpretation"

### Step 6: Output
Save to `03_synthesis/manuscript/related_work.md`:
- 3-5 theme paragraphs, each with 3-5 citations
- 1 positioning paragraph
- All citations in author-year format
- Bibliography entries cross-referenced with `references.bib`

---

## Paragraph Template

```
### [Theme Name]

[Opening sentence introducing the theme with 1-2 citations.] [Evidence sentence with specific findings, effect sizes, and sample sizes from 2-3 papers.] [Consensus sentence noting agreement across studies.] [Contradiction sentence if applicable, noting possible methodological reasons.] [Gap sentence: what this theme leaves unanswered.]
```

---

## Validation
- [ ] 3-5 theme paragraphs written
- [ ] Each paragraph cites 3-5 papers
- [ ] Every claim grounded in evidence matrix
- [ ] Positioning paragraph identifies specific gap
- [ ] No hallucinated citations or findings
- [ ] Output saved to `03_synthesis/manuscript/related_work.md`
