---
skill_id: "synthesize_literature"
version: "2.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
estimated_tokens: 2500
depends_on: ["extract_claims"]
produces: ["literature_synthesis.md"]
---

# Skill: Literature Synthesis & Gap Analysis

## Purpose
Synthesize the evidence matrix to identify consensus, contradictions, and research gaps.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `evidence_matrix` | Path | Yes | Path to extracted claims |

## Execution Protocol

### Step 1: Thematic Clustering
- Group papers by methodology or dependent variable

### Step 2: Consensus Scoring
- Identify directional agreement (e.g., 80% of papers show positive effect)

### Step 3: Gap Identification
- Identify areas with high contradiction or lack of empirical testing

## Output Specification
- `literature_synthesis.md`: Narrative synthesis of the field

## Validation Criteria
- [ ] Synthesis must explicitly cite papers using their DOI or Author-Year format
- [ ] Must explicitly list at least one research gap
