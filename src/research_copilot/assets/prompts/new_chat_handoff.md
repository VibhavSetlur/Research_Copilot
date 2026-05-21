# New Chat Handoff Template

> Inject this at the start of a new conversation to restore context without re-reading entire history.
> Target: under 800 tokens.

---

## Context Restoration

You are resuming a Research Copilot project. Here is the current state:

### Project Overview
- **Project**: {{project_title}}
- **Current Phase**: {{current_phase}} (step {{current_step}})
- **Active Branch**: {{active_branch}}
- **Last Updated**: {{last_updated}}

### Phase Progress
{{phase_checkpoints}}

### Last 3 Decisions
{{last_decisions}}

### Key Findings So Far
{{key_findings}}

### Dead Ends to Avoid
{{dead_ends}}

### Pending Actions
{{pending_actions}}

### Data Scale Profile
{{data_scale_profile}}

---

## Instructions

1. Read `.research/cache/state.json` for the full structured state
2. Read the latest CTM from `.research/cache/context_transfer_memos/` if one exists
3. Read `03_synthesis/state_ledger.json` for the global ledger
4. Load only the skill needed for the next action — do NOT load all skills
5. Continue from the phase indicated above
6. If a CTM exists, read its `immediate_goals` and `open_questions` first
7. Do NOT repeat completed phases unless explicitly asked

## Quick Reference

- **Next agent to run**: {{next_agent}}
- **Current experiment directory**: {{experiment_dir}}
- **Token budget**: {{token_budget_used}} / {{token_budget_limit}} used
- **Resumable from**: {{resumable_from}}

## If State Is Missing

If any of the state files above do not exist, the project has not been initialized. Run `research_init` first.
