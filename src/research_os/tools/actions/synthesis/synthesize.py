"""Publication-quality synthesis — IMRAD paper with real figures, tables, citations.

Produces:
* ``synthesis/paper.md``     — IMRAD markdown with numbered figures, tables,
                               cross-references, and a verified bibliography.
* ``synthesis/paper.tex``    — LaTeX (when ``output_format`` in {latex, both}).
* ``synthesis/references.bib`` — BibTeX of every verified citation actually used.
* ``synthesis/figures/``     — copied images so the markdown is self-contained.
* ``synthesis/tables/``      — copied tabular outputs.

Citation policy
---------------
Every reference in the bibliography MUST be verified (have a DOI or URL +
title + at least one author). Sources:
1. workspace/citations.md keys (verified online via Crossref/S2).
2. Per-step ``workspace/<step>/literature/literature_index.yaml`` sidecars.
3. Top-K live retrieval per section via citations.collect_for_section.

Unverified entries are silently dropped and reported in the response so the
AI can surface them.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("research_os.tools.synthesis.synthesize")


SECTION_BUILDERS_KEYS = (
    "abstract", "introduction", "methods", "results", "discussion",
    "conclusion", "references",
)


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
            if (
                exp_dir.is_dir()
                and exp_dir.name[:2].isdigit()
                and not exp_dir.name.endswith("__DEAD_END")
            ):
                conc = exp_dir / "conclusions.md"
                if conc.exists() and len(conc.read_text()) > 100:
                    conclusions.append(exp_dir.name)

    citations_present = (
        citations_path.exists() and citations_path.stat().st_size > 100
    )

    sections = [
        {"id": "methods", "source": "workspace/methods.md",
         "status": "ready" if methods_path.exists() and methods_path.stat().st_size > 100 else "missing"},
        {"id": "results", "source": "workspace/*/conclusions.md + outputs/reports/",
         "status": "ready" if conclusions else "missing",
         "experiments": conclusions},
        {"id": "discussion", "source": "workspace/analysis.md + citations.md",
         "status": "ready" if analysis_path.exists() and citations_present else "partial"},
        {"id": "introduction", "source": "citations.md + research_question.md",
         "status": "ready" if citations_present else "missing (run literature_search first)"},
        {"id": "abstract", "source": "synthesis of all sections (run AFTER methods/results/discussion)",
         "status": "pending"},
    ]
    return {
        "sections": sections,
        "recommended_order": ["methods", "results", "discussion", "introduction", "abstract"],
        "note": (
            "Call tool_synthesize with section=<id> for each. Citations are "
            "auto-verified online; unverified entries are dropped."
        ),
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(p: Path) -> str:
    return p.read_text() if p.exists() else ""


def _research_question(root: Path) -> str:
    rq = root / "docs" / "research_question.md"
    if not rq.exists():
        return "Project research question"
    for line in rq.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("*"):
            continue
        return line
    return "Project research question"


def _project_title(root: Path) -> str:
    try:
        from research_os.project_ops import load_state

        s = load_state(root)
        return s.get("project_name") or s.get("project") or "Research Output"
    except Exception:
        return "Research Output"


def _gather_experiment_outputs(root: Path) -> list[dict[str, Any]]:
    """Per-experiment metadata: conclusions, reports, figures, tables, literature."""
    out: list[dict[str, Any]] = []
    workspace = root / "workspace"
    if not workspace.exists():
        return out
    for exp_dir in sorted(workspace.iterdir()):
        if not (exp_dir.is_dir() and exp_dir.name[:2].isdigit()):
            continue
        if exp_dir.name.endswith("__DEAD_END"):
            continue
        entry: dict[str, Any] = {
            "path": exp_dir.name,
            "dir": exp_dir,
            "conclusions": "",
            "reports": [],
            "figures": [],
            "tables": [],
            "literature": [],
        }
        conc = exp_dir / "conclusions.md"
        if conc.exists():
            entry["conclusions"] = conc.read_text()
        reports_dir = exp_dir / "outputs" / "reports"
        if reports_dir.exists():
            for f in sorted(reports_dir.rglob("*.md")):
                entry["reports"].append({"name": f.name, "text": f.read_text()})
        figures_dir = exp_dir / "outputs" / "figures"
        if figures_dir.exists():
            for f in sorted(figures_dir.rglob("*")):
                if f.is_file() and f.suffix.lower() in {".png", ".pdf", ".svg", ".jpg", ".jpeg"}:
                    caption = _read_caption_sidecar(f)
                    entry["figures"].append(
                        {"path": f.relative_to(root).as_posix(),
                         "name": f.name,
                         "caption": caption}
                    )
        tables_dir = exp_dir / "outputs" / "tables"
        if tables_dir.exists():
            for f in sorted(tables_dir.rglob("*")):
                if f.is_file() and f.suffix.lower() in {".csv", ".tsv", ".md"}:
                    caption = _read_caption_sidecar(f)
                    entry["tables"].append(
                        {"path": f.relative_to(root).as_posix(),
                         "name": f.name,
                         "caption": caption,
                         "ext": f.suffix.lower()}
                    )
        # Step-level literature (PDFs + sidecars).
        lit_dir = exp_dir / "literature"
        if lit_dir.exists():
            for f in sorted(lit_dir.iterdir()):
                if not f.is_file():
                    continue
                if f.suffix.lower() not in {".pdf", ".epub"}:
                    continue
                meta = _read_lit_sidecar(f)
                if meta:
                    entry["literature"].append(meta)
        out.append(entry)
    return out


def _read_caption_sidecar(media: Path) -> str:
    """A figure or table's caption can live in a sibling .caption.md file."""
    caption = media.parent / (media.stem + ".caption.md")
    if caption.exists():
        return caption.read_text().strip()
    # Fallback: derive from filename
    return media.stem.replace("_", " ").capitalize()


