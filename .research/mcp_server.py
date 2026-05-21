#!/usr/bin/env python3
"""Compatibility shim for the packaged Research Copilot MCP server."""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from research_copilot.server import main


if __name__ == "__main__":
    main()
