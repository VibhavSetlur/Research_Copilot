---
agent_id: "peer_review_prep"
version: "1.0.0"
description: "Prepare response-to-reviewers template. Anticipate reviewer concerns and pre-draft responses."
domain_compatibility: ["all"]
depends_on: ["audit_validate"]
composes:
  - "methods_checklist"
produces:
  - "03_synthesis/peer_review_prep/cover_letter.md"
  - "03_synthesis/peer_review_prep/anticipated_comments.md"
  - "03_synthesis/peer_review_prep/response_template.md"
  - "03_synthesis/peer_review_prep/reviewer_checklist.json"
---

# Agent: Peer Review Preparation

## Purpose
After audit passes, anticipate reviewer concerns and prepare a response-to-reviewers template. Generates cover letter, anticipated comments with pre-drafted responses, and a reviewer checklist.

---

## Protocol

### Step 1: Load Project State
Read `03_synthesis/state_ledger.json`, `03_synthesis/manuscript/`, audit report, and methods checklist. Extract: study design, sample size, missing data rate, key findings, limitations stated.

### Step 2: Anticipate Reviewer Concerns by Study Design

**Observational studies:**
- "How did you address confounding by X?" → Response: list controlled confounders, residual confounding discussion
- "Why not use an instrumental variable / regression discontinuity?" → Response: justify identification strategy, acknowledge limitations
- "Selection bias concern" → Response: describe sampling frame, compare sample to population

**Small sample size (N < 100):**
- "Underpowered to detect effect" → Response: report observed power, acknowledge as limitation, frame as exploratory
- "Wide confidence intervals" → Response: report exact CIs, discuss precision

**Missing data (>10%):**
- "How does missingness affect results?" → Response: describe missingness mechanism, imputation method, sensitivity analysis results

**Multiple comparisons:**
- "No correction for multiple testing" → Response: apply Bonferroni/FDR, or justify why not needed (pre-registered hypotheses)

**Generalizability:**
- "Sample not representative" → Response: describe sample characteristics, discuss external validity limits

**Methodological:**
- "Why this method over X?" → Response: justify method choice, cite methodological literature
- "Assumption violations" → Response: report assumption checks, robustness analyses

### Step 3: Generate Cover Letter
Format:
1. Editor salutation
2. 1-paragraph summary: question, method, key finding
3. Novelty statement: what this adds to literature
4. Fit statement: why this journal
5. Required declarations: no dual submission, all authors approve, conflicts disclosed
6. Suggested reviewers (3 names with expertise and email)
7. Opposed reviewers (if any, with reason)

### Step 4: Generate Response Template
For each anticipated comment:
```
**Reviewer Comment:** [anticipated concern]
**Response:** [pre-drafted response]
**Manuscript change:** [specific text added/modified, with location]
```

### Step 5: Generate Reviewer Checklist
JSON with anticipated concerns, severity (major/minor), likelihood (high/medium/low), and whether response is ready.

### Step 6: Output
Save to `03_synthesis/peer_review_prep/`:
- `cover_letter.md` — submission-ready cover letter
- `anticipated_comments.md` — anticipated comments with responses
- `response_template.md` — fill-in template for actual reviewer comments
- `reviewer_checklist.json` — structured concern tracking

---

## Validation
- [ ] Study design identified
- [ ] At least 5 anticipated comments generated
- [ ] Each comment has pre-drafted response
- [ ] Each response references manuscript location
- [ ] Cover letter includes all required declarations
- [ ] Reviewer checklist JSON saved
- [ ] All outputs in `03_synthesis/peer_review_prep/`
