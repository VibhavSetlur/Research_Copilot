#!/usr/bin/env bash
# Example 01: Literature Review Workflow

echo "Running Literature Review Workflow..."

# Create a clean workspace for this example
mkdir -p workspace

research-os run "Conduct a comprehensive literature review on the applications of Graph Neural Networks in Drug Discovery. Retrieve at least 5 recent papers, summarize their methodologies, and compile a structured Markdown report."

echo "Workflow complete. Check workspace/manuscript/ for your report and workspace/lab_notebook.md for the step-by-step reasoning."
