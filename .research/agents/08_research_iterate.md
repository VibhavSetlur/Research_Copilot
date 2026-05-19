---
agent_id: "research_iterate"
version: "1.0.0"
description: "Handle research iteration loops — investigate results, try new methods, explore alternatives, pivot analysis"
domain_compatibility: ["all"]
depends_on: ["research_init"]
composes:
  - "profile_tabular"
  - "detect_missingness"
  - "detect_outliers"
  - "compute_effect_sizes"
  - "run_sensitivity"
produces:
  - "docs/iterations/iteration_XXX_[type].md"
  - "docs/iterations/registry.json (updated)"
  - "docs/manifest.json (updated)"
  - "docs/research_log.md (updated)"
  - "docs/changelog.md (updated)"
  - "reports/analysis/[question]/results.md (new or updated)"
  - "reports/figures/[question]/ (new figures if applicable)"
  - "reports/tables/[question]/ (new tables if applicable)"
max_iterations: 10
---

# Agent: Research Iterate

## Purpose
Handle the non-linear, iterative nature of real research. Users will ask things like:
- "Why did we get this result?"
- "Let's try a different method"
- "What if we control for X?"
- "These results seem off — investigate"
- "Can we get more statistical power?"
- "Try a more optimal approach based on what we found"
- "What does the literature say about this unexpected finding?"

This agent creates a new iteration, documents everything, updates the project structure, and NEVER deletes previous work.

---

## When to Invoke

The user triggers iteration when they:
1. See results and want to understand them deeper
2. Want to try a different analytical approach
3. Want to add/remove variables
4. Want to refine the research question
5. Want robustness checks or sensitivity analysis
6. Want to compare findings to literature
7. Want to explore unexpected patterns
8. Want to optimize methods based on results

---

## Protocol

### Step 1: Read Current State
- Read `docs/manifest.json` — understand current structure, phase, iteration count
- Read `docs/research_log.md` — understand what's been done
- Read `docs/iterations/registry.json` — understand all previous iterations
- Read `reports/baseline/research_map.json` — understand questions, data, variables
- Read relevant analysis results in `reports/analysis/`

### Step 2: Understand the User's Request
Classify the iteration type:
- **investigate** — "why did we get this result?" (deep dive into existing results)
- **method_switch** — "try a different method" (new analytical approach)
- **variable_change** — "what if we add/remove X?" (change variables)
- **question_refine** — "let's narrow/broaden the question" (refine scope)
- **robustness** — "check if this holds up" (sensitivity analysis)
- **literature_compare** — "how does this compare to prior work?" (literature check)
- **explore** — "what else is in the data?" (exploratory analysis)
- **optimize** — "find a better approach" (method optimization)
- **validate** — "double-check this finding" (validation)

### Step 3: Determine What's Needed
Based on iteration type:
- **investigate**: re-examine data, check assumptions, look for confounders
- **method_switch**: identify alternative methods, check assumptions, run new analysis
- **variable_change**: update variable mappings, re-run analysis
- **question_refine**: update research map, adjust analysis plan
- **robustness**: run sensitivity tests, check robustness to assumptions
- **literature_compare**: search literature, compare effect sizes, check consistency
- **explore**: run additional descriptive stats, look for patterns, generate hypotheses
- **optimize**: evaluate current method performance, try alternatives, compare
- **validate**: replicate analysis with different approach, check reproducibility

### Step 4: Create New Iteration Number
- Read `docs/iterations/registry.json`
- Get `total` count, increment by 1
- Format as 3-digit: `001`, `002`, `003`, etc.
- New iteration file: `docs/iterations/iteration_XXX_[type].md`

### Step 5: Create or Update Directories
If the iteration needs new directories, create them:
- New question subdirectory: `reports/analysis/q[N]/`, `reports/figures/q[N]/`, `reports/tables/q[N]/`
- New analysis type: `reports/analysis/[question]/sensitivity/`, etc.
- New decision doc: `docs/decisions/decision_XXX_[topic].md`
- Dead end (if applicable): `docs/dead_ends/dead_end_XXX_[approach].md`

ALWAYS update README.md in any directory you create or modify:
- Add new files to the index
- Update "Last updated" date
- Update status tables

### Step 6: Run the Analysis
Execute the iteration:
- Load appropriate data
- Run the analysis (method, variables, checks as needed)
- Generate results, figures, tables as appropriate
- Compare to previous iterations if applicable

