# MCP Tools Reference

This document provides a comprehensive reference for all MCP tools exposed by Research OS.

## Tool Categories

- **sys.*** - System tools (state, health, workspace management)
- **mem.*** - Memory tools (methods, analysis, citations)
- **tool.*** - Research tools (data transform, statistical tests, figures)

---

## SYS.* Tools

### `sys.branch.create`

Create an experiment branch.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    },
    "hypothesis": {
      "type": "string"
    },
    "parent": {
      "type": "string"
    }
  },
  "required": [
    "name"
  ]
}
```

---

### `sys.branch.list`

List all branches.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.branch.merge`

Merge branches.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "source": {
      "type": "string"
    },
    "target": {
      "type": "string"
    },
    "message": {
      "type": "string"
    }
  },
  "required": [
    "source",
    "target",
    "message"
  ]
}
```

---

### `sys.branch.switch`

Switch to another branch.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "branch_id": {
      "type": "string"
    }
  },
  "required": [
    "branch_id"
  ]
}
```

---

### `sys.checkpoint.approve`

Approve a pending action.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.checkpoint.create`

Snapshot workspace state.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "description": {
      "type": "string"
    }
  }
}
```

---

### `sys.checkpoint.list`

List all checkpoints.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.checkpoint.pending`

Register a pending action for approval.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "description": {
      "type": "string"
    },
    "requires_approval": {
      "type": "boolean"
    }
  },
  "required": [
    "description",
    "requires_approval"
  ]
}
```

---

### `sys.checkpoint.rollback`

Rollback to a checkpoint.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "checkpoint_id": {
      "type": "string"
    }
  },
  "required": [
    "checkpoint_id"
  ]
}
```

---

### `sys.config.get`

Get researcher configuration.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.config.init`

Initialize researcher configuration.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.config.set`

Set a specific config value.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string"
    },
    "value": {
      "type": "string"
    }
  },
  "required": [
    "key",
    "value"
  ]
}
```

---

### `sys.config.validate`

Validate configuration and API keys.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.external_mcp.discover`

Discover external MCP servers.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.file.delete`

Delete a file.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string"
    }
  },
  "required": [
    "filepath"
  ]
}
```

---

### `sys.file.list`

List files in a directory.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "directory": {
      "type": "string"
    }
  },
  "required": [
    "directory"
  ]
}
```

---

### `sys.file.read`

Securely read a file from the workspace.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string"
    }
  },
  "required": [
    "filepath"
  ]
}
```

---

### `sys.file.write`

Securely write to a file in the workspace.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string"
    },
    "content": {
      "type": "string"
    },
    "force": {
      "type": "boolean",
      "description": "Force overwrite even in protected directories like synthesis/"
    }
  },
  "required": [
    "filepath",
    "content"
  ]
}
```

---

### `sys.guidance.get`

Returns the full YAML content of a guidance protocol.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "protocol_name": {
      "type": "string",
      "description": "Protocol name (e.g., domain_analysis)"
    }
  },
  "required": [
    "protocol_name"
  ]
}
```

---

### `sys.guidance.list`

Lists all available protocols with one-line summaries.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.guidance.validate`

Validates if the expected outputs of a protocol exist in the workspace.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "protocol_name": {
      "type": "string",
      "description": "Protocol name (e.g., domain_analysis)"
    }
  },
  "required": [
    "protocol_name"
  ]
}
```

---

### `sys.notify`

Notify researcher.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "message": {
      "type": "string"
    },
    "level": {
      "type": "string"
    }
  },
  "required": [
    "message",
    "level"
  ]
}
```

---

### `sys.state.get`

Get full workspace state.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.state.minimal_context`

Get a <=500 token snapshot of the current state, optimized for small models.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.state.summary`

Get a brief summary of the state.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.task.kill`

Kill a background task.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string"
    }
  },
  "required": [
    "task_id"
  ]
}
```

---

### `sys.task.monitor`

Monitor a background task.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string"
    }
  },
  "required": [
    "task_id"
  ]
}
```

---

### `sys.tool.info`

Get full schema for a tool.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "tool_name": {
      "type": "string"
    }
  },
  "required": [
    "tool_name"
  ]
}
```

---

### `sys.tool.search`

Search tools by description.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string"
    }
  },
  "required": [
    "query"
  ]
}
```

---

### `sys.workspace.scaffold`

Create the full directory structure for a new project.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "project_name": {
      "type": "string"
    }
  }
}
```

---

## MEM.* Tools

### `mem.analysis.log`

Append to workspace/analysis.md

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "entry": {
      "type": "string"
    }
  },
  "required": [
    "entry"
  ]
}
```

---

### `mem.methods.append`

Append to workspace/methods.md

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "method": {
      "type": "string"
    }
  },
  "required": [
    "method"
  ]
}
```

---

## TOOL.* Tools

### `tool.audit.synthesis`

Audit a generated manuscript for completeness and scientific claims.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "paper_path": {
      "type": "string"
    }
  },
  "required": [
    "paper_path"
  ]
}
```

---

### `tool.data.sample`

Sample data.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string"
    },
    "n_rows": {
      "type": "number"
    },
    "strategy": {
      "type": "string"
    }
  },
  "required": [
    "filepath",
    "n_rows",
    "strategy"
  ]
}
```

---

### `tool.env.freeze`

Freeze current environment.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `tool.env.restore`

Restore environment.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `tool.literature.download`

Download a paper PDF.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string"
    },
    "filename": {
      "type": "string"
    }
  },
  "required": [
    "url",
    "filename"
  ]
}
```

---

### `tool.log.decision`

Log a key reasoning step.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "context": {
      "type": "string"
    },
    "selected": {
      "type": "string"
    },
    "rationale": {
      "type": "string"
    }
  },
  "required": [
    "context",
    "selected",
    "rationale"
  ]
}
```

---

### `tool.package.install`

Install Python packages.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "packages": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "packages"
  ]
}
```

---

### `tool.python.exec`

Execute a python script in the workspace. WARNING: Scripts run with the same permissions as the host OS user. For strict sandboxing, run Research OS inside a Docker container.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "script_path": {
      "type": "string"
    }
  },
  "required": [
    "script_path"
  ]
}
```

---

### `tool.search.crossref`

Search Crossref.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string"
    },
    "limit": {
      "type": "number"
    }
  },
  "required": [
    "query"
  ]
}
```

---

### `tool.search.pubmed`

Search PubMed.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string"
    },
    "limit": {
      "type": "number"
    }
  },
  "required": [
    "query"
  ]
}
```

---

### `tool.search.semantic_scholar`

Search Semantic Scholar.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string"
    },
    "limit": {
      "type": "number"
    }
  },
  "required": [
    "query"
  ]
}
```

---

### `tool.search.web`

Search the web.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string"
    },
    "limit": {
      "type": "number"
    }
  },
  "required": [
    "query"
  ]
}
```

---

### `tool.web.scrape`

Scrape a webpage.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string"
    }
  },
  "required": [
    "url"
  ]
}
```

---

