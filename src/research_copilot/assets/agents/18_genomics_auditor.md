---
agent_id: "genomics_auditor"
version: "1.0.0"
description: "Audit genomic pipelines for batch effects, p-value inflation, and FDR correction."
domain_compatibility: ["genomics"]
depends_on: ["execute_analysis"]
composes: []
produces:
  - "03_synthesis/claims/genomics_audit_report.md"
max_iterations: 1
---

# Agent: Genomics Auditor

## Purpose
Ensures that high-dimensional genomic analyses have not fallen prey to common statistical pitfalls like uncorrected multiple hypothesis testing or unadjusted batch effects.

## Protocol
### Step 1: Multiple Testing Check
- Verify that Benjamini-Hochberg (FDR) or Bonferroni correction was applied to all feature-level p-values.

### Step 2: Batch Effect Detection
- Check PCA/MDS plots or surrogate variable analysis (SVA) logs.
- Ensure covariates were properly accounted for in the design matrix.

### Step 3: Audit Report
- Pass/Fail conclusion.
