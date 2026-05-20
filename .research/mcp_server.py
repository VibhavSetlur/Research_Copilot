#!/usr/bin/env python3
"""Research Copilot MCP Server — exposes CLI commands as MCP tools.

This server wraps the Research Copilot CLI in the Model Context Protocol (MCP),
allowing any MCP-compatible client (Claude Desktop, Cursor, generic LLMs) to
call research commands as native functions without parsing stdout.

Usage:
    # Stdio mode (for Claude Desktop, Cursor):
    python .research/mcp_server.py

    # HTTP mode (for remote clients):
    python .research/mcp_server.py --transport http --port 8080

Configuration:
    Add to your MCP client config:
    {
        "mcpServers": {
            "research-copilot": {
                "command": "python",
                "args": ["/path/to/.research/mcp_server.py"]
            }
        }
    }
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

# Add parent to path for imports
_research_path = Path(__file__).parent
_core_path = _research_path / "core"
_cli_path = _research_path
if str(_core_path) not in sys.path:
    sys.path.insert(0, str(_core_path))
if str(_cli_path) not in sys.path:
    sys.path.insert(0, str(_cli_path))
if str(_research_path / "scripts" / "utils") not in sys.path:
    sys.path.insert(0, str(_research_path / "scripts" / "utils"))

# Try to import mcp, fall back to stdio protocol if not available
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


# Tool definitions for MCP
TOOL_DEFINITIONS = {
    "research_status": {
        "description": "Show project state, token budget, pipeline status, iterations, and next recommended step",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_scan": {
        "description": "Scan inputs/ directory, build research map of available data and context files",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_map": {
        "description": "Show the current research map (grounding context for all decisions)",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_intake": {
        "description": "Show intake form status — what fields are filled, what is missing",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_followups": {
        "description": "Show follow-up questions the user needs to answer to proceed",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_iterations": {
        "description": "Show iteration history — what has been tried, results, and decisions",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_budget": {
        "description": "Show token budget status, usage by phase, and CTM history",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_dag": {
        "description": "Show execution DAG summary — what scripts have run, their dependencies, and status",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_data_scale": {
        "description": "Show data scale analysis and library constraints for the current dataset",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_hooks": {
        "description": "Show registered lifecycle hooks and execution log",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_validate": {
        "description": "Run quality gate check for a specific phase or all phases",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phase": {
                    "type": "string",
                    "description": "Phase to validate (omit for all phases). Options: research_init, literature_deep, method_route, data_scaffold, execute_analysis, compile_outputs, audit_validate",
                },
            },
            "required": [],
        },
    },
    "research_approve": {
        "description": "Approve a pending phase gate request, allowing the pipeline to proceed",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phase": {
                    "type": "string",
                    "description": "Phase to approve",
                },
            },
            "required": ["phase"],
        },
    },
    "research_reject": {
        "description": "Reject a pending phase gate request with feedback, sending it back for revision",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phase": {
                    "type": "string",
                    "description": "Phase to reject",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for rejection",
                },
            },
            "required": ["phase", "reason"],
        },
    },
    "research_agent": {
        "description": "Show a specific agent's full instructions and protocol",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Agent name (e.g., research_init, literature_deep, method_route, data_scaffold, execute_analysis, compile_outputs, audit_validate, research_iterate, critic, methodology_scout, replication_validator)",
                },
            },
            "required": ["name"],
        },
    },
    "research_agents": {
        "description": "List all available agents with descriptions",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_skill": {
        "description": "Show a specific skill's methodology and instructions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Skill name",
                },
            },
            "required": ["name"],
        },
    },
    "research_skills": {
        "description": "List all available skills by category",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_skill_search": {
        "description": "Search for skills matching a keyword or query",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string",
                },
            },
            "required": ["query"],
        },
    },
    "research_workflow": {
        "description": "Show current workflow configuration, pipeline stages, and iteration support",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_verify_citations": {
        "description": "Run three-pass citation verification on the current bibliography (existence, content, retraction)",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_trace_claims": {
        "description": "Run claim tracer on the current manuscript, building a claim-to-evidence graph",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_debug": {
        "description": "Auto-debug a failing script with up to 3 attempts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "Path to the failing script",
                },
                "max_attempts": {
                    "type": "integer",
                    "description": "Maximum debug attempts (default: 3)",
                },
            },
            "required": ["script"],
        },
    },
    "research_cache_stats": {
        "description": "Show cache statistics — hit rates, size, table counts",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "research_cache_clear": {
        "description": "Prune old cache entries",
        "inputSchema": {
            "type": "object",
            "properties": {
                "older_than": {
                    "type": "string",
                    "description": "Clear entries older than this (e.g., '7d', '30d')",
                },
            },
            "required": [],
        },
    },
    "research_intake_interview": {
        "description": "Start a conversational intake interview — the AI will ask guiding questions to build the intake form automatically",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "User's response to the current interview question",
                },
                "start": {
                    "type": "boolean",
                    "description": "Set to true to start a new interview",
                },
            },
            "required": [],
        },
    },
    "research_preregistration": {
        "description": "Generate an OSF-compatible pre-registration document with hypotheses, power analysis, and statistical tests",
        "inputSchema": {
            "type": "object",
            "properties": {
                "hypotheses": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of hypotheses to pre-register",
                },
                "analysis_plan": {
                    "type": "string",
                    "description": "Path to the analysis plan file",
                },
            },
            "required": [],
        },
    },
    "research_reviewer2": {
        "description": "Run the adversarial 'Reviewer 2' critic on research findings — tries to destroy the conclusions by finding unaddressed confounders, alternative explanations, and methodological flaws",
        "inputSchema": {
            "type": "object",
            "properties": {
                "findings_path": {
                    "type": "string",
                    "description": "Path to the research findings file to critique",
                },
            },
            "required": [],
        },
    },
    "research_dependency_check": {
        "description": "Check for uninstalled imports in a script and auto-resolve dependencies using uv or pip",
        "inputSchema": {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "Path to the Python script to check",
                },
                "auto_install": {
                    "type": "boolean",
                    "description": "Automatically install missing dependencies (default: false)",
                },
            },
            "required": ["script"],
        },
    },
}


def _capture_output(func, *args, **kwargs) -> str:
    """Capture stdout from a CLI command function and return as string."""
    import io
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    try:
        func(*args, **kwargs)
    except SystemExit:
        pass
    except Exception as e:
        sys.stdout = old_stdout
        return f"Error: {str(e)}"
    finally:
        sys.stdout = old_stdout
    return captured.getvalue()


def _run_cli_command(command: str, args: Optional[dict] = None) -> str:
    """Run a research.py CLI command via direct function invocation (no subprocess)."""
    args = args or {}

    command_handlers = {
        "status": lambda: _capture_output(
            _import_cmd("project").cmd_status, _make_namespace(args)
        ),
        "scan": lambda: _capture_output(
            _import_cmd("scan").cmd_scan, _make_namespace(args)
        ),
        "map": lambda: _capture_output(
            _import_cmd("project").cmd_map, _make_namespace(args)
        ),
        "intake": lambda: _capture_output(
            _import_cmd("project").cmd_intake, _make_namespace(args)
        ),
        "followups": lambda: _capture_output(
            _import_cmd("info").cmd_followups, _make_namespace(args)
        ),
        "iterations": lambda: _capture_output(
            _import_cmd("info").cmd_iterations, _make_namespace(args)
        ),
        "budget": lambda: _capture_output(
            _import_cmd("tracking").cmd_budget, _make_namespace(args)
        ),
        "dag": lambda: _capture_output(
            _import_cmd("tracking").cmd_dag, _make_namespace(args)
        ),
        "data-scale": lambda: _capture_output(
            _import_cmd("tracking").cmd_data_scale, _make_namespace(args)
        ),
        "hooks": lambda: _capture_output(
            _import_cmd("tracking").cmd_hooks, _make_namespace(args)
        ),
        "agents": lambda: _capture_output(
            _import_cmd("info").cmd_agents, _make_namespace(args, name=None)
        ),
        "skills": lambda: _capture_output(
            _import_cmd("info").cmd_skills, _make_namespace(args, name=None)
        ),
        "workflow": lambda: _capture_output(
            _import_cmd("info").cmd_workflow, _make_namespace(args)
        ),
        "validate": lambda: _capture_output(
            _import_cmd("analysis").cmd_validate, _make_namespace(args)
        ),
        "approve": lambda: _capture_output(
            _import_cmd("approval").cmd_approve, _make_namespace(args)
        ),
        "reject": lambda: _capture_output(
            _import_cmd("approval").cmd_reject, _make_namespace(args)
        ),
        "agent": lambda: _capture_output(
            _import_cmd("info").cmd_agents, _make_namespace(args)
        ),
        "skill": lambda: _capture_output(
            _import_cmd("info").cmd_skills, _make_namespace(args)
        ),
        "skill-search": lambda: _capture_output(
            _import_cmd("info").cmd_skill_search, _make_namespace(args)
        ),
        "verify-citations": lambda: _capture_output(
            _import_cmd("citations").cmd_verify_citations, _make_namespace(args)
        ),
        "trace-claims": lambda: _capture_output(
            _import_cmd("citations").cmd_trace_claims, _make_namespace(args)
        ),
        "debug": lambda: _capture_output(
            _import_cmd("analysis").cmd_debug, _make_namespace(args)
        ),
        "cache": lambda: _capture_output(
            _import_cmd("cache").cmd_cache, _make_namespace(args)
        ),
    }

    handler = command_handlers.get(command)
    if handler:
        try:
            return handler()
        except Exception as e:
            return f"Error executing '{command}': {str(e)}"
    return f"Error: Unknown command '{command}'"


def _import_cmd(module_name: str):
    """Lazily import a CLI command module."""
    from cli.commands import __dict__ as cmd_modules
    if module_name not in cmd_modules:
        import importlib
        importlib.import_module(f"cli.commands.{module_name}")
        from cli.commands import __dict__ as cmd_modules
    return __import__("cli.commands", fromlist=[module_name])


def _make_namespace(args: dict, **defaults) -> Any:
    """Convert dict to argparse.Namespace for CLI command compatibility."""
    class NS:
        pass
    ns = NS()
    for k, v in {**defaults, **args}.items():
        setattr(ns, k.replace("-", "_"), v)
    return ns


def _handle_tool_call(name: str, arguments: dict) -> list:
    """Handle a tool call and return MCP-compatible content."""
    command_map = {
        "research_status": ("status", {}),
        "research_scan": ("scan", {}),
        "research_map": ("map", {}),
        "research_intake": ("intake", {}),
        "research_followups": ("followups", {}),
        "research_iterations": ("iterations", {}),
        "research_budget": ("budget", {}),
        "research_dag": ("dag", {}),
        "research_data_scale": ("data-scale", {}),
        "research_hooks": ("hooks", {}),
        "research_agents": ("agents", {}),
        "research_skills": ("skills", {}),
        "research_workflow": ("workflow", {}),
        "research_verify_citations": ("verify-citations", {}),
        "research_trace_claims": ("trace-claims", {}),
        "research_cache_stats": ("cache", {"action": "stats"}),
    }

    if name in command_map:
        cmd, defaults = command_map[name]
        args = {**defaults, **(arguments or {})}
        output = _run_cli_command(cmd, args)
        return [TextContent(type="text", text=output)]

    if name == "research_validate":
        phase = arguments.get("phase", "")
        output = _run_cli_command("validate", {"phase": phase} if phase else {})
        return [TextContent(type="text", text=output)]

    if name == "research_approve":
        output = _run_cli_command("approve", {"phase": arguments["phase"]})
        return [TextContent(type="text", text=output)]

    if name == "research_reject":
        output = _run_cli_command("reject", {
            "phase": arguments["phase"],
            "reason": arguments["reason"],
        })
        return [TextContent(type="text", text=output)]

    if name == "research_agent":
        output = _run_cli_command("agent", {"name": arguments["name"]})
        return [TextContent(type="text", text=output)]

    if name == "research_skill":
        output = _run_cli_command("skill", {"name": arguments["name"]})
        return [TextContent(type="text", text=output)]

    if name == "research_skill_search":
        output = _run_cli_command("skill-search", {"query": arguments["query"]})
        return [TextContent(type="text", text=output)]

    if name == "research_debug":
        args = {"script": arguments["script"]}
        if "max_attempts" in arguments:
            args["max_attempts"] = arguments["max_attempts"]
        output = _run_cli_command("debug", args)
        return [TextContent(type="text", text=output)]

    if name == "research_cache_clear":
        args = {"action": "clear"}
        if "older_than" in arguments:
            args["older_than"] = arguments["older_than"]
        output = _run_cli_command("cache", args)
        return [TextContent(type="text", text=output)]

    if name == "research_intake_interview":
        from cli.commands.intake_interview import run_intake_interview
        result = run_intake_interview(
            start=arguments.get("start", False),
            message=arguments.get("message", ""),
        )
        return [TextContent(type="text", text=result)]

    if name == "research_preregistration":
        from cli.commands.preregistration import generate_preregistration
        result = generate_preregistration(
            hypotheses=arguments.get("hypotheses", []),
            analysis_plan=arguments.get("analysis_plan", ""),
        )
        return [TextContent(type="text", text=result)]

    if name == "research_reviewer2":
        from cli.commands.reviewer2 import run_reviewer2
        result = run_reviewer2(
            findings_path=arguments.get("findings_path", ""),
        )
        return [TextContent(type="text", text=result)]

    if name == "research_dependency_check":
        from cli.commands.dependency_check import check_dependencies
        result = check_dependencies(
            script=arguments["script"],
            auto_install=arguments.get("auto_install", False),
        )
        return [TextContent(type="text", text=result)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


# MCP Server implementation
if HAS_MCP:
    server = Server("research-copilot")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available Research Copilot tools."""
        tools = []
        for name, schema in TOOL_DEFINITIONS.items():
            tools.append(
                Tool(
                    name=name,
                    description=schema["description"],
                    inputSchema=schema["inputSchema"],
                )
            )
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list:
        """Execute a Research Copilot tool."""
        return _handle_tool_call(name, arguments)

    async def run_stdio():
        """Run the MCP server in stdio mode."""
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    async def run_http(port: int = 8080):
        """Run the MCP server in HTTP mode."""
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route
        from starlette.responses import PlainTextResponse
        import uvicorn

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await server.run(
                    streams[0], streams[1], server.create_initialization_options()
                )

        app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
                Route("/health", endpoint=lambda r: PlainTextResponse("OK")),
            ]
        )

        config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
        server_uvicorn = uvicorn.Server(config)
        await server_uvicorn.serve()