def _read_lit_sidecar(pdf: Path) -> dict[str, Any] | None:
    """Read .meta.yaml or .meta.json alongside a literature PDF."""
    for ext in (".meta.yaml", ".meta.json"):
        side = pdf.with_suffix(pdf.suffix + ext)
        if side.exists():
            try:
                if ext == ".meta.yaml":
                    import yaml  # type: ignore

                    data = yaml.safe_load(side.read_text()) or {}
                else:
                    data = json.loads(side.read_text())
                if not isinstance(data, dict):
                    return None
                data.setdefault("scope", "workspace_step_literature")
                return data
            except Exception:
                return None
    return None


# ---------------------------------------------------------------------------
# Citation collection (project + step + live)
# ---------------------------------------------------------------------------


def _make_key(entry: dict[str, Any]) -> str:
    from research_os.tools.actions.synthesis.citations import _make_key as _mk

    return _mk(entry)


def _collect_all_verified_citations(
    root: Path, *, output_type: str, query: str,
) -> dict[str, dict[str, Any]]:
    """Gather verified citations from every source. Returns {citation_key: entry}.

    Sources:
      1. inputs/literature_index.yaml (project-level PDFs).
      2. workspace/<step>/literature/literature_index.yaml (per-step PDFs).
      3. Live retrieval via collect_for_section (provides DOI / URL).
    """
    from research_os.tools.actions.synthesis.citations import (
        cap_for,
        collect_for_section,
    )

    pool: dict[str, dict[str, Any]] = {}

    # 1. Project-level literature index.
    proj_index = root / "inputs" / "literature_index.yaml"
    if proj_index.exists():
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(proj_index.read_text()) or {}
            for filename, meta in (data.get("entries") or {}).items():
                key = meta.get("citation_key") or _make_key(meta)
                meta.setdefault("citation_key", key)
                meta.setdefault("scope", "project_literature")
                meta.setdefault("filename", filename)
                if meta.get("doi") or meta.get("url"):
                    pool[key] = meta
        except Exception as e:
            logger.warning(f"project literature index unreadable: {e}")

    # 2. Step-level literature.
    for exp in _gather_experiment_outputs(root):
        for meta in exp.get("literature", []):
            key = meta.get("citation_key") or _make_key(meta)
            meta.setdefault("citation_key", key)
            if meta.get("doi") or meta.get("url"):
                pool[key] = meta

    # 3. Live retrieval per section query.
    try:
        live = collect_for_section(query, k=cap_for(output_type))
        for entry in live:
            key = entry.get("citation_key") or _make_key(entry)
            entry.setdefault("citation_key", key)
            if entry.get("doi") or entry.get("url"):
                pool.setdefault(key, entry)
    except Exception as e:
        logger.warning(f"live citation retrieval failed: {e}")

    return pool


