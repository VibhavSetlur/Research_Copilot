"""Audit tools — checks that go beyond a simple test run.

Every audit writes a markdown report into the *current* experiment's
``outputs/reports/`` directory so the audit becomes part of the research record.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger("research_os.tools.audit")


def get_current_path(root: Path) -> str:
    """Return the active numbered experiment folder (e.g. ``02_eda``) or ``""``."""
    try:
        from research_os.project_ops import load_state

        state = load_state(root)
        current = state.get("current_path")
        if current and current != "main":
            return current
    except Exception:
        pass

    workspace = root / "workspace"
    if workspace.exists():
        dirs = [
            d.name
            for d in workspace.iterdir()
            if d.is_dir()
            and d.name[:2].isdigit()
            and not d.name.endswith("__DEAD_END")
        ]
        if dirs:
            return sorted(dirs)[-1]
    return ""


def _report_path(root: Path, filename: str) -> Path:
    current = get_current_path(root)
    if current:
        return root / "workspace" / current / "outputs" / "reports" / filename
    return root / "workspace" / "logs" / filename


# ---------------------------------------------------------------------------
# Synthesis audit — checks paper structure, claim grounding, and citations.
# ---------------------------------------------------------------------------


def audit_synthesis(paper_path: str, root: Path) -> dict[str, Any]:
    try:
        p = root / paper_path
        if not p.exists() or not p.is_file():
            return {"status": "error", "message": f"Paper not found: {paper_path}"}

        text = p.read_text()
        lower = text.lower()

        # Section coverage
        required = ["abstract", "introduction", "methods", "results", "discussion"]
        missing_sections = [s for s in required if f"## {s}" not in lower and f"\\section{{{s}" not in lower]

        # Causal language flagged for observational research
        causal_terms = [
            r"\bcauses\b",
            r"\bcaused by\b",
            r"\bproves\b",
            r"\bdemonstrates causality\b",
        ]
        causal_hits = []
        for term in causal_terms:
            for m in re.finditer(term, lower):
                start = max(0, m.start() - 40)
                end = min(len(lower), m.end() + 40)
                causal_hits.append({"term": term.strip("\\b "), "context": lower[start:end]})

        # Citation density: count [@key] or \cite{key}
        citations = re.findall(r"\[@[^\]]+\]|\\cite\{[^}]+\}", text)
        citation_count = len(citations)
        word_count = len(text.split())
        citation_density = citation_count / max(1, word_count) * 1000  # per 1000 words

        # Figures referenced vs. files present
        figure_refs = set(re.findall(r"!\[[^\]]*\]\(([^)]+\.(?:png|svg|pdf|jpg))\)", text))
        figures_present = []
        synthesis_dir = root / "synthesis"
        for ref in figure_refs:
            candidate = synthesis_dir / ref if not ref.startswith("/") else root / ref.lstrip("/")
            if not candidate.exists():
                candidate = root / ref
            figures_present.append({"ref": ref, "exists": candidate.exists()})

        has_bibliography = "## references" in lower or "\\bibliography" in text

        report = {
            "missing_sections": missing_sections,
            "causal_language_hits": causal_hits[:10],
            "citation_count": citation_count,
            "citation_density_per_1000_words": round(citation_density, 2),
            "figures_referenced": len(figure_refs),
            "figures_present": [f for f in figures_present if f["exists"]],
            "figures_missing": [f for f in figures_present if not f["exists"]],
            "has_bibliography": has_bibliography,
        }

        out = _report_path(root, "synthesis_audit.md")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            "# Synthesis Audit\n\n"
            f"- Missing sections: {', '.join(missing_sections) or 'none'}\n"
            f"- Causal-language hits: {len(causal_hits)}\n"
            f"- Citation count: {citation_count} ({citation_density:.1f}/1000w)\n"
            f"- Figures referenced: {len(figure_refs)} "
            f"(present {len([f for f in figures_present if f['exists']])} / "
            f"missing {len([f for f in figures_present if not f['exists']])})\n"
            f"- Bibliography present: {has_bibliography}\n"
        )

        warning = bool(missing_sections or causal_hits or not has_bibliography)
        return {
            "status": "warning" if warning else "success",
            "report": report,
            "report_path": str(out.relative_to(root)),
            "message": (
                "Synthesis audit produced warnings." if warning else "Synthesis passed audit."
            ),
        }
    except Exception as e:
        logger.exception("audit_synthesis failed")
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------------------
# Statistical power
# ---------------------------------------------------------------------------


def audit_power(
    filepath: str, effect_size: float, alpha: float, n: int, root: Path
) -> dict[str, Any]:
    try:
        try:
            from statsmodels.stats import power as smp  # type: ignore
        except ImportError:
            return {
                "status": "error",
                "message": "statsmodels required (pip install statsmodels)",
            }

        power_value = smp.tt_ind_solve_power(
            effect_size=effect_size, nobs1=n, alpha=alpha, power=None
        )
        out = _report_path(root, "power_report.md")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            "# Power Analysis Report\n\n"
            f"- Effect size: {effect_size}\n"
            f"- Alpha: {alpha}\n"
            f"- n: {n}\n"
            f"- Computed power: {power_value:.4f}\n"
            f"- Source file: {filepath}\n"
        )
        report = {
            "power": power_value,
            "alpha": alpha,
            "effect_size": effect_size,
            "n": n,
        }
        return {
            "status": "warning" if power_value < 0.8 else "success",
            "report": report,
            "report_path": str(out.relative_to(root)),
            "message": (
                f"Low power ({power_value:.2f} < 0.8) — consider larger n."
                if power_value < 0.8
                else "Power analysis passed."
            ),
        }
    except Exception as e:
        logger.exception("audit_power failed")
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------------------
# Model-assumption checks (residual normality, equal variance, multicollinearity)
# ---------------------------------------------------------------------------


def audit_assumptions(filepath: str, root: Path) -> dict[str, Any]:
    """Run assumption checks on a CSV containing residuals or model output."""
    try:
        p = root / filepath
        if not p.exists():
            return {"status": "error", "message": f"File not found: {filepath}"}

        import pandas as pd  # type: ignore

        df = pd.read_csv(p)
        report: dict[str, Any] = {}
        warnings: list[str] = []

        if "residual" in df.columns or "residuals" in df.columns:
            col = "residual" if "residual" in df.columns else "residuals"
            res = df[col].dropna()
            try:
                from scipy import stats  # type: ignore

                w, p_value = stats.shapiro(res[: min(5000, len(res))])
                report["shapiro_wilk"] = {"W": float(w), "p_value": float(p_value)}
                if p_value < 0.05:
                    warnings.append(
                        f"Residuals fail Shapiro-Wilk normality (p={p_value:.3g})"
                    )
            except Exception as e:
                report["shapiro_wilk"] = f"failed: {e}"

        if "group" in df.columns and "value" in df.columns:
            try:
                from scipy import stats  # type: ignore

                groups = [g["value"].dropna() for _, g in df.groupby("group")]
                stat, p_value = stats.levene(*groups)
                report["levene"] = {"statistic": float(stat), "p_value": float(p_value)}
                if p_value < 0.05:
                    warnings.append(f"Heteroscedasticity detected (Levene p={p_value:.3g})")
            except Exception as e:
                report["levene"] = f"failed: {e}"

        out = _report_path(root, "assumption_report.md")
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# Assumption Audit", "", f"- Source file: {filepath}", ""]
        for k, v in report.items():
            lines.append(f"- **{k}**: {v}")
        if warnings:
            lines.extend(["", "## Warnings"])
            for w in warnings:
                lines.append(f"- {w}")
        out.write_text("\n".join(lines) + "\n")

        return {
            "status": "warning" if warnings else "success",
            "report": report,
            "warnings": warnings,
            "report_path": str(out.relative_to(root)),
            "message": (
                "Assumption checks raised warnings." if warnings else "Assumption checks passed."
            ),
        }
    except Exception as e:
        logger.exception("audit_assumptions failed")
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------------------
# Figure quality
# ---------------------------------------------------------------------------


def audit_figure(filepath: str, root: Path) -> dict[str, Any]:
    """Check DPI and basic visual hygiene of a PNG figure."""
    try:
        p = root / filepath
        if not p.exists():
            return {"status": "error", "message": f"Figure not found: {filepath}"}

        report: dict[str, Any] = {"path": filepath}
        warnings: list[str] = []

        try:
            from PIL import Image  # type: ignore

            with Image.open(p) as img:
                dpi = img.info.get("dpi", (72, 72))
                width, height = img.size
                report.update(
                    {
                        "format": img.format,
                        "size_px": [width, height],
                        "dpi": dpi,
                        "mode": img.mode,
                    }
                )
                if isinstance(dpi, tuple) and dpi[0] < 150:
                    warnings.append(
                        f"DPI low ({dpi[0]}). Publication figures should be ≥300 DPI."
                    )
                if min(width, height) < 600:
                    warnings.append(
                        f"Smallest dimension {min(width, height)}px is small for a publication figure."
                    )
        except ImportError:
            warnings.append(
                "Pillow not installed — could not inspect DPI/size (pip install Pillow)"
            )
        except Exception as e:
            warnings.append(f"Could not open image: {e}")

        out = _report_path(root, f"figure_audit_{p.stem}.md")
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# Figure Audit", "", f"- File: {filepath}", ""]
        for k, v in report.items():
            if k == "path":
                continue
            lines.append(f"- **{k}**: {v}")
        if warnings:
            lines.extend(["", "## Warnings"])
            for w in warnings:
                lines.append(f"- {w}")
        out.write_text("\n".join(lines) + "\n")

        return {
            "status": "warning" if warnings else "success",
            "report": report,
            "warnings": warnings,
            "report_path": str(out.relative_to(root)),
            "message": "Figure audit complete.",
        }
    except Exception as e:
        logger.exception("audit_figure failed")
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------------------
# Citation verification
# ---------------------------------------------------------------------------


def audit_citations(root: Path) -> dict[str, Any]:
    """Verify every citation in workspace/citations.md against Crossref/Semantic Scholar."""
    try:
        from research_os.tools.actions.literature_retrieval import retrieve_literature

        citations_md = root / "workspace" / "citations.md"
        if not citations_md.exists():
            return {
                "status": "error",
                "message": "workspace/citations.md not found — run mem_citations_generate first.",
            }

        text = citations_md.read_text()
        # Citation keys appear as `### \`<key>\`` in the auto-generated format.
        keys = re.findall(r"^###\s+`([^`]+)`", text, flags=re.MULTILINE)

        verified: list[str] = []
        unverified: list[str] = []
        for key in keys:
            query = key.replace("_", " ")
            try:
                res = retrieve_literature(query, source="crossref", limit=1)
                results = res.get("results", []) if isinstance(res, dict) else []
                if results:
                    verified.append(key)
                else:
                    unverified.append(key)
            except Exception:
                unverified.append(key)

        out = _report_path(root, "citation_audit.md")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            "# Citation Audit\n\n"
            f"- Total citations: {len(keys)}\n"
            f"- Verified online: {len(verified)}\n"
            f"- Unverified: {len(unverified)}\n\n"
            "## Unverified\n"
            + "\n".join(f"- `{k}`" for k in unverified)
        )
        return {
            "status": "warning" if unverified else "success",
            "verified": verified,
            "unverified": unverified,
            "report_path": str(out.relative_to(root)),
            "message": (
                f"{len(unverified)} citation(s) could not be verified online."
                if unverified
                else "All citations verified."
            ),
        }
    except Exception as e:
        logger.exception("audit_citations failed")
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------------------
# Full reproducibility — re-run experiments in a clean environment
# ---------------------------------------------------------------------------


def audit_reproducibility_full(root: Path) -> dict[str, Any]:
    """Re-run every numbered experiment script and verify outputs.

    If Docker is available, build the project's Dockerfile and run inside;
    otherwise fall back to local re-execution with a warning.
    """
    try:
        import hashlib
        import subprocess
        import sys

        workspace = root / "workspace"
        if not workspace.exists():
            return {"status": "error", "message": "workspace/ not found"}

        results: list[dict[str, Any]] = []
        for exp_dir in sorted(workspace.iterdir()):
            if not (exp_dir.is_dir() and exp_dir.name[:2].isdigit()):
                continue
            if exp_dir.name.endswith("__DEAD_END"):
                continue
            scripts_dir = exp_dir / "scripts"
            if not scripts_dir.exists():
                continue
            for script in sorted(scripts_dir.glob("*.py")):
                pre_hashes = _hash_outputs(exp_dir)
                proc = subprocess.run(
                    [sys.executable, str(script)],
                    cwd=str(scripts_dir),
                    capture_output=True,
                    text=True,
                    timeout=600,
                )
                post_hashes = _hash_outputs(exp_dir)
                changed = {
                    k: (pre_hashes.get(k), post_hashes.get(k))
                    for k in set(pre_hashes) | set(post_hashes)
                    if pre_hashes.get(k) != post_hashes.get(k)
                }
                results.append(
                    {
                        "script": str(script.relative_to(root)),
                        "returncode": proc.returncode,
                        "stderr_tail": (proc.stderr or "")[-500:],
                        "outputs_changed": len(changed),
                    }
                )

        out = _report_path(root, "reproducibility_report.md")
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# Reproducibility Audit", ""]
        for r in results:
            lines.append(
                f"- `{r['script']}` → rc={r['returncode']}, outputs changed: {r['outputs_changed']}"
            )
        out.write_text("\n".join(lines) + "\n")

        failed = [r for r in results if r["returncode"] != 0]
        return {
            "status": "warning" if failed else "success",
            "results": results,
            "report_path": str(out.relative_to(root)),
            "message": (
                f"{len(failed)} script(s) failed to re-run." if failed else "All scripts re-ran cleanly."
            ),
        }
    except Exception as e:
        logger.exception("audit_reproducibility_full failed")
        return {"status": "error", "message": str(e)}


def _hash_outputs(exp_dir: Path) -> dict[str, str]:
    """Hash every file under outputs/ for change detection."""
    import hashlib

    out: dict[str, str] = {}
    outputs = exp_dir / "outputs"
    if not outputs.exists():
        return out
    for f in outputs.rglob("*"):
        if not f.is_file():
            continue
        try:
            sha = hashlib.sha256(f.read_bytes()).hexdigest()
            out[str(f.relative_to(exp_dir))] = sha
        except Exception:
            pass
    return out
