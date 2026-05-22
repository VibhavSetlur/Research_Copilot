# MCP Tools Reference

This document provides a comprehensive reference for all MCP tools exposed by Research OS.

## Tool Categories

- **sys.*** - System tools (state, health, workspace management)
- **mem.*** - Memory tools (methods, analysis, citations)
- **view.*** - View tools (workspace tree, data preview, figure display)
- **tool.*** - Research tools (data transform, statistical tests, figures)

---

## SYS.* Tools

### `sys.analysis.log`

Append a human/AI note to analysis.md and update the Mermaid workflow diagram.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "entry": {
      "type": "string",
      "description": "The note or observation to log"
    },
    "step": {
      "type": "string",
      "description": "The step/experiment name (e.g. 01_experiment_baseline)"
    },
    "status": {
      "type": "string",
      "enum": [
        "planned",
        "running",
        "complete",
        "failed",
        "dead_end"
      ],
      "description": "Node status for Mermaid diagram coloring"
    }
  },
  "required": [
    "entry"
  ]
}
```

---

### `sys.branch.abandon`

Mark a branch as abandoned/dead-end. The branch folder is preserved but marked as inactive.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "branch_id": {
      "type": "string",
      "description": "Branch ID to abandon"
    },
    "reason": {
      "type": "string",
      "description": "Reason for abandonment"
    }
  },
  "required": [
    "branch_id"
  ]
}
```

---

### `sys.branch.create`

Create a numbered experiment folder (01_name/) under workspace/ with full subdirectory tree. Optionally copy from a source step.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Branch/experiment name (used for folder slug)"
    },
    "hypothesis": {
      "type": "string",
      "description": "Research hypothesis or goal"
    },
    "parent": {
      "type": "string",
      "description": "Parent branch to fork from"
    },
    "from_step": {
      "type": "string",
      "description": "Copy contents from an existing step folder (e.g. 01_exploration)"
    }
  },
  "required": [
    "name"
  ]
}
```

---

### `sys.branch.merge`

Merge findings from one branch into another. Copies conclusions.md into the target branch's directory and merges state ledger entries. Manual review required.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "source": {
      "type": "string",
      "description": "Source branch ID to merge from"
    },
    "target": {
      "type": "string",
      "description": "Target branch ID to merge into (default: main)"
    },
    "message": {
      "type": "string",
      "description": "Merge rationale / commit message"
    }
  },
  "required": [
    "source"
  ]
}
```

---

### `sys.checkpoint`

Snapshot the entire workspace/ into .os_state/checkpoints/<id>/ for rollback. Large data files (csv, parquet, etc.) are hash-referenced, not copied.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "checkpoint_id": {
      "type": "string",
      "description": "Unique checkpoint ID (e.g. before_model_training). Auto-generated if omitted."
    },
    "description": {
      "type": "string",
      "description": "Human-readable description of this checkpoint"
    }
  },
  "required": []
}
```

---

### `sys.checkpoint.list`

List all available checkpoints with timestamps and descriptions.

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

### `sys.health`

Health check endpoint — returns version, uptime, loaded tool count, memory usage. Alias for sys.heartbeat.

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

### `sys.heartbeat`

Lightweight health check — returns version, uptime, loaded tool count, memory usage.

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

### `sys.rollback`

Restore workspace to a previous checkpoint. Current state is saved as backup before rollback.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "checkpoint_id": {
      "type": "string",
      "description": "ID of the checkpoint to restore"
    }
  },
  "required": [
    "checkpoint_id"
  ]
}
```

---

### `sys.scaffold.synthesis`

Populate synthesis/ directory with template files (abstract.md, paper.tex, references.bib, supplementary/).

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "project_name": {
      "type": "string",
      "description": "Project name for templates"
    }
  },
  "required": []
}
```

---

### `sys.state`

Return the full workspace snapshot: folder tree, pipeline stage, last checkpoint, branches. Enables instant session resume.

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

### `sys.synthesize`

Compile all workspace findings into synthesis/ outputs: abstract.md, paper.tex, references.bib, workflow diagram. Only call when the user explicitly says 'I\'m done' or triggers synthesis.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "project_name": {
      "type": "string",
      "description": "Project name for the paper title"
    },
    "formats": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "pdf",
          "html",
          "md"
        ]
      },
      "description": "Output formats"
    }
  },
  "required": []
}
```

---

### `sys.workspace.scaffold`

Create the full directory tree for a new research project in one call.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "project_name": {
      "type": "string",
      "description": "Name of the research project",
      "default": "My Research Project"
    }
  },
  "required": []
}
```

---

## MEM.* Tools

### `mem.citation.add`

Add a BibTeX citation to workspace/citations.md with verified: false flag. The citation_verifier can later flip the flag.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "bibtex": {
      "type": "string",
      "description": "BibTeX entry"
    },
    "citation_key": {
      "type": "string",
      "description": "Unique citation key (e.g. author2024title)"
    },
    "source": {
      "type": "string",
      "description": "Where this citation came from (DOI, manual, search)"
    }
  },
  "required": [
    "bibtex"
  ]
}
```

