#!/usr/bin/env python3
"""Adversarial 'Reviewer 2' Critic CLI command.

Reads research findings and explicitly tries to destroy the conclusions by
finding unaddressed confounders, alternative explanations, and methodological flaws.
"""

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
    }

    findings_lower = findings.lower()

    # Check for causal language without causal design
    causal_words = ["causes", "caused", "causal", "leads to", "results in", "drives", "determines"]
    if methodology and "randomized" not in methodology.lower() and "instrumental" not in methodology.lower():
        for word in causal_words:
            if word in findings_lower:
                critique["overclaiming_instances"].append(
                    f"Uses causal language ('{word}') without RCT or valid identification strategy"
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

    report_lines = [
        "# Reviewer 2 — Adversarial Critique Report",
        f"\n**Generated**: {now_iso()}",
        f"**Findings File**: {findings_path or 'reports/manuscript/research_findings.md'}",
        f"**Total Issues Found**: {total_issues}",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"This adversarial review identified **{total_issues} potential issues** across "
        f"{len(critique)} categories. Each issue represents a vulnerability that a "
        f"real reviewer could exploit to undermine the findings.",
        "",
    ]

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
        "categories": {k: len(v) for k, v in critique.items()},
        "critique": critique,
    }

    with open(json_path, "w") as f:
        json.dump(critique_json, f, indent=2, default=str)

    # Console output
    output = [
        f"🔍 **Reviewer 2 Adversarial Critique Complete**",
        f"",
        f"Total issues found: {total_issues}",
        f"",
    ]

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
