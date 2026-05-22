# Example Walkthrough

This document shows a typical conversation flow between a Researcher and the AI powered by Research OS v3.0.

**User:** "I have a dataset of patient responses in `inputs/raw_data/patients.csv`. I want to know if Drug A is better than Drug B."

**AI:** (Calls `sys.workspace.scaffold` to set up the directories, then calls `sys.guidance.get("domain_analysis")` to understand the domain.)
"I have scaffolded the workspace. Based on the domain analysis protocol, this appears to be a clinical trial dataset. I will enforce CONSORT reporting standards. Next, I will run the methodology selection protocol to determine the best statistical approach."

**User:** "Go ahead."

**AI:** (Calls `sys.guidance.get("methodology_selection")`. Reads `patients.csv` via `sys.file.read` or by writing a quick EDA script and executing it via `tool.python.exec`. Discovers the data is skewed.)
"The data is highly skewed. The methodology protocol suggests using a Mann-Whitney U test rather than a standard t-test. I will create a branch for this experiment."
(Calls `sys.branch.create(name="mann_whitney_test")`)

**User:** "Sounds good, run the analysis."

**AI:** (Writes `workspace/scripts/01_analysis.py`, executes it via `tool.python.exec`, logs the results to `workspace/analysis.md`, and saves the figures to `workspace/figures/`.)
"The analysis is complete. The p-value is 0.03, indicating a statistically significant difference. I have logged the methods used and the results."

**User:** "Great. Let's start writing."

**AI:** (Calls `sys.guidance.get("writing_standards")` and begins drafting the manuscript in `synthesis/paper.tex`.)