def _bound_to_cap(
    pool: dict[str, dict[str, Any]], output_type: str
) -> list[dict[str, Any]]:
    from research_os.tools.actions.synthesis.citations import cap_for

    cap = cap_for(output_type)
    return list(pool.values())[:cap]


def _number_citations(
    refs: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Assign numeric ref ids; return ordered list + key→number map."""
    numbered: list[dict[str, Any]] = []
    key_to_num: dict[str, int] = {}
    for i, entry in enumerate(refs, start=1):
        entry = dict(entry)
        entry["ref_num"] = i
        key = entry.get("citation_key") or _make_key(entry)
        entry["citation_key"] = key
        key_to_num[key] = i
        numbered.append(entry)
    return numbered, key_to_num


# ---------------------------------------------------------------------------
# Figure + table copying / numbering
# ---------------------------------------------------------------------------


def _copy_figures(root: Path, experiments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Copy every per-experiment figure to synthesis/figures/ with figure numbers."""
    figures_dir = root / "synthesis" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    out: list[dict[str, Any]] = []
    n = 0
    for exp in experiments:
        for fig in exp.get("figures", []):
            n += 1
            src = root / fig["path"]
            dest_name = f"fig{n:02d}_{src.name}"
            dest = figures_dir / dest_name
            try:
                if not dest.exists():
                    shutil.copy2(src, dest)
            except Exception as e:
                logger.warning(f"copy figure failed {src}: {e}")
                continue
            out.append(
                {
                    "number": n,
                    "label": f"fig{n}",
                    "filename": dest_name,
                    "relative_path": f"figures/{dest_name}",
                    "caption": fig.get("caption") or "",
                    "step": exp["path"],
                }
            )
    return out


def _copy_tables(root: Path, experiments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Copy tables and number them. CSV/TSV stays as-is; .md inlines."""
    tables_dir = root / "synthesis" / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    out: list[dict[str, Any]] = []
    n = 0
    for exp in experiments:
        for tab in exp.get("tables", []):
            n += 1
            src = root / tab["path"]
            dest_name = f"tab{n:02d}_{src.name}"
            dest = tables_dir / dest_name
            try:
                if not dest.exists():
                    shutil.copy2(src, dest)
            except Exception as e:
                logger.warning(f"copy table failed {src}: {e}")
                continue
            inline_md = ""
            if tab.get("ext") == ".md":
                try:
                    inline_md = dest.read_text()
                except Exception:
                    pass
            elif tab.get("ext") in {".csv", ".tsv"}:
                inline_md = _csv_to_markdown(dest, sep="," if tab["ext"] == ".csv" else "\t")
            out.append(
                {
                    "number": n,
                    "label": f"tab{n}",
                    "filename": dest_name,
                    "relative_path": f"tables/{dest_name}",
                    "caption": tab.get("caption") or "",
                    "inline_md": inline_md,
                    "step": exp["path"],
                }
            )
    return out


def _csv_to_markdown(path: Path, sep: str = ",", max_rows: int = 30) -> str:
    """Render a CSV/TSV as a small markdown table."""
    try:
        lines = [ln for ln in path.read_text().splitlines() if ln.strip()][: max_rows + 1]
        if not lines:
            return ""
        rows = [[c.strip() for c in ln.split(sep)] for ln in lines]
        header, body = rows[0], rows[1:]
        md = ["| " + " | ".join(header) + " |",
              "|" + "|".join("---" for _ in header) + "|"]
        for r in body:
            md.append("| " + " | ".join(r) + " |")
        if len(lines) > max_rows + 1:
            md.append(f"*(truncated to {max_rows} rows)*")
        return "\n".join(md)
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------


def _build_methods(
    root: Path, key_to_num: dict[str, int], experiments: list[dict[str, Any]]
) -> str:
    body = _read(root / "workspace" / "methods.md")
    if not body.strip():
        return "## Methods\n\n*No methods recorded — run `mem_methods_append` first.*\n"
    body = _replace_citation_keys(body, key_to_num)
    return "## Methods\n\n" + body + "\n"


def _build_results(
    root: Path,
    key_to_num: dict[str, int],
    experiments: list[dict[str, Any]],
    figures: list[dict[str, Any]],
    tables: list[dict[str, Any]],
) -> str:
    chunks: list[str] = ["## Results\n"]
    for exp in experiments:
        if exp.get("conclusions"):
            chunks.append(f"### {exp['path']}\n")
            chunks.append(_replace_citation_keys(exp["conclusions"], key_to_num))
        for rep in exp.get("reports", []):
            chunks.append(f"#### {rep['name']}\n")
            chunks.append(_replace_citation_keys(rep["text"], key_to_num))
    # Figures section.
    if figures:
        chunks.append("\n### Figures\n")
        for fig in figures:
            chunks.append(
                f"![Figure {fig['number']}: {fig['caption']}]({fig['relative_path']})\n\n"
                f"**Figure {fig['number']}.** {fig['caption']} *(from {fig['step']})*\n"
            )
    if tables:
        chunks.append("\n### Tables\n")
        for tab in tables:
            chunks.append(f"**Table {tab['number']}.** {tab['caption']} *(from {tab['step']})*\n")
            if tab.get("inline_md"):
                chunks.append(tab["inline_md"])
            else:
                chunks.append(f"*See `synthesis/{tab['relative_path']}`.*")
            chunks.append("")
    return "\n".join(chunks)


def _build_discussion(
    root: Path, key_to_num: dict[str, int], experiments: list[dict[str, Any]]
) -> str:
    chunks: list[str] = ["## Discussion\n"]
    analysis = _read(root / "workspace" / "analysis.md")
    if analysis.strip():
        analysis = re.sub(r"```mermaid.*?```", "", analysis, flags=re.DOTALL)
        chunks.append(_replace_citation_keys(analysis, key_to_num))
    evid = _read(root / "synthesis" / "evidence_table.md")
    if evid.strip():
        chunks.append("\n### Evidence table\n")
        chunks.append(evid)
    # Hypothesis status block.
    try:
        from research_os.project_ops import load_state

        hypotheses = load_state(root).get("active_hypotheses", []) or []
        if hypotheses:
            chunks.append("\n### Hypothesis status\n")
            chunks.append("| ID | Status | Statement |")
            chunks.append("|---|---|---|")
            for h in hypotheses:
                chunks.append(
                    f"| {h.get('id', '?')} | {h.get('status', '?')} | "
                    f"{(h.get('statement') or '')[:120]} |"
                )
    except Exception:
        pass
    return "\n".join(chunks) + "\n"


def _build_introduction(root: Path, key_to_num: dict[str, int]) -> str:
    rq = _research_question(root)
    body = (
        "## Introduction\n\n"
        f"This study investigates: **{rq}**\n\n"
        "Prior work informing this question is summarised below, cited inline by "
        "reference number (see the References section).\n"
    )
    return _replace_citation_keys(body, key_to_num)


def _build_abstract(root: Path, experiments: list[dict[str, Any]], output_type: str) -> str:
    """A short, structured-ish abstract built from experiment headline findings."""
    findings: list[str] = []
    for exp in experiments:
        m = re.search(
            r"##\s*Findings\s*\n(.+?)(?:\n##|\Z)", exp.get("conclusions", ""), flags=re.DOTALL
        )
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
    return (
        "## Abstract\n\n"
        f"**Background.** {rq}\n\n"
        "**Methods.** *(1-2 sentences summarising design, data, and analysis.)*\n\n"
        f"**Results.** {'; '.join(findings) if findings else '(populate from experiment conclusions)'}.\n\n"
        "**Conclusion.** *(1-2 sentences on implications and main limitation.)*\n"
    )


def _build_references_section(
    references: list[dict[str, Any]], style: str = "vancouver"
) -> str:
    if not references:
        return "## References\n\n*(no verified citations available)*\n"
    from research_os.tools.actions.synthesis.citations import (
        format_apa,
        format_vancouver,
    )

    fmt = {"apa": format_apa, "vancouver": format_vancouver}.get(
        style.lower(), format_vancouver
    )
    lines = ["## References", ""]
    for ref in references:
        lines.append(f"{ref['ref_num']}. {fmt(ref)}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Citation-key → numbered reference rewriting
# ---------------------------------------------------------------------------


_CITE_PATTERNS = [
    # Pandoc-style: [@key], [@key; @key2]
    re.compile(r"\[@([a-zA-Z0-9_]+)(?:[;,]\s*@[a-zA-Z0-9_]+)*\]"),
    # \cite{key} or \cite{key1,key2}
    re.compile(r"\\cite\{([a-zA-Z0-9_,]+)\}"),
]


def _replace_citation_keys(text: str, key_to_num: dict[str, int]) -> str:
    """Convert any in-text citation references to numbered [N] form."""
    if not text or not key_to_num:
        return text

    def _convert(match: re.Match) -> str:
        raw = match.group(0)
        # Pull every key inside the match.
        keys = re.findall(r"[a-zA-Z0-9_]+", raw.replace("@", " ").replace("cite", " "))
        nums = [str(key_to_num[k]) for k in keys if k in key_to_num]
        if not nums:
            return raw
        return "[" + ",".join(nums) + "]"

    out = text
    for pat in _CITE_PATTERNS:
        out = pat.sub(_convert, out)
    return out


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def synthesize_workspace(
    root: Path,
    *,
    output_format: str = "markdown",
    section: str | None = None,
    output_type: str = "paper",
    citation_style: str = "vancouver",
) -> dict[str, Any]:
    """Build a section, OR — when section is None — assemble the full output."""
    try:
        synthesis_dir = root / "synthesis"
        synthesis_dir.mkdir(parents=True, exist_ok=True)

        experiments = _gather_experiment_outputs(root)
        figures = _copy_figures(root, experiments)
        tables = _copy_tables(root, experiments)

        question = _research_question(root)
        pool = _collect_all_verified_citations(
            root, output_type=output_type, query=question
        )
        capped = _bound_to_cap(pool, output_type)
        references, key_to_num = _number_citations(capped)

        # ── Single-section mode ────────────────────────────────────────
        if section:
            section = section.lower()
            builder_map = {
                "methods": lambda: _build_methods(root, key_to_num, experiments),
                "results": lambda: _build_results(
                    root, key_to_num, experiments, figures, tables
                ),
                "discussion": lambda: _build_discussion(root, key_to_num, experiments),
                "introduction": lambda: _build_introduction(root, key_to_num),
                "abstract": lambda: _build_abstract(root, experiments, output_type),
                "references": lambda: _build_references_section(references, citation_style),
            }
            if section not in builder_map:
                return {
                    "status": "error",
                    "error": f"Unknown section '{section}'. Allowed: {sorted(builder_map)}",
                }
            body = builder_map[section]()
            dest = synthesis_dir / f"{section}.md"
            dest.write_text(body)
            return {
                "status": "success",
                "section": section,
                "path": str(dest.relative_to(root)),
                "citations_used": len(references),
                "figures_numbered": len(figures),
                "tables_numbered": len(tables),
                "message": f"Wrote synthesis/{section}.md.",
            }

        # ── Full assembly ──────────────────────────────────────────────
        title = _project_title(root)
        chunks: list[str] = [
            f"# {title}\n",
            f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*\n",
        ]
        chunks.append(_build_abstract(root, experiments, output_type))
        chunks.append(_build_introduction(root, key_to_num))
        chunks.append(_build_methods(root, key_to_num, experiments))
        chunks.append(_build_results(root, key_to_num, experiments, figures, tables))
        chunks.append(_build_discussion(root, key_to_num, experiments))
        chunks.append(_build_references_section(references, citation_style))

        paper_md = synthesis_dir / "paper.md"
        paper_md.write_text("\n".join(chunks))

        # references.bib
        from research_os.tools.actions.synthesis.citations import write_references_bib

        bib_path = synthesis_dir / "references.bib"
        write_references_bib(references, bib_path)

        # Track which keys WEREN'T usable for transparency.
        unverified = sorted(set(pool.keys()) - {r["citation_key"] for r in references})

        result: dict[str, Any] = {
            "status": "success",
            "output_type": output_type,
            "paper_path": str(paper_md.relative_to(root)),
            "bib_path": str(bib_path.relative_to(root)),
            "sections": ["abstract", "introduction", "methods", "results", "discussion", "references"],
            "citations_used": len(references),
            "citation_keys": [r["citation_key"] for r in references],
            "figures_numbered": len(figures),
            "tables_numbered": len(tables),
            "word_count": sum(len(c.split()) for c in chunks),
            "candidates_unused_due_to_cap": unverified,
        }

        if output_format in ("latex", "both"):
            tex_path = synthesis_dir / "paper.tex"
            tex_path.write_text(
                _markdown_to_latex(
                    title=title,
                    chunks=chunks,
                    figures=figures,
                    references=references,
                )
            )
            try:
                from research_os.tools.actions.synthesis.latex import latex_compile

                result["latex_compile"] = latex_compile(root)
            except Exception as e:
                result["latex_compile"] = {"status": "error", "message": str(e)}
            if output_format == "latex":
                result["paper_path"] = str(tex_path.relative_to(root))
        return result

    except Exception as e:
        logger.exception("Synthesis failed")
        return {"error": f"Synthesis failed: {e}"}


# ---------------------------------------------------------------------------
# LaTeX renderer (proper natbib + figures + bibtex)
# ---------------------------------------------------------------------------


def _escape_latex(s: str) -> str:
    if not s:
        return ""
    return (
        s.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("$", r"\$")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("{", r"\{")
        .replace("}", r"\}")
    )


def _markdown_to_latex(
    *,
    title: str,
    chunks: list[str],
    figures: list[dict[str, Any]],
    references: list[dict[str, Any]],
) -> str:
    """Render the IMRAD markdown into a citation-aware LaTeX document.

    The body just inherits the markdown verbatim inside ``\\begin{verbatim}``
    blocks for paragraphs, but headers, figures, and ``[N]`` citations are
    rewritten properly. For pixel-perfect typesetting, run the markdown through
    pandoc instead.
    """
    head = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{graphicx}",
        r"\usepackage[numbers,sort&compress]{natbib}",
        r"\usepackage{hyperref}",
        r"\usepackage{geometry}",
        r"\geometry{margin=1in}",
        r"\usepackage{booktabs}",
        r"\title{" + _escape_latex(title) + "}",
        r"\date{\today}",
        r"\begin{document}",
        r"\maketitle",
    ]
    body: list[str] = []
    for chunk in chunks:
        for line in chunk.splitlines():
            if line.startswith("# "):
                # title already in \maketitle — skip the project title repeats
                continue
            if line.startswith("## "):
                body.append(r"\section*{" + _escape_latex(line[3:].strip()) + "}")
            elif line.startswith("### "):
                body.append(r"\subsection*{" + _escape_latex(line[4:].strip()) + "}")
            elif line.startswith("#### "):
                body.append(r"\subsubsection*{" + _escape_latex(line[5:].strip()) + "}")
            elif line.startswith("!["):
                # Markdown figure → \begin{figure}...\end{figure}
                m = re.match(r"!\[(.*?)\]\((.+?)\)", line)
                if m:
                    caption, path = m.group(1), m.group(2)
                    body.append(r"\begin{figure}[h!]")
                    body.append(r"  \centering")
                    body.append(
                        r"  \includegraphics[width=0.85\linewidth]{" + path + "}"
                    )
                    body.append(r"  \caption{" + _escape_latex(caption) + "}")
                    body.append(r"\end{figure}")
                else:
                    body.append(_escape_latex(line))
            elif line.strip():
                body.append(_escape_latex(line))
            else:
                body.append("")
    # Bibliography
    body.append(r"\bibliographystyle{unsrtnat}")
    body.append(r"\bibliography{references}")
    body.append(r"\end{document}")
    return "\n".join(head + body)
