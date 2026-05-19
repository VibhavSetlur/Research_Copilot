---
skill_id: "audit_statistical_reporting"
version: "2.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "re"]
estimated_tokens: 2500
depends_on: ["write_imrad"]
produces: ["stats_reporting_report.md"]
---

# Skill: Audit Statistical Reporting

## Purpose
Ensure all reported statistics comply with APA guidelines (e.g., leading zeros, decimal precision).

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `manuscript_path` | Path | Yes | Path to manuscript |

## Execution Protocol

### Step 1: P-Value Checking
- Ensure p-values do not have leading zeros (e.g., `.04` not `0.04`)
- Ensure p-values are not reported as `p = 0.000`

### Step 2: Statistic Formatting
- Ensure test statistics are italicized (e.g., *t*, *F*, *p*)

## Output Specification
- List of formatting violations

## Validation Criteria
- [ ] Must flag any instance of 'p = 0' or 'p = 0.00'
