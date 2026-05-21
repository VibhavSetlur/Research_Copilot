#!/usr/bin/env python3
"""Research Copilot MCP server with direct in-memory tool execution."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from research_copilot.engine import ResearchEngine
from research_copilot.project_ops import compute_input_hashes, current_branch
from research_copilot.utils.asset_manager import AssetManager

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


TOOL_DEFINITIONS: dict[str, dict[str, Any]] = {
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
        "description": "Classify a user query and compile a transient workflow for a depth profile",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language research request"},
                "depth": {"type": "string", "enum": DEPTH_ENUM, "description": "Routing depth"},
            },
            "required": ["query"],
        },
    },
    "create_experiment_branch": {
        "description": "Create an isolated experiment branch under 02_experiments and update the state ledger",
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
        "description": "Save a text artifact into the active experiment and create a sibling .meta.yaml",
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
        "description": "Surgically edit specific functions or lines in a file by replacing a search block with a new block.",
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
        "description": "Dump step-by-step reasoning, calculations, and data shape analyses to avoid bloating context memory.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "thought": {"type": "string", "description": "The reasoning or calculation to record"}
            },
            "required": ["thought"],
        },
    },
    "query_research_context": {
        "description": "Query the serialized Context Transfer Memoranda (CTMs) to retrieve specific research context without loading the entire document.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The question to ask against the CTMs"}
            },
            "required": ["question"],
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


def _handle_tool_call(name: str, arguments: dict | None) -> list[TextContent]:
    arguments = arguments or {}
    root = _project_root()
    manager = AssetManager(root)

    if name == "research_status":
        engine = ResearchEngine(root)
        state = engine.ledger._load()
        return _text(
            {
                "workspace": str(root),
                "current_branch": state.get("current_branch", current_branch(root)),
                "branches": state.get("branches", {}),
                "input_hash_count": len(compute_input_hashes(root)),
                "local_override_root": str(manager.override_root) if manager.override_root.exists() else None,
            }
        )

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
        return _text(engine.route_and_execute(arguments["query"], depth=arguments.get("depth", "academic")))

    if name == "create_experiment_branch":
        engine = ResearchEngine(root)
        return _text(engine.create_branch(arguments["name"], hypothesis=arguments.get("hypothesis", "")))

    if name == "log_decision":
        engine = ResearchEngine(root)
        return _text(
            engine.log_decision(
                context=arguments["context"],
                selected_option=arguments["selected"],
                rationale=arguments["rationale"],
                branch=arguments.get("branch_id"),
            )
        )

    if name == "save_artifact":
        engine = ResearchEngine(root)
        return _text(
            engine.save_artifact(
                filepath=arguments["filename"],
                content=arguments["content"],
                artifact_type=arguments.get("artifact_type", "artifact"),
                branch=arguments.get("branch_id"),
            )
        )

    if name == "search_skills":
        query = arguments.get("query", "").lower()
        index_path = root / ".research" / "cache" / "skill_index.json"
        if not index_path.exists():
            return _text("Skill index not found. Please run skill indexer.")
        try:
            with open(index_path, "r") as f:
                index = json.load(f)
            results = [s for s in index.get("skills", []) if query in s["title"].lower() or query in s["description"].lower() or any(query in kw for kw in s.get("keywords", []))]
            return _text(results)
        except Exception as e:
            return _text(f"Error searching skills: {e}")

    if name == "load_skill_context":
        skill_name = arguments.get("skill_name")
        rel = _asset_by_name(manager, "skills", skill_name)
        return _text(manager.read_text(rel) if rel else f"Skill '{skill_name}' not found.")

    if name == "patch_file":
        try:
            from research_copilot.utils.diff_editor import patch_file
            return _text(patch_file(str(root), arguments["filepath"], arguments["search_block"], arguments["replace_block"]))
        except Exception as e:
            return _text(f"Error patching file: {e}")

    if name == "write_to_scratchpad":
        thought = arguments.get("thought", "")
        scratchpad_path = root / ".research" / "cache" / "scratchpad.txt"
        scratchpad_path.parent.mkdir(parents=True, exist_ok=True)
        with open(scratchpad_path, "a") as f:
            f.write(f"{thought}\n---\n")
        return _text("Thought recorded successfully.")

    if name == "query_research_context":
        try:
            from research_copilot.utils.knowledge_graph import KnowledgeGraph
            kg = KnowledgeGraph(root)
            return _text(kg.query_research_context(arguments.get("question", "")))
        except Exception as e:
            return _text(f"Error querying research context: {e}")

    return _text(f"Unknown tool: {name}")


if HAS_MCP:
    server = Server("research-copilot")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name=name, description=schema["description"], inputSchema=schema["inputSchema"])
            for name, schema in TOOL_DEFINITIONS.items()
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
                response = {
                    "result": {"tools": [{"name": n, **schema} for n, schema in TOOL_DEFINITIONS.items()]},
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
                        "serverInfo": {"name": "research-copilot", "version": "9.0.0"},
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
    parser = argparse.ArgumentParser(description="Research Copilot MCP Server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--list-tools", action="store_true", help="List available tools and exit")
    args = parser.parse_args()

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
