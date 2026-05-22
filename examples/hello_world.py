#!/usr/bin/env python3
"""Hello World example for Research Copilot using MCP."""

import asyncio
import logging
from research_copilot.intent_router import IntentRouter
from research_copilot.utils.common import find_project_root

logging.basicConfig(level=logging.INFO)

async def main():
    root = find_project_root()
    router = IntentRouter(root)
    
    query = "Analyze the basic demographics of the provided dataset and create a summary report."
    print(f"Routing query: '{query}'")
    
    result = router.route(query, depth="quick")
    
    print("\nRouting Result:")
    print(f"Primary Intent: {result['classification']['primary_intent']}")
    print(f"Agents Required: {', '.join(result['context']['agents'])}")
    print(f"Skills Required: {', '.join(result['context']['skills'])}")
    print("\nNext step: Start the MCP server using `rcp start` and submit the query via your MCP client.")

if __name__ == "__main__":
    asyncio.run(main())