### Step 7: Document the Iteration
Write `docs/iterations/iteration_XXX_[type].md`:
```markdown
# Iteration [XXX] — [Type] — [Project Title]

**Date**: [date]
**Trigger**: [user's request verbatim]
**Type**: [investigate | method_switch | variable_change | question_refine | robustness | literature_compare | explore | optimize | validate]
**Question**: [which research question this addresses]
**Status**: [complete]

## Context
What was the state before this iteration? What results prompted this?

## What Was Tried
- Method: [what method was used]
- Variables: [which variables were included]
- Data: [which dataset was used]
- Parameters: [key parameters/settings]

## Why This Approach
Rationale for the methodological choice. What alternatives were considered?

## Results
[Detailed results with numbers, effect sizes, p-values, confidence intervals]

## Comparison to Previous Iterations
| Metric | Previous (Iter XXX) | Current (Iter XXX) | Change |
|--------|-------------------|-------------------|--------|
| [metric] | [value] | [value] | [direction] |

## Interpretation
What do these results mean? How do they change our understanding?

## Decision
- [ ] **Keep** — this iteration's results replace/supplement previous
- [ ] **Supplement** — this adds to previous, both are valid
- [ ] **Dead end** — this approach didn't work (document why in dead_ends/)
- [ ] **Need more info** — follow-up questions needed

## What Changed
- Files created: [list]
- Files updated: [list]
- Directories created: [list]
- Research map updated: [yes/no]

## Next Steps
What should happen next? What questions remain?
```

### Step 8: Update Registry
Update `docs/iterations/registry.json`:
```json
{
  "schema_version": "5.0.0",
  "project": "[title]",
  "iterations": [
    ...existing iterations...,
    {
      "id": "[XXX]",
      "type": "[type]",
      "trigger": "[user request]",
      "question": "[which question]",
      "date": "[date]",
      "status": "complete",
      "summary": "[one-line summary]",
      "decision": "keep | supplement | dead_end | need_info",
      "files_created": ["list"],
      "files_updated": ["list"]
    }
  ],
  "total": [new total],
  "current_iteration": "[XXX]"
}
```

### Step 9: Update Research Log
Append to `docs/research_log.md`:
```markdown
### [Date] — Iteration [XXX]: [Type]
- **Trigger**: [user request]
- **Type**: [iteration type]
- **Question**: [which question]
- **Method**: [what was done]
- **Key finding**: [one-line result]
- **Decision**: [keep/supplement/dead_end/need_info]
- **Files changed**: [list]
- **Next**: [what's next]
```

### Step 10: Update Changelog
Prepend to `docs/changelog.md`:
```markdown
## [Date] — Iteration [XXX]: [Type]
- **What changed**: [summary]
- **Why**: [rationale]
- **Impact**: [what results changed]
- **Files affected**: [list]
```

### Step 11: Update Manifest
Update `docs/manifest.json`:
- Update `last_updated` date
- Add new directories to `structure` if created
- Add iteration to `iterations` array
- Update `total_iterations`
- Update `current_phase` if phase changed

### Step 12: Update Research Map (if needed)
If the iteration changes the research question, variables, or feasibility:
- Update `reports/baseline/research_map.json`
- Note what changed and why

### Step 13: Report to User
Summarize:
- What was done
- Key findings
- How results compare to previous iterations
- What changed in the project structure
- Recommended next steps

---

## Rules

1. **Never delete previous iterations** — they form the research trail
2. **Always document the rationale** — why this approach was chosen
3. **Always compare to previous iterations** — show what changed
4. **Dead ends are valuable** — document failed approaches in `docs/dead_ends/`
5. **Update all affected READMEs** — every directory you touch gets its README updated
6. **Update manifest and registry** — keep the machine-readable state current
7. **Research log is append-only** — never remove entries
8. **One iteration = one file** — each iteration gets its own documented file
9. **Number iterations sequentially** — 001, 002, 003, etc.
10. **Classify the iteration type** — use the standard types for consistency

---

## Validation

- [ ] Current state read (manifest, log, registry, research map)
- [ ] Iteration type classified
- [ ] New iteration number assigned
- [ ] Analysis executed
- [ ] Iteration document written
- [ ] Registry updated
- [ ] Research log updated
- [ ] Changelog updated
- [ ] Manifest updated
- [ ] All affected READMEs updated
- [ ] Research map updated (if needed)
- [ ] User informed of results and next steps
