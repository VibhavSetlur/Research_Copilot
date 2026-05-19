---
agent_id: "audit_validate"
version: "10.0.0"
description: "Multi-dimensional audit with auto-healing loop: reproducibility, reporting, causal language, completeness"
domain_compatibility: ["all"]
depends_on: ["compile_outputs"]
composes:
  - "audit_reproducibility"
  - "audit_statistical_reporting"
  - "audit_causal_language"
  - "audit_figure_completeness"
  - "audit_code_quality"
  - "quality_gate"
produces:
  - "reports/audit/full_audit_report.md"
  - "reports/audit/reproducibility_audit.json"
  - "reports/audit/statistical_reporting_audit.json"
  - "reports/audit/causal_language_audit.json"
  - "reports/audit/figure_completeness_audit.json"
  - "reports/audit/code_quality_audit.json"
  - "docs/quality_gates/gate_007_audit_validate.md"
max_iterations: 3
---

# Agent: Audit & Validate

## Purpose
Run 5 audits. Produce pass/fail verdict with remediation steps. If FAIL or CONDITIONAL, AUTO-HEAL: trigger research_iterate with failures, fix issues, re-validate. Loop up to 3 times.

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

### Step 3: Run Quality Gate
Run `research validate audit_validate`. Record results in `docs/quality_gates/gate_007_audit_validate.md`.

### Step 4: Verdict
**PASS**: all audits pass, quality gate passes
**CONDITIONAL**: minor issues with clear remediation plan (formatting, missing labels, incomplete references)
**FAIL**: critical issues (reproducibility failure, causal overclaim, unanswered research question, quality gate FAIL)

### Step 5: Auto-Healing Loop
If verdict is FAIL or CONDITIONAL:

1. **Create remediation brief** — List every failure with specific fix instructions
2. **Trigger research_iterate** with type `validate` and the remediation brief
3. **research_iterate fixes the issues** — Rewrites code, updates figures, corrects manuscript
4. **Re-run audit** — Execute steps 1-4 again
5. **Check if PASS** — If yes, stop. If no, repeat (max 3 iterations)
6. **If still failing after 3 attempts** — Document as dead end, report to user with manual fix instructions

#### Auto-Healing Protocol
```
audit_result = run_audit()
attempt = 1
max_attempts = 3

while audit_result.verdict in (FAIL, CONDITIONAL) and attempt <= max_attempts:
    remediation = build_remediation_brief(audit_result.failures)
    trigger_research_iterate(
        type="validate",
        remediation=remediation,
        previous_failures=audit_result.failures,
    )
    audit_result = run_audit()
    attempt += 1

if audit_result.verdict == PASS:
    record_success()
else:
    record_dead_end(
        approach="auto_healing_audit",
        reason=f"Failed after {max_attempts} attempts: {audit_result.failures}",
    )
    report_to_user("Manual intervention required")
```

### Step 6: Document Dead Ends
If auto-healing fails after max attempts, document in `docs/dead_ends/`:
- What was tried
- What failures persisted
- What manual intervention is needed
- Why automated fixes couldn't resolve it

### Step 7: Report
`full_audit_report.md`: verdict, per-audit results, auto-healing attempts, final status.

---

## Auto-Healing Remediation Mapping

| Audit Failure | Auto-Healing Action |
|--------------|-------------------|
| Reproducibility: script fails | Fix import errors, correct file paths, add missing dependencies |
| Reproducibility: output mismatch | Re-run analysis, update manuscript with correct values |
| Statistical: missing effect size | Re-compute with effect size, update tables/figures |
| Statistical: missing CI | Add confidence intervals to all results |
| Statistical: p-value thresholded | Replace "p < 0.05" with exact p-value |
| Causal: causal language for observational | Change "causes" to "associated with", add limitations |
| Causal: unblocked backdoor | Add confounder controls, update methods section |
| Figure: missing axis labels | Add labels with units to all figures |
| Figure: wrong color palette | Replace with Okabe-Ito palette |
| Code: no error handling | Add try/except blocks, input validation |
| Code: hardcoded paths | Replace with config-based paths |
| Quality gate: missing section | Draft the missing manuscript section |

---

## Validation

- [ ] All 5 audits executed
- [ ] Research map consistency checked
- [ ] Quality gate run and recorded
- [ ] Verdict assigned
- [ ] If FAIL/CONDITIONAL: auto-healing triggered
- [ ] Auto-healing loop: max 3 attempts
- [ ] Each attempt documented in research log
- [ ] Final status: PASS or documented dead end
- [ ] Dead end created if auto-healing exhausted
