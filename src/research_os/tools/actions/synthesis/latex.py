"""LaTeX paper + tikzposter + high-quality HTML dashboard generation.

The dashboard is single-file (all CSS + JS embedded) so it opens directly
without any server. Features:
  * sortable tables (click any column header)
  * lightbox-style image gallery (click any thumbnail)
  * light/dark toggle (auto-detects prefers-color-scheme)
  * print-friendly stylesheet
  * semantic landmarks (header / main / aside / footer)
  * audience-tailored layout (academic | executive | technical | teaching)
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("research_os.tools.synthesis.latex")


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
        _run_pdflatex()

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
    """Generate a tikzposter LaTeX poster and compile to PDF."""
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
# Dashboard — single-file HTML with embedded CSS + JS
# ---------------------------------------------------------------------------


_DASHBOARD_CSS = r"""
:root {
  --bg: #ffffff; --fg: #1d2330; --muted: #5a6478;
  --card: #fafbfd; --border: #e1e5ec; --accent: #1f6feb;
  --accent-soft: #e9eefb; --shadow: 0 1px 2px rgba(0,0,0,.04);
  --code-bg: #0d1117; --code-fg: #e6edf3;
}
@media (prefers-color-scheme: dark) {
  :root { --bg: #0e1117; --fg: #e6edf3; --muted: #8b94a7;
          --card: #161b22; --border: #30363d; --accent: #58a6ff;
          --accent-soft: #1f2a48; --shadow: 0 1px 2px rgba(0,0,0,.5); }
}
html[data-theme="light"] { --bg: #ffffff; --fg: #1d2330; --muted: #5a6478;
  --card: #fafbfd; --border: #e1e5ec; --accent: #1f6feb;
  --accent-soft: #e9eefb; --shadow: 0 1px 2px rgba(0,0,0,.04); }
html[data-theme="dark"] { --bg: #0e1117; --fg: #e6edf3; --muted: #8b94a7;
  --card: #161b22; --border: #30363d; --accent: #58a6ff;
  --accent-soft: #1f2a48; --shadow: 0 1px 2px rgba(0,0,0,.5); }

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  line-height: 1.55; -webkit-font-smoothing: antialiased; }
header { padding: 1.5rem 2rem; border-bottom: 1px solid var(--border);
  display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
  position: sticky; top: 0; background: var(--bg); z-index: 10; }
header h1 { margin: 0; font-size: 1.6rem; }
.meta { color: var(--muted); font-size: 0.9rem; margin-top: 0.25rem; }
nav.toolbar { display: flex; gap: 0.5rem; align-items: center; }
nav.toolbar button {
  background: var(--accent-soft); color: var(--accent); border: 1px solid var(--border);
  border-radius: 6px; padding: 0.4rem 0.8rem; cursor: pointer; font-size: 0.9rem; }
nav.toolbar button:hover { background: var(--accent); color: var(--bg); }

main { max-width: 1200px; margin: 0 auto; padding: 1.5rem 2rem 3rem; }
section { margin-top: 2rem; }
h2 { font-size: 1.3rem; color: var(--accent); border-bottom: 1px solid var(--border);
  padding-bottom: 0.3rem; margin-top: 2rem; }
h3 { font-size: 1.05rem; margin-top: 1.4rem; }

.card { border: 1px solid var(--border); border-radius: 10px;
  padding: 1rem 1.4rem; margin: 1rem 0; background: var(--card); box-shadow: var(--shadow); }
.tag { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 999px;
  background: var(--accent-soft); color: var(--accent); font-size: 0.78rem; margin-right: 0.4rem; }
.tag.warn { background: #fff4e5; color: #ad6b00; }
.tag.danger { background: #fde7e7; color: #b42318; }
.tag.ok { background: #e7f6ec; color: #1a7f37; }

table { border-collapse: collapse; width: 100%; margin: 0.5rem 0; }
th, td { border: 1px solid var(--border); padding: 0.5rem 0.8rem;
  text-align: left; font-size: 0.95rem; }
th { background: var(--accent-soft); color: var(--accent);
  position: sticky; top: 0; cursor: pointer; user-select: none; }
th[data-sort-asc]::after  { content: " \25B2"; opacity: 0.7; }
th[data-sort-desc]::after { content: " \25BC"; opacity: 0.7; }
tbody tr:hover { background: var(--accent-soft); }

.gallery { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
.gallery figure { margin: 0; cursor: zoom-in; transition: transform 0.15s; }
.gallery figure:hover { transform: scale(1.02); }
.gallery img { width: 100%; border-radius: 6px; border: 1px solid var(--border);
  display: block; }
.gallery figcaption { font-size: 0.85rem; color: var(--muted); margin-top: 0.3rem; }

#lightbox { position: fixed; inset: 0; background: rgba(0,0,0,0.85);
  display: none; align-items: center; justify-content: center; z-index: 100; cursor: zoom-out; }
#lightbox img { max-width: 95vw; max-height: 95vh; border-radius: 6px; }
#lightbox.open { display: flex; }

pre { background: var(--code-bg); color: var(--code-fg); padding: 1rem;
  border-radius: 8px; overflow-x: auto; font-size: 0.85rem; }
code { font-family: 'SF Mono', Consolas, monospace; }

aside.cta { padding: 1.5rem 2rem; background: var(--accent-soft); border-radius: 10px;
  margin-top: 2rem; border-left: 4px solid var(--accent); }
aside.cta h3 { color: var(--accent); margin-top: 0; }

footer { margin-top: 3rem; padding: 1rem 2rem; border-top: 1px solid var(--border);
  font-size: 0.85rem; color: var(--muted); text-align: center; }

@media print {
  header, nav.toolbar, #lightbox { display: none !important; }
  main { max-width: 100%; padding: 0; }
  .card, table { page-break-inside: avoid; }
  body { background: white; color: black; }
}
"""

_DASHBOARD_JS = r"""
(function() {
  const root = document.documentElement;
  const btn = document.getElementById('theme-toggle');
  if (btn) {
    btn.addEventListener('click', () => {
      const current = root.getAttribute('data-theme') ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      root.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
    });
  }
  document.querySelectorAll('table.sortable th').forEach((th, idx) => {
    th.addEventListener('click', () => {
      const table = th.closest('table');
      const tbody = table.tBodies[0];
      const rows = Array.from(tbody.rows);
      const asc = !th.hasAttribute('data-sort-asc');
      table.querySelectorAll('th').forEach(h => {
        h.removeAttribute('data-sort-asc');
        h.removeAttribute('data-sort-desc');
      });
      th.setAttribute(asc ? 'data-sort-asc' : 'data-sort-desc', '');
      rows.sort((a, b) => {
        const av = a.cells[idx].textContent.trim();
        const bv = b.cells[idx].textContent.trim();
        const an = parseFloat(av), bn = parseFloat(bv);
        const cmp = (!isNaN(an) && !isNaN(bn))
          ? an - bn
          : av.localeCompare(bv, undefined, {numeric: true});
        return asc ? cmp : -cmp;
      });
      rows.forEach(r => tbody.appendChild(r));
    });
  });
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = lightbox ? lightbox.querySelector('img') : null;
  if (lightbox && lightboxImg) {
    document.querySelectorAll('.gallery img').forEach(img => {
      img.addEventListener('click', () => {
        lightboxImg.src = img.src;
        lightbox.classList.add('open');
      });
    });
    lightbox.addEventListener('click', () => lightbox.classList.remove('open'));
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') lightbox.classList.remove('open');
    });
  }
})();
"""


_AUDIENCE_SECTIONS: dict[str, list[str]] = {
    "academic": ["project", "methods", "figures", "conclusions", "references"],
    "executive": ["headline", "impact", "methods_summary", "next_steps"],
    "technical": ["project", "pipeline", "methods", "outputs", "reproducibility", "references"],
    "teaching": ["big_idea", "process", "findings", "try_it_yourself"],
}


def _gather_dashboard_data(root: Path) -> dict[str, Any]:
    from research_os.project_ops import load_state
    from research_os.tools.actions.state.path import list_paths

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
    if (root / "workspace").exists():
        for exp in (root / "workspace").iterdir():
            if not (exp.is_dir() and exp.name[:2].isdigit()):
                continue
            if exp.name.endswith("__DEAD_END"):
                continue
            conc = exp / "conclusions.md"
            if conc.exists():
                conclusions.append({"path": exp.name, "text": conc.read_text()})
            figs_dir = exp / "outputs" / "figures"
            if figs_dir.exists():
                for f in sorted(figs_dir.rglob("*")):
                    if f.suffix.lower() in {".png", ".svg", ".jpg", ".jpeg"}:
                        figures.append(
                            {"path": exp.name, "rel": f.relative_to(root).as_posix(), "name": f.name}
                        )
            reps = exp / "outputs" / "reports"
            if reps.exists():
                for f in sorted(reps.rglob("*.md")):
                    reports.append(
                        {
                            "path": exp.name,
                            "rel": f.relative_to(root).as_posix(),
                            "name": f.name,
                            "text": f.read_text()[:2000],
                        }
                    )

    mermaid_path = root / "workspace" / "workflow.mermaid"
    mermaid = mermaid_path.read_text() if mermaid_path.exists() else ""

    return {
        "state": state,
        "paths": paths,
        "methods": methods,
        "citations": citations,
        "conclusions": conclusions,
        "figures": figures,
        "reports": reports,
        "mermaid": mermaid,
    }


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _status_tag(status: str) -> str:
    return {"completed": "ok", "active": "", "dead_end": "danger",
            "missing_on_disk": "warn"}.get(status, "")


def _render_section(
    sec: str,
    data: dict[str, Any],
    path_table: str,
    gallery: str,
    conclusion_cards: str,
    report_cards: str,
) -> str:
    """Render an audience-section block."""
    titles = {
        "project": "Project overview",
        "headline": "Headline",
        "impact": "Impact",
        "methods": "Methods",
        "methods_summary": "Methods (summary)",
        "figures": "Figures",
        "conclusions": "Conclusions",
        "references": "References",
        "pipeline": "Pipeline",
        "outputs": "Outputs",
        "reproducibility": "Reproducibility",
        "next_steps": "Next steps",
        "big_idea": "The big idea",
        "process": "Process",
        "findings": "Findings",
        "try_it_yourself": "Try it yourself",
    }
    h = titles.get(sec, sec.replace("_", " ").title())

    if sec in ("project", "headline", "big_idea"):
        state = data["state"]
        return (
            f"<section><h2>{h}</h2><div class='card'>"
            f"<p><strong>Pipeline stage:</strong> {state.get('pipeline_stage', state.get('phase', 'init'))}</p>"
            f"<p><strong>Active path:</strong> {state.get('current_path', 'main')}</p>"
            f"<p><strong>Hypotheses tracked:</strong> {len(state.get('active_hypotheses', []) or [])}</p>"
            f"{path_table}</div></section>"
        )
    if sec in ("methods", "methods_summary"):
        body = data["methods"][:8000] if sec == "methods" else data["methods"][:1500]
        return (
            f"<section><h2>{h}</h2><div class='card'><pre>"
            + _escape_html(body or "(empty)")
            + "</pre></div></section>"
        )
    if sec == "figures" or sec == "findings":
        return f"<section><h2>{h}</h2>{gallery}</section>"
    if sec == "conclusions":
        return (
            f"<section><h2>{h}</h2>"
            + (conclusion_cards or "<p><em>None yet.</em></p>")
            + "</section>"
        )
    if sec == "references":
        return (
            f"<section><h2>{h}</h2><div class='card'><pre>"
            + _escape_html(data["citations"][:8000] or "(empty)")
            + "</pre></div></section>"
        )
    if sec == "pipeline":
        return (
            f"<section><h2>{h}</h2><div class='card'><pre>"
            + _escape_html(data["mermaid"] or "(no pipeline yet)")
            + "</pre><p class='meta'>Paste into a mermaid renderer to visualise.</p></div></section>"
        )
    if sec == "outputs":
        return (
            f"<section><h2>{h}</h2>"
            + (report_cards or "<p><em>No reports.</em></p>")
            + "</section>"
        )
    if sec == "reproducibility":
        return (
            "<section><h2>Reproducibility</h2><div class='card'>"
            "<p>Each experiment captures its own <code>environment/requirements.txt</code>. "
            "Re-run via <code>tool_audit_reproducibility</code>.</p></div></section>"
        )
    if sec == "impact":
        return (
            "<section><h2>Impact</h2><div class='card'>"
            "<p>Headline findings — see Conclusions below for full evidence chain.</p>"
            f"{conclusion_cards or '<p><em>Run experiments first.</em></p>'}"
            "</div></section>"
        )
    if sec == "next_steps":
        return (
            "<section><h2>Next steps</h2><div class='card'>"
            "<p>The team's recommended next actions are summarised in "
            "<code>workspace/analysis.md</code> (latest plan-next-step report).</p>"
            "</div></section>"
        )
    if sec == "process":
        return (
            f"<section><h2>{h}</h2><div class='card'>"
            "<ol><li>Collect data (inputs/raw_data)</li>"
            "<li>Read background literature (inputs/literature)</li>"
            "<li>Profile data + propose methods (workspace/methods.md)</li>"
            "<li>Run experiments (workspace/NN_*)</li>"
            "<li>Synthesise findings (synthesis/)</li></ol>"
            "</div></section>"
        )
    if sec == "try_it_yourself":
        return (
            f"<section><h2>{h}</h2><div class='card'>"
            "<p>Clone the repo, drop your own data into <code>inputs/raw_data/</code>, "
            "and ask the AI: <em>'fill out the intake'</em>.</p>"
            "</div></section>"
        )
    return f"<section><h2>{h}</h2><div class='card'>(section not yet rendered)</div></section>"


def create_dashboard(
    root: Path, title: str | None = None, audience: str = "academic"
) -> dict[str, Any]:
    """Render a single-file HTML dashboard at ``synthesis/dashboard.html``."""
    try:
        title = title or _project_name(root)
        audience = (audience or "academic").lower()
        if audience not in _AUDIENCE_SECTIONS:
            audience = "academic"

        data = _gather_dashboard_data(root)
        synthesis_dir = root / "synthesis"
        synthesis_dir.mkdir(parents=True, exist_ok=True)
        out_path = synthesis_dir / "dashboard.html"

        # Copy figures next to dashboard for offline use.
        figure_blocks: list[str] = []
        for fig in data["figures"]:
            src = root / fig["rel"]
            dest_dir = synthesis_dir / "dashboard_figures" / fig["path"]
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / src.name
            try:
                if not dest.exists():
                    shutil.copy2(src, dest)
                rel = dest.relative_to(synthesis_dir).as_posix()
                figure_blocks.append(
                    f'<figure><img src="{rel}" alt="{_escape_html(src.name)}" loading="lazy"/>'
                    f'<figcaption><span class="tag">{_escape_html(fig["path"])}</span>'
                    f'{_escape_html(src.name)}</figcaption></figure>'
                )
            except Exception:
                continue

        # Paths table (sortable).
        path_rows = "".join(
            f"<tr><td>{_escape_html(p['path_id'])}</td>"
            f"<td><span class='tag {_status_tag(p['status'])}'>{p['status']}</span></td>"
            f"<td>{'✓' if p['has_readme'] else '✗'}</td>"
            f"<td>{'✓' if p['has_conclusions'] else '✗'}</td></tr>"
            for p in data["paths"]
        )
        path_table = (
            "<table class='sortable'><thead><tr>"
            "<th>Path</th><th>Status</th><th>README</th><th>Conclusions</th>"
            "</tr></thead><tbody>" + path_rows + "</tbody></table>"
        ) if data["paths"] else "<p><em>No experiment paths yet.</em></p>"

        conclusion_cards = "".join(
            f'<div class="card"><h3>{_escape_html(c["path"])}</h3>'
            f'<pre>{_escape_html(c["text"][:4000])}</pre></div>'
            for c in data["conclusions"]
        )

        report_cards = "".join(
            f'<div class="card"><h3>{_escape_html(r["name"])} '
            f'<span class="tag">{_escape_html(r["path"])}</span></h3>'
            f'<pre>{_escape_html(r["text"])}</pre></div>'
            for r in data["reports"]
        )

        gallery = (
            f'<div class="gallery">{"".join(figure_blocks)}</div>'
            if figure_blocks
            else "<p><em>No figures generated yet.</em></p>"
        )

        sections = _AUDIENCE_SECTIONS[audience]
        section_html_blocks: list[str] = []
        for sec in sections:
            section_html_blocks.append(
                _render_section(sec, data, path_table, gallery, conclusion_cards, report_cards)
            )

        cta_html = ""
        if audience == "executive":
            cta_html = (
                "<aside class='cta'><h3>Request follow-up</h3>"
                "<p>For deeper analysis or to discuss recommendations, "
                "contact the research team via your usual channel.</p></aside>"
            )
        elif audience == "teaching":
            cta_html = (
                "<aside class='cta'><h3>Try it yourself</h3>"
                "<p>The data + scripts live in <code>workspace/</code>. "
                "Use <code>workspace/scratch/</code> as your sandbox.</p></aside>"
            )

        state = data["state"]
        meta = (
            f"<div class='meta'>Generated "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
            f" · Stage: <strong>{_escape_html(state.get('pipeline_stage', state.get('phase', 'init')))}</strong>"
            f" · Active path: <code>{_escape_html(state.get('current_path', 'main'))}</code>"
            f" · Audience: <code>{audience}</code></div>"
        )

        body = (
            "<!doctype html>\n"
            "<html lang='en'>\n<head>\n"
            "<meta charset='utf-8'>\n"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>\n"
            f"<title>{_escape_html(title)} · Research OS</title>\n"
            f"<style>{_DASHBOARD_CSS}</style>\n"
            "</head>\n<body>\n"
            "<header>\n"
            f"  <div><h1>{_escape_html(title)}</h1>{meta}</div>\n"
            "  <nav class='toolbar'>\n"
            "    <button id='theme-toggle' title='Toggle light/dark'>Theme</button>\n"
            "    <button onclick='window.print()' title='Print'>Print</button>\n"
            "  </nav>\n"
            "</header>\n"
            "<main>\n"
            + "\n".join(section_html_blocks)
            + cta_html
            + "</main>\n"
            f"<footer>Generated by Research OS · audience: {audience}</footer>\n"
            "<div id='lightbox'><img alt=''/></div>\n"
            f"<script>{_DASHBOARD_JS}</script>\n"
            "</body>\n</html>\n"
        )

        out_path.write_text(body)
        return {
            "status": "success",
            "dashboard_path": str(out_path.relative_to(root)),
            "audience": audience,
            "figures": len(figure_blocks),
            "paths": len(data["paths"]),
            "sections": sections,
        }
    except Exception as e:
        logger.exception("create_dashboard failed")
        return {"status": "error", "message": str(e)}
