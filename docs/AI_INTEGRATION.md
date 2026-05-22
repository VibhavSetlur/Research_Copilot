# AI Integration

Research OS is exposed entirely via the Model Context Protocol (MCP). 

## Tools exposed to the AI

Instead of high-level tools that obscure the scientific process, the AI is given OS-level primitives.

### File & Workspace
- `sys.workspace.scaffold`
- `sys.file.read` / `sys.file.write`
- `sys.file.list` / `sys.file.delete`

### Guidance
- `sys.guidance.get`
- `sys.guidance.list`

### Search & Literature
- `tool.search.semantic_scholar`
- `tool.search.pubmed`
- `tool.search.crossref`
- `tool.search.web`
- `tool.web.scrape`
- `tool.literature.download`

### Execution
- `tool.python.exec`
- `tool.package.install`
- `tool.env.freeze`

### State & Branching
- `sys.state.get`
- `sys.checkpoint.create`
- `sys.branch.create` / `sys.branch.merge`
- `mem.analysis.log`

## Execution Philosophy

The AI should NEVER guess what to do. It should:
1. View available guidance with `sys.guidance.list`.
2. Load the relevant protocol with `sys.guidance.get`.
3. Follow the protocol explicitly.
4. Write Python code to `workspace/scripts/`.
5. Execute it via `tool.python.exec`.
6. Log its decisions using `tool.log.decision` and `mem.analysis.log`.
