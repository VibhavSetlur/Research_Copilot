---
skill_id: "audit_causal_language"
version: "2.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "re"]
estimated_tokens: 2500
depends_on: ["write_imrad"]
produces: ["causal_language_report.md"]
---

# Skill: Audit Causal Language

## Purpose
Scan the final manuscript to ensure causal language is strictly justified by the study design.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `manuscript_path` | Path | Yes | Path to manuscript |
| `study_design` | Str | Yes | Design type (e.g., 'observational', 'rct') |

## Execution Protocol

### Step 1: Regex Scanning
- Scan for restricted words (e.g., 'causes', 'impacts', 'determines') if study is observational

### Step 2: Flagging
- Generate line numbers for flagged causal claims requesting softening to associational language (e.g., 'associated with')

## Output Specification
- List of flagged lines and suggested corrections

## Validation Criteria
- [ ] Flagged lines must specify the exact line number in the source markdown
