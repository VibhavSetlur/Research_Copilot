# Agent 06 — Audit and Validate

**Purpose:** Execute a full cold-start reproducibility sweep and compliance audit across all analytical, documentation, causal, and code-quality dimensions. This agent is the release gatekeeper. Nothing is published until this produces PASS.

---

## Prerequisites

Load `agents/00_core_guardrails.md` into context before executing.

## Trigger Command

```
Load agents/00_core_guardrails.md. Execute agents/06_audit_and_validate.md across the complete repository.
```

---

## Input Spec

The entire repository. No single input file required — this agent audits everything.

**Pre-audit check:** Verify `environment/env_manifest.json` exists and is non-empty. If not → halt, log ERROR.

---

## Action Mechanics

### Step 1 — Environment Reset & Verification

1. Delete all `__pycache__/`, `*.pyc`, `.pytest_cache/`, and `.ipynb_checkpoints/` directories and files.
2. Delete all intermediate outputs: `data/02_processed/`, `data/03_analytical/`, `reports/figures/`, `reports/tables/`, `reports/dashboards/analysis_app.py`.
3. Re-run `environment/setup_env.sh` from scratch.
4. After installation, compare every package version and hash in the new `env_manifest.json` against `environment/requirements.txt`. Any version mismatch or hash mismatch → audit FAIL.

### Step 2 — Cold Pipeline Execution

Run scripts in strict sequence. Do not skip any script even if prior steps are clean:

```bash
python scripts/01_validation.py
python scripts/02_transformation.py
python scripts/03_modeling.py
```

For each script:
- Capture stdout and stderr separately.
- Record exit code (0 = success).
- Record wall-clock execution time.
- Any non-zero exit code or uncaught exception → mark phase FAILED, log full stderr, halt.

### Step 3 — SHA-256 Hash Verification

Recompute SHA-256 hashes for all files in:
- `data/01_ingested/`
- `data/02_processed/`
- `data/03_analytical/`

Compare each against the value in `docs/data_dictionary.md`. Any mismatch → audit FAIL. Log file path, recorded hash, recomputed hash.

### Step 4 — Methods Log Coherence Check

For every `PIVOT` entry in `docs/methods_log.md`:
1. Verify the alternative method named in the pivot entry has a corresponding function call in `scripts/03_modeling.py`.
2. Verify the corresponding output file exists in `data/03_analytical/`.
3. Verify the pivot rationale cites a named publication (at minimum: Author, Year).

Any broken pivot → audit FAIL.

### Step 5 — Data Leakage & Causal Coherence Sweep

1. **Target Leakage:** Cross-reference every column classified as Outcome (Y) or Mediator (M) in `docs/data_dictionary.md` against the feature matrices built in `scripts/02_transformation.py` and `scripts/03_modeling.py`. Any Y or M appearing as a predictor → audit FAIL.
2. **Causal Language Coherence:** Scan `reports/research_findings.md` for causal language keywords ("caused", "impact of", "effect of", "led to"). For each occurrence, verify the corresponding RQ used a causal estimator (DiD, IV, matching, Double ML, or RCT) OR the language is appropriately hedged ("associated with", "correlates with"). Mismatch → audit FAIL.
3. **Propensity Score Validity (if matching used):** Verify post-matching SMD < 0.1 for all covariates is documented in `docs/methods_log.md`.

### Step 6 — Statistical Reporting Compliance Sweep

Scan all markdown files (`reports/research_findings.md`, `docs/methods_log.md`, all `docs/*.md`) for:

| Violation | Pattern to Detect | Severity |
|---|---|---|
| Unformatted p-value | `p=\d` or `p < 0.05` without test statistic | HIGH |
| Missing degrees of freedom | p-value present but no `(df)` notation | HIGH |
| Missing effect size | Test result without Cohen's d, η²_p, OR, HR, etc. | HIGH |
| Colloquial language | "Let's", "Now we'll", "clearly", "simply", "interesting" | MEDIUM |
| Unsupported causal claim | "X caused Y" without causal estimator in methods | HIGH |
| Missing CI on point estimate | β̂ or M reported without `95% CI [LL, UL]` | MEDIUM |

### Step 7 — Figure Compliance Check

For every research question, verify:
- `reports/figures/{rq_slug}_*.png` exists and is non-zero bytes.
- `reports/figures/{rq_slug}_*.html` exists and is non-zero bytes.
- `reports/figures/{rq_slug}_caption.txt` exists and contains all three parts (Title, Methods note, Interpretation).

Any missing figure or caption → audit FAIL.

### Step 8 — Docstring & Code Quality Audit

Scan every `.py` file in `scripts/`:
- Every function must have a docstring with all four sections: `Parameters`, `Returns`, `Raises`, `Notes`.
- Every function must have type hints on all arguments and the return value.
- Report coverage percentage per file.
- Scan for any `print()` statements (should be `logging`). Flag as MEDIUM severity.

### Step 9 — Dashboard Execution Check

Execute the dashboard in headless/test mode to confirm it starts without errors:

```bash
# marimo
marimo run reports/dashboards/analysis_app.py --headless || exit 1

# panel (fallback)
timeout 30 panel serve reports/dashboards/analysis_app.py &
sleep 10
curl -s http://localhost:5006/ | grep -q "html" || exit 1
```

Any startup error → audit FAIL.

---

## Output Spec

Write `docs/validation_audit_report.md`:

```markdown
# Validation Audit Report
Generated: {ISO 8601}
Auditor: 06_audit_and_validate.md
Environment: Python {version} on {platform}

## 1. Environment Verification
| Package | Required Version | Installed Version | Hash Match | Status |
|---------|-----------------|------------------|------------|--------|

## 2. Pipeline Execution
| Script | Exit Code | Duration (s) | stdout (first 500 chars) | Status |
|--------|-----------|--------------|--------------------------|--------|

## 3. Hash Verification
| File | Recorded Hash (first 12) | Recomputed Hash (first 12) | Match | Status |
|------|--------------------------|---------------------------|-------|--------|

## 4. Methods Log Coherence
| Timestamp | RQ | Pivot Alternative | Code Found | Output Exists | Citation Present | Status |
|-----------|----|--------------------|------------|---------------|------------------|--------|

## 5. Data Leakage & Causal Coherence
| Check | Variable / Claim | Finding | Status |
|-------|-----------------|---------|--------|

## 6. Statistical Reporting Compliance
| File | Line | Violation Type | Exact Text | Severity | Status |
|------|------|---------------|------------|----------|--------|

## 7. Figure Completeness
| RQ | PNG | HTML | Caption | Status |
|----|-----|------|---------|--------|

## 8. Code Quality
| Script | Functions Total | Docstring Coverage | Type Hint Coverage | print() Count | Status |
|--------|----------------|-------------------|-------------------|---------------|--------|

## 9. Dashboard Execution
Status: PASS | FAIL
Error (if any): {message}

## Final Verdict
**PASS** | **FAIL**

## Required Remediation Steps
{Numbered, file-path-specific actionable fixes — present only if FAIL}
```

**Release gate:** The repository must not be shared, published, deposited in a data repository, or used to inform any policy or clinical decision until this agent produces `Final Verdict: PASS`.
