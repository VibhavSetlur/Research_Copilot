"""LaTeX & dashboard generation — publication-quality outputs."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("research_os.tools.latex")


def _project_name(root: Path) -> str:
    try:
        from research_os.project_ops import load_state

        state = load_state(root)
        return state.get("project_name") or state.get("project") or "Research Project"
    except Exception:
        return "Research Project"


# ---------------------------------------------------------------------------
# LaTeX paper compile
# ---------------------------------------------------------------------------


def latex_compile(root: Path) -> dict[str, Any]:
    """Compile ``synthesis/paper.tex`` to PDF (pdflatex × bibtex × pdflatex × pdflatex)."""
    tex_path = root / "synthesis" / "paper.tex"
    if not tex_path.exists():
        return {"status": "error", "message": "synthesis/paper.tex not found", "success": False}

    pdflatex = shutil.which("pdflatex")
    bibtex = shutil.which("bibtex")
    if not pdflatex:
        return {
            "status": "error",
            "message": "pdflatex not found. Install TeX Live.",
            "success": False,
        }

    log_lines: list[str] = []

    def _run_pdflatex() -> int:
        res = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=str(tex_path.parent),
            capture_output=True,
            text=True,
            timeout=120,
        )
        log_lines.append(res.stdout[-1500:])
        return res.returncode

    success = _run_pdflatex() == 0
    if success and bibtex and tex_path.with_suffix(".aux").exists():
        subprocess.run(
            [bibtex, tex_path.with_suffix(".aux").name],
            cwd=str(tex_path.parent),
            capture_output=True,
            text=True,
            timeout=60,
        )
    if success:
        _run_pdflatex()
        _run_pdflatex()  # ensure cross-refs resolve

    pdf = tex_path.with_suffix(".pdf")
    return {
        "status": "success" if (success and pdf.exists()) else "error",
        "pdf_path": str(pdf.relative_to(root)) if pdf.exists() else None,
        "success": success and pdf.exists(),
        "log": "\n".join(log_lines[-3:]),
    }


# ---------------------------------------------------------------------------
# Poster
# ---------------------------------------------------------------------------


def create_poster(root: Path) -> dict[str, Any]:
    """Generate a tikzposter LaTeX poster and compile to PDF.

    Pulls the title from state, copies any workspace PNGs adjacent for
    ``\\includegraphics`` to find, and renders a 3-block portrait poster.
    """
    synthesis_dir = root / "synthesis"
    synthesis_dir.mkdir(parents=True, exist_ok=True)
    poster_tex = synthesis_dir / "poster.tex"
    title = _project_name(root)

    figures: list[str] = []
    workspace = root / "workspace"
    if workspace.exists():
        for f in sorted(workspace.rglob("*.png")):
            dest = synthesis_dir / f.name
            try:
                if not dest.exists():
                    shutil.copy2(f, dest)
                figures.append(f.name)
            except Exception:
                pass

    fig_blocks = ""
    if figures:
        fig_blocks = "\n".join(
            [
                "    \\begin{center}",
                *[
                    "        \\includegraphics[width=0.85\\linewidth]{" + name + "}\n        \\vspace{0.6cm}"
                    for name in figures[:3]
                ],
                "    \\end{center}",
            ]
        )
    else:
        fig_blocks = "    \\textit{No figures available yet.}"

    poster_tex.write_text(
        "\\documentclass[20pt, a0paper, portrait]{tikzposter}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage{graphicx}\n"
        f"\\title{{{title}}}\n"
        "\\author{Research OS}\n"
        "\\institute{}\n"
        "\\usetheme{Board}\n"
        "\\begin{document}\n"
        "\\maketitle\n\n"
        "\\begin{columns}\n"
        "\\column{0.5}\n"
        "\\block{Background}{\n"
        "    \\vspace{0.5cm} Findings from the Research OS pipeline. \\vspace{0.5cm}\n"
        "}\n"
        "\\block{Methods}{\n"
        "    \\vspace{0.5cm}\n"
        "    \\begin{itemize}\n"
        "        \\item Data profiling and EDA\n"
        "        \\item Statistical or ML modelling\n"
        "        \\item Literature-grounded methodology\n"
        "    \\end{itemize}\n"
        "    \\vspace{0.5cm}\n"
        "}\n"
        "\\column{0.5}\n"
        "\\block{Results}{\n"
        + fig_blocks
        + "\n}\n"
        "\\block{Conclusions}{\n"
        "    \\vspace{0.5cm} See \\texttt{synthesis/paper.md} for full discussion. \\vspace{0.5cm}\n"
        "}\n"
        "\\end{columns}\n"
        "\\end{document}\n"
    )

    pdflatex = shutil.which("pdflatex")
    if not pdflatex:
        return {
            "status": "error",
            "message": "pdflatex not found",
            "tex_path": str(poster_tex.relative_to(root)),
            "success": False,
        }
    res = subprocess.run(
        [pdflatex, "-interaction=nonstopmode", poster_tex.name],
        cwd=str(synthesis_dir),
        capture_output=True,
        text=True,
        timeout=120,
    )
    pdf = poster_tex.with_suffix(".pdf")
    return {
        "status": "success" if (res.returncode == 0 and pdf.exists()) else "error",
        "pdf_path": str(pdf.relative_to(root)) if pdf.exists() else None,
        "log": res.stdout[-1500:],
    }


# ---------------------------------------------------------------------------
# Dashboard (single-file HTML)
# ---------------------------------------------------------------------------


_DASHBOARD_CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
       max-width: 1100px; margin: 2rem auto; padding: 0 1.5rem; color: #1d2330; line-height: 1.55; }
h1 { font-size: 2rem; border-bottom: 2px solid #1f6feb; padding-bottom: .4rem; }
h2 { font-size: 1.4rem; margin-top: 2.4rem; color: #1f6feb; }
h3 { font-size: 1.1rem; margin-top: 1.6rem; }
.meta { color: #555; font-size: .9rem; }
.card { border: 1px solid #e1e5ec; border-radius: 10px; padding: 1rem 1.4rem; margin: 1rem 0;
        background: #fafbfd; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
table { border-collapse: collapse; width: 100%; margin: .5rem 0; }
th, td { border: 1px solid #e1e5ec; padding: .45rem .8rem; text-align: left; font-size: .95rem; }
th { background: #f1f4f9; }
.gallery { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
.gallery figure { margin: 0; }
.gallery img { width: 100%; border-radius: 6px; border: 1px solid #dfe2e9; }
.tag { display:inline-block; padding:.15rem .5rem; border-radius: 999px; background:#e9eefb;
       color:#1f6feb; font-size:.78rem; margin-right:.4rem; }
pre { background: #0d1117; color: #e6edf3; padding: 1rem; border-radius: 8px; overflow-x: auto; }
"""


