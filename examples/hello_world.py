#!/usr/bin/env python3
"""Hello World example for Research OS using MCP."""

import asyncio
import logging
from research_os.intent_router import IntentAnalyzer
from research_os.utils.common import find_project_root

logging.basicConfig(level=logging.INFO)

async def main():
    root = find_project_root()
    analyzer = IntentAnalyzer(root)

    query = "Analyze the basic demographics of the provided dataset and create a summary report."
    print(f"Analyzing query: '{query}'")

    intake = analyzer.build_bootstrap_intake(query)

    cls = intake.get("classification", {})
    print("\nIntake Analysis:")
    print(f"Primary Intent: {cls.get('primary_intent', 'unknown')}")
    print(f"Suggested Skills: {', '.join(intake.get('suggested_skills', []))}")
    print(f"Suggested Agents: {', '.join(intake.get('suggested_agents', []))}")
    print("\nNext step: IDE uses this intake to decide which MCP tools to call.")

if __name__ == "__main__":
    asyncio.run(main())
