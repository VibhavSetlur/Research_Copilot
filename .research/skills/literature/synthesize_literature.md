---
skill_id: "synthesize_literature"
version: "7.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["extract_claims"]
produces: ["literature/literature_synthesis.md", "literature/gap_analysis.md"]
complexity: "advanced"
---

# Skill: Literature Synthesis & Gap Analysis

## Purpose
Synthesize the evidence matrix into a narrative review identifying consensus, contradictions, and research gaps.

## When to Use
- After claim extraction from all papers
- Before writing introduction or discussion sections
- Need to position research within existing literature

## When NOT to Use
- Evidence matrix not yet built
- Only annotated bibliography needed

## Execution Protocol

### Step 1: Thematic Clustering
- Group papers by: methodology, theoretical framework, or dependent variable
- Identify dominant themes (topics addressed by ≥ 3 papers)
- Identify niche themes (addressed by 1-2 papers)

### Step 2: Consensus Assessment
- For each claim/hypothesis: count supporting, contradicting, and neutral papers
- Compute directional agreement: percentage of papers supporting the claim
- Classify: strong consensus (> 80% agree), moderate (60-80%), contested (40-60%), no consensus (< 40%)

### Step 3: Contradiction Analysis
- For contested claims: identify sources of disagreement
  - Methodological differences (design, sample, measures)
  - Contextual differences (population, setting, time period)
  - Analytical differences (statistical method, covariate adjustment)
- Determine if contradictions are resolvable or fundamental

### Step 4: Gap Identification
- **Evidence gaps**: claims with no empirical testing
- **Methodological gaps**: claims tested only with weak designs
- **Population gaps**: claims tested only in specific populations
- **Temporal gaps**: claims not tested recently (> 5 years)
- **Integration gaps**: claims tested in isolation, not in combination

### Step 5: Synthesis Narrative
- Structure: introduction → themes → consensus → contradictions → gaps → implications
- Cite papers using Author-Year format with DOI
- For each theme: summarize findings, note quality of evidence, identify gaps
- Conclude with: how the current research addresses identified gaps

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Themes identified | ≥ 2 themes | Literature too narrow or diverse |
| Consensus classified | All claims classified | Insufficient papers per claim |
| Gaps identified | ≥ 1 gap | Literature is complete; rare |
| Citations complete | All claims cited | Missing references |

## Output Specification
- `literature/literature_synthesis.md`: narrative synthesis with citations
- `literature/gap_analysis.md`: structured gap analysis with priority ranking

## Validation Checks
- [ ] All claims from evidence matrix addressed
- [ ] Consensus percentages computed
- [ ] At least one research gap identified
- [ ] All citations have DOI or Author-Year format
