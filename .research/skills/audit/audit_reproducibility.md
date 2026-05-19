---
skill_id: "audit_reproducibility"
version: "7.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "hashlib", "subprocess"]
depends_on: ["compute_hashes"]
produces: ["audit/reproducibility_audit.json"]
complexity: "intermediate"
---

# Skill: Reproducibility Audit

## Purpose
Verify that the entire research pipeline can be reproduced from raw data to final results in a clean environment.

## When to Use
- After all analysis completed
- Before finalizing manuscript
- For submission to reproducible research journals

## When NOT to Use
- Analysis still in progress
- Data not yet finalized

## Execution Protocol

### Step 1: Environment Documentation
- Record: Python version, OS, all package versions (pip freeze)
- Verify: requirements.txt or environment.yml specifies exact versions
- Check: no system-level dependencies (all pip-installable)

### Step 2: Data Integrity
- Recompute SHA-256 hashes for all raw data files
- Compare to hash manifest from compute_hashes
- Flag: any file with mismatched hash (modified or corrupted)

### Step 3: Script Execution
- In a clean environment (new virtualenv or container):
  - Install dependencies from requirements.txt
  - Run each analysis script in dependency order
  - Record: exit code, execution time, warnings
- Verify: all scripts exit with code 0

### Step 4: Output Verification
- Compare regenerated outputs to original outputs
- Numerical tolerance: results within 1e-6 of original (floating-point variation acceptable)
- Exact match: tables, figures (pixel-perfect for figures may not be possible)
- Flag: any output that differs beyond tolerance

### Step 5: Documentation Completeness
- Check: README explains how to reproduce
- Check: data availability statement included
- Check: code repository link provided
- Check: analysis pipeline documented (workflow DAG)

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| Hash match | All files unchanged | Investigate modification; restore from backup |
| Script execution | All exit 0 | Debug failing script |
| Output match | Within tolerance | Check for non-deterministic operations |
| Documentation | Complete | Fill gaps before submission |

## Output Specification
- `audit/reproducibility_audit.json`: pass/fail per check, details of failures, environment snapshot

## Validation Checks
- [ ] All data hashes verified
- [ ] All scripts execute successfully
- [ ] Outputs match within tolerance
- [ ] Documentation complete
