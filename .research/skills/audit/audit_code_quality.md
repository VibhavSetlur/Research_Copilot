---
skill_id: "audit_code_quality"
version: "2.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "flake8", "black"]
estimated_tokens: 2500
depends_on: []
produces: ["code_quality_report.txt"]
---

# Skill: Audit Code Quality

## Purpose
Run static analysis (flake8, black) on generated analysis scripts.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scripts_dir` | Path | Yes | Path to scripts |

## Execution Protocol

### Step 1: Linting
- Run flake8 on all `.py` files

### Step 2: Formatting
- Run black --check on all `.py` files

## Output Specification
- Output of flake8 and black

## Validation Criteria
- [ ] Critical syntax errors (E999) must cause audit failure
