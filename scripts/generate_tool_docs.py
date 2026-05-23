#!/usr/bin/env python3
"""Generate MCP_TOOLS_REFERENCE.md from tool schemas.

This script reads tool definitions from server.py and generates
comprehensive documentation in docs/MCP_TOOLS_REFERENCE.md.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from research_os.server import TOOL_DEFINITIONS


def generate_docs():
    """Generate MCP tools reference documentation."""

    output = []
    output.append("# MCP Tools Reference\n")
    output.append("\n")
    output.append(
        "This document provides a comprehensive reference for all MCP tools exposed by Research OS.\n"
    )
    output.append("\n")
    output.append("## Tool Categories\n")
    output.append("\n")
    output.append("- **sys.*** - System tools (state, health, workspace management)\n")
    output.append("- **mem.*** - Memory tools (methods, analysis, citations)\n")
    output.append(
        "- **tool.*** - Research tools (data transform, statistical tests, figures)\n"
    )
    output.append("\n")
    output.append("---\n")
    output.append("\n")

    # Group tools by category
    categories = {
        "sys": [],
        "mem": [],
        "tool": [],
    }

    for name in sorted(TOOL_DEFINITIONS.keys()):
        if name.startswith("sys."):
            categories["sys"].append(name)
        elif name.startswith("mem."):
            categories["mem"].append(name)
        elif name.startswith("tool."):
            categories["tool"].append(name)
        else:
            # Add to tool category by default
            categories["tool"].append(name)

    # Generate documentation for each category
    for category, tool_names in categories.items():
        if not tool_names:
            continue

        output.append(f"## {category.upper()}.* Tools\n")
        output.append("\n")

        for name in tool_names:
            schema = TOOL_DEFINITIONS[name]
            output.append(f"### `{name}`\n")
            output.append("\n")
            output.append(f"{schema['description']}\n")
            output.append("\n")
            output.append("#### Input Schema\n")
            output.append("\n")
            output.append("```json\n")
            import json

            output.append(json.dumps(schema["inputSchema"], indent=2))
            output.append("\n")
            output.append("```\n")
            output.append("\n")
            output.append("---\n")
            output.append("\n")

    # Write to file
    docs_path = Path(__file__).parent.parent / "docs" / "MCP_TOOLS_REFERENCE.md"
    docs_path.parent.mkdir(parents=True, exist_ok=True)

    with open(docs_path, "w", encoding="utf-8") as f:
        f.write("".join(output))

    print(f"✅ Generated MCP tools reference: {docs_path}")
    print(f"   Documented {len(TOOL_DEFINITIONS)} tools")


if __name__ == "__main__":
    generate_docs()
