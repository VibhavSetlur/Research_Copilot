# The Guidance System

Instead of bundling static, black-box Python functions for things like t-tests, Research OS relies on **Guidance Protocols**. 

## What is a Guidance Protocol?

A Guidance Protocol is a YAML-based decision graph that tells the AI *how* to approach a specific phase of the research lifecycle. When an AI receives a protocol via `sys.guidance.get`, it reads the structured steps, expected outputs, and checkpoints, then autonomously writes the code or performs the web searches needed to fulfill those steps.

## Core Protocols

Located in `src/research_os/protocols/`:

1. **`domain_analysis.yaml`**: Identifies the scientific domain and dictates necessary reporting standards (e.g., STROBE, CONSORT) and common pitfalls.
2. **`research_design.yaml`**: Helps the AI map a research question to a formal design (RCT, DiD, exploratory, etc.).
3. **`methodology_selection.yaml`**: Recommends statistical or computational approaches based on data profiles.
4. **`literature_search.yaml`**: Provides a rigorous workflow for Boolean queries, deduplication, and snowballing.
5. **`evidence_synthesis.yaml`**: Extracts claims and assesses evidence strength.
6. **`analysis_plan.yaml`**: Dictates how to structure and scaffold numbered experiment directories.
7. **`writing_standards.yaml`**: Enforces the IMRAD format and strict, non-causal language where appropriate.
8. **`figure_guidelines.yaml`**: Best practices for publication-ready visual styling.
9. **`reproducibility.yaml`**: Enforces pinned dependencies, random seeds, and checksums.
10. **`audit_and_validation.yaml`**: The final check before a paper is compiled.

## How the AI uses them

The AI should lazily load these protocols as needed. For example, if a user says "Let's begin the methodology selection," the AI will call `sys.guidance.get(protocol_name="methodology_selection")`, read the instructions, profile the data, suggest the methods to the user, and once approved, write the actual Python code to execute it.