def _gather_dashboard_data(root: Path) -> dict[str, Any]:
    from research_os.project_ops import load_state
    from research_os.tools.actions.path import list_paths

    state = load_state(root)
    paths = list_paths(root).get("paths", []) or []

    citations = ""
    cit_path = root / "workspace" / "citations.md"
    if cit_path.exists():
        citations = cit_path.read_text()

    methods = ""
    m_path = root / "workspace" / "methods.md"
    if m_path.exists():
        methods = m_path.read_text()

    conclusions: list[dict[str, str]] = []
    figures: list[dict[str, str]] = []
    reports: list[dict[str, str]] = []
    for exp in (root / "workspace").iterdir() if (root / "workspace").exists() else []:
        if not (exp.is_dir() and exp.name[:2].isdigit() and not exp.name.endswith("__DEAD_END")):
            continue
        conc = exp / "conclusions.md"
        if conc.exists():
            conclusions.append({"path": exp.name, "text": conc.read_text()})
        figs_dir = exp / "outputs" / "figures"
        if figs_dir.exists():
            for f in sorted(figs_dir.rglob("*")):
                if f.suffix.lower() in {".png", ".svg", ".jpg", ".jpeg"}:
                    figures.append({"path": exp.name, "rel": f.relative_to(root).as_posix()})
        reps = exp / "outputs" / "reports"
        if reps.exists():
            for f in sorted(reps.rglob("*.md")):
                reports.append({"path": exp.name, "rel": f.relative_to(root).as_posix(), "text": f.read_text()[:2000]})

    return {
        "state": state,
        "paths": paths,
        "methods": methods,
        "citations": citations,
        "conclusions": conclusions,
        "figures": figures,
        "reports": reports,
    }


