---
skill_id: "audit_figure_completeness"
version: "2.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "os", "re"]
estimated_tokens: 2500
depends_on: ["write_imrad"]
produces: ["figure_completeness_report.json"]
---

# Skill: Audit Figure Completeness

## Purpose
Verify that all figures referenced in text exist and have appropriate captions.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `manuscript_path` | Path | Yes | Path to manuscript |
| `figures_dir` | Path | Yes | Path to figures directory |

## Execution Protocol

### Step 1: Reference Extraction
- Extract all 'Figure X' references from manuscript

### Step 2: File Verification
- Check that `figures_dir` contains files corresponding to each reference

### Step 3: Caption Check
- Ensure every figure has a descriptive caption in the markdown

## Output Specification
- Mapping of references to files

## Validation Criteria
- [ ] Every referenced figure must physically exist
- [ ] Every figure file must be referenced at least once in text
