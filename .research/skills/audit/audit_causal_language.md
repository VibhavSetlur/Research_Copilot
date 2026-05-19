---
skill_id: "audit_causal_language"
version: "7.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["causal_inference"]
produces: ["audit/causal_language_audit.json"]
complexity: "intermediate"
---

# Skill: Causal Language Audit

## Purpose
Scan manuscript text for causal claims that are not justified by the study design, and flag overstatements.

## When to Use
- After manuscript written
- Before submission
- When study is observational (not experimental)

## When NOT to Use
- Study is a randomized experiment (causal language is appropriate)
- Only descriptive analysis (no claims made)

## Execution Protocol

### Step 1: Claim Extraction
- Scan all sections (abstract, results, discussion, conclusion)
- Extract sentences containing causal language:
  - Strong: "causes", "leads to", "results in", "produces", "effect of"
  - Moderate: "associated with", "predicts", "related to", "influences"
  - Weak: "linked to", "corresponds to", "co-occurs with"

### Step 2: Design Assessment
- Classify study design: RCT, quasi-experimental, observational, cross-sectional
- Determine justified causal strength:
  - RCT: strong causal claims justified
  - Quasi-experimental: moderate causal claims (with caveats)
  - Observational: associational language only
  - Cross-sectional: correlational language only

### Step 3: Mismatch Detection
- Compare claim strength to design-justified strength
- Flag: claims stronger than design supports
- For each flagged claim: suggest alternative wording

### Step 4: Confounding Acknowledgment
- Check: does discussion acknowledge potential confounding?
- Check: are alternative explanations considered?
- Check: limitations section addresses causal inference limits

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| No overclaims | All claims ≤ design strength | Rewrite flagged sentences |
| Confounding acknowledged | Yes | Add to limitations |
| Alternative explanations | ≥ 2 discussed | Add to discussion |

## Output Specification
- `audit/causal_language_audit.json`: flagged claims, suggested rewrites, design assessment

## Validation Checks
- [ ] All sections scanned
- [ ] Flagged claims have suggested alternatives
- [ ] Design correctly classified
- [ ] Confounding acknowledged in limitations