def create_dashboard(root: Path, title: str | None = None) -> dict[str, Any]:
    """Render a single-file HTML dashboard at ``synthesis/dashboard.html``."""
    try:
        title = title or _project_name(root)
        data = _gather_dashboard_data(root)
        synthesis_dir = root / "synthesis"
        synthesis_dir.mkdir(parents=True, exist_ok=True)
        out_path = synthesis_dir / "dashboard.html"

        # Copy figures next to dashboard so relative <img src=> resolves.
        figure_blocks: list[str] = []
        for fig in data["figures"]:
            src = root / fig["rel"]
            dest_dir = synthesis_dir / "figures" / fig["path"]
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / src.name
            try:
                if not dest.exists():
                    shutil.copy2(src, dest)
                rel = dest.relative_to(synthesis_dir).as_posix()
                figure_blocks.append(
                    f'<figure><img src="{rel}" alt="{src.name}"/>'
                    f'<figcaption><span class="tag">{fig["path"]}</span>{src.name}</figcaption></figure>'
                )
            except Exception:
                continue

        path_rows = "".join(
            f"<tr><td>{p['path_id']}</td><td>{p['status']}</td>"
            f"<td>{'✓' if p['has_readme'] else '✗'}</td>"
            f"<td>{'✓' if p['has_conclusions'] else '✗'}</td></tr>"
            for p in data["paths"]
        )
        path_table = (
            "<table><tr><th>Path</th><th>Status</th><th>README</th><th>Conclusions</th></tr>"
            + path_rows
            + "</table>"
        ) if data["paths"] else "<p><em>No experiment paths yet.</em></p>"

        conclusion_cards = "".join(
            f'<div class="card"><h3>{c["path"]}</h3><pre>{c["text"][:4000]}</pre></div>'
            for c in data["conclusions"]
        )

        report_cards = "".join(
            f'<div class="card"><h3>{r["rel"]}</h3><pre>{r["text"]}</pre></div>'
            for r in data["reports"]
        )

        gallery = (
            f'<div class="gallery">{"".join(figure_blocks)}</div>'
            if figure_blocks
            else "<p><em>No figures generated yet.</em></p>"
        )

        state = data["state"]
        meta = (
            f"<p class='meta'>Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
            f" · Pipeline stage: <strong>{state.get('pipeline_stage', state.get('phase', 'init'))}</strong>"
            f" · Active path: <code>{state.get('current_path', 'main')}</code></p>"
        )

        out_path.write_text(
            "<!doctype html>\n"
            f"<html><head><meta charset='utf-8'><title>{title} · Research OS</title>"
            f"<style>{_DASHBOARD_CSS}</style></head><body>"
            f"<h1>{title}</h1>{meta}"
            f"<h2>Experiment paths</h2>{path_table}"
            f"<h2>Figures</h2>{gallery}"
            f"<h2>Conclusions</h2>{conclusion_cards or '<p><em>None yet.</em></p>'}"
            f"<h2>Reports</h2>{report_cards or '<p><em>None yet.</em></p>'}"
            f"<h2>Methods log</h2><pre>{data['methods'][:8000] or '(empty)'}</pre>"
            f"<h2>Citations</h2><pre>{data['citations'][:8000] or '(empty)'}</pre>"
            "</body></html>"
        )

        return {
            "status": "success",
            "dashboard_path": str(out_path.relative_to(root)),
            "figures": len(figure_blocks),
            "paths": len(data["paths"]),
        }
    except Exception as e:
        logger.exception("create_dashboard failed")
        return {"status": "error", "message": str(e)}