---

### `mem.citations.generate`

Regenerate workspace/citations.md from the literature index.

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

### `mem.literature.index`

Scan inputs/literature/ and build/refresh literature_index.yaml mapping filenames to citation keys.

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

### `mem.methods.append`

Append a structured method entry to workspace/methods.md (append-only).

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "method": {
      "type": "string",
      "description": "Method name or description"
    },
    "parameters": {
      "type": "string",
      "description": "Key parameters used"
    },
    "citation": {
      "type": "string",
      "description": "Optional BibTeX citation key"
    },
    "tool": {
      "type": "string",
      "description": "Tool that ran this method"
    }
  },
  "required": [
    "method"
  ]
}
```

---

### `mem.regenerate.intake`

Re-scan inputs/ and regenerate inputs/intake.md with current SHA-256 hashes, domain, and depth.

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

## VIEW.* Tools

### `view.analyze_intent`

Passively analyze a user query and return a structured ResearchIntake schema. The IDE uses this to decide which tools to call next — no routing or execution is performed.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Natural language research request"
    },
    "depth": {
      "type": "string",
      "enum": [
        "exploratory",
        "academic",
        "publication"
      ],
      "description": "Analysis depth"
    }
  },
  "required": [
    "query"
  ]
}
```

---

### `view.data.head`

Return first N rows + column types (dtype, null%) + summary stats for any data file. Use before any analysis to understand data shape.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string",
      "description": "Relative path to data file in workspace"
    },
    "n": {
      "type": "number",
      "description": "Number of rows",
      "default": 5
    }
  },
  "required": [
    "filepath"
  ]
}
```

---

### `view.figure.show`

Return a base64-encoded PNG of a figure for IDE preview. Accepts path to any PNG/JPG/SVG in workspace.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string",
      "description": "Relative path to figure file in workspace"
    }
  },
  "required": [
    "filepath"
  ]
}
```

---

### `view.workspace.tree`

Return the full workspace directory tree with file sizes and last-modified timestamps. Use instead of guessing file paths.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "max_depth": {
      "type": "number",
      "description": "Maximum directory depth",
      "default": 4
    }
  },
  "required": []
}
```

---

## TOOL.* Tools

### `create_experiment_branch`

[Compatibility alias] Use sys.branch.create instead. Creates an isolated experiment branch.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Branch idea or explicit exp_XXX_slug name"
    },
    "hypothesis": {
      "type": "string",
      "description": "Hypothesis or rationale for this branch"
    },
    "parent": {
      "type": "string",
      "description": "Parent branch, defaults to current branch"
    }
  },
  "required": [
    "name"
  ]
}
```

---

### `load_skill_context`

Load the full context of a specific skill by its name/id

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "skill_name": {
      "type": "string",
      "description": "The id/name of the skill"
    }
  },
  "required": [
    "skill_name"
  ]
}
```

---

### `log_decision`

Append a methodological choice to the active experiment decisions.yaml

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
    },
    "options_considered": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "linked_literature": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "branch_id": {
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

### `patch_file`

Surgically edit specific functions or lines in a file. Returns absolute path and checksum of modified file.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string",
      "description": "Path to the file to edit"
    },
    "search_block": {
      "type": "string",
      "description": "The exact block of code to search for and replace"
    },
    "replace_block": {
      "type": "string",
      "description": "The new block of code to insert"
    }
  },
  "required": [
    "filepath",
    "search_block",
    "replace_block"
  ]
}
```

---

### `query_research_context`

Query the serialized Context Transfer Memoranda (CTMs) to retrieve specific research context

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "question": {
      "type": "string",
      "description": "The question to ask against the CTMs"
    }
  },
  "required": [
    "question"
  ]
}
```

---

### `research_agent`

Read a packaged agent prompt, honoring a project-local override if present

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Agent name, e.g. research_init"
    }
  },
  "required": [
    "name"
  ]
}
```

---

### `research_data_scale`

Analyze input data files and report size classifications and library constraints

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

### `research_preflight`

Run environment preflight checks to verify all dependencies are installed and ready

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

### `research_skill`

Read a packaged skill methodology, honoring a project-local override if present

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Skill name"
    }
  },
  "required": [
    "name"
  ]
}
```

---

### `research_status`

Show clean workspace state, active branch, and input hash count

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

### `research_workflow`

Read a packaged workflow YAML

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Workflow name"
    }
  },
  "required": []
}
```

---

### `route_intent`

