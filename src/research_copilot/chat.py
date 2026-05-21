#!/usr/bin/env python3
"""Persistent Conversational Control Plane for Research Copilot.

Provides a chat interface that routes user intents directly.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

from research_copilot.core.state_ledger import ResearchLedger
from research_copilot.utils.common import find_project_root
from research_copilot.engine import ResearchEngine

logger = logging.getLogger("research.chat")

def call_llm(prompt: str) -> str:
    """Fallback LLM call via Ollama."""
    try:
        res = subprocess.run(["ollama", "run", "llama3", prompt], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception as e:
        return f"Error calling LLM: {e}"

def start_chat_loop():
    root = find_project_root()
    if not root:
        print("ERROR: Not in a Research Copilot workspace.")
        sys.exit(1)

    ledger = ResearchLedger(root / "03_synthesis" / "state_ledger.json")
    engine = ResearchEngine(root, hitl_enabled=True)
    
    from research_copilot.control_plane.supervisor import SupervisorAgent
    from research_copilot.control_plane.scheduler import TaskScheduler
    supervisor = SupervisorAgent(root, ledger, call_llm_fn=call_llm)
    scheduler = TaskScheduler(ledger)
    
    print("=" * 60)
    print("Research Copilot - Conversational Control Plane")
    print("=" * 60)
    print("Type your request (or 'exit' / 'quit' to stop).")
    
    while True:
        try:
            user_msg = input("\n> ")
        except (KeyboardInterrupt, EOFError):
            print()
            break
            
        user_msg = user_msg.strip()
        if not user_msg:
            continue
        if user_msg.lower() in ("exit", "quit"):
            break

        print("Supervisor is analyzing request...")
        decision = supervisor.process_request(user_msg)
        
        print(f"\n[{decision.task_type.upper()} | {decision.intent.upper()}] {decision.next_action}")
        
        if decision.needs_clarification:
            continue
            
        if decision.selected_workflow or decision.task_type in ("new_task", "continuation"):
            # Get the current plan from state
            current_plan = ledger.get().get("current_plan", {})
            next_step = scheduler.get_next_executable_node(current_plan)
            
            if next_step:
                print(f"Scheduler selected next node: {next_step}")
                res = engine.execute_node(next_step)
                print("Result:")
                print(f" - {res.get('node', 'unknown')}: {res.get('status', 'unknown')}")
            else:
                print("No executable nodes remaining in the plan.")

if __name__ == "__main__":
    start_chat_loop()
