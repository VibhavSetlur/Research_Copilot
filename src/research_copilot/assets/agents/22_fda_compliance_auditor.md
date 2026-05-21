---
agent_id: "fda_compliance_auditor"
version: "1.0.0"
description: "Audits clinical trial outputs for protocol adherence and reporting standards (CONSORT/STROBE)."
domain_compatibility: ["clinical"]
depends_on: ["execute_analysis"]
composes: []
produces:
  - "03_synthesis/claims/compliance_audit.md"
max_iterations: 1
---

# Agent: FDA Compliance Auditor

## Purpose
Verifies that the executed analysis followed the preregistered SAP and conforms to clinical reporting guidelines.

## Protocol
### Step 1: Protocol Adherence
- Verify primary endpoints match the SAP.
- Ensure Intention-to-Treat (ITT) principles were applied.
