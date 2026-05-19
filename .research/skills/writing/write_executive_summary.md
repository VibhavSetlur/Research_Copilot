---
skill_id: "write_executive_summary"
version: "3.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic"]
estimated_tokens: 2500
depends_on: ["write_imrad"]
produces: ["reports/executive_summary.md"]
---

# Skill: Write Executive Summary

## Purpose
Condense the full research findings into a 1-page executive summary for stakeholders.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `paper_path` | Path | Yes | Path to the compiled IMRAD paper |

## Execution Protocol

### Step 1: Key Component Extraction
- Extract the core research objective, total sample size, primary findings, and key recommendations from the manuscript.

### Step 2: Outlining and Structuring
- Organize the summary into three sections:
  1. **Background**: Brief context and goal of the study.
  2. **Key Findings**: Bulleted list of findings. Each bullet must state a quantitative value (e.g., effect size, percentage difference).
  3. **Strategic Implications**: What the results mean for policy, business, or further development.

### Step 3: Precision Editing
- Refine text to ensure total length does not exceed 500 words.

## Output Specification
Produces:
- `reports/executive_summary.md`

## Validation Criteria
- [ ] Total word count is under 500 words.
- [ ] Contains a minimum of 3 quantitative bullet points under Key Findings.