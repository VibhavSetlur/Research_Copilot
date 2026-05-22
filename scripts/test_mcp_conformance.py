#!/usr/bin/env python3
"""MCP protocol conformance test.

This script tests that the MCP server conforms to the MCP protocol specification.
It can be used with mcp-inspector or run standalone to verify basic conformance.
"""

import sys
import subprocess
from pathlib import Path


def test_with_inspector():
    """Run MCP conformance test using mcp-inspector."""
    print("Testing MCP conformance with mcp-inspector...")
    
    # Check if mcp-inspector is installed
    try:
        subprocess.run(
            ["npx", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
    except FileNotFoundError:
        print("❌ npx not found. Please install Node.js to use mcp-inspector.")
        print("   Alternatively, run the standalone conformance test.")
        return False
    
    # Run mcp-inspector
    cmd = [
        "npx",
        "-y",
        "@modelcontextprotocol/inspector",
        "python",
        "-m",
        "research_os.server",
        "--transport",
        "stdio"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print("✅ MCP conformance test passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ MCP conformance test failed: {e}")
        return False


def test_standalone_conformance():
    """Run standalone MCP conformance tests."""
    print("Running standalone MCP conformance tests...")
    
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    
    from research_os.server import TOOL_DEFINITIONS, _handle_tool_call
    import json
    
    errors = []
    
    # Test 1: All tools have valid schemas
    print("  Testing tool schemas...")
    for name, schema in TOOL_DEFINITIONS.items():
        if "description" not in schema:
            errors.append(f"Tool {name} missing description")
        if "inputSchema" not in schema:
            errors.append(f"Tool {name} missing inputSchema")
        else:
            input_schema = schema["inputSchema"]
            if "type" not in input_schema:
                errors.append(f"Tool {name} inputSchema missing type")
            elif input_schema["type"] != "object":
                errors.append(f"Tool {name} inputSchema type must be 'object'")
    
    # Test 2: sys.health tool exists and returns correct structure
    print("  Testing sys.health tool...")
    try:
        result = _handle_tool_call("sys.health", {})
        if len(result) != 1:
            errors.append("sys.health should return exactly one content item")
        else:
            data = json.loads(result[0].text)
            if data.get("status") != "success":
                errors.append("sys.health should return success status")
            if "version" not in data.get("data", {}):
                errors.append("sys.health should return version")
    except Exception as e:
        errors.append(f"sys.health test failed: {e}")
    
    # Test 3: sys.heartbeat tool exists
    print("  Testing sys.heartbeat tool...")
    try:
        result = _handle_tool_call("sys.heartbeat", {})
        if len(result) != 1:
            errors.append("sys.heartbeat should return exactly one content item")
        else:
            data = json.loads(result[0].text)
            if data.get("status") != "success":
                errors.append("sys.heartbeat should return success status")
    except Exception as e:
        errors.append(f"sys.heartbeat test failed: {e}")
    
    # Test 4: sys.state tool exists
    print("  Testing sys.state tool...")
    try:
        result = _handle_tool_call("sys.state", {})
        if len(result) != 1:
            errors.append("sys.state should return exactly one content item")
        else:
            data = json.loads(result[0].text)
            if data.get("status") != "success":
                errors.append("sys.state should return success status")
    except Exception as e:
        errors.append(f"sys.state test failed: {e}")
    
    if errors:
        print("❌ Standalone conformance test failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ Standalone conformance test passed")
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP protocol conformance test")
    parser.add_argument("--inspector", action="store_true", help="Use mcp-inspector for testing")
    parser.add_argument("--standalone", action="store_true", help="Run standalone tests")
    args = parser.parse_args()
    
    if args.inspector:
        success = test_with_inspector()
    elif args.standalone:
        success = test_standalone_conformance()
    else:
        # Default to standalone test
        success = test_standalone_conformance()
        print("\nTip: Use --inspector to run with mcp-inspector for full conformance testing")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
