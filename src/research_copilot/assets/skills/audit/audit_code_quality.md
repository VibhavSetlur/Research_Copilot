---
skill_id: "audit_code_quality"
version: "7.0.0"
category: "audit"
domain_compatibility: ["all"]
required_tools: ["python", "pylint|flake8", "black"]
depends_on: []
produces: ["audit/code_quality_audit.json"]
complexity: "basic"
---

# Skill: Code Quality Audit

## Purpose
Assess analysis code for quality, readability, reproducibility, and best practices.

## When to Use
- After analysis scripts written
- Before sharing code publicly
- For code review

## When NOT to Use
- Code is exploratory/throwaway
- Only results matter (not code)

## Execution Protocol

### Step 1: Style Check
- PEP 8 compliance: naming, indentation, line length
- Consistent formatting: run black formatter
- Docstrings: all functions have docstrings with Args, Returns, Examples
- Comments: explain why, not what

### Step 2: Reproducibility Check
- Random seeds set for all stochastic operations
- No hardcoded paths: use relative paths or config
- No hardcoded parameters: use config files or function arguments
- Version control: all code in git with meaningful commits

### Step 3: Error Handling
- Try/except blocks for file I/O and API calls
- Meaningful error messages (not just "Error occurred")
- Input validation: check types, ranges, missing values
- Logging: not just print statements

### Step 4: Complexity Check
- Function length: < 50 lines (refactor if longer)
- Nesting depth: < 4 levels
- Cyclomatic complexity: < 10 per function
- No code duplication: DRY principle

### Step 5: Dependency Check
- All imports used (no unused imports)
- No circular imports
- Dependencies listed in requirements.txt
- No deprecated function calls

## Diagnostics & Interpretation

| Check | Pass | Fail → Action |
|-------|------|---------------|
| PEP 8 | No violations | Run black and fix remaining |
| Docstrings | All functions documented | Add missing docstrings |
| Reproducibility | Seeds set, no hardcoded values | Fix reproducibility issues |
| Complexity | All functions < 50 lines | Refactor long functions |

## Output Specification
- `audit/code_quality_audit.json`: per-file quality scores, violation details, recommendations

## Validation Checks
- [ ] All Python files pass style check
- [ ] All functions documented
- [ ] No hardcoded paths or parameters
- [ ] Random seeds set
