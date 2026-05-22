# Agentic Research OS

**An MCP-compliant Research Operating System.**

Connect Cursor, Claude, or any LLM to autonomously conduct literature reviews, execute exploratory data analysis, and compile publication-ready papers.

Agentic Research OS separates the *cognitive engine* (the AI models) from the *operating system layer* (memory tracking, execution sandboxing, data pipelining, and project operations). It provides a strict, rigid framework to stop LLMs from hallucinating file paths, generating poor code structures, and writing non-academic fluff.

## Features
- **Model Context Protocol (MCP)**: Run the OS securely within IDEs like Cursor via the MCP standard.
- **Strict Execution Pipelines**: Forces models to perform "Data Peek" protocols and automated EDA before blindly writing analysis code.
- **Visualization Governance**: Automatically injects strict styling (`research_style.mplstyle`) for high DPI, colorblind-friendly charts.
- **Publication-Grade Compilation**: Autonomously map figures into Markdown/LaTeX, generate `references.bib`, and run `pdflatex` to output PDFs.
- **Clean Workspace Taxonomy**:
```
workspace/
├── data/
│   ├── raw/           (Immutable inputs)
│   └── derived/       (Cleaned datasets)
├── figures/           (300 DPI PNGs/PDFs)
├── manuscript/        (Tex, Bib, and final PDF)
├── logs/              (Execution trails)
└── lab_notebook.md    (Live human-readable timeline)
```

## Universal Intake
Trigger the entire pipeline natively from the command line using natural language:

```bash
research-os run "Analyze the correlation between global shipping volume and ocean acidity from 2015-2025"
```

## Installation

```bash
pip install -e .
```

## Documentation

For full documentation on Agents, Skills, and architecture, refer to `docs/`.
