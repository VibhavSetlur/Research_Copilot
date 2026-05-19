---
skill_id: "write_executive_summary"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
depends_on: ["write_results_narrative"]
produces: ["reports/executive_summary.md"]
complexity: "basic"
---

# Skill: Write Executive Summary

## Purpose
Generate a concise, non-technical summary of research findings for stakeholders, policymakers, or decision-makers.

## When to Use
- Results finalized
- Need to communicate to non-research audience
- Policy brief or briefing document

## When NOT to Use
- Only academic audience
- Results preliminary

## Execution Protocol

### Step 1: Key Findings
- 3-5 main findings in plain language
- Each finding: what was found, how big the effect is, confidence level
- No statistical jargon: no p-values, CIs, or test names

### Step 2: Context
- Why this research matters
- What question was asked
- How it was studied (one sentence)

### Step 3: Implications
- What the findings mean for practice or policy
- Recommended actions (if applicable)
- Caveats: limitations in plain language

### Step 4: Format
- Length: 1-2 pages maximum
- Structure: headings, bullet points, short paragraphs
- Visual: include 1-2 key figures (simplified)

## Output Specification
- `reports/executive_summary.md`: plain-language summary

## Validation Checks
- [ ] No statistical jargon
- [ ] All findings supported by results
- [ ] Limitations acknowledged
- [ ] Length ≤ 2 pages
