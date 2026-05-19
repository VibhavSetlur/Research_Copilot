---
skill_id: "extract_claims"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["search_semantic_scholar", "snowball_citations"]
produces: ["literature/evidence_matrix.json"]
complexity: "intermediate"
---

# Skill: Claim Extraction from Literature

## Purpose
Extract key claims, methods, findings, and limitations from each paper in the corpus into a structured evidence matrix.

## When to Use
- After literature search and snowballing
- Before literature synthesis
- Need structured comparison across papers

## When NOT to Use
- Only bibliographic data needed
- Corpus too large (> 200 papers; sample first)

## Execution Protocol

### Step 1: Paper Preparation
- For each paper: compile title, abstract, full text (if available)
- If full text not available: work with abstract + key sections
- Format: structured prompt for LLM extraction

### Step 2: Claim Extraction (per paper)
Extract the following fields:
- **Research question**: what does this paper investigate?
- **Methodology**: study design, sample size, analytical method
- **Key findings**: main results with effect sizes and p-values
- **Claims**: specific assertions made by authors
- **Limitations**: acknowledged limitations
- **Conflicts of interest**: funding sources, author disclosures
- **Replication status**: has this been replicated? (check citation context)

### Step 3: Evidence Matrix Construction
- Rows: papers (identified by DOI)
- Columns: claims/hypotheses from research brief
- Cells: support (+), contradict (-), neutral (0), not addressed (N/A)
- Add confidence rating: high (direct evidence), medium (indirect), low (speculative)

### Step 4: Quality Assessment
- Study design quality: RCT > cohort > case-control > cross-sectional > case report
- Sample size adequacy: powered for primary outcome?
- Statistical rigor: appropriate methods, multiple testing addressed?
- Replication: confirmed by independent studies?

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Claims extracted | All papers processed | Some papers lack sufficient text |
| Evidence matrix filled | > 80% cells populated | Claims too specific; broaden |
| Quality scores assigned | All papers scored | Insufficient methodological detail |

## Output Specification
- `literature/evidence_matrix.json`: per-paper claims, methods, findings, quality scores, evidence matrix (papers × claims)

## Validation Checks
- [ ] Each paper has at least one claim extracted
- [ ] Evidence matrix covers all research brief hypotheses
- [ ] Quality scores use consistent scale
- [ ] Confidence ratings assigned
