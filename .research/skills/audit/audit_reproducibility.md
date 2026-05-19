---
skill_id: "audit_reproducibility"
version: "2.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "subprocess"]
estimated_tokens: 2500
depends_on: []
produces: ["reproducibility_audit.json"]
---

# Skill: Audit Reproducibility

## Purpose
Test cold-start reproducibility of the entire pipeline by verifying hashes and re-running scripts in a clean environment.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `script_paths` | List[Path] | Yes | Paths to execution scripts |
| `data_hashes` | Path | Yes | Original data hashes |

## Execution Protocol

### Step 1: Environment Validation
- Verify `requirements.txt` specifies exact versions

### Step 2: Hash Verification
- Recompute raw data hashes and compare to manifest

### Step 3: Cold-Start Execution
- Execute scripts in sequence and verify 0 exit codes

## Output Specification
- `reproducibility_audit.json`: Pass/fail metrics for reproducibility

## Validation Criteria
- [ ] Pipeline must execute from start to finish without manual intervention
- [ ] Hashes must match perfectly
