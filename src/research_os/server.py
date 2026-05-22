#!/usr/bin/env python3
"""Research OS MCP server — Hands, Eyes, and Memory for AI-Driven Research.

The AI IDE is the brain.  This server provides the Hands (tools), Eyes
(observability), and Memory (state) that the IDE uses to execute research.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
import logging
import sys

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("research-os.server")

from research_os.engine import ResearchEngine
from research_os.errors import WriteProtectedError, check_write_permitted
from research_os.project_ops import (
    compute_input_hashes,
    compute_file_hash,
    create_numbered_experiment,
    current_branch,
    generate_citations_md,
    load_state,
    now_iso,
    regenerate_intake,
    render_workflow_diagram,
    scaffold_minimal_workspace,
    scaffold_synthesis,
    update_literature_index,
)
from research_os.tools.tool_impls import (
    latex_compile,
    pubmed_search,
    semantic_scholar_search,
    google_scholar_search,
    data_transform,
    statistical_test,
    figure_create,
    dashboard_create,
    workspace_tree,
    data_head,
    figure_show,
)
from research_os.utils.asset_manager import AssetManager
from research_os.intent_router import IntentAnalyzer

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool

    HAS_MCP = True
except ImportError:  # pragma: no cover - fallback protocol covers this path.
    HAS_MCP = False

    @dataclass
    class TextContent:  # type: ignore[no-redef]
        type: str
        text: str


DEPTH_ENUM = ["exploratory", "academic", "publication"]

_START_TIME = time.time()


# ---------------------------------------------------------------------------
# Rate Limiter
# ---------------------------------------------------------------------------

class RateLimiter:
    """Simple in-memory rate limiter for tool calls."""
    
    def __init__(self, max_calls: int = 100, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = defaultdict(list)
    
    def is_allowed(self, client_id: str = "default") -> bool:
        """Check if a call is allowed for the given client."""
        now = time.time()
        client_calls = self.calls[client_id]
        
        # Remove calls outside the time window
        self.calls[client_id] = [t for t in client_calls if now - t < self.window_seconds]
        
        if len(self.calls[client_id]) >= self.max_calls:
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return False
        
        self.calls[client_id].append(now)
        return True


_rate_limiter = RateLimiter(max_calls=100, window_seconds=60)


# ---------------------------------------------------------------------------
# Standardized response envelope (Section 4.3 of TODO.md)
# ---------------------------------------------------------------------------

def _envelope(
    data: Any = None,
    *,
    status: str = "success",
    paths_created: list[str] | None = None,
    paths_modified: list[str] | None = None,
    next_suggested_tools: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict:
    """Build the standardized response envelope."""
    checksums: dict[str, str] = {}
    for path_list in ([], paths_created or [], paths_modified or []):
        for p in path_list:
            fp = Path(p)
            if fp.exists():
                checksums[p] = f"sha256:{compute_file_hash(fp)}"
    return {
        "status": status,
        "data": data or {},
        "paths": {
            "created": paths_created or [],
            "modified": paths_modified or [],
        },
        "checksums": checksums,
        "next_suggested_tools": next_suggested_tools or [],
        "warnings": warnings or [],
    }


def _success_envelope(data: Any = None, **kw) -> dict:
    return _envelope(data, status="success", **kw)


def _error_envelope(message: str, **kw) -> dict:
    return _envelope({"error": message}, status="error", **kw)


# ---------------------------------------------------------------------------
# Tool definitions — complete JSON Schema for every MCP tool
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS: dict[str, dict[str, Any]] = {
    # ── System tools (sys.*) ──────────────────────────────────────────
    "sys.state": {
        "description": "Return the full workspace snapshot: folder tree, pipeline stage, last checkpoint, branches. Enables instant session resume.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "sys.heartbeat": {
        "description": "Lightweight health check — returns version, uptime, loaded tool count, memory usage.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "sys.health": {
        "description": "Health check endpoint — returns version, uptime, loaded tool count, memory usage. Alias for sys.heartbeat.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "sys.workspace.scaffold": {
        "description": "Create the full directory tree for a new research project in one call.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Name of the research project", "default": "My Research Project"},
            },
            "required": [],
        },
    },
    "sys.rollback": {
        "description": "Restore workspace to a previous checkpoint. Current state is saved as backup before rollback.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "checkpoint_id": {"type": "string", "description": "ID of the checkpoint to restore"},
            },
            "required": ["checkpoint_id"],
        },
    },
    "sys.analysis.log": {
        "description": "Append a human/AI note to analysis.md and update the Mermaid workflow diagram.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entry": {"type": "string", "description": "The note or observation to log"},
                "step": {"type": "string", "description": "The step/experiment name (e.g. 01_experiment_baseline)"},
                "status": {"type": "string", "enum": ["planned", "running", "complete", "failed", "dead_end"], "description": "Node status for Mermaid diagram coloring"},
            },
            "required": ["entry"],
        },
    },
    "sys.synthesize": {
        "description": "Compile all workspace findings into synthesis/ outputs: abstract.md, paper.tex, references.bib, workflow diagram. Only call when the user explicitly says 'I\\'m done' or triggers synthesis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name for the paper title"},
                "formats": {"type": "array", "items": {"type": "string", "enum": ["pdf", "html", "md"]}, "description": "Output formats"},
            },
            "required": [],
        },
    },
    "sys.scaffold.synthesis": {
        "description": "Populate synthesis/ directory with template files (abstract.md, paper.tex, references.bib, supplementary/).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name for templates"},
            },
            "required": [],
        },
    },
    "mem.methods.append": {
        "description": "Append a structured method entry to workspace/methods.md (append-only).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "description": "Method name or description"},
                "parameters": {"type": "string", "description": "Key parameters used"},
                "citation": {"type": "string", "description": "Optional BibTeX citation key"},
                "tool": {"type": "string", "description": "Tool that ran this method"},
            },
            "required": ["method"],
        },
    },
    "mem.citation.add": {
        "description": "Add a BibTeX citation to workspace/citations.md with verified: false flag. The citation_verifier can later flip the flag.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bibtex": {"type": "string", "description": "BibTeX entry"},
                "citation_key": {"type": "string", "description": "Unique citation key (e.g. author2024title)"},
                "source": {"type": "string", "description": "Where this citation came from (DOI, manual, search)"},
            },
            "required": ["bibtex"],
        },
    },
    "mem.regenerate.intake": {
        "description": "Re-scan inputs/ and regenerate inputs/intake.md with current SHA-256 hashes, domain, and depth.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "mem.citations.generate": {
        "description": "Regenerate workspace/citations.md from the literature index.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "mem.literature.index": {
        "description": "Scan inputs/literature/ and build/refresh literature_index.yaml mapping filenames to citation keys.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    # ── Query analysis (view.*) ───────────────────────────────────────
    "view.analyze_intent": {
        "description": "Passively analyze a user query and return a structured ResearchIntake schema. The IDE uses this to decide which tools to call next — no routing or execution is performed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language research request"},
                "depth": {"type": "string", "enum": DEPTH_ENUM, "description": "Analysis depth"},
            },
            "required": ["query"],
        },
    },
    # ── Legacy tools (kept for backward compatibility) ────────────────
    "research_status": {
        "description": "Show clean workspace state, active branch, and input hash count",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "research_agent": {
        "description": "Read a packaged agent prompt, honoring a project-local override if present",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Agent name, e.g. research_init"}},
            "required": ["name"],
        },
    },
    "research_skill": {
        "description": "Read a packaged skill methodology, honoring a project-local override if present",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Skill name"}},
            "required": ["name"],
        },
    },
    "research_workflow": {
        "description": "Read a packaged workflow YAML",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Workflow name"}},
            "required": [],
        },
    },
    "route_intent": {
        "description": "[Deprecated] Use view.analyze_intent instead. Returns a passive intake schema for the IDE to consume.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language research request"},
                "depth": {"type": "string", "enum": DEPTH_ENUM, "description": "Routing depth"},
            },
            "required": ["query"],
        },
    },
    "sys.checkpoint": {
        "description": "Snapshot the entire workspace/ into .os_state/checkpoints/<id>/ for rollback. Large data files (csv, parquet, etc.) are hash-referenced, not copied.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "checkpoint_id": {"type": "string", "description": "Unique checkpoint ID (e.g. before_model_training). Auto-generated if omitted."},
                "description": {"type": "string", "description": "Human-readable description of this checkpoint"},
            },
            "required": [],
        },
    },
    "sys.checkpoint.list": {
        "description": "List all available checkpoints with timestamps and descriptions.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "sys.branch.create": {
        "description": "Create a numbered experiment folder (01_name/) under workspace/ with full subdirectory tree. Optionally copy from a source step.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Branch/experiment name (used for folder slug)"},
                "hypothesis": {"type": "string", "description": "Research hypothesis or goal"},
                "parent": {"type": "string", "description": "Parent branch to fork from"},
                "from_step": {"type": "string", "description": "Copy contents from an existing step folder (e.g. 01_exploration)"},
            },
            "required": ["name"],
        },
    },
    "sys.branch.merge": {
        "description": "Merge findings from one branch into another. Copies conclusions.md into the target branch's directory and merges state ledger entries. Manual review required.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source branch ID to merge from"},
                "target": {"type": "string", "description": "Target branch ID to merge into (default: main)"},
                "message": {"type": "string", "description": "Merge rationale / commit message"},
            },
            "required": ["source"],
        },
    },
    "sys.branch.abandon": {
        "description": "Mark a branch as abandoned/dead-end. The branch folder is preserved but marked as inactive.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "branch_id": {"type": "string", "description": "Branch ID to abandon"},
                "reason": {"type": "string", "description": "Reason for abandonment"},
            },
            "required": ["branch_id"],
        },
    },
    "create_experiment_branch": {
        "description": "[Compatibility alias] Use sys.branch.create instead. Creates an isolated experiment branch.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Branch idea or explicit exp_XXX_slug name"},
                "hypothesis": {"type": "string", "description": "Hypothesis or rationale for this branch"},
                "parent": {"type": "string", "description": "Parent branch, defaults to current branch"},
            },
            "required": ["name"],
        },
    },
    "log_decision": {
        "description": "Append a methodological choice to the active experiment decisions.yaml",
        "inputSchema": {
            "type": "object",
            "properties": {
                "context": {"type": "string"},
                "selected": {"type": "string"},
                "rationale": {"type": "string"},
                "options_considered": {"type": "array", "items": {"type": "string"}},
                "linked_literature": {"type": "array", "items": {"type": "string"}},
                "branch_id": {"type": "string"},
            },
            "required": ["context", "selected", "rationale"],
        },
    },
    "save_artifact": {
        "description": "Save a text artifact. Returns absolute path + SHA-256 checksum.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "content": {"type": "string"},
                "artifact_type": {"type": "string", "enum": ["artifact", "analysis", "figure", "table"]},
                "generated_by": {"type": "string"},
                "source_script": {"type": "string"},
                "input_files": {"type": "array", "items": {"type": "string"}},
                "decisions_applied": {"type": "array", "items": {"type": "string"}},
                "branch_id": {"type": "string"},
            },
            "required": ["filename", "content"],
        },
    },
    "search_skills": {
        "description": "Search the skill index for a specific topic or keyword",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search keyword or phrase"}},
            "required": ["query"],
        },
    },
    "load_skill_context": {
        "description": "Load the full context of a specific skill by its name/id",
        "inputSchema": {
            "type": "object",
            "properties": {"skill_name": {"type": "string", "description": "The id/name of the skill"}},
            "required": ["skill_name"],
        },
    },
    "patch_file": {
        "description": "Surgically edit specific functions or lines in a file. Returns absolute path and checksum of modified file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Path to the file to edit"},
                "search_block": {"type": "string", "description": "The exact block of code to search for and replace"},
                "replace_block": {"type": "string", "description": "The new block of code to insert"},
            },
            "required": ["filepath", "search_block", "replace_block"],
        },
    },
    "write_to_scratchpad": {
        "description": "Record step-by-step reasoning. Returns absolute path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "thought": {"type": "string", "description": "The reasoning or calculation to record"}
            },
            "required": ["thought"],
        },
    },
    "query_research_context": {
        "description": "Query the serialized Context Transfer Memoranda (CTMs) to retrieve specific research context",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The question to ask against the CTMs"}
            },
            "required": ["question"],
        },
    },
    "research_preflight": {
        "description": "Run environment preflight checks to verify all dependencies are installed and ready",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "research_data_scale": {
        "description": "Analyze input data files and report size classifications and library constraints",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    # ── §4.2 missing tools (tool.*) ─────────────────────────────────
    "tool.latex.compile": {
        "description": "Run pdflatex + bibtex on synthesis/paper.tex to produce paper.pdf.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "tool.pubmed.search": {
        "description": "Search PubMed for publications matching a query.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (e.g. 'machine learning diabetes')"},
                "limit": {"type": "number", "description": "Max results (max 20)", "default": 5},
            },
            "required": ["query"],
        },
    },
    "tool.semantic_scholar.search": {
        "description": "Search Semantic Scholar for papers matching a query. Includes abstracts and citation counts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "number", "description": "Max results (max 20)", "default": 5},
            },
            "required": ["query"],
        },
    },
    "tool.google.scholar.search": {
        "description": "Search Google Scholar for publications. Requires `scholarly` package (pip install scholarly).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "number", "description": "Max results", "default": 5},
            },
            "required": ["query"],
        },
    },
    "tool.data.transform": {
        "description": "Apply data cleaning transformations (normalize, impute, encode, drop, rename) to a CSV/Parquet file using sklearn.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Relative path to data file in workspace"},
                "operations": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of operations: {type, columns, strategy, value}",
                },
                "output": {"type": "string", "description": "Output path (default: workspace/data/derived/transformed_<name>)"},
            },
            "required": ["filepath", "operations"],
        },
    },
    "tool.statistical.test": {
        "description": "Run a statistical test (ttest, anova, chi_square, mann_whitney, kruskal) with automatic assumption checks (normality, homoscedasticity).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Absolute path to data file"},
                "test_type": {"type": "string", "enum": ["ttest", "anova", "chi_square", "mann_whitney", "kruskal"], "description": "Type of test"},
                "x_column": {"type": "string", "description": "Primary column (dependent variable or first variable)"},
                "y_column": {"type": "string", "description": "Secondary column (for paired tests or contingency)"},
                "group_column": {"type": "string", "description": "Grouping column (for independent tests)"},
            },
            "required": ["filepath", "test_type", "x_column"],
        },
    },
    "tool.figure.create": {
        "description": "Create a publication-quality figure (scatter, line, bar, hist, box, violin, heatmap, pairplot) from data. Returns 300 DPI PNG.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Relative path to data file in workspace"},
                "chart_type": {"type": "string", "enum": ["scatter", "line", "bar", "hist", "box", "violin", "heatmap", "pairplot"]},
                "x_column": {"type": "string", "description": "X-axis column"},
                "y_column": {"type": "string", "description": "Y-axis column"},
                "group_column": {"type": "string", "description": "Grouping/hue column"},
                "title": {"type": "string", "description": "Figure title"},
                "output": {"type": "string", "description": "Output path (default: workspace/figures/)"},
            },
            "required": ["filepath", "chart_type", "x_column"],
        },
    },
    "tool.dashboard.create": {
        "description": "Generate an interactive Panel dashboard (or static HTML fallback) from a data file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Relative path to data file in workspace"},
                "dashboard_type": {"type": "string", "enum": ["panel", "html"], "default": "panel"},
            },
            "required": ["filepath"],
        },
    },
    # ── §4.2 missing tools (view.*) ─────────────────────────────────
    "view.workspace.tree": {
        "description": "Return the full workspace directory tree with file sizes and last-modified timestamps. Use instead of guessing file paths.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "max_depth": {"type": "number", "description": "Maximum directory depth", "default": 4},
            },
            "required": [],
        },
    },
    "view.data.head": {
        "description": "Return first N rows + column types (dtype, null%) + summary stats for any data file. Use before any analysis to understand data shape.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Relative path to data file in workspace"},
                "n": {"type": "number", "description": "Number of rows", "default": 5},
            },
            "required": ["filepath"],
        },
    },
    "view.figure.show": {
        "description": "Return a base64-encoded PNG of a figure for IDE preview. Accepts path to any PNG/JPG/SVG in workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Relative path to figure file in workspace"},
            },
            "required": ["filepath"],
        },
    },
}


def _project_root() -> Path:
    return AssetManager.find_project_root()


def _text(payload: Any) -> list[TextContent]:
    if isinstance(payload, str):
        return [TextContent(type="text", text=payload)]
    return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]


def _asset_by_name(manager: AssetManager, directory: str, name: str) -> str | None:
    exact = f"{directory}/{name}.md"
    if manager.exists(exact):
        return exact
    for ref in manager.iter_files(directory, "*.md"):
        stem = Path(ref.relative_path).stem
        normalized = stem.split("_", 1)[1] if "_" in stem else stem
        if stem == name or normalized == name:
            return ref.relative_path
    return None


def _walk_tree(path: Path, prefix: str = "") -> list[str]:
    """Build a text tree of a directory."""
    lines = []
    entries = sorted(path.iterdir()) if path.exists() else []
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        size = f" ({entry.stat().st_size / 1024:.1f} KB)" if entry.is_file() else ""
        lines.append(f"{prefix}{connector}{entry.name}{size}")
        if entry.is_dir():
            extension = "    " if is_last else "│   "
            lines.extend(_walk_tree(entry, prefix + extension))
    return lines


def _compute_file_sha256(path: Path) -> str:
    sha = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
    except (FileNotFoundError, PermissionError, OSError):
        return "error"
    return sha.hexdigest()


def _handle_tool_call(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool call with rate limiting and error handling."""
    # Rate limiting check
    if not _rate_limiter.is_allowed():
        logger.warning(f"Rate limit exceeded for tool call: {name}")
        return _text(_error_envelope("Rate limit exceeded. Please try again later."))
    
    arguments = arguments or {}
    root = _project_root()
    manager = AssetManager(root)
    
    logger.info(f"Tool call: {name} with arguments: {list(arguments.keys())}")

    # ── System tools ──────────────────────────────────────────────

    if name == "sys.state":
        engine = ResearchEngine(root)
        state = load_state(root)
        tree = "\n".join(_walk_tree(root / "workspace")) if (root / "workspace").exists() else "(no workspace)"
        suggested_tools = ["view.analyze_intent", "sys.heartbeat"]
        if not (root / "workspace").exists():
            suggested_tools.insert(0, "sys.workspace.scaffold")
        return _text(_success_envelope(
            {
                "workspace_root": str(root.absolute()),
                "folder_tree": tree,
                "current_branch": state.get("current_branch", "main"),
                "branches": list(state.get("branches", {}).keys()),
                "pipeline_stage": state.get("pipeline_stage", "init"),
                "checkpoints": state.get("checkpoints", []),
            },
            next_suggested_tools=suggested_tools,
        ))

    if name == "sys.heartbeat":
        uptime_seconds = int(time.time() - _START_TIME)
        tool_count = len(TOOL_DEFINITIONS)
        return _text(_success_envelope({
            "version": "10.0.0",
            "uptime_seconds": uptime_seconds,
            "loaded_tools": tool_count,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }))

    if name == "sys.health":
        # Alias for sys.heartbeat
        uptime_seconds = int(time.time() - _START_TIME)
        tool_count = len(TOOL_DEFINITIONS)
        return _text(_success_envelope({
            "version": "10.0.0",
            "uptime_seconds": uptime_seconds,
            "loaded_tools": tool_count,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }))

    if name == "sys.workspace.scaffold":
        project_name = arguments.get("project_name", "My Research Project")
        scaffold_minimal_workspace(root, project_name)
        tree = "\n".join(_walk_tree(root / "workspace"))
        return _text(_success_envelope(
            {"workspace": str(root.absolute()), "tree": tree},
            paths_created=[str(root.absolute())],
            next_suggested_tools=["view.analyze_intent", "sys.state"],
        ))

    if name == "sys.rollback":
        checkpoint_id = arguments.get("checkpoint_id")
        if not checkpoint_id:
            return _text(_error_envelope("checkpoint_id is required"))
        engine = ResearchEngine(root)
        try:
            result = engine.ledger.rollback(checkpoint_id)
            return _text(_success_envelope(
                {"checkpoint_id": checkpoint_id, "restored": True, "result": result},
                paths_modified=[str(root.absolute())],
            ))
        except Exception as e:
            return _text(_error_envelope(f"Rollback failed: {e}"))

    if name == "sys.analysis.log":
        entry = arguments.get("entry", "")
        step = arguments.get("step", "general")
        status = arguments.get("status", "planned")
        analysis_path = root / "workspace" / "analysis.md"
        analysis_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Append chronological log entry
        with open(analysis_path, "a") as f:
            f.write(f"[{timestamp}] {step}: {entry}\n")

        # Update Mermaid workflow diagram
        mermaid_path = root / "workspace" / "workflow.mermaid"
        mermaid_lines = ["graph TD"]
        if mermaid_path.exists():
            existing = mermaid_path.read_text()
            mermaid_lines = existing.strip().split("\n")
            if not mermaid_lines[0].startswith("graph"):
                mermaid_lines = ["graph TD"]

        status_class = status.replace(" ", "_")
        node_id = re.sub(r"[^a-zA-Z0-9]", "_", step)
        node_line = f"    {node_id}[{step}]:::{status_class}"
        if node_line not in mermaid_lines:
            mermaid_lines.append(node_line)

        # Add class definitions
        for cls_line in [
            "    classDef planned fill:#f0f0f0,stroke:#999",
            "    classDef running fill:#fff3cd,stroke:#ffc107",
            "    classDef complete fill:#d4edda,stroke:#28a745",
            "    classDef failed fill:#f8d7da,stroke:#dc3545",
            "    classDef dead_end fill:#f8d7da,stroke:#dc3545,stroke-dasharray: 5 5",
        ]:
            if cls_line not in mermaid_lines:
                mermaid_lines.append(cls_line)

        mermaid_path.write_text("\n".join(mermaid_lines) + "\n")

        # Try to render the Mermaid diagram to PNG
        diagram_result = render_workflow_diagram(root)

        sha = _compute_file_sha256(analysis_path)
        mermaid_sha = _compute_file_sha256(mermaid_path)
        response = {
            "logged": True,
            "mermaid_updated": True,
            "diagram_png": diagram_result.get("png_path"),
        }
        if diagram_result.get("warning"):
            response["diagram_warning"] = diagram_result["warning"]
        if diagram_result.get("rendered"):
            response["diagram_rendered"] = True

        return _text(_success_envelope(
            response,
            paths_modified=[
                str(analysis_path.absolute()),
                str(mermaid_path.absolute()),
            ],
            warnings=[diagram_result["warning"]] if diagram_result.get("warning") else None,
        ))

    # ── System synthesis ──────────────────────────────────────────

    if name == "sys.synthesize":
        project_name = arguments.get("project_name", "Research Project")
        # Scaffold synthesis templates
        result = scaffold_synthesis(root, project_name)

        # Regenerate citations from literature index
        citations = generate_citations_md(root)

        # Regenerate intake
        intake = regenerate_intake(root, project_name)

        suggested_tools = [
            "mem.citations.generate",
            "view.workspace.tree",
        ]
        return _text(_success_envelope(
            {
                "synthesis_dir": result.get("synthesis_dir"),
                "templates_created": result.get("paths_created"),
                "citations_generated": citations,
                "intake_regenerated": intake,
                "message": "Synthesis directory populated. Edit templates and run LaTeX to compile.",
            },
            paths_created=result.get("paths_created", []),
            next_suggested_tools=suggested_tools,
        ))

    if name == "sys.scaffold.synthesis":
        project_name = arguments.get("project_name", "Research Project")
        result = scaffold_synthesis(root, project_name)
        return _text(_success_envelope(
            result,
            paths_created=result.get("paths_created", []),
        ))

    # ── Memory tools (mem.*) ───────────────────────────────────────

    if name == "mem.methods.append":
        method = arguments.get("method", "")
        parameters = arguments.get("parameters", "")
        citation = arguments.get("citation", "")
        tool = arguments.get("tool", "")
        methods_path = root / "workspace" / "methods.md"
        methods_path.parent.mkdir(parents=True, exist_ok=True)

        from datetime import datetime as _dt
        ts = _dt.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        lines = [f"## {ts}", f"- **Method**: {method}"]
        if parameters:
            lines.append(f"  - **Parameters**: {parameters}")
        if tool:
            lines.append(f"  - **Tool**: {tool}")
        if citation:
            lines.append(f"  - **Citation**: {citation}")
        lines.append("")

        with open(methods_path, "a") as f:
            f.write("\n".join(lines) + "\n")

        sha = _compute_file_sha256(methods_path)
        return _text(_success_envelope(
            {"appended": True, "method": method},
            paths_modified=[str(methods_path.absolute())],
        ))

    if name == "mem.citation.add":
        bibtex = arguments.get("bibtex", "")
        citation_key = arguments.get("citation_key", "")
        source = arguments.get("source", "manual")
        citations_path = root / "workspace" / "citations.md"
        citations_path.parent.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        entry_lines = [
            f"### `{citation_key}`",
            f"  - **Added**: {ts}",
            f"  - **Source**: {source}",
            f"  - **Verified**: false",
            "",
            "```bibtex",
            bibtex,
            "```",
            "",
        ]
        with open(citations_path, "a") as f:
            f.write("\n".join(entry_lines) + "\n")

        sha = _compute_file_sha256(citations_path)
        return _text(_success_envelope(
            {"added": citation_key or "unnamed", "verified": False},
            paths_modified=[str(citations_path.absolute())],
        ))

    if name == "mem.regenerate.intake":
        intake_path = regenerate_intake(root)
        return _text(_success_envelope(
            {"intake_path": intake_path},
            paths_modified=[intake_path],
        ))

    if name == "mem.citations.generate":
        cit_path = generate_citations_md(root)
        return _text(_success_envelope(
            {"citations_path": cit_path},
            paths_modified=[cit_path],
        ))

    if name == "mem.literature.index":
        index = update_literature_index(root)
        count = len(index.get("entries", {}))
        return _text(_success_envelope(
            {"indexed": count, "entries": index["entries"]},
            next_suggested_tools=["mem.citations.generate"],
        ))

    # ── Query analysis ─────────────────────────────────────────────

    if name == "view.analyze_intent":
        query = arguments.get("query")
        if not query:
            return _text(_error_envelope("Missing required argument: query"))
        analyzer = IntentAnalyzer(root)
        intake = analyzer.build_bootstrap_intake(query)
        intake["constraints"]["depth"] = arguments.get("depth", "academic")
        suggested = intake.get("suggested_skills", [])[:3]
        return _text(_success_envelope(
            intake,
            next_suggested_tools=[f"tool.{s}" for s in suggested] if suggested else None,
        ))

    # ── Legacy / compatibility tools ───────────────────────────────

    if name == "research_status":
        engine = ResearchEngine(root)
        state = engine.ledger._load()
        return _text(_success_envelope(
            {
                "workspace": str(root.absolute()),
                "current_branch": state.get("current_branch", current_branch(root)),
                "branches": state.get("branches", {}),
                "input_hash_count": len(compute_input_hashes(root)),
                "local_override_root": str(manager.override_root) if manager.override_root.exists() else None,
            }
        ))

    if name == "research_agent":
        rel = _asset_by_name(manager, "agents", arguments["name"])
        return _text(manager.read_text(rel) if rel else f"Agent '{arguments['name']}' not found.")

    if name == "research_skill":
        rel = _asset_by_name(manager, "skills", arguments["name"])
        return _text(manager.read_text(rel) if rel else f"Skill '{arguments['name']}' not found.")

    if name == "research_workflow":
        config = yaml.safe_load(manager.read_text("config.yaml")) or {}
        workflow_id = arguments.get("name") or config.get("default_workflow", "quick_exploratory")
        rel = f"workflows/{workflow_id}.yaml"
        return _text(manager.read_text(rel) if manager.exists(rel) else f"Workflow '{workflow_id}' not found.")

    if name == "route_intent":
        engine = ResearchEngine(root)
        result = engine.analyze_query(arguments["query"], depth=arguments.get("depth", "academic"))
        return _text(result)

    if name in ("sys.branch.create", "create_experiment_branch"):
        from_step = arguments.get("from_step")
        result = create_numbered_experiment(
            root=root,
            name=arguments.get("name", "experiment"),
            hypothesis=arguments.get("hypothesis", ""),
            parent=arguments.get("parent"),
            from_step=from_step,
        )
        return _text(_success_envelope(result, paths_created=result.get("paths_created", [])))

    if name == "sys.checkpoint":
        ckpt_id = arguments.get("checkpoint_id") or f"ckpt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        description = arguments.get("description", "")
        from research_os.state.state_ledger import ResearchLedger as _Ledger
        ledger = _Ledger(root / ".os_state" / "state_ledger.json")
        result = ledger.snapshot_workspace(ckpt_id, root)

        # Record checkpoint in state
        state = load_state(root)
        state.setdefault("checkpoint_history", []).append({
            "id": ckpt_id,
            "step": state.get("current_branch", "main"),
            "timestamp": now_iso(),
            "description": description,
            "files": result["files_snapshotted"],
        })
        save_state(root, state)

        return _text(_success_envelope(
            result,
            next_suggested_tools=["sys.rollback"],
        ))

    if name == "sys.checkpoint.list":
        from research_os.state.checkpoint_manager import CheckpointManager as _CkptMgr
        mgr = _CkptMgr(root / ".os_state" / "checkpoints")
        all_cps = mgr.list_all()

        # Also read from state ledger's checkpoint_history
        state = load_state(root)
        history = state.get("checkpoint_history", [])

        return _text(_success_envelope({
            "checkpoints": all_cps,
            "history": history,
        }))

    if name == "sys.branch.merge":
        from research_os.state.state_ledger import ResearchLedger as _Ledger
        source = arguments["source"]
        target = arguments.get("target", "main")
        msg = arguments.get("message", "")

        ledger = _Ledger(root / ".os_state" / "state_ledger.json")
        ledger.merge_branch(source, target, msg)

        # Also sync into project_ops state
        state = load_state(root)
        if source in state.get("branches", {}):
            state["branches"][source]["status"] = "merged"
            state["branches"][source]["merge_commit"] = f"merge_{source}_into_{target}"
            state["branches"][source]["merged_at"] = now_iso()
        state["current_branch"] = target
        save_state(root, state)

        return _text(_success_envelope({
            "source": source,
            "target": target,
            "merged_at": now_iso(),
            "message": msg or f"Merged {source} into {target}",
        }))

    if name == "sys.branch.abandon":
        branch_id = arguments["branch_id"]
        reason = arguments.get("reason", "")

        state = load_state(root)
        if branch_id not in state.get("branches", {}):
            return _text(_error_envelope(f"Branch '{branch_id}' does not exist"))

        if branch_id == "main":
            return _text(_error_envelope("Cannot abandon the main branch"))

        state["branches"][branch_id]["status"] = "abandoned"
        state["branches"][branch_id]["evaluation"] = {
            "decision": "abandon",
            "rationale": reason or "Branch abandoned",
        }
        if state.get("current_branch") == branch_id:
            state["current_branch"] = "main"
        save_state(root, state)

        return _text(_success_envelope(
            {"branch_id": branch_id, "status": "abandoned", "reason": reason},
        ))

    if name == "log_decision":
        engine = ResearchEngine(root)
        result = engine.log_decision(
            context=arguments["context"],
            selected_option=arguments["selected"],
            rationale=arguments["rationale"],
            branch=arguments.get("branch_id"),
        )
        return _text(result)

    if name == "save_artifact":
        check_write_permitted(root / arguments["filename"])
        engine = ResearchEngine(root)
        result = engine.save_artifact(
            filepath=arguments["filename"],
            content=arguments["content"],
            artifact_type=arguments.get("artifact_type", "artifact"),
            branch=arguments.get("branch_id"),
        )
        abs_path = str((root / result["artifact"]).absolute())
        sha = _compute_file_sha256(Path(abs_path))
        return _text(_success_envelope(
            result,
            paths_created=[abs_path],
        ))

    if name == "search_skills":
        query = arguments.get("query", "").lower()
        index_path = root / ".research" / "cache" / "skill_index.json"
        if not index_path.exists():
            return _text(_error_envelope("Skill index not found. Please run skill indexer."))
        try:
            with open(index_path, "r") as f:
                index = json.load(f)
            results = [
                s for s in index.get("skills", [])
                if query in s["title"].lower() or query in s["description"].lower() or any(query in kw for kw in s.get("keywords", []))
            ]
            return _text(_success_envelope({"results": results}))
        except Exception as e:
            return _text(_error_envelope(f"Error searching skills: {e}"))

    if name == "load_skill_context":
        skill_name = arguments.get("skill_name")
        rel = _asset_by_name(manager, "skills", skill_name)
        return _text(manager.read_text(rel) if rel else f"Skill '{skill_name}' not found.")

    if name == "patch_file":
        try:
            check_write_permitted(root / arguments["filepath"])
            from research_os.utils.diff_editor import patch_file
            result = patch_file(str(root), arguments["filepath"], arguments["search_block"], arguments["replace_block"])
            abs_path = str((root / arguments["filepath"]).absolute())
            sha = _compute_file_sha256(Path(abs_path))
            return _text(_success_envelope(
                {"result": result},
                paths_modified=[abs_path],
            ))
        except Exception as e:
            return _text(_error_envelope(f"Error patching file: {e}"))

    if name == "write_to_scratchpad":
        thought = arguments.get("thought", "")
        scratchpad_path = root / ".research" / "cache" / "scratchpad.txt"
        scratchpad_path.parent.mkdir(parents=True, exist_ok=True)
        with open(scratchpad_path, "a") as f:
            f.write(f"{thought}\n---\n")
        abs_path = str(scratchpad_path.absolute())
        sha = _compute_file_sha256(scratchpad_path)
        return _text(_success_envelope(
            {"recorded": True},
            paths_modified=[abs_path],
        ))

    if name == "query_research_context":
        try:
            from research_os.utils.knowledge_graph import KnowledgeGraph
            kg = KnowledgeGraph(root)
            result = kg.query_research_context(arguments.get("question", ""))
            return _text(_success_envelope({"answer": result}))
        except Exception as e:
            return _text(_error_envelope(f"Error querying research context: {e}"))

    if name == "research_preflight":
        try:
            from research_os.utils.common import find_project_root
            project_root = find_project_root() or root
            checks = {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "workspace": str(project_root),
                "assets_dir": str(project_root / ".research") if (project_root / ".research").exists() else "not_found",
                "inputs_dir": str(project_root / "00_inputs") if (project_root / "00_inputs").exists() else "not_found",
            }
            return _text(_success_envelope({"status": "ok", "checks": checks}))
        except Exception as e:
            return _text(_error_envelope(f"Preflight error: {e}"))

    if name == "research_data_scale":
        try:
            from research_os.utils.data_scale_detector import detect_data_scale
            inputs_dir = root / "00_inputs" / "raw_data"
            if not inputs_dir.exists():
                return _text(_success_envelope({"status": "no_data", "message": "No raw data directory found"}))
            results = detect_data_scale(inputs_dir)
            return _text(_success_envelope(results))
        except Exception as e:
            return _text(_error_envelope(f"Data scale error: {e}"))

    # ── §4.2 Missing tool handlers ──────────────────────────────────

    if name == "tool.latex.compile":
        result = latex_compile(root)
        return _text(_success_envelope(
            {"pdf_path": result["pdf_path"], "success": result["success"]},
            warnings=[result["warning"]] if result.get("warning") else None,
        ))

    if name == "tool.pubmed.search":
        result = pubmed_search(
            query=arguments.get("query", ""),
            limit=arguments.get("limit", 5),
        )
        return _text(_success_envelope(result))

    if name == "tool.semantic_scholar.search":
        result = semantic_scholar_search(
            query=arguments.get("query", ""),
            limit=arguments.get("limit", 5),
        )
        return _text(_success_envelope(result))

    if name == "tool.google.scholar.search":
        result = google_scholar_search(
            query=arguments.get("query", ""),
            limit=arguments.get("limit", 5),
        )
        return _text(_success_envelope(result))

    if name == "tool.data.transform":
        try:
            result = data_transform(
                root=root,
                filepath=arguments.get("filepath", ""),
                operations=arguments.get("operations", []),
                output=arguments.get("output"),
            )
            paths = [result["output_path"]] if result.get("output_path") else []
            return _text(_success_envelope(result, paths_created=paths))
        except Exception as e:
            return _text(_error_envelope(str(e)))

    if name == "tool.statistical.test":
        try:
            result = statistical_test(
                filepath=arguments.get("filepath", ""),
                test_type=arguments.get("test_type", ""),
                x_column=arguments.get("x_column", ""),
                y_column=arguments.get("y_column"),
                group_column=arguments.get("group_column"),
            )
            return _text(_success_envelope(result))
        except Exception as e:
            return _text(_error_envelope(str(e)))

    if name == "tool.figure.create":
        try:
            result = figure_create(
                root=root,
                filepath=arguments.get("filepath", ""),
                chart_type=arguments.get("chart_type", ""),
                x_column=arguments.get("x_column", ""),
                y_column=arguments.get("y_column"),
                group_column=arguments.get("group_column"),
                title=arguments.get("title", ""),
                output=arguments.get("output"),
            )
            paths = [result["figure_path"]] if result.get("figure_path") else []
            return _text(_success_envelope(result, paths_created=paths))
        except Exception as e:
            return _text(_error_envelope(str(e)))

    if name == "tool.dashboard.create":
        try:
            result = dashboard_create(
                root=root,
                filepath=arguments.get("filepath", ""),
                dashboard_type=arguments.get("dashboard_type", "panel"),
            )
            paths = [result["dashboard_path"]] if result.get("dashboard_path") else []
            return _text(_success_envelope(result, paths_created=paths))
        except Exception as e:
            return _text(_error_envelope(str(e)))

    if name == "view.workspace.tree":
        result = workspace_tree(root, max_depth=arguments.get("max_depth", 4))
        return _text(_success_envelope(result))

    if name == "view.data.head":
        try:
            result = data_head(root, filepath=arguments.get("filepath", ""), n=arguments.get("n", 5))
            return _text(_success_envelope(result))
        except Exception as e:
            return _text(_error_envelope(str(e)))

    if name == "view.figure.show":
        try:
            result = figure_show(root, filepath=arguments.get("filepath", ""))
            return _text(_success_envelope(result))
        except Exception as e:
            return _text(_error_envelope(str(e)))

    return _text(_error_envelope(f"Unknown tool: {name}"))


