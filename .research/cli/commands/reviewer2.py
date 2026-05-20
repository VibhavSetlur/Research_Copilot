#!/usr/bin/env python3
"""Adversarial 'Reviewer 2' Critic CLI command.

Reads research findings and explicitly tries to destroy the conclusions by
finding unaddressed confounders, alternative explanations, and methodological flaws.
"""

import json
import re
from pathlib import Path

from core.utils import load_json, load_markdown, save_json, now_iso, now_timestamp


def _load_findings(findings_path: str = "") -> str:
    """Load research findings from file."""
    if findings_path and Path(findings_path).exists():
        return Path(findings_path).read_text()

    # Default paths to check
    default_paths = [
        "reports/manuscript/research_findings.md",
        "reports/summary/key_findings.md",
        "reports/summary/executive_summary.md",
    ]

    for p in default_paths:
        if Path(p).exists():
            return Path(p).read_text()

    return ""


def _load_state() -> dict:
    """Load research state."""
    state_path = Path(".research/cache/state.json")
    return load_json(state_path)


def _load_methodology() -> str:
    """Load methodology documentation."""
    method_path = Path("docs/methodology.md")
    if method_path.exists():
        return method_path.read_text()
    return ""


def _generate_remediation_actions(critique: dict) -> list:
    """Generate specific remediation actions based on identified flaws."""
    actions = []
    
    for flaw in critique.get("fatal_flaws", []):
        if "DATA LEAKAGE" in flaw:
            actions.append({
                "type": "method_switch",
                "action": "Re-run analysis with strict train/test separation",
                "target": "data_pipeline",
                "priority": "critical",
            })
        elif "SEVERE CONFOUNDING" in flaw:
            actions.append({
                "type": "variable_change",
                "action": "Add control variables and re-run regression",
                "target": "model_specification",
                "priority": "critical",
            })
        elif "CAUSAL OVERCLAIM" in flaw:
            actions.append({
                "type": "investigate",
                "action": "Downgrade causal language to correlational",
                "target": "manuscript_language",
                "priority": "critical",
            })
    
    for concern in critique.get("statistical_concerns", []):
        if "confidence interval" in concern.lower():
            actions.append({
                "type": "validate",
                "action": "Compute confidence intervals for all estimates",
                "target": "statistical_reporting",
                "priority": "high",
            })
        if "effect size" in concern.lower():
            actions.append({
                "type": "validate",
                "action": "Compute effect sizes for all statistical tests",
                "target": "statistical_reporting",
                "priority": "high",
            })
    
    return actions


