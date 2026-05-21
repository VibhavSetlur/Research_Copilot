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

<objective>
One sentence: what this skill does and when it fires.
</objective>

<routing_logic>
IF condition_1 → use method_A
ELIF condition_2 → use method_B
ELSE → use method_C with caveat
</routing_logic>

<protocol>
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
</protocol>

<constraints>
- Check assumption A before proceeding.
- Do not use method B if condition C is met.
</constraints>

<output_schema>
{
  "summary": "human-readable summary",
  "diagnostics": {"pass": true},
  "metrics": {}
}
</output_schema>
