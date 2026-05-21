---
skill_id: "progress_reporter"
version: "1.0.0"
category: "core"
depends_on: []
produces: ["stdout progress lines"]
complexity: "quick"
---

# Skill: Progress Reporter

## Purpose
Emit machine-parseable progress lines at each major step. Enables real-time feedback without verbose logging. Future UI can render progress bars from these lines.

---

## Protocol

### Step 1: Format Progress Line
Every progress line follows this format:
```
[PHASE: <phase_name> | STEP: <current>/<total> | STATUS: <status_text> | ETA: <estimate>]
```

### Step 2: Emit at Each Step
Call at the start of each major step. Update STATUS as step progresses:
- `starting` — step just began
- `running <subtask>` — actively working
- `complete` — step finished
- `failed: <reason>` — step failed

### Step 3: Phase Step Counts
Know the step count for each phase:
- `research_init`: 5 steps
- `literature_deep`: 7 steps
- `method_route`: 4 steps
- `data_scaffold`: 6 steps
- `execute_analysis`: 8 steps
- `compile_outputs`: 5 steps
- `audit_validate`: 9 steps
- `research_iterate`: variable (report as `X/?`)

### Step 4: ETA Estimation
- `quick` skills: ~30s
- `standard` skills: ~3 min
- `intensive` skills: ~10 min
- Adjust based on actual elapsed time from previous steps

---

## Examples

```
[PHASE: execute_analysis | STEP: 3/8 | STATUS: running assumption_checks | ETA: ~3 min]
[PHASE: execute_analysis | STEP: 3/8 | STATUS: running normality_tests | ETA: ~2 min]
[PHASE: execute_analysis | STEP: 4/8 | STATUS: complete | ETA: ~5 min]
[PHASE: literature_deep | STEP: 2/7 | STATUS: running semantic_scholar_search | ETA: ~1 min]
[PHASE: audit_validate | STEP: 7/9 | STATUS: running claim_trace | ETA: ~4 min]
[PHASE: compile_outputs | STEP: 1/5 | STATUS: starting manuscript_assembly | ETA: ~8 min]
```

---

## Machine Parsing
Line starts with `[PHASE:` and ends with `]`. Fields separated by ` | `. Each field is `KEY: VALUE`.

Regex: `^\[PHASE: (.+?) \| STEP: (\d+)/(\d+|\?) \| STATUS: (.+?) \| ETA: (.+?)\]$`

---

## Validation
- [ ] Line format matches `[PHASE: ... | STEP: ... | STATUS: ... | ETA: ...]`
- [ ] Phase name is valid
- [ ] Step numbers are accurate
- [ ] Status is descriptive
- [ ] ETA is reasonable estimate
