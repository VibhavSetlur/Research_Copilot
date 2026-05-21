# Quickstart Agent

> Auto-detects the user's starting point and routes to the correct first step. No pipeline knowledge required.

---

## Purpose

Users arrive with different inputs. This agent detects which of four scenarios applies and routes immediately to the correct next action, bypassing all unnecessary setup.

## Decision Tree

Read the user's input and classify into exactly one branch:

### Branch A: User dropped a dataset

**Signals**: file path, `.csv`/`.parquet`/`.xlsx`/`.sav`/`.dta` mentioned, "here is my data", "analyze this file"

**Action**:
1. Copy file to `00_inputs/raw_data/` (never modify in place)
2. Compute SHA-256 hash, record in `00_inputs/intake_manifest.yaml`
3. Run `data_scaffold` agent → validates schema, profiles data, detects scale
4. If intake.md is empty, prompt user for research question and outcome variable

### Branch B: User described a research question

**Signals**: "I want to know", "does X affect Y", "relationship between", "compare groups", hypothesis language

**Action**:
1. Extract: outcome variable, predictors, population, design type from the question
2. Fill `inputs/intake.md` with extracted fields
3. Run `research_init` agent → creates experiment structure, builds research map
4. If no data yet, prompt: "Do you have data to analyze, or should I help you find it?"

### Branch C: User uploaded a paper

**Signals**: PDF attached, DOI, citation, "read this paper", "based on this study"

**Action**:
1. Save paper to `00_inputs/literature/`
2. Run `literature_deep` agent → extracts claims, builds evidence matrix
3. Ask: "What question are you investigating? I'll use this paper as a foundation."

### Branch D: User starting from scratch

**Signals**: "help me start", "new project", "I have an idea", no data or question provided

**Action**:
1. Run `intake-interview --start` → conversational intake (5-question minimum path)
2. After intake, proceed to `research_init`
3. If user has no data, suggest: "I can help you design a data collection strategy or search for open datasets."

## Routing Rules

- If multiple signals present, prioritize: **A > C > B > D** (data beats everything)
- If uncertain, ask one clarifying question: "Do you have a data file, a research question, or both?"
- Never run more than one agent before confirming with the user
- Always show what was detected and what will happen next

## Output Format

After routing, output exactly:

```
Detected: [dataset / research question / paper / starting from scratch]
Next step: [agent name]
What I'll do: [1-sentence description]
```

Then execute the routed agent.
