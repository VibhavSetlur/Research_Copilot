import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("research.tools.synthesize")


def synthesize_workspace(
    root: Path, output_format: str = "markdown", section: str | None = None
) -> dict[str, Any]:
    """Gather all workspace findings and compile a publication-ready paper or specific section."""
    try:
        synthesis_dir = root / "synthesis"
        synthesis_dir.mkdir(parents=True, exist_ok=True)

        if section:
            section_path = root / "workspace" / f"{section}.md"
            section_content = section_path.read_text() if section_path.exists() else f"*No {section} recorded.*"
            dest_md = synthesis_dir / f"{section}.md"
            dest_md.write_text(section_content)
            return {
                "status": "success",
                "message": f"Generated {section}.md in synthesis/",
                "path": str(dest_md.relative_to(root)),
            }

        analysis_path = root / "workspace" / "analysis.md"
        methods_path = root / "workspace" / "methods.md"
        citations_path = root / "workspace" / "citations.md"

        analysis_content = analysis_path.read_text() if analysis_path.exists() else ""
        methods_content = methods_path.read_text() if methods_path.exists() else ""
        citations_content = (
            citations_path.read_text() if citations_path.exists() else ""
        )

        synthesis_dir = root / "synthesis"
        synthesis_dir.mkdir(parents=True, exist_ok=True)

        figures_dir = root / "workspace" / "figures"
        figure_files = sorted(
            f.relative_to(root).as_posix()
            for f in figures_dir.rglob("*")
            if f.is_file() and f.suffix in {".png", ".pdf", ".svg", ".jpg", ".jpeg"}
        )

        paper_sections = {
            "title": "# Research Synthesis Report\n\n",
            "metadata": f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*\n\n",
            "methods": "## Methods\n\n"
            + (methods_content if methods_content else "*No methods recorded.*\n\n"),
            "analysis": "## Analysis\n\n"
            + (analysis_content if analysis_content else "*No analysis recorded.*\n\n"),
            "figures": "## Figures\n\n"
            + (
                "\n".join(f"![{f}]({f})" for f in figure_files) + "\n\n"
                if figure_files
                else "*No figures generated.*\n\n"
            ),
            "citations": "## Citations\n\n"
            + (
                citations_content
                if citations_content
                else "*No citations recorded.*\n\n"
            ),
        }

        paper_content = "".join(paper_sections.values())

        paper_md = synthesis_dir / "paper.md"
        paper_md.write_text(paper_content)

        result = {
            "status": "success",
            "paper_path": str(paper_md.relative_to(root)),
            "sections": list(paper_sections.keys()),
            "figure_count": len(figure_files),
            "word_count": len(paper_content.split()),
        }

        if output_format in ("latex", "both"):
            from research_os.tools.actions.latex import latex_compile

            tex_path = synthesis_dir / "paper.tex"
            tex_content = _markdown_to_latex(paper_content)
            tex_path.write_text(tex_content)
            compile_result = latex_compile(root)
            result["latex_compile"] = compile_result
            if output_format == "latex":
                result["paper_path"] = str(tex_path.relative_to(root))

        return result

    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        return {"error": f"Synthesis failed: {e}"}


def _markdown_to_latex(md: str) -> str:
    lines = md.split("\n")
    tex_lines = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{graphicx}",
        r"\usepackage{hyperref}",
        r"\usepackage{geometry}",
        r"\geometry{margin=1in}",
        r"\title{Research Synthesis Report}",
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