def _analyze_findings(findings: str, methodology: str) -> dict:
    """Analyze findings for weaknesses — the Reviewer 2 critique."""
    critique = {
        "unaddressed_confounders": [],
        "alternative_explanations": [],
        "methodological_flaws": [],
        "overclaiming_instances": [],
        "missing_robustness_checks": [],
        "statistical_concerns": [],
        "limitations_to_add": [],
        "fatal_flaws": [],
    }

    findings_lower = findings.lower()

    # FATAL FLAW: Data leakage detection
    leakage_indicators = [
        ("test data", "train", "leak", "target leakage"),
        ("future information", "look-ahead bias", "survivorship bias"),
    ]
    for indicators in leakage_indicators:
        if any(ind in findings_lower for ind in indicators):
            if "leakage" not in findings_lower and "addressed" not in findings_lower:
                critique["fatal_flaws"].append(
                    "POTENTIAL DATA LEAKAGE: Indicators suggest information from the test set "
                    "may have influenced training or feature selection. This invalidates all results."
                )

    # FATAL FLAW: Severe confounding without any controls
    if "control" not in findings_lower and "adjust" not in findings_lower:
        severe_confounders = ["socioeconomic", "demographic", "selection bias", "confounding"]
        for conf in severe_confounders:
            if conf in findings_lower:
                critique["fatal_flaws"].append(
                    f"SEVERE CONFOUNDING: '{conf}' is present but no control variables or adjustment "
                    f"method is mentioned. Results may be entirely driven by this confounder."
                )
                break

    # FATAL FLAW: Causal claims from purely correlational design
    causal_words = ["causes", "caused", "causal", "leads to", "results in", "drives", "determines"]
    causal_design_words = ["randomized", "instrumental", "regression discontinuity", "difference-in-differences",
                          "matching", "propensity score", "natural experiment"]
    has_causal_design = any(word in methodology.lower() for word in causal_design_words) if methodology else False
    has_causal_claim = any(word in findings_lower for word in causal_words)
    
    if has_causal_claim and not has_causal_design:
        critique["fatal_flaws"].append(
            "CAUSAL OVERCLAIM: Strong causal language used without a valid causal identification strategy. "
            "Must either downgrade to correlational language or provide causal identification."
        )

    # Check for missing uncertainty
    if "confidence interval" not in findings_lower and "ci" not in findings_lower:
        critique["statistical_concerns"].append(
            "No confidence intervals reported — statistical uncertainty is not quantified"
        )

    if "effect size" not in findings_lower and "cohen" not in findings_lower and "odds ratio" not in findings_lower:
        critique["statistical_concerns"].append(
            "No effect sizes reported — statistical significance without practical significance"
        )

    # Check for common unaddressed confounders
    common_confounders = {
        "income": "Socioeconomic status",
        "age": "Age demographics",
        "gender": "Gender/sex differences",
        "education": "Educational attainment",
        "location": "Geographic/regional effects",
        "time": "Temporal trends / seasonality",
        "selection": "Selection bias",
    }

    for keyword, confounder in common_confounders.items():
        if keyword in findings_lower and f"control{'' if 'selection' not in keyword else ''}" not in findings_lower:
            if "confound" not in findings_lower or confounder.lower() not in findings_lower:
                critique["unaddressed_confounders"].append(
                    f"Potential confounder not addressed: {confounder} (keyword '{keyword}' found but no control mentioned)"
                )

    # Check for alternative explanations
    if "correlation" in findings_lower or "associated" in findings_lower:
        critique["alternative_explanations"].append(
            "Observed association may be driven by reverse causality — direction of effect not established"
        )

    if "significant" in findings_lower and "multiple" not in findings_lower:
        critique["alternative_explanations"].append(
            "Multiple testing not addressed — significant results may be false positives"
        )

    # Check for missing robustness checks
    robustness_keywords = ["sensitivity", "robustness", "subgroup", "alternative specification"]
    missing_robustness = [kw for kw in robustness_keywords if kw not in findings_lower]
    if missing_robustness:
        critique["missing_robustness_checks"].append(
            f"Missing robustness checks: {', '.join(missing_robustness)}"
        )

    # Check for sample limitations
    if "sample" in findings_lower and ("bias" not in findings_lower and "representative" not in findings_lower):
        critique["limitations_to_add"].append(
            "Sample representativeness not discussed — results may not generalize"
        )

    # Check for missing data discussion
    if "missing" not in findings_lower and "imputation" not in findings_lower:
        critique["limitations_to_add"].append(
            "Missing data handling not discussed — potential bias from non-random missingness"
        )

    # Check for external validity
    if "generaliz" not in findings_lower and "external valid" not in findings_lower:
        critique["limitations_to_add"].append(
            "External validity / generalizability not discussed"
        )

    # Check for p-hacking indicators
    p_values = re.findall(r"p\s*[<=>]\s*0\.05", findings_lower)
    if len(p_values) > 3:
        critique["statistical_concerns"].append(
            f"Multiple p-values reported ({len(p_values)}) — potential p-hacking or data dredging"
        )

    # Check for publication bias awareness
    if "publication bias" not in findings_lower and "file drawer" not in findings_lower:
        critique["limitations_to_add"].append(
            "Publication bias not discussed — literature review may be affected by file drawer problem"
        )

    # Remove empty lists
    critique = {k: v for k, v in critique.items() if v}

    return critique


