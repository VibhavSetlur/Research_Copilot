"""Standalone implementations for all §4.2 missing MCP tools.

Each function is self-contained and can be called directly from server.py handlers.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger("research.tools")


# ---------------------------------------------------------------------------
# tool.latex.compile
# ---------------------------------------------------------------------------


def latex_compile(root: Path) -> dict:
    """Run pdflatex + bibtex on synthesis/paper.tex.

    Runs: pdflatex → bibtex → pdflatex (×2) for proper cross-referencing.
    Returns dict with 'pdf_path', 'log', 'success', and optional 'warning'.
    """
    tex_path = root / "synthesis" / "paper.tex"
    if not tex_path.exists():
        return {
            "pdf_path": None,
            "success": False,
            "log": "",
            "warning": "synthesis/paper.tex not found",
        }

    pdflatex = shutil.which("pdflatex")
    bibtex = shutil.which("bibtex")
    if not pdflatex:
        return {
            "pdf_path": None,
            "success": False,
            "log": "",
            "warning": "pdflatex not found. Install TeX Live.",
        }

    synthesis_dir = tex_path.parent
    log_lines: list[str] = []
    success = True

    def _run_pdflatex() -> bool:
        result = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=str(synthesis_dir),
            capture_output=True,
            text=True,
            timeout=120,
        )
        log_lines.append(
            result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
        )
        return result.returncode == 0

    def _run_bibtex() -> bool:
        if not bibtex:
            log_lines.append(
                "[WARN] bibtex not found — skipping bibliography compilation"
            )
            return True
        aux = tex_path.with_suffix(".aux")
        if not aux.exists():
            return True
        result = subprocess.run(
            [bibtex, aux.name],
            cwd=str(synthesis_dir),
            capture_output=True,
            text=True,
            timeout=60,
        )
        log_lines.append(
            result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout
        )
        return True

    # Run 1: pdflatex
    if not _run_pdflatex():
        success = False
        log_lines.append("[ERROR] First pdflatex run failed")

    if success:
        _run_bibtex()

    # Run 2: pdflatex
    if success and not _run_pdflatex():
        success = False
        log_lines.append("[ERROR] Second pdflatex run failed")

    # Run 3: pdflatex (resolve all cross-refs)
    if success and not _run_pdflatex():
        success = False
        log_lines.append("[ERROR] Third pdflatex run failed")

    pdf_path = tex_path.with_suffix(".pdf")
    return {
        "pdf_path": str(pdf_path.absolute()) if pdf_path.exists() else None,
        "success": success,
        "log": "\n".join(log_lines[-50:]),
        "warning": None
        if success
        else "LaTeX compilation failed — see log for details",
    }