def run_fallback_stdio():
    """Fallback JSON-RPC-like protocol over stdin/stdout when mcp package is not installed.

    This provides a simple protocol that LLMs can use without the full MCP SDK.
    Format: {"method": "tool_name", "params": {...}}
    Response: {"result": "...", "error": null} or {"result": null, "error": "..."}
    """
    import sys

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line.strip())
            method = request.get("method", "")
            params = request.get("params", {})

            if method == "list_tools":
                result = {
                    "tools": [
                        {"name": name, **schema}
                        for name, schema in TOOL_DEFINITIONS.items()
                    ]
                }
                response = {"result": result, "error": None}
            elif method == "call_tool":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                contents = _handle_tool_call(tool_name, arguments)
                result = {
                    "content": [
                        {"type": c.type, "text": c.text} for c in contents
                    ]
                }
                response = {"result": result, "error": None}
            elif method == "initialize":
                response = {
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": False},
                        },
                        "serverInfo": {
                            "name": "research-copilot",
                            "version": "8.0.0",
                        },
                    },
                    "error": None,
                }
            else:
                response = {"result": None, "error": f"Unknown method: {method}"}

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError:
            sys.stdout.write(
                json.dumps({"result": None, "error": "Invalid JSON"}) + "\n"
            )
            sys.stdout.flush()
        except KeyboardInterrupt:
            break
        except Exception as e:
            sys.stdout.write(
                json.dumps({"result": None, "error": str(e)}) + "\n"
            )
            sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description="Research Copilot MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for HTTP transport (default: 8080)",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List available tools and exit",
    )
    args = parser.parse_args()

    if args.list_tools:
        for name, schema in TOOL_DEFINITIONS.items():
            print(f"\n{name}:")
            print(f"  {schema['description']}")
            if schema["inputSchema"]["properties"]:
                print("  Parameters:")
                for param, param_schema in schema["inputSchema"]["properties"].items():
                    required = param in schema["inputSchema"].get("required", [])
                    print(f"    - {param} ({param_schema['type']}){' [required]' if required else ''}: {param_schema.get('description', '')}")
        return

    if HAS_MCP:
        import asyncio

        if args.transport == "http":
            asyncio.run(run_http(args.port))
        else:
            asyncio.run(run_stdio())
    else:
        run_fallback_stdio()


if __name__ == "__main__":
    main()
