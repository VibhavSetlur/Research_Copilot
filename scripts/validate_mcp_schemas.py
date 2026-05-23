#!/usr/bin/env python3
"""Validate MCP tool schemas in server.py.

This script checks that all tool definitions in TOOL_DEFINITIONS have:
- Valid JSON schemas
- Required fields (description, inputSchema)
- Proper structure
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from research_os.server import TOOL_DEFINITIONS


def validate_tool_schema(name: str, schema: dict) -> list[str]:
    """Validate a single tool schema. Returns list of errors."""
    errors = []

    # Check required fields
    if "description" not in schema:
        errors.append(f"{name}: Missing 'description' field")
    elif not isinstance(schema["description"], str):
        errors.append(f"{name}: 'description' must be a string")

    if "inputSchema" not in schema:
        errors.append(f"{name}: Missing 'inputSchema' field")
    elif not isinstance(schema["inputSchema"], dict):
        errors.append(f"{name}: 'inputSchema' must be a dict")
    else:
        # Validate inputSchema structure
        input_schema = schema["inputSchema"]
        if "type" not in input_schema:
            errors.append(f"{name}: inputSchema missing 'type' field")
        elif input_schema["type"] != "object":
            errors.append(f"{name}: inputSchema type must be 'object'")

        # Check properties if present
        if "properties" in input_schema and not isinstance(
            input_schema["properties"], dict
        ):
            errors.append(f"{name}: inputSchema 'properties' must be a dict")

        # Check required if present
        if "required" in input_schema and not isinstance(
            input_schema["required"], list
        ):
            errors.append(f"{name}: inputSchema 'required' must be a list")

    return errors


def main():
    """Validate all MCP tool schemas."""
    all_errors = []

    for name, schema in TOOL_DEFINITIONS.items():
        errors = validate_tool_schema(name, schema)
        all_errors.extend(errors)

    if all_errors:
        print("❌ MCP tool schema validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print(f"✅ All {len(TOOL_DEFINITIONS)} MCP tool schemas are valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
