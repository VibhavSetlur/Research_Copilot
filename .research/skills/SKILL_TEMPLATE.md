---
skill_id: "skill_id_here"
version: "1.0.0"
category: "data|analysis|literature|visualization|writing|audit|integration"
domain_compatibility: ["all"]
required_tools: []
depends_on: []
produces: []
complexity: "basic|intermediate|advanced"
---

# Skill: {Human-Readable Name}

## Purpose
One sentence: what this skill does and when it fires.

## When to Use
- Condition A
- Condition B

## When NOT to Use
- Condition A
- Condition B

## Decision Protocol

### Routing Logic
```
IF condition_1 → use method_A
ELIF condition_2 → use method_B
ELSE → use method_C with caveat
```

### Method Selection Criteria
| Condition | Method | Rationale |
|-----------|--------|-----------|
| criterion | method_name | why this choice |

## Execution Protocol

### Step 1: Pre-checks
- Validate inputs
- Check assumptions
- Flag violations before proceeding

### Step 2: Core Procedure
- Numbered steps with branching
- Include parameter defaults
- Note where domain conventions differ

### Step 3: Diagnostics
- Run diagnostic tests
- Interpret each result
- Branch based on pass/fail

### Step 4: Robustness
- Sensitivity checks
- Alternative specifications
- Compare conclusions across methods

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| test_name | p > 0.05 | what failure means | what to do next |

### Red Flags
- **Flag 1**: symptom → likely cause → remediation
- **Flag 2**: symptom → likely cause → remediation

## Domain Conventions

| Domain | Reporting Standard | Effect Size | Significance |
|--------|-------------------|-------------|--------------|
| Psychology | APA 7th | Cohen's d | p < .05 |
| Epidemiology | STROBE | OR/RR | p < .05 |
| Econometrics | AEA | β coefficients | p < .05, .01, .001 |

## Reporting Template
> "We [method] to [purpose]. [Key result with statistic, CI, p-value]. [Diagnostic result]. [Interpretation in domain terms]."

## Output Specification
- `path/to/output.json`: structure summary
- `path/to/output.md`: human-readable summary

## Validation Checks
- [ ] Output contains required fields
- [ ] Results within theoretical bounds
- [ ] Diagnostics logged
- [ ] No unhandled warnings
