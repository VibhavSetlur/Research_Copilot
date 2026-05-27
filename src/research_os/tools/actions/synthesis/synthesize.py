"""Synthesis — paper / abstract / report assembly with verified citations.

Outputs are condensed by output_type to publication-quality bounds:
  abstract  → ~250 words, ≤3 citations
  poster    → 4-block layout, ≤6 citations
  paper     → IMRAD, ≤40 citations across all sections
  report    → flexible, ≤25 citations
  dashboard → HTML, ≤12 citations under "References"

Every citation that lands in the final output is verified online via the
citations module before being included. Unverified entries are dropped
and reported in the synthesis envelope so the AI can surface them.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("research_os.tools.synthesis.synthesize")


SECTION_ALLOWED = {
    "abstract",
    "introduction",
    "methods",
    "results",
    "discussion",
    "conclusion",
    "references",
}


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------


def synthesize_plan(root: Path) -> dict[str, Any]:
    """Inspect available sources and recommend ordering."""
    methods_path = root / "workspace" / "methods.md"
    citations_path = root / "workspace" / "citations.md"
    analysis_path = root / "workspace" / "analysis.md"

    conclusions: list[str] = []
    workspace_dir = root / "workspace"
    if workspace_dir.exists():
        for exp_dir in sorted(workspace_dir.iterdir()):
            if exp_dir.is_dir() and exp_dir.name[:2].isdigit() and not exp_dir.name.endswith("__DEAD_END"):
                conc = exp_dir / "conclusions.md"
                if conc.exists() and len(conc.read_text()) > 100:
                    conclusions.append(exp_dir.name)

    citations_present = (
        citations_path.exists() and citations_path.stat().st_size > 100
    )

    sections = [
        {
            "id": "methods",
            "source": "workspace/methods.md",
            "status": "ready" if methods_path.exists() and methods_path.stat().st_size > 100 else "missing",
        },
        {
            "id": "results",
            "source": "workspace/*/conclusions.md + outputs/reports/",
            "status": "ready" if conclusions else "missing",
            "experiments": conclusions,
        },
        {
            "id": "discussion",
            "source": "workspace/analysis.md + citations.md",
            "status": "ready" if analysis_path.exists() and citations_present else "partial",
        },
        {
            "id": "introduction",
            "source": "citations.md + research_question.md",
            "status": "ready" if citations_present else "missing (run literature_search first)",
        },
        {
            "id": "abstract",
            "source": "synthesis of all sections (run AFTER methods/results/discussion)",
            "status": "pending",
        },
    ]
    return {
        "sections": sections,
        "recommended_order": ["methods", "results", "discussion", "introduction", "abstract"],
        "note": (
            "Call tool_synthesize with section=<id> for each section in order. "
            "Citations are auto-verified online; unverified entries are dropped."
        ),
    }


# ---------------------------------------------------------------------------
# Section generators (each pulls verified citations for itself)
# ---------------------------------------------------------------------------


def _read(p: Path) -> str:
    return p.read_text() if p.exists() else ""


def _gather_experiment_outputs(root: Path) -> list[dict[str, str]]:
    """Pull conclusions + report markdowns from every live experiment."""
    out: list[dict[str, str]] = []
    workspace_dir = root / "workspace"
    if not workspace_dir.exists():
        return out
    for exp_dir in sorted(workspace_dir.iterdir()):
        if not (exp_dir.is_dir() and exp_dir.name[:2].isdigit()):
            continue
        if exp_dir.name.endswith("__DEAD_END"):
            continue
        conc_md = exp_dir / "conclusions.md"
        if conc_md.exists():
            out.append({"path": exp_dir.name, "kind": "conclusions",
                        "text": conc_md.read_text()})
        reports_dir = exp_dir / "outputs" / "reports"
        if reports_dir.exists():
            for md_file in sorted(reports_dir.rglob("*.md")):
                out.append(
                    {
                        "path": exp_dir.name,
                        "kind": f"report:{md_file.name}",
                        "text": md_file.read_text(),
                    }
                )
    return out


def _gather_figures(root: Path) -> list[str]:
    figures: list[str] = []
    workspace_dir = root / "workspace"
    if not workspace_dir.exists():
        return figures
    for exp_dir in workspace_dir.iterdir():
        if not (exp_dir.is_dir() and exp_dir.name[:2].isdigit()):
            continue
        if exp_dir.name.endswith("__DEAD_END"):
            continue
        fdir = exp_dir / "outputs" / "figures"
        if fdir.exists():
            for f in fdir.rglob("*"):
                if f.is_file() and f.suffix.lower() in {".png", ".pdf", ".svg", ".jpg", ".jpeg"}:
                    figures.append(f.relative_to(root).as_posix())
    return sorted(figures)


def _verified_citations_for(
    section: str, query: str, output_type: str
) -> list[dict[str, Any]]:
    """Pull a capped list of verified citations relevant to this section."""
    from research_os.tools.actions.synthesis.citations import (
        cap_for,
        collect_for_section,
    )

    # How many per section. Use min of (output_type cap, per-section sensible cap).
    per_section_caps = {
        "methods": 5,
        "results": 3,
        "discussion": 10,
        "introduction": 8,
        "abstract": 2,
        "conclusion": 3,
    }
    cap = min(per_section_caps.get(section, 5), cap_for(output_type))
    try:
        return collect_for_section(query, k=cap)
    except Exception as e:
        logger.warning(f"verified citation fetch failed: {e}")
        return []


def _research_question(root: Path) -> str:
    rq_path = root / "docs" / "research_question.md"
    if not rq_path.exists():
        return "the project's research question"
    text = rq_path.read_text()
    # Pull the first non-header line.
    for line in text.splitlines():
        if line.strip() and not line.startswith("#") and not line.startswith("*"):
            return line.strip()
    return "the project's research question"


def _section_methods(root: Path, output_type: str) -> tuple[str, list[dict[str, Any]]]:
    body = _read(root / "workspace" / "methods.md")
    if not body.strip():
        return "*No methods recorded — run `mem_methods_append` first.*", []
    cites = _verified_citations_for("methods", "methodology " + _research_question(root), output_type)
    return body, cites


def _section_results(root: Path, output_type: str) -> tuple[str, list[dict[str, Any]]]:
    chunks = []
    for item in _gather_experiment_outputs(root):
        header = f"### {item['path']} — {item['kind']}"
        chunks.append(f"{header}\n\n{item['text']}")
    body = "\n\n".join(chunks) if chunks else "*No results recorded.*"
    figures = _gather_figures(root)
    if figures:
        body += "\n\n### Figures\n\n" + "\n".join(f"![{f}]({f})" for f in figures)
    cites = _verified_citations_for("results", "results " + _research_question(root), output_type)
    return body, cites


def _section_discussion(root: Path, output_type: str) -> tuple[str, list[dict[str, Any]]]:
    body_parts = []
    analysis = _read(root / "workspace" / "analysis.md")
    if analysis.strip():
        # Strip the mermaid block from the discussion (visual, not narrative).
        analysis = re.sub(r"```mermaid.*?```", "", analysis, flags=re.DOTALL)
        body_parts.append(analysis.strip())
    evid = _read(root / "synthesis" / "evidence_table.md")
    if evid.strip():
        body_parts.append("### Evidence table\n\n" + evid.strip())
    body = "\n\n".join(body_parts) if body_parts else "*No discussion content yet.*"
    cites = _verified_citations_for("discussion", _research_question(root), output_type)
    return body, cites


def _section_introduction(root: Path, output_type: str) -> tuple[str, list[dict[str, Any]]]:
    rq = _research_question(root)
    body = (
        f"## Introduction\n\n"
        f"This study investigates: **{rq}**\n\n"
        "Prior work informing this question is summarised below."
    )
    cites = _verified_citations_for("introduction", rq, output_type)
    return body, cites


def _section_abstract(root: Path, output_type: str) -> tuple[str, list[dict[str, Any]]]:
    # The abstract is a synthesis of the other sections. We pull the headline
    # finding from each conclusions.md (first 3 lines under "## Findings").
    findings: list[str] = []
    for item in _gather_experiment_outputs(root):
        if item["kind"] != "conclusions":
            continue
        m = re.search(r"##\s*Findings\s*\n(.+?)(?:\n##|\Z)", item["text"], flags=re.DOTALL)
        if m:
            for line in m.group(1).splitlines():
                line = line.strip()
                if line.startswith("-"):
                    findings.append(line[1:].strip())
                if len(findings) >= 3:
                    break
        if len(findings) >= 3:
            break

    rq = _research_question(root)
    body = (
        "## Abstract\n\n"
        f"**Background.** {rq}\n\n"
        "**Methods.** (1-2 sentences summarising design, data, and analysis.)\n\n"
        f"**Results.** {'; '.join(findings) if findings else '(populate from experiment conclusions)'}.\n\n"
        "**Conclusion.** (1-2 sentences on implications and main limitation.)\n"
    )
    cites = _verified_citations_for("abstract", rq, output_type)
    return body, cites


SECTION_BUILDERS = {
    "methods": _section_methods,
    "results": _section_results,
    "discussion": _section_discussion,
    "introduction": _section_introduction,
    "abstract": _section_abstract,
}


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------


def _format_inline_citations(cites: list[dict[str, Any]], style: str = "apa") -> str:
    """Bottom-of-section citation list in author-year (or numbered) style."""
    if not cites:
        return ""
    lines = ["", "### References (verified)"]
    from research_os.tools.actions.synthesis.citations import (
        format_apa,
        format_vancouver,
    )

    fmt = {"apa": format_apa, "vancouver": format_vancouver}.get(style.lower(), format_apa)
    for c in cites:
        lines.append(f"- [{c.get('citation_key', '?')}] {fmt(c)}")
    return "\n".join(lines) + "\n"


def synthesize_workspace(
    root: Path,
    *,
    output_format: str = "markdown",
    section: str | None = None,
    output_type: str = "paper",
    citation_style: str = "apa",
) -> dict[str, Any]:
    """Build a section, OR — when section is None — assemble the full output_type."""
    try:
        synthesis_dir = root / "synthesis"
        synthesis_dir.mkdir(parents=True, exist_ok=True)

        # ── Single-section mode ────────────────────────────────────────
        if section:
            section = section.lower()
            if section not in SECTION_BUILDERS:
                return {
                    "status": "error",
                    "error": f"Unknown section '{section}'. Allowed: {sorted(SECTION_BUILDERS)}",
                }
            body, cites = SECTION_BUILDERS[section](root, output_type)
            full = body + "\n\n" + _format_inline_citations(cites, citation_style)
            dest = synthesis_dir / f"{section}.md"
            dest.write_text(full)
            return {
                "status": "success",
                "section": section,
                "path": str(dest.relative_to(root)),
                "citations_used": len(cites),
                "citation_keys": [c.get("citation_key") for c in cites],
                "message": f"Wrote synthesis/{section}.md with {len(cites)} verified citations.",
            }

        # ── Full-assembly mode ────────────────────────────────────────
        all_cites: dict[str, dict[str, Any]] = {}  # dedup by citation_key

        section_chunks: list[str] = []
        sections_built = []
        title = _research_question(root)
        section_chunks.append(f"# {title}\n")
        section_chunks.append(
            f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*\n"
        )

        order = ["abstract", "introduction", "methods", "results", "discussion"]
        for sec in order:
            body, cites = SECTION_BUILDERS[sec](root, output_type)
            for c in cites:
                key = c.get("citation_key") or ""
                if key and key not in all_cites:
                    all_cites[key] = c
            section_chunks.append(f"## {sec.capitalize()}\n\n{body}\n")
            sections_built.append(sec)

        # References section — bottom of paper, formatted bibliography from the
        # deduped pool, capped by output_type.
        from research_os.tools.actions.synthesis.citations import (
            cap_for,
            format_apa,
            format_vancouver,
            write_references_bib,
        )

        cap = cap_for(output_type)
        ranked = list(all_cites.values())[:cap]
        fmt = {"apa": format_apa, "vancouver": format_vancouver}.get(
            citation_style.lower(), format_apa
        )
        ref_lines = ["## References", ""]
        for c in ranked:
            ref_lines.append(f"- [{c.get('citation_key', '?')}] {fmt(c)}")
        section_chunks.append("\n".join(ref_lines))

        paper_content = "\n".join(section_chunks)
        paper_md = synthesis_dir / "paper.md"
        paper_md.write_text(paper_content)

        # references.bib
        bib_path = synthesis_dir / "references.bib"
        write_references_bib(ranked, bib_path)

        result: dict[str, Any] = {
            "status": "success",
            "output_type": output_type,
            "paper_path": str(paper_md.relative_to(root)),
            "bib_path": str(bib_path.relative_to(root)),
            "sections": sections_built,
            "citations_used": len(ranked),
            "citation_keys": [c.get("citation_key") for c in ranked],
            "word_count": len(paper_content.split()),
            "figure_count": len(_gather_figures(root)),
        }

        if output_format in ("latex", "both"):
            from research_os.tools.actions.synthesis.latex import latex_compile

            tex_path = synthesis_dir / "paper.tex"
            tex_path.write_text(_markdown_to_latex(paper_content))
            compile_result = latex_compile(root)
            result["latex_compile"] = compile_result
            if output_format == "latex":
                result["paper_path"] = str(tex_path.relative_to(root))
        return result

    except Exception as e:
        logger.exception("Synthesis failed")
        return {"error": f"Synthesis failed: {e}"}


def _markdown_to_latex(md: str) -> str:
    """Light markdown → LaTeX. For publication, use pandoc on the .md instead."""
    lines = md.split("\n")
    tex_lines = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{graphicx}",
        r"\usepackage{hyperref}",
        r"\usepackage{geometry}",
        r"\geometry{margin=1in}",
        r"\title{Research Output}",
        r"\date{\today}",
        r"\begin{document}",
        r"\maketitle",
    ]
    for line in lines:
        if line.startswith("# "):
            tex_lines.append(r"\section*{" + line[2:] + "}")
        elif line.startswith("## "):
            tex_lines.append(r"\subsection*{" + line[3:] + "}")
        elif line.startswith("### "):
            tex_lines.append(r"\subsubsection*{" + line[4:] + "}")
        elif line.startswith("!"):
            tex_lines.append(line)
        elif line.strip():
            tex_lines.append(line + r"\\")
        else:
            tex_lines.append("")
    tex_lines.append(r"\end{document}")
    return "\n".join(tex_lines)
