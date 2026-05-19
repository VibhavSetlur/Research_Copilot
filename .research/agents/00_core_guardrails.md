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
