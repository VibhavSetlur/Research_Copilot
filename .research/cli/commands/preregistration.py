#!/usr/bin/env python3
"""OSF Pre-Registration Generator CLI command.

Generates a timestamped, OSF-compatible pre-registration document detailing
hypotheses, power analysis, and exact statistical tests before analysis begins.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def _load_state() -> dict:
    """Load the research state ledger."""
    state_path = Path(".research/cache/state.json")
    if state_path.exists():
        with open(state_path) as f:
            return json.load(f)
    return {}


def _load_research_map() -> dict:
    """Load the research map."""
    map_path = Path(".research/cache/research_map.json")
    if map_path.exists():
        with open(map_path) as f:
            return json.load(f)
    return {}


def _load_intake() -> dict:
    """Parse intake.md for key information."""
    intake_path = Path("inputs/intake.md")
    if not intake_path.exists():
        return {}

    content = intake_path.read_text()
    info = {}

    for line in content.split("\n"):
        if "**Project title**" in line:
            info["title"] = line.split("**Project title**: ")[-1].strip()
        elif "**Primary research question**" in line:
            info["research_question"] = line.split("**Primary research question**: ")[-1].strip()
        elif "**Outcome variable**" in line:
            info["outcome"] = line.split("**Outcome variable**: ")[-1].strip()
        elif "**Key predictors**" in line:
            info["predictors"] = line.split("**Key predictors**: ")[-1].strip()
        elif "**Hypothesis**" in line:
            info["hypothesis"] = line.split("**Hypothesis**: ")[-1].strip()
        elif "**Domain**" in line:
            info["domain"] = line.split("**Domain**: ")[-1].strip()

    return info


def generate_preregistration(hypotheses: list = None, analysis_plan: str = "") -> str:
    """Generate an OSF-compatible pre-registration document.

    Args:
        hypotheses: List of hypotheses to pre-register (overrides intake)
        analysis_plan: Path to analysis plan file

    Returns:
        Path to generated pre-registration document
    """
    state = _load_state()
    intake = _load_intake()
    research_map = _load_research_map()

    # Output directory
    prereg_dir = Path("reports/literature")
    prereg_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    prereg_path = prereg_dir / f"preregistration_{timestamp}.md"
    prereg_json_path = prereg_dir / f"preregistration_{timestamp}.json"

    # Gather hypotheses
    if hypotheses:
        hyp_list = hypotheses
    elif intake.get("hypothesis"):
        hyp_list = [intake["hypothesis"]]
    else:
        hyp_list = ["[HYPOTHESIS TO BE SPECIFIED]"]

    # Gather data info
    data_files = research_map.get("data_files", [])
    data_summary = []
    for f in data_files:
        data_summary.append(f"- `{f.get('name', 'unknown')}`: {f.get('rows', '?')} rows, {f.get('columns', '?')} columns")

    # Power analysis placeholder
    power_info = (
        "Power analysis will be computed during the data_scaffold phase.\n"
        "Target power: 0.80 (80%)\n"
        "Minimum acceptable power: 0.50 (50%)\n"
        "Effect size estimation: Will be derived from literature review and pilot data."
    )

    # Statistical tests placeholder
    tests_info = (
        "Statistical tests will be selected during the method_route phase.\n"
        "Selection criteria:\n"
        "  1. Outcome variable type (continuous, binary, count, time-to-event)\n"
        "  2. Research design (RCT, observational, quasi-experimental)\n"
        "  3. Assumption compliance (normality, homoskedasticity, independence)\n"
        "  4. Sample size adequacy\n"
        "All tests will be two-tailed with alpha = 0.05 unless justified otherwise."
    )

    # Read analysis plan if provided
    analysis_plan_content = ""
    if analysis_plan and Path(analysis_plan).exists():
        analysis_plan_content = Path(analysis_plan).read_text()

    # Generate the pre-registration document
    prereg_content = f"""# Pre-Registration Document

**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Project**: {intake.get('title', state.get('project', 'Research Copilot Project'))}
**Schema Version**: OSF Preregistration Template v2.0
**Pre-Registration ID**: PREREG-{timestamp}

---

## 1. Research Questions

### Primary Research Question
{intake.get('research_question', '[NOT SPECIFIED]')}

### Secondary Research Questions
[To be specified during method_route phase]

---

## 2. Hypotheses