[Deprecated] Use view.analyze_intent instead. Returns a passive intake schema for the IDE to consume.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Natural language research request"
    },
    "depth": {
      "type": "string",
      "enum": [
        "exploratory",
        "academic",
        "publication"
      ],
      "description": "Routing depth"
    }
  },
  "required": [
    "query"
  ]
}
```

---

### `save_artifact`

Save a text artifact. Returns absolute path + SHA-256 checksum.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filename": {
      "type": "string"
    },
    "content": {
      "type": "string"
    },
    "artifact_type": {
      "type": "string",
      "enum": [
        "artifact",
        "analysis",
        "figure",
        "table"
      ]
    },
    "generated_by": {
      "type": "string"
    },
    "source_script": {
      "type": "string"
    },
    "input_files": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "decisions_applied": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "branch_id": {
      "type": "string"
    }
  },
  "required": [
    "filename",
    "content"
  ]
}
```

---

### `search_skills`

Search the skill index for a specific topic or keyword

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search keyword or phrase"
    }
  },
  "required": [
    "query"
  ]
}
```

---

### `tool.dashboard.create`

Generate an interactive Panel dashboard (or static HTML fallback) from a data file.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string",
      "description": "Relative path to data file in workspace"
    },
    "dashboard_type": {
      "type": "string",
      "enum": [
        "panel",
        "html"
      ],
      "default": "panel"
    }
  },
  "required": [
    "filepath"
  ]
}
```

---

### `tool.data.transform`

Apply data cleaning transformations (normalize, impute, encode, drop, rename) to a CSV/Parquet file using sklearn.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string",
      "description": "Relative path to data file in workspace"
    },
    "operations": {
      "type": "array",
      "items": {
        "type": "object"
      },
      "description": "List of operations: {type, columns, strategy, value}"
    },
    "output": {
      "type": "string",
      "description": "Output path (default: workspace/data/derived/transformed_<name>)"
    }
  },
  "required": [
    "filepath",
    "operations"
  ]
}
```

---

### `tool.figure.create`

Create a publication-quality figure (scatter, line, bar, hist, box, violin, heatmap, pairplot) from data. Returns 300 DPI PNG.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string",
      "description": "Relative path to data file in workspace"
    },
    "chart_type": {
      "type": "string",
      "enum": [
        "scatter",
        "line",
        "bar",
        "hist",
        "box",
        "violin",
        "heatmap",
        "pairplot"
      ]
    },
    "x_column": {
      "type": "string",
      "description": "X-axis column"
    },
    "y_column": {
      "type": "string",
      "description": "Y-axis column"
    },
    "group_column": {
      "type": "string",
      "description": "Grouping/hue column"
    },
    "title": {
      "type": "string",
      "description": "Figure title"
    },
    "output": {
      "type": "string",
      "description": "Output path (default: workspace/figures/)"
    }
  },
  "required": [
    "filepath",
    "chart_type",
    "x_column"
  ]
}
```

---

### `tool.google.scholar.search`

Search Google Scholar for publications. Requires `scholarly` package (pip install scholarly).

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query"
    },
    "limit": {
      "type": "number",
      "description": "Max results",
      "default": 5
    }
  },
  "required": [
    "query"
  ]
}
```

---

### `tool.latex.compile`

Run pdflatex + bibtex on synthesis/paper.tex to produce paper.pdf.

#### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

---

### `tool.pubmed.search`

Search PubMed for publications matching a query.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query (e.g. 'machine learning diabetes')"
    },
    "limit": {
      "type": "number",
      "description": "Max results (max 20)",
      "default": 5
    }
  },
  "required": [
    "query"
  ]
}
```

---

### `tool.semantic_scholar.search`

Search Semantic Scholar for papers matching a query. Includes abstracts and citation counts.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query"
    },
    "limit": {
      "type": "number",
      "description": "Max results (max 20)",
      "default": 5
    }
  },
  "required": [
    "query"
  ]
}
```

---

### `tool.statistical.test`

Run a statistical test (ttest, anova, chi_square, mann_whitney, kruskal) with automatic assumption checks (normality, homoscedasticity).

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "filepath": {
      "type": "string",
      "description": "Absolute path to data file"
    },
    "test_type": {
      "type": "string",
      "enum": [
        "ttest",
        "anova",
        "chi_square",
        "mann_whitney",
        "kruskal"
      ],
      "description": "Type of test"
    },
    "x_column": {
      "type": "string",
      "description": "Primary column (dependent variable or first variable)"
    },
    "y_column": {
      "type": "string",
      "description": "Secondary column (for paired tests or contingency)"
    },
    "group_column": {
      "type": "string",
      "description": "Grouping column (for independent tests)"
    }
  },
  "required": [
    "filepath",
    "test_type",
    "x_column"
  ]
}
```

---

### `write_to_scratchpad`

Record step-by-step reasoning. Returns absolute path.

#### Input Schema

```json
{
  "type": "object",
  "properties": {
    "thought": {
      "type": "string",
      "description": "The reasoning or calculation to record"
    }
  },
  "required": [
    "thought"
  ]
}
```

---

