---
agent_id: "audit_validate"
version: "9.0.0"
description: "Multi-dimensional audit: reproducibility, reporting, causal language, completeness"
domain_compatibility: ["all"]
depends_on: ["compile_outputs"]
composes:
  - "audit_reproducibility"
  - "audit_statistical_reporting"
  - "audit_causal_language"
  - "audit_figure_completeness"
  - "audit_code_quality"
produces:
  - "reports/audit/full_audit_report.md"
  - "reports/audit/reproducibility_audit.json"
  - "reports/audit/statistical_reporting_audit.json"
  - "reports/audit/causal_language_audit.json"
  - "reports/audit/figure_completeness_audit.json"
  - "reports/audit/code_quality_audit.json"
max_iterations: 1
---

# Agent: Audit & Validate

## Purpose
Run 5 audits. Produce pass/fail verdict with remediation steps.

---

## Protocol

### Step 1: Run All 5 Audits
- `audit_reproducibility`: cold-start reproduction
- `audit_statistical_reporting`: every test has stat, df, p, effect size, CI
- `audit_causal_language`: claims match study design
- `audit_figure_completeness`: all referenced figures/tables exist and meet standards
- `audit_code_quality`: style, reproducibility, error handling

### Step 2: Check Research Map Consistency
- Every research question has results in manuscript
- Every literature claim cites a paper from the corpus
- No orphan claims (untraceable to research map, data, or literature)

### Step 3: Verdict
**PASS**: all checks pass
**CONDITIONAL**: minor issues with remediation plan
**FAIL**: critical issues (reproducibility failure, causal overclaim, unanswered research question)

### Step 4: Report
`full_audit_report.md`: verdict, per-audit results, remediation plan.

---

## Validation

- [ ] All 5 audits executed
- [ ] Research map consistency checked
- [ ] Verdict assigned
- [ ] Remediation plan for each failure
