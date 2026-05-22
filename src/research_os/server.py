#!/usr/bin/env python3
"""Research OS MCP server v3.0 — Research Guidance Engine"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("research-os.server")

from research_os.project_ops import (
    compute_file_hash,
    create_experiment_branch,
    load_state,
    now_iso,
    scaffold_minimal_workspace,
    log_decision,
)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool

    HAS_MCP = True
except ImportError:
    HAS_MCP = False

    @dataclass
    class TextContent:
        type: str
        text: str

_START_TIME = time.time()

# ---------------------------------------------------------------------------
# Rate Limiter
# ---------------------------------------------------------------------------

class RateLimiter:
    def __init__(self, max_calls: int = 100, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = defaultdict(list)
    
    def is_allowed(self, client_id: str = "default") -> bool:
        now = time.time()
        self.calls[client_id] = [t for t in self.calls[client_id] if now - t < self.window_seconds]
        if len(self.calls[client_id]) >= self.max_calls:
            logger.warning(f"Rate limit exceeded for {client_id}")
            return False
        self.calls[client_id].append(now)
        return True

_rate_limiter = RateLimiter()

# ---------------------------------------------------------------------------
# Envelope
# ---------------------------------------------------------------------------

def _envelope(data: Any = None, *, status: str = "success") -> dict:
    return {"status": status, "data": data or {}}

def _success_envelope(data: Any = None) -> dict:
    return _envelope(data, status="success")

def _error_envelope(message: str) -> dict:
    return _envelope({"error": message}, status="error")

def _text(payload: Any) -> list[TextContent]:
    if isinstance(payload, str):
        return [TextContent(type="text", text=payload)]
    return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]

# ---------------------------------------------------------------------------
# Tool Definitions
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = {
    "sys.guidance.get": {
        "description": "Returns the full YAML content of a guidance protocol.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "protocol_name": {"type": "string", "description": "Protocol name (e.g., domain_analysis)"}
            },
            "required": ["protocol_name"]
        }
    },
    "sys.guidance.list": {
        "description": "Lists all available protocols with one-line summaries.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "sys.workspace.scaffold": {
        "description": "Create the full directory structure for a new project.",
        "inputSchema": {
            "type": "object",
            "properties": {"project_name": {"type": "string"}},
        }
    },
    "sys.file.read": {
        "description": "Securely read a file from the workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {"filepath": {"type": "string"}},
            "required": ["filepath"]
        }
    },
    "sys.file.write": {
        "description": "Securely write to a file in the workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {"filepath": {"type": "string"}, "content": {"type": "string"}},
            "required": ["filepath", "content"]
        }
    },
    "sys.file.list": {
        "description": "List files in a directory.",
        "inputSchema": {
            "type": "object",
            "properties": {"directory": {"type": "string"}},
            "required": ["directory"]
        }
    },
    "sys.file.delete": {
        "description": "Delete a file.",
        "inputSchema": {
            "type": "object",
            "properties": {"filepath": {"type": "string"}},
            "required": ["filepath"]
        }
    },
    "sys.state.get": {
        "description": "Get full workspace state.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "sys.state.summary": {
        "description": "Get a brief summary of the state.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "sys.checkpoint.create": {
        "description": "Snapshot workspace state.",
        "inputSchema": {
            "type": "object",
            "properties": {"description": {"type": "string"}}
        }
    },
    "sys.checkpoint.rollback": {
        "description": "Rollback to a checkpoint.",
        "inputSchema": {
            "type": "object",
            "properties": {"checkpoint_id": {"type": "string"}},
            "required": ["checkpoint_id"]
        }
    },
    "sys.checkpoint.list": {
        "description": "List all checkpoints.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "sys.branch.create": {
        "description": "Create an experiment branch.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "hypothesis": {"type": "string"},
                "parent": {"type": "string"}
            },
            "required": ["name"]
        }
    },
    "sys.branch.switch": {
        "description": "Switch to another branch.",
        "inputSchema": {
            "type": "object",
            "properties": {"branch_id": {"type": "string"}},
            "required": ["branch_id"]
        }
    },
    "sys.branch.list": {
        "description": "List all branches.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "sys.branch.merge": {
        "description": "Merge branches.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "target": {"type": "string"},
                "message": {"type": "string"}
            },
            "required": ["source"]
        }
    },
    "mem.analysis.log": {
        "description": "Append to workspace/analysis.md",
        "inputSchema": {
            "type": "object",
            "properties": {"entry": {"type": "string"}},
            "required": ["entry"]
        }
    },
    "mem.methods.append": {
        "description": "Append to workspace/methods.md",
        "inputSchema": {
            "type": "object",
            "properties": {"method": {"type": "string"}},
            "required": ["method"]
        }
    },
    "tool.search.semantic_scholar": {
        "description": "Search Semantic Scholar.",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "limit": {"type": "number"}},
            "required": ["query"]
        }
    },
    "tool.search.pubmed": {
        "description": "Search PubMed.",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "limit": {"type": "number"}},
            "required": ["query"]
        }
    },
    "tool.search.crossref": {
        "description": "Search Crossref.",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "limit": {"type": "number"}},
            "required": ["query"]
        }
    },
    "tool.search.web": {
        "description": "Search the web.",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    },
    "tool.web.scrape": {
        "description": "Scrape a webpage.",
        "inputSchema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"]
        }
    },
    "tool.literature.download": {
        "description": "Download a paper PDF.",
        "inputSchema": {
            "type": "object",
            "properties": {"url": {"type": "string"}, "filename": {"type": "string"}},
            "required": ["url", "filename"]
        }
    },
    "tool.python.exec": {
        "description": "Execute a Python script.",
        "inputSchema": {
            "type": "object",
            "properties": {"script_path": {"type": "string"}},
            "required": ["script_path"]
        }
    },
    "tool.package.install": {
        "description": "Install Python packages.",
        "inputSchema": {
            "type": "object",
            "properties": {"packages": {"type": "array", "items": {"type": "string"}}},
            "required": ["packages"]
        }
    },
    "tool.env.freeze": {
        "description": "Freeze current environment.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "tool.env.restore": {
        "description": "Restore environment.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "tool.log.decision": {
        "description": "Log a key reasoning step.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "context": {"type": "string"},
                "selected": {"type": "string"},
                "rationale": {"type": "string"}
            },
            "required": ["context", "selected", "rationale"]
        }
    }
}

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def _log_search(root: Path, tool_name: str, query: str, count: int):
    log_path = root / "workspace" / "logs" / "searches.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps({
            "timestamp": now_iso(),
            "tool": tool_name,
            "query": query,
            "results_count": count
        }) + "\n")

def _handle_tool_call(name: str, arguments: dict, root: Path) -> list[TextContent]:
    if not _rate_limiter.is_allowed():
        return _text(_error_envelope("Rate limit exceeded."))
    
    logger.info(f"Tool call: {name}")

    if name == "sys.guidance.list":
        p_dir = Path(__file__).parent / "protocols"
        if not p_dir.exists():
            return _text(_error_envelope("Protocols directory not found"))
        protocols = []
        for p in p_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(p.read_text())
                protocols.append({"name": p.stem, "description": data.get("description", "")})
            except:
                pass
        return _text(_success_envelope({"protocols": protocols}))
        
    if name == "sys.guidance.get":
        p_name = arguments.get("protocol_name")
        p_file = Path(__file__).parent / "protocols" / f"{p_name}.yaml"
        if not p_file.exists():
            return _text(_error_envelope("Protocol not found"))
        return _text(_success_envelope({"content": p_file.read_text()}))

    if name == "sys.workspace.scaffold":
        scaffold_minimal_workspace(root, arguments.get("project_name", "Research Project"))
        return _text(_success_envelope({"scaffolded": True}))

    if name == "sys.file.read":
        p = root / arguments["filepath"]
        if not p.exists() or not p.is_file():
            return _text(_error_envelope("File not found"))
        return _text(_success_envelope({"content": p.read_text()}))

    if name == "sys.file.write":
        p = root / arguments["filepath"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(arguments["content"])
        return _text(_success_envelope({"written": True, "checksum": compute_file_hash(p)}))

    if name == "sys.file.list":
        p = root / arguments["directory"]
        if not p.exists() or not p.is_dir():
            return _text(_error_envelope("Directory not found"))
        files = [str(f.relative_to(root)) for f in p.rglob("*") if f.is_file()]
        return _text(_success_envelope({"files": files}))

    if name == "sys.file.delete":
        p = root / arguments["filepath"]
        if p.exists() and p.is_file():
            p.unlink()
            return _text(_success_envelope({"deleted": True}))
        return _text(_error_envelope("File not found"))

    if name == "sys.state.get":
        return _text(_success_envelope(load_state(root)))

    if name == "sys.state.summary":
        state = load_state(root)
        return _text(_success_envelope({
            "current_branch": state.get("current_branch"),
            "branches": list(state.get("branches", {}).keys())
        }))

    if name == "sys.branch.create":
        res = create_experiment_branch(arguments["name"], arguments.get("hypothesis", ""), arguments.get("parent"), root=root)
        return _text(_success_envelope(res))

    if name == "mem.analysis.log":
        log_path = root / "workspace" / "analysis.md"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"[{now_iso()}] {arguments['entry']}\n")
        return _text(_success_envelope({"logged": True}))

    if name == "mem.methods.append":
        m_path = root / "workspace" / "methods.md"
        m_path.parent.mkdir(parents=True, exist_ok=True)
        with open(m_path, "a") as f:
            f.write(f"- {arguments['method']}\n")
        return _text(_success_envelope({"logged": True}))

    if name == "tool.search.web":
        q = arguments["query"]
        _log_search(root, name, q, 0)
        return _text(_success_envelope({"message": "Placeholder for web search backend", "query": q}))

    if name == "tool.python.exec":
        p = root / arguments["script_path"]
        if not p.exists():
            return _text(_error_envelope("Script not found"))
        res = subprocess.run([sys.executable, str(p)], cwd=str(p.parent), capture_output=True, text=True)
        return _text(_success_envelope({"stdout": res.stdout, "stderr": res.stderr, "code": res.returncode}))

    if name == "tool.log.decision":
        res = log_decision(arguments["context"], arguments["selected"], arguments["rationale"], root=root)
        return _text(_success_envelope(res))

    # Catch-all for unimplemeted tools (placeholders for phase 2 completeness)
    if name.startswith("sys.") or name.startswith("tool.") or name.startswith("mem."):
        return _text(_success_envelope({"message": f"{name} is a stub implementation."}))

    return _text(_error_envelope(f"Unknown tool: {name}"))


if HAS_MCP:
    server = Server("research-os")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name=name, description=schema["description"], inputSchema=schema["inputSchema"])
            for name, schema in TOOL_DEFINITIONS.items()
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        import os
        root = Path(os.getcwd())
        return _handle_tool_call(name, arguments, root)

    async def run_stdio() -> None:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio")
    parser.add_argument("--workspace", type=str)
    args = parser.parse_args()

    if args.workspace:
        os.chdir(args.workspace)

    if HAS_MCP:
        import asyncio
        asyncio.run(run_stdio())
    else:
        sys.exit("MCP package missing.")

if __name__ == "__main__":
    main()