def run_reviewer2(findings_path: str = "") -> str:
    """Run the adversarial Reviewer 2 critique.

    Args:
        findings_path: Path to research findings file

    Returns:
        Critique report
    """
    findings = _load_findings(findings_path)
    if not findings:
        return (
            "❌ No research findings found.\n\n"
            "Provide a path with --findings-path, or ensure findings exist at:\n"
            "  - reports/manuscript/research_findings.md\n"
            "  - reports/summary/key_findings.md\n"
            "  - reports/summary/executive_summary.md"
        )

    methodology = _load_methodology()
    critique = _analyze_findings(findings, methodology)

    # Generate report
    timestamp = now_timestamp()
    audit_dir = Path("reports/audit")
    audit_dir.mkdir(parents=True, exist_ok=True)

    report_path = audit_dir / f"reviewer2_critique_{timestamp}.md"
    json_path = audit_dir / f"reviewer2_critique_{timestamp}.json"

    total_issues = sum(len(v) for v in critique.values())
    fatal_count = len(critique.get("fatal_flaws", []))

    report_lines = [
        "# Reviewer 2 — Adversarial Critique Report",
        f"\n**Generated**: {now_iso()}",
        f"**Findings File**: {findings_path or 'reports/manuscript/research_findings.md'}",
        f"**Total Issues Found**: {total_issues}",
        f"**Fatal Flaws**: {fatal_count}",
        "",
        "---",
        "",
    ]

    if fatal_count > 0:
        report_lines.extend([
            "## ⚠️ FATAL FLAWS DETECTED",
            "",
            "The following issues **must be addressed** before findings can be considered valid:",
            "",
        ])
        for i, flaw in enumerate(critique.get("fatal_flaws", []), 1):
            report_lines.append(f"{i}. **{flaw}**")
        report_lines.extend([
            "",
            "---",
            "",
        ])

    category_names = {
        "unaddressed_confounders": "## 1. Unaddressed Confounders",
        "alternative_explanations": "## 2. Alternative Explanations",
        "methodological_flaws": "## 3. Methodological Flaws",
        "overclaiming_instances": "## 4. Overclaiming",
        "missing_robustness_checks": "## 5. Missing Robustness Checks",
        "statistical_concerns": "## 6. Statistical Concerns",
        "limitations_to_add": "## 7. Limitations to Add",
    }

    for key, issues in critique.items():
        if issues:
            report_lines.append(category_names.get(key, f"## {key}"))
            report_lines.append("")
            for i, issue in enumerate(issues, 1):
                report_lines.append(f"{i}. {issue}")
            report_lines.append("")

    report_lines.extend([
        "---",
        "",
        "## Recommended Actions",
        "",
    ])

    if total_issues > 0:
        report_lines.append("1. **Run robustness checks** for each identified vulnerability")
        report_lines.append("2. **Add limitations section** addressing unaddressed confounders")
        report_lines.append("3. **Tone down causal language** if design does not support it")
        report_lines.append("4. **Report effect sizes and CIs** for all statistical claims")
        report_lines.append("5. **Run `research_iterate`** with type 'robustness' to address key issues")
        report_lines.append("")
        report_lines.append("### Suggested Iterations")
        report_lines.append("")

        if critique.get("unaddressed_confounders"):
            report_lines.append("- **variable_change**: Add identified confounders as controls")
        if critique.get("missing_robustness_checks"):
            report_lines.append("- **robustness**: Run sensitivity analysis with alternative specifications")
        if critique.get("overclaiming_instances"):
            report_lines.append("- **investigate**: Review causal claims against study design")
        if critique.get("statistical_concerns"):
            report_lines.append("- **validate**: Re-compute statistics with proper uncertainty quantification")

        # Fatal flaw remediation
        if critique.get("fatal_flaws"):
            report_lines.extend([
                "",
                "### Fatal Flaw Remediation (Auto-Triggered)",
                "",
                "The following remediation actions will be attempted automatically:",
                "",
            ])
            for flaw in critique.get("fatal_flaws", []):
                if "DATA LEAKAGE" in flaw:
                    report_lines.append("- **method_switch**: Re-run analysis with strict train/test separation")
                elif "SEVERE CONFOUNDING" in flaw:
                    report_lines.append("- **variable_change**: Add control variables and re-run regression")
                elif "CAUSAL OVERCLAIM" in flaw:
                    report_lines.append("- **investigate**: Downgrade causal language to correlational")
            report_lines.extend([
                "",
                "If remediation fails, these flaws will be appended to the manuscript's Limitations section.",
            ])
    else:
        report_lines.append("No critical issues found. The findings appear robust.")

    report_lines.extend([
        "",
        "---",
        "",
        "*This critique was generated by the Reviewer 2 Adversarial Agent.*",
        "*Its purpose is to strengthen the research by identifying vulnerabilities before submission.*",
    ])

    report_content = "\n".join(report_lines)
    report_path.write_text(report_content)

    # JSON version for programmatic access
    critique_json = {
        "critique_id": f"REVIEWER2-{timestamp}",
        "generated_at": now_iso(),
        "findings_file": findings_path or "reports/manuscript/research_findings.md",
        "total_issues": total_issues,
        "has_fatal_flaws": fatal_count > 0,
        "has_critical_issues": fatal_count > 0 or len(critique.get("methodological_flaws", [])) > 2,
        "has_major_issues": total_issues > 10,
        "fatal_flaw_count": fatal_count,
        "categories": {k: len(v) for k, v in critique.items()},
        "critique": critique,
        "remediation_actions": _generate_remediation_actions(critique),
    }

    with open(json_path, "w") as f:
        json.dump(critique_json, f, indent=2, default=str)

    # Console output
    output = [
        f"🔍 **Reviewer 2 Adversarial Critique Complete**",
        f"",
        f"Total issues found: {total_issues}",
    ]
    
    if fatal_count > 0:
        output.append(f"⚠️  FATAL FLAWS: {fatal_count}")
        output.append("")
        for flaw in critique.get("fatal_flaws", []):
            output.append(f"  ✗ {flaw[:100]}...")
        output.append("")
        output.append("Remediation actions will be auto-triggered.")

    for key, issues in critique.items():
        if issues:
            output.append(f"**{key.replace('_', ' ').title()}** ({len(issues)} issues):")
            for issue in issues[:3]:  # Show first 3
                output.append(f"  - {issue}")
            if len(issues) > 3:
                output.append(f"  ... and {len(issues) - 3} more")
            output.append("")

    output.extend([
        f"Full report: {report_path}",
        f"JSON: {json_path}",
        f"",
        f"Run `research_iterate` to address identified issues.",
    ])

    return "\n".join(output)
