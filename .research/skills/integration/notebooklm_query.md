---
skill_id: "notebooklm_query"
version: "2.0.0"
category: "integration"
domain_compatibility: ["all"]
required_tools: ["python", "notebooklm-py"]
estimated_tokens: 2500
depends_on: []
produces: ["notebook_response.json"]
---

# Skill: NotebookLM Query

## Purpose
Query an existing NotebookLM notebook for Q&A based on the research corpus.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `notebook_id` | Str | Yes | ID of the notebook |
| `query` | Str | Yes | Question string |

## Execution Protocol

### Step 1: API Request
- Send query to NotebookLM via API

### Step 2: Response Parsing
- Extract text response and citation markers

## Output Specification
- Response text and source citations

## Validation Criteria
- [ ] Response must include source document citations