if HAS_MCP:
    server = Server("research-os")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        from research_os.tools.tool_registry import ToolRegistry
        registry = ToolRegistry()
        dynamic_tools = {}
        for tool_meta in registry.get_all():
            dynamic_tools[tool_meta.tool_name] = {
                "description": f"Capabilities: {', '.join(tool_meta.capabilities)}",
                "inputSchema": tool_meta.inputSchema
            }

        merged_tools = {**TOOL_DEFINITIONS, **dynamic_tools}

        return [
            Tool(name=name, description=schema["description"], inputSchema=schema["inputSchema"])
            for name, schema in merged_tools.items()
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        return _handle_tool_call(name, arguments)

    async def run_stdio() -> None:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())


def run_fallback_stdio() -> None:
    import sys

    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method", "")
            params = request.get("params", {})
            if method == "list_tools":
                from research_os.tools.tool_registry import ToolRegistry
                registry = ToolRegistry()
                dynamic_tools = {}
                for tool_meta in registry.get_all():
                    dynamic_tools[tool_meta.tool_name] = {
                        "description": f"Capabilities: {', '.join(tool_meta.capabilities)}",
                        "inputSchema": tool_meta.inputSchema
                    }
                merged_tools = {**TOOL_DEFINITIONS, **dynamic_tools}
                response = {
                    "result": {"tools": [{"name": n, **schema} for n, schema in merged_tools.items()]},
                    "error": None,
                }
            elif method == "call_tool":
                contents = _handle_tool_call(params.get("name", ""), params.get("arguments", {}))
                response = {
                    "result": {"content": [{"type": item.type, "text": item.text} for item in contents]},
                    "error": None,
                }
            elif method == "initialize":
                response = {
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": False}},
                        "serverInfo": {"name": "research-os", "version": "10.0.0"},
                    },
                    "error": None,
                }
            else:
                response = {"result": None, "error": f"Unknown method: {method}"}
        except Exception as exc:  # Keep fallback server alive for client retries.
            response = {"result": None, "error": str(exc)}
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


def main() -> None:
    parser = argparse.ArgumentParser(description="Research OS MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "http"], default="stdio", help="Transport mode: stdio (default), sse, or http")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP/SSE transport")
    parser.add_argument("--workspace", type=str, help="Path to workspace directory (defaults to current directory)")
    parser.add_argument("--list-tools", action="store_true", help="List available tools and exit")
    parser.add_argument("--resume", action="store_true", help="Resume from the latest state on disk instead of starting fresh")
    args = parser.parse_args()

    # Set workspace from argument if provided
    if args.workspace:
        import os
        os.chdir(args.workspace)

    if args.list_tools:
        for name, schema in TOOL_DEFINITIONS.items():
            print(f"{name}: {schema['description']}")
        return

    if args.transport == "http":
        raise SystemExit("HTTP transport is not implemented in the package-native server yet. Use --transport stdio.")

    if HAS_MCP:
        import asyncio

        asyncio.run(run_stdio())
    else:
        run_fallback_stdio()


if __name__ == "__main__":
    main()
