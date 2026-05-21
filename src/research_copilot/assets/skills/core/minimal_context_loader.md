---
skill_id: "minimal_context_loader"
version: "1.0.0"
category: "core"
depends_on: []
produces: []
complexity: "quick"
---

# Skill: Minimal Context Loader

## Purpose
Load only what's needed for each task. Never load all skills or agents at once. Stay under 20k tokens of context per task.

---

## Protocol

### Rule 1: One Skill at a Time
Before any analysis, call `rcp skills <skill_name>` to load exactly 1 skill. Match the skill to the current step. Do NOT load all skills.

### Rule 2: One Agent at a Time
Before invoking an agent, call `rcp agent <agent_name>` to load exactly 1 agent. Do NOT preload multiple agents.

### Rule 3: Load State Once
Read `03_synthesis/state_ledger.json` at the start of each conversation. Use it as the single source of truth for phase, decisions, and file pointers.

### Context Budget

| Resource | Token Cost | When to Load |
|----------|-----------|--------------|
| 1 skill | ~2,000 | Before executing a specific step |
| 1 agent | ~3,000 | Before invoking an agent |
| 1 workflow | ~1,000 | When routing a multi-step task |
| State ledger | ~2,000 | At conversation start (once) |
| **Total per task** | **<20,000** | **Hard limit** |

### Loading Order

1. Read state ledger (~2k tokens) — understand current phase
2. Load 1 skill (~2k tokens) — the one needed for the next step
3. If agent needed: load 1 agent (~3k tokens)
4. Execute step
5. Release context: skill context is discarded after step completes
6. Repeat for next step

### Anti-Patterns
- Loading all 40+ skills at once (~80k tokens) — NEVER do this
- Pre-loading agents you might need later — load on demand
- Re-reading state ledger every step — read once, cache in memory
- Loading full literature corpus — use knowledge graph queries instead

### When to Break the Rule
Only load multiple skills simultaneously when a single step explicitly requires cross-skill coordination (e.g., visualization + statistical test in one figure). Maximum 4 skills at once.
