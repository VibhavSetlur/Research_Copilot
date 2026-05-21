# CLI Reference

All Research Copilot commands. The CLI is available as both `rcp` and `research`.

## Core Commands

| Command | Description |
|---------|-------------|
| `rcp init <name>` | Create a new Research Copilot project |
| `rcp status` | Project state, token budget, pipeline status, next step |
| `rcp scan` | Scan inputs, build research map |
| `rcp map` | Show research map (grounding context) |
| `rcp intake` | Show intake form status |
| `rcp preflight` | Run environment preflight checks |

## Intake Interview

| Command | Description |
|---------|-------------|
| `rcp intake-interview --start` | Start conversational intake interview |
| `rcp intake-interview --message "..."` | Reply to intake interview question |
| `rcp followups` | Show unanswered follow-up questions |

## Agents & Skills

| Command | Description |
|---------|-------------|
| `rcp agents` | List all 13 agents with descriptions |
| `rcp agent <name>` | Show a specific agent's full instructions |
| `rcp skills` | List all skills by category |
| `rcp skill <name>` | Show a specific skill's methodology |

## Workflow & Pipeline

| Command | Description |
|---------|-------------|
| `rcp workflow` | Show current workflow, pipeline, iteration support |
| `rcp iterations` | Show iteration history |
| `rcp intent <query>` | Route query through intent router |

## Approval Gates

| Command | Description |
|---------|-------------|
| `rcp approve <phase>` | Approve a pending phase gate |
| `rcp reject <phase> --reason "..."` | Reject with feedback |

## Analysis

| Command | Description |
|---------|-------------|
| `rcp preregistration` | Generate OSF-compatible pre-registration |
| `rcp reviewer2` | Run adversarial Reviewer 2 critique |
| `rcp parallel --questions q1,q2,q3` | Run questions in parallel |
| `rcp debug <script>` | Auto-debug a failing script |

## Branching

| Command | Description |
|---------|-------------|
| `rcp branch <name>` | Create a new research branch |
| `rcp branches` | List all branches and status |
| `rcp switch <name>` | Switch to a different branch |
| `rcp merge <name>` | Merge a branch into target |
| `rcp abandon <name>` | Abandon a research branch |

## Cache & DAG

| Command | Description |
|---------|-------------|
| `rcp cache stats` | Show cache hit rates, size |
| `rcp cache clear --older-than 7d` | Prune old cache entries |
| `rcp dag` | Show execution DAG summary |
| `rcp dag-viewer` | Generate interactive DAG visualization HTML |

## Data & Knowledge

| Command | Description |
|---------|-------------|
| `rcp data-scale` | Show data scale analysis and library constraints |
| `rcp graph` | Show knowledge graph summary |
| `rcp graph-stats` | Show knowledge graph statistics |
| `rcp graph-query --confounders "X"` | Query knowledge graph |
| `rcp graph-query --relation "mediates"` | Query by relation type |
| `rcp taxonomy` | Show semantic file system taxonomy |

## Export

| Command | Description |
|---------|-------------|
| `rcp export --format latex` | Export manuscript to LaTeX |
| `rcp export --format pdf` | Export manuscript to PDF |
| `rcp export --format journal --journal nature` | Format for specific journal |

## Dependencies

| Command | Description |
|---------|-------------|
| `rcp dependency-check <script>` | Check for uninstalled imports |
| `rcp dependency-check <script> --auto-install` | Auto-install missing dependencies |

## MCP

| Command | Description |
|---------|-------------|
| `rcp mcp` | Start MCP server for AI IDE integration |

## Session Management

| Command | Description |
|---------|-------------|
| `rcp restore` | Print restoration prompt for new chat session |
| `rcp snapshot` | Generate compact state snapshot |
| `rcp budget` | Show token budget status and CTM history |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Environment not active |
| 4 | Missing dependencies |
| 5 | Approval gate pending |
| 6 | Token budget exceeded |
