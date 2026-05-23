# MCP Tools Reference

This document provides a comprehensive reference for all MCP tools exposed by Research OS.

## Tool Categories

- **sys.*** - System tools (state, health, workspace management)
- **mem.*** - Memory tools (methods, analysis, citations)
- **tool.*** - Research tools (data transform, statistical tests, figures)

---

## SYS.* Tools

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

### `sys.env.docker.generate`

Generates a Dockerfile to run all snapshotted environments.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.env.snapshot`

Snapshot current multi-language environment (Python, R, Julia).

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

### `sys.path.abandon`

Mark an experiment path as a dead end (renames directory with __DEAD_END suffix).

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "path_name": {
      "type": "string",
      "description": "Name of the path directory (e.g. 03_bayesian_model)"
    },
    "rationale": {
      "type": "string",
      "description": "Why this path was abandoned"
    }
  },
  "required": [
    "path_name",
    "rationale"
  ]
}
```

---

### `sys.path.create`

Create a numbered experiment path in workspace/.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Short name for the experiment (e.g. bayesian_model)"
    }
  },
  "required": [
    "name"
  ]
}
```

---

### `sys.path.list`

List all numbered experiment paths with their status.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `sys.session.handoff`

Creates a structured markdown summary + next step prompt for session handoff.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
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

### `sys.state.health`

Returns current context estimate, paths, and handoff recommendation.

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

### `tool.audit.assumptions`

Re-run assumption checks on the fitted model or residuals.

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

### `tool.audit.figure_quality`

Check figure quality (DPI, colorblind-friendly, labels, error bars).

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

### `tool.audit.reproducibility_full`

Run a full reproducibility check using Docker.

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

### `tool.audit.statistical_power`

Compute post-hoc power for statistical tests. Warns if power < 0.8.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string"
    },
    "effect_size": {
      "type": "number"
    },
    "alpha": {
      "type": "number"
    },
    "n": {
      "type": "number"
    }
  },
  "required": [
    "filepath",
    "alpha",
    "n"
  ]
}
```

---

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

### `tool.bash.exec`

Execute a Bash script in the workspace.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "script_path": {
      "type": "string"
    },
    "timeout": {
      "type": "number",
      "description": "Timeout in seconds (default 300)"
    }
  },
  "required": [
    "script_path"
  ]
}
```

---

### `tool.data.convert`

Convert data between common formats (CSV, RDS, Feather, Parquet).

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string",
      "description": "Input file path"
    },
    "output_format": {
      "type": "string",
      "description": "Desired output format (e.g. csv, rds, feather, parquet)"
    }
  },
  "required": [
    "filepath",
    "output_format"
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

Freeze current environment (Deprecated, use sys.env.snapshot).

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
}
```

---

### `tool.env.restore`

Restore a frozen environment.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "requirements": {
      "type": "string",
      "description": "Requirements format text"
    }
  },
  "required": []
}
```

---

### `tool.julia.exec`

Execute a Julia script in the workspace.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "script_path": {
      "type": "string"
    },
    "timeout": {
      "type": "number",
      "description": "Timeout in seconds (default 300)"
    }
  },
  "required": [
    "script_path"
  ]
}
```

---

### `tool.latex.compile`

Compile paper.tex in the synthesis directory to PDF using pdflatex and bibtex.

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
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

### `tool.poster.create`

Generate a professional LaTeX poster in synthesis/poster.pdf using tikzposter.

#### Input Schema

```json
{
  "type": "object",
  "properties": {}
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

### `tool.r.exec`

Execute an R script in the workspace.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "script_path": {
      "type": "string"
    },
    "timeout": {
      "type": "number",
      "description": "Timeout in seconds (default 300)"
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

### `tool.synthesize`

Gather all workspace findings and compile a publication-ready paper in synthesis/. Combines analysis.md, methods.md, citations, figures, and audit report into synthesis/paper.md.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "output_format": {
      "type": "string",
      "enum": [
        "markdown",
        "latex",
        "both"
      ],
      "description": "Output format for the compiled paper (default: markdown)"
    },
    "section": {
      "type": "string",
      "description": "Specific section to generate (e.g. abstract, methods, results, discussion). If omitted, generates the full paper."
    }
  },
  "required": []
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

