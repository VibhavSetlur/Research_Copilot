---
skill_id: "quality_gate"
version: "1.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python"]
depends_on: []
produces: ["docs/quality_gates/gate_XXX_[phase].md"]
complexity: "intermediate"
---

# Skill: Quality Gate Checks

## Purpose
Automated phase completion checks that prevent the pipeline from advancing until all requirements are met. Each phase has a checklist. The AI cannot proceed until the gate passes.

## When to Use
- After completing each pipeline phase
- Before moving to the next phase
- When the user asks "is this phase complete?"
- During audit to verify pipeline integrity

---

## Gate Definitions

### Gate 1: research_init
**File**: `docs/quality_gates/gate_001_research_init.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Intake form is filled (no `[Your answer]` placeholders) | ☐ | |
| 2 | At least one research question is defined | ☐ | |
| 3 | Data files exist in 00_inputs/raw_data/ | ☐ | |
| 4 | Data files are readable (correct format, not corrupted) | ☐ | |
| 5 | Research map is created (reports/baseline/research_map.json) | ☐ | |
| 6 | Feasibility verdict is assigned (go/caution/stop) | ☐ | |
| 7 | Full directory structure is created (docs/, reports/, data/, scripts/) | ☐ | |
| 8 | README.md exists in every subdirectory | ☐ | |
| 9 | manifest.json is created and valid | ☐ | |
| 10 | research_log.md has first entry | ☐ | |
| 11 | Iteration registry is created | ☐ | |
| 12 | Follow-up questions generated if needed | ☐ | |

**Pass criteria**: All required checks (1-7) pass. Warnings (8-12) noted but don't block.

### Gate 2: literature_deep
**File**: `docs/quality_gates/gate_002_literature_deep.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Literature corpus exists (reports/literature/literature_corpus.json) | ☐ | |
| 2 | Minimum paper count met (config: literature_min_papers, default 10) | ☐ | |
| 3 | Evidence matrix is created (reports/literature/evidence_matrix.md) | ☐ | |
| 4 | Each research question has mapped literature | ☐ | |
| 5 | Gap analysis is written | ☐ | |
| 6 | Papers are deduplicated | ☐ | |
| 7 | Citation information is complete (authors, year, title, DOI) | ☐ | |

**Pass criteria**: All checks pass. If paper count < minimum, gate fails with warning.

### Gate 3: method_route
**File**: `docs/quality_gates/gate_003_method_route.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Analysis plan exists (reports/analysis/analysis_plan.md) | ☐ | |
| 2 | Each research question has assigned method | ☐ | |
| 3 | Method is appropriate for question type | ☐ | |
| 4 | Assumptions are listed for each method | ☐ | |
| 5 | Power analysis is conducted (if applicable) | ☐ | |
| 6 | Alternative methods considered and documented | ☐ | |
| 7 | Multiple testing correction plan is specified | ☐ | |

**Pass criteria**: All checks pass. Method must be justified for each question type.

### Gate 4: data_scaffold
**File**: `docs/quality_gates/gate_004_data_scaffold.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Ingested data exists in data/01_ingested/ | ☐ | |
| 2 | Processed data exists in data/02_processed/ | ☐ | |
| 3 | Analytical datasets exist in data/03_analytical/ | ☐ | |
| 4 | Data lineage is recorded (docs/data_lineage.json) | ☐ | |
| 5 | Missingness is documented (< config: missingness_warning) | ☐ | |
| 6 | Outliers are identified and handled | ☐ | |
| 7 | Variable types are correct (numeric, categorical, etc.) | ☐ | |
| 8 | Analytical datasets have correct variables for each question | ☐ | |
| 9 | Data integrity check passes (raw hashes match) | ☐ | |

**Pass criteria**: All checks pass. Missingness > warning threshold requires documentation.

### Gate 5: execute_analysis
**File**: `docs/quality_gates/gate_005_execute_analysis.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Results exist for ALL research questions | ☐ | |
| 2 | Each result has effect size with confidence interval | ☐ | |
| 3 | Each result has p-value (exact, not thresholded) | ☐ | |
| 4 | Assumption checks are performed and documented | ☐ | |
| 5 | Non-significant results reported with same detail | ☐ | |
| 6 | Figures are generated for each question | ☐ | |
| 7 | Tables are generated for each question | ☐ | |
| 8 | Results are compared to prior literature | ☐ | |
| 9 | Sensitivity analysis is performed | ☐ | |
| 10 | Robustness checks are documented | ☐ | |

**Pass criteria**: All checks pass. Missing results for any question = gate fails.

### Gate 6: compile_outputs
**File**: `docs/quality_gates/gate_006_compile_outputs.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Manuscript draft exists (reports/manuscript/) | ☐ | |
| 2 | All required sections present (Intro, Methods, Results, Discussion, Limitations) | ☐ | |
| 3 | All figures referenced in manuscript | ☐ | |
| 4 | All tables referenced in manuscript | ☐ | |
| 5 | References are complete and formatted | ☐ | |
| 6 | Key findings summary exists (reports/summary/key_findings.md) | ☐ | |
| 7 | Executive summary exists (reports/summary/executive_summary.md) | ☐ | |
| 8 | Causal language audit passed (if causal analysis) | ☐ | |

**Pass criteria**: All checks pass. Missing sections = gate fails.

### Gate 7: audit_validate
**File**: `docs/quality_gates/gate_007_audit_validate.md`

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Full audit report exists (reports/audit/full_audit_report.md) | ☐ | |
| 2 | Statistical reporting audit passes | ☐ | |
| 3 | Reproducibility audit passes (scripts run end-to-end) | ☐ | |
| 4 | Code quality audit passes | ☐ | |
| 5 | Causal language audit passes (if applicable) | ☐ | |
| 6 | All previous gates passed | ☐ | |
| 7 | No unresolved follow-up questions | ☐ | |

**Pass criteria**: All checks pass. Any failed audit = gate fails.

---

## Gate Execution Protocol

### Step 1: Create Gate File
When a phase completes, create `docs/quality_gates/gate_XXX_[phase].md` with the checklist.

### Step 2: Evaluate Each Check
For each check:
- Mark ☑ if passed
- Mark ☐ if failed
- Add notes explaining why

### Step 3: Determine Gate Status
- **PASS**: All required checks passed
- **FAIL**: One or more required checks failed
- **WARN**: All required checks passed but warnings exist

### Step 4: Report to User
If gate fails:
1. List all failed checks
2. Explain what needs to be fixed
3. Do NOT proceed to next phase

If gate passes:
1. Confirm all checks passed
2. Note any warnings
3. Proceed to next phase

### Step 5: Record in Research Log
Append gate result to `docs/research_log.md`:
```markdown
### [Date] — Quality Gate: [phase]
- **Status**: PASS / FAIL / WARN
- **Checks**: X/Y passed
- **Failed**: [list if any]
- **Warnings**: [list if any]
```

---

## CLI Integration

`rcp status` — Run state and quality gate check.

---

## Validation Checklist
- [ ] Gate file created for the phase
- [ ] All checks evaluated with status
- [ ] Gate status determined (PASS/FAIL/WARN)
- [ ] Result recorded in research log
- [ ] User informed of gate status
- [ ] Pipeline blocked if gate fails
