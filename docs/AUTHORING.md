# Agent and Skill Authoring

Agents and Skills are defined using a structured format inside the `assets/registry.json`.

## Authoring an Agent
An Agent is defined by its role, context requirements, and allowed tools.
Example:
```json
{
  "id": "DataAnalyst",
  "description": "Analyzes raw data and produces statistical summaries.",
  "system_prompt": "You are a data analyst...",
  "tools_allowed": ["python_repl", "query_database"]
}
```

## Authoring a Skill
A Skill is a reusable capability that agents can invoke. It is exposed as an MCP tool.
Example:
```json
{
  "id": "run_regression",
  "description": "Runs a linear regression on the specified dataset.",
  "parameters": {
    "dataset": "string",
    "target": "string"
  }
}
```
