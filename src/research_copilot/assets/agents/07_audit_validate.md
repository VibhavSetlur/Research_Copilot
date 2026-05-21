---
agent_id: "audit_validate"
version: "13.0.0"
description: "Multi-dimensional audit with auto-healing loop: reproducibility, reporting, causal language, completeness, citation verification, claim tracing, visualization standards, code quality"
domain_compatibility: ["all"]
depends_on: ["compile_outputs"]
composes:
  - "audit_reproducibility"
  - "audit_statistical_reporting"
  - "audit_causal_language"
  - "audit_figure_completeness"
  - "audit_code_quality"
  - "audit_citations"
  - "audit_claim_trace"
  - "audit_visualizations"
  - "quality_gate"
produces:
  - "reports/audit/full_audit_report.md"
  - "reports/audit/reproducibility_audit.json"
  - "reports/audit/statistical_reporting_audit.json"
  - "reports/audit/causal_language_audit.json"
  - "reports/audit/figure_completeness_audit.json"
  - "reports/audit/code_quality_audit.json"
  - "reports/literature/citation_verification_report.json"
  - "reports/audit/claim_trace_report.json"
  - "reports/audit/visualization_audit.json"
  - "docs/quality_gates/gate_007_audit_validate.md"
max_iterations: 3
---

# Agent: Audit & Validate

## Purpose
Run 7 audits. Produce pass/fail verdict with remediation steps. If FAIL or CONDITIONAL, AUTO-HEAL: trigger research_iterate with failures, fix issues, re-validate. Loop up to 3 times.

---

## Protocol

### Step 1: Run All 8 Audits
- `audit_reproducibility`: cold-start reproduction
- `audit_statistical_reporting`: every test has stat, df, p, effect size, CI
- `audit_causal_language`: claims match study design
- `audit_figure_completeness`: all referenced figures/tables exist and meet standards
- `audit_code_quality`: style, reproducibility, error handling
- `audit_citations`: three-pass citation verification (existence, content, retraction)
- `audit_claim_trace`: every claim traced to data or verified citation
- `audit_visualizations`: DPI, colorblind safety, axis labels, font sizes

### Step 2: Run Citation Verification (Audit #6)
Execute the three-pass citation verification pipeline:
1. Run `python .research/scripts/utils/citation_verifier.py --bibliography reports/literature/bibliography.bib --corpus reports/literature/literature_corpus.json`
2. If bibliography doesn't exist, extract DOIs from manuscript: `--manuscript reports/manuscript/research_findings.md`
3. Review `reports/literature/citation_verification_report.json`
4. **FAIL if:** any citation is retracted, or >10% are unverified
5. **CONDITIONAL if:** some citations are partial_match
6. Remove any retracted citations from the manuscript immediately

### Step 3: Run Claim Tracer (Audit #7)
Execute the claim-to-evidence graph builder:
1. Run `python .research/scripts/utils/claim_tracer.py --manuscript reports/manuscript/research_findings.md --data-lineage docs/data_lineage.json --citation-report reports/literature/citation_verification_report.json`
2. Review `reports/audit/claim_trace_report.json`
3. **FAIL if:** any claim is unsupported
4. **CONDITIONAL if:** any claim is partially traced
5. For each unsupported claim: either find a trace or remove from manuscript

### Step 3b: Run Visualization Audit (Audit #8)
Execute automated figure validation:
1. Run `python .research/scripts/utils/figure_validator.py --directory reports/figures/`
2. Review `reports/audit/visualization_audit.json`
3. **FAIL if:** any figure below 300 DPI, not colorblind-safe, or missing axis labels
4. **CONDITIONAL if:** figures have warnings (font size, file size)
5. For failed figures: re-render with corrected parameters

### Step 4: Check Research Map Consistency
- Every research question has results in manuscript
- Every literature claim cites a paper from the corpus
- No orphan claims (untraceable to research map, data, or literature)

### Step 4b: Container & Runtime Reproducibility
- Record container image IDs or digests for each runtime
- Log non-Python tool versions (R, Bioconductor, FSL, GATK, etc.) in `env_manifest.json`

### Step 4c: Domain Sanity Checks
- Run domain-specific sanity checks (e.g., RNA-seq DE gene counts not 0% or 100%)
- Flag implausible outputs with remediation steps

### Step 5: Run Quality Gate
Run `research validate audit_validate`. Record results in `docs/quality_gates/gate_007_audit_validate.md`.

### Step 6: Verdict
**PASS**: all 8 audits pass, quality gate passes
**CONDITIONAL**: minor issues with clear remediation plan (formatting, missing labels, incomplete references, partial claim traces, figure warnings)
**FAIL**: critical issues (reproducibility failure, causal overclaim, unanswered research question, retracted citation, unsupported claim, figure below standard, quality gate FAIL)

### Step 7: Auto-Healing Loop
If verdict is FAIL or CONDITIONAL:

1. **Create remediation brief** — List every failure with specific fix instructions
2. **Trigger research_iterate** with type `validate` and the remediation brief
3. **research_iterate fixes the issues** — Rewrites code, updates figures, corrects manuscript
4. **Re-run audit** — Execute steps 1-6 again
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

### Step 8: Document Dead Ends
If auto-healing fails after max attempts, document in `docs/dead_ends/`:
- What was tried
- What failures persisted
- What manual intervention is needed
- Why automated fixes couldn't resolve it

### Step 9: Report
`full_audit_report.md`: verdict, per-audit results (all 8 audits), auto-healing attempts, final status.

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
| Citation: DOI returns 404 | Search CrossRef by title+author, find correct DOI, update bibliography |
| Citation: content mismatch | Remove citation from claim, flag for manual replacement |
| Citation: retracted paper | Remove citation from manuscript entirely, find replacement |
| Citation: unverified | Tag as [UNVERIFIED] or find alternative verified source |
| Claim: no trace | Search analysis outputs for supporting data, or flag as UNSUPPORTED |
| Claim: data hash mismatch | Re-run analysis pipeline, regenerate claim with fresh data |
| Figure: below 300 DPI | Re-render at 300 DPI using saved figure parameters |
| Figure: colorblind palette violation | Re-render with Okabe-Ito substitution |
| Figure: missing confidence intervals | Re-render with CI bands or error bars |
| Figure: rainbow/jet colormap | Re-render with viridis or perceptually uniform palette |
| LaTeX: compilation error | Auto-debug with traceback, fix encoding/special character issues |
| Visualization: font size below 8pt | Re-render with larger fonts |
| Visualization: file size > 5MB | Optimize image compression, reduce resolution for web |

---

## Validation

- [ ] All 8 audits executed
- [ ] Citation verification report generated (Audit #6)
- [ ] Claim trace report generated (Audit #7)
- [ ] Visualization audit report generated (Audit #8)
- [ ] Research map consistency checked
- [ ] Quality gate run and recorded
- [ ] Verdict assigned
- [ ] If FAIL/CONDITIONAL: auto-healing triggered
- [ ] Auto-healing loop: max 3 attempts
- [ ] Each attempt documented in research log
- [ ] Final status: PASS or documented dead end
- [ ] Dead end created if auto-healing exhausted