"""

    for i, hyp in enumerate(hyp_list, 1):
        prereg_content += f"""### Hypothesis {i}
{hyp}

"""

    prereg_content += f"""---

## 3. Study Design

### Design Type
{intake.get('domain', 'Observational study — design type to be confirmed during method_route')}

### Data Source
{chr(10).join(data_summary) if data_summary else 'Data files to be identified during research_init phase'}

### Sample
Sample characteristics will be documented during the data_scaffold phase.

---

## 4. Variables

### Outcome Variable
{intake.get('outcome', '[TO BE SPECIFIED]')}

### Key Predictors
{intake.get('predictors', '[TO BE SPECIFIED]')}

### Control Variables
Control variables will be identified during method_route based on:
1. Prior literature confounders
2. Domain-specific known confounders
3. Data availability

---

## 5. Power Analysis

{power_info}

---

## 6. Statistical Analysis Plan

{tests_info}

### Analysis Plan Details
{analysis_plan_content if analysis_plan_content else 'Detailed analysis plan will be generated during method_route phase.'}

### Robustness Checks
The following robustness checks will be performed:
1. Alternative model specifications
2. Subgroup analysis (where sample size permits)
3. Sensitivity to outliers and influential observations
4. Alternative functional forms

---

## 7. Exclusion Criteria

Data exclusion criteria will be documented during data_scaffold phase.
No data will be excluded without documented justification.

---

## 8. Missing Data

Missing data handling will be specified during data_scaffold phase.
Options include:
- Complete case analysis (if missingness < 5%)
- Multiple imputation (if missingness is MAR)
- Sensitivity analysis for MNAR

---

## 9. Reproducibility

All analysis will be conducted using:
- Numbered scripts in `scripts/` directory
- Version-controlled dependencies in `environment/requirements.txt`
- Data pipeline: raw → ingested → processed → analytical
- Execution DAG tracked in `.research/cache/execution_dag.json`

---

## 10. Deviations from Pre-Registration

Any deviations from this pre-registration will be:
1. Documented in `docs/changelog.md`
2. Justified methodologically
3. Reported transparently in the final manuscript

---

## 11. Significance Criteria

- Primary tests: two-tailed, alpha = 0.05
- Multiple comparison corrections: Bonferroni or FDR as appropriate
- Effect sizes will be reported with 95% confidence intervals
- Both statistical and practical significance will be evaluated

---

## 12. Timeline

| Phase | Status |
|-------|--------|
| research_init | {state.get('checkpoints', {}).get('research_init', 'pending')} |
| literature_deep | {state.get('checkpoints', {}).get('literature_deep', 'pending')} |
| method_route | {state.get('checkpoints', {}).get('method_route', 'pending')} |
| data_scaffold | {state.get('checkpoints', {}).get('data_scaffold', 'pending')} |
| execute_analysis | {state.get('checkpoints', {}).get('execute_analysis', 'pending')} |
| compile_outputs | {state.get('checkpoints', {}).get('compile_outputs', 'pending')} |
| audit_validate | {state.get('checkpoints', {}).get('audit_validate', 'pending')} |

---

*This pre-registration was generated automatically by Research Copilot.
It is timestamped and intended for submission to the Open Science Framework (OSF).*
*Any modifications after this point must be documented as deviations.*
"""

    # Write the markdown file
    prereg_path.write_text(prereg_content)

    # Write the JSON metadata
    prereg_json = {
        "preregistration_id": f"PREREG-{timestamp}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": intake.get("title", state.get("project", "")),
        "research_question": intake.get("research_question", ""),
        "hypotheses": hyp_list,
        "outcome_variable": intake.get("outcome", ""),
        "key_predictors": intake.get("predictors", ""),
        "domain": intake.get("domain", ""),
        "data_files": [f.get("name", "") for f in data_files],
        "power_target": 0.80,
        "alpha": 0.05,
        "two_tailed": True,
        "markdown_path": str(prereg_path),
        "osf_compatible": True,
    }

    with open(prereg_json_path, "w") as f:
        json.dump(prereg_json, f, indent=2)

    return (
        f"✅ Pre-registration generated:\n\n"
        f"  Markdown: {prereg_path}\n"
        f"  JSON: {prereg_json_path}\n\n"
        f"This document is OSF-compatible and timestamped.\n"
        f"Submit to https://osf.io/prereg/ before beginning analysis."
    )
