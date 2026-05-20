# Core Guardrails

> Injected into every agent. Non-negotiable.

---

## 1. Cite Everything

Every methodological choice, interpretation, and claim needs a source. Hierarchy:
1. Domain standards (STROBE, APA, etc.)
2. Peer-reviewed methodology papers
3. Empirical literature in the domain
4. Statistical textbooks
5. Software docs

Format: `Decision: [what] | Source: [Author, Year, DOI] | Confidence: HIGH|MEDIUM|LOW`

## 2. Compare to Literature

After every finding, compare to what prior research found. If results differ, explain why.

## 3. Try to Disprove Yourself

After reaching a conclusion, ask: what would change my mind? Run at least one sensitivity check.

## 4. Iterate Only When Needed

Don't loop 3 times by default. Only iterate when:
- An assumption test fails
- A result contradicts well-established literature
- The finding is fragile (depends on arbitrary choices)
- Something is ambiguous

## 5. Methods Log

Every decision, pivot, or failure appends to `reports/logs/methods_log.md`:

```
---
Timestamp: {ISO 8601}
Agent: {agent}
Phase: {observe|test|validate|pivot}
Decision: {what was chosen}
Source: {Author, Year, DOI}
If PIVOT:
  Trigger: {what caused it}
  Alternative: {new approach}
---
```

## 6. Code Standards

- Python 3.10+, type hints, docstrings with methodological Notes
- Comments explain WHY (scientific reasoning), never WHAT
- Set random seeds before stochastic operations
- pip-installable packages preferred

## 7. Reporting

- No colloquial language
- Exact p-values with test stat, df, test name
- Effect sizes mandatory
- Confidence intervals for every estimate
- Non-significant results reported with same detail

## 8. Data Provenance

- `inputs/data/` is immutable
- Every output file: YAML frontmatter with producing_skill, agent, timestamp, input hashes

## 9. Figures

- 300 DPI, colorblind-safe palettes
- Diagnostic sub-panels per analysis type
- On-image statistical annotations

## 10. Tables

- Publication-ready, no vertical lines
- Significance in footnotes only
- Save as .md and .tex (booktabs)

## 11. Dead End Enforcement (MANDATORY)

BEFORE writing any new code, trying any new method, or choosing any new approach:

1. **Read ALL files in `docs/dead_ends/`** — understand what has already failed
2. **Check your planned approach against dead ends** — if it matches, DO NOT try it
3. **Choose a different approach** — document why the dead end was rejected
4. **If ALL approaches are dead ends** — report to user, do not loop infinitely

This prevents the agent from getting stuck in infinite loops, repeatedly trying the same
failed technique (e.g., Multiple Imputation, a specific model, a data cleaning method).

Dead ends are created when:
- An approach produces invalid results
- A method's assumptions are violated and cannot be fixed
- A technique fails to converge
- A result is contradicted by robustness checks
- The user explicitly rejects an approach

Format dead end entries as:
```
Approach: [what was tried]
Reason: [why it failed]
Date: [when]
Alternatives to try: [what to try instead]
```

## 12. State Ledger & Checkpoint System

The global research ledger (`.research/cache/state.json`) is the single source of truth.

- **Read state** before starting any phase: `research state`
- **Update state** after completing any phase using `ResearchLedger.complete_phase()`
- **Save checkpoints** at phase boundaries using `CheckpointManager.save()`
- **Resume** from failures: `research resume --from <phase>`
- **Never** skip state updates — every phase transition must be recorded

## 13. Token Budget Management

Monitor context window usage via the token budget in state.json.

- At 60%: summarize completed phases into 3-sentence abstracts
- At 80%: flush non-essential skill docs, keep only active skill
- At 90%: force checkpoint, split into new conversation with state transfer
- Check budget: `research budget`

## 14. Atomic Instruction Format

Every agent instruction must follow this format so any LLM can execute it without ambiguity:

1. EXACTLY ONE action per numbered step
2. Each step specifies: what to DO, what FILE to read, what FILE to write
3. No compound instructions ("do X and also Y and then Z")
4. Decision branches are IF/ELIF/ELSE, never ambiguous prose
5. Every output file has exact path and schema specified
6. Every input file has exact path specified
7. Verification: every step ends with a checkable condition

## 15. Anti-Hallucination Rules (non-negotiable)

1. Never invent a citation. If you cannot find a real DOI, write [CITATION NEEDED].
2. Never invent a p-value, effect size, or sample size. Compute or mark [COMPUTED NEEDED].
3. Never assume a file exists without checking via ls or Path.exists().
4. Never assume a variable name exists in data without checking schema_cache.json.
5. If unsure about a library API, invoke Context7 before writing code.
   CODE GENERATION RULE: For ANY library function call, first verify the 
   current API signature via Context7. Training knowledge of library APIs 
   may be outdated. This is non-negotiable and prevents broken code.
6. If a number in your output cannot be traced to a file in the project, flag it.
7. When uncertain: understate, not overstate. Use "may" not "demonstrates".

## 16. Skill Loading Efficiency

Before executing any task:
1. Query the skill index (`.research/cache/skill_index.json` if available)
2. Load ONLY skills directly relevant to the current step
3. If unsure which skill applies, match by keyword
4. Never load more than 4 skills simultaneously unless explicitly required
