---
skill_id: "write_imrad"
version: "7.0.0"
category: "writing"
domain_compatibility: ["all"]
required_tools: ["python", "openai|anthropic|litellm", "pandoc"]
depends_on: ["write_methods_section", "write_results_narrative", "synthesize_literature", "generate_bibtex"]
produces: ["reports/research_findings.md"]
complexity: "advanced"
---

# Skill: Write IMRAD Manuscript

## Purpose
Assemble a complete IMRAD-format academic manuscript from component sections, with integrated literature review, results interpretation, and formatted references.

## When to Use
- All component sections written
- Final manuscript assembly
- Ready for submission or review

## When NOT to Use
- Sections not yet complete
- Only a report (not manuscript) needed

## Execution Protocol

### Step 1: Introduction
- Context: background and significance
- Literature gap: what is unknown (from literature synthesis)
- Research question: clearly stated
- Hypotheses: specific and testable
- Objectives: primary and secondary

### Step 2: Methods
- Insert methods_section.md
- Verify: all analysis methods described
- Verify: ethical considerations included

### Step 3: Results
- Insert results_section.md
- Verify: all hypotheses addressed
- Verify: tables and figures referenced correctly
- Add: table and figure captions

### Step 4: Discussion
- Interpret findings: what do results mean?
- Compare to literature: consistent or contradictory with prior work?
- Mechanisms: plausible explanations for findings
- Limitations: statistical, methodological, generalizability
- Implications: theoretical, practical, policy
- Future research: specific directions

### Step 5: References
- Insert formatted references from references.bib
- Use pandoc-citeproc for citation formatting
- Verify: all in-text citations have reference entries
- Verify: all reference entries cited in text

### Step 6: Final Checks
- Title: concise, informative, includes key variables
- Abstract: structured (Background, Methods, Results, Conclusion)
- Keywords: 3-6 domain-appropriate terms
- Word count: within journal limits
- Formatting: journal-specific style guide

## Output Specification
- `reports/research_findings.md`: complete IMRAD manuscript

## Validation Checks
- [ ] All four IMRAD sections present
- [ ] In-text citations match reference list
- [ ] Tables and figures referenced
- [ ] Abstract matches manuscript content
- [ ] Word count within limits
