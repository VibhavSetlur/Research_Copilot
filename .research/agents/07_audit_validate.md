---
agent_id: "audit_validate"
version: "1.0.0"
description: "Cold-start reproducibility + reporting compliance audit (release gate)."
domain_compatibility: ["all"]
depends_on:
  - "compile_outputs"
composes:
  - "audit_reproducibility"
produces:
  - "reports/audit/validation_audit_report.md"
---

# Agent: Audit & Validate

## Purpose
Execute a full compliance and reproducibility audit as the release gate.

## Inputs
Entire repository.

## Execution Protocol
Execute the composed audit skills and emit a PASS/FAIL verdict.
