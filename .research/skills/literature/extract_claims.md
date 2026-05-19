---
skill_id: "extract_claims"
version: "2.0.0"
category: "literature"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm"]
estimated_tokens: 2500
depends_on: ["snowball_citations"]
produces: ["evidence_matrix.json"]
---

# Skill: Extract Claims & Findings

## Purpose
Use LLMs to extract key claims, methodologies, and quantitative findings from abstracts.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `corpus_path` | Path | Yes | Path to paper JSON corpus |

## Execution Protocol

### Step 1: Prompt Construction
- Format prompt requesting extraction of: 1) Main Hypothesis, 2) Methodology, 3) Key Quantitative Finding
- Enforce strict JSON output from LLM

### Step 2: LLM Invocation
- Pass each abstract through the LLM
- Use async processing for speed if batch size > 10

### Step 3: Aggregation
- Compile extracted claims into an Evidence Matrix

## Output Specification
- `evidence_matrix.json`: Matrix of papers vs. extracted claims

## Validation Criteria
- [ ] Extracted JSON must strictly adhere to the defined schema
- [ ] Failed extractions must be logged, not crash the process
