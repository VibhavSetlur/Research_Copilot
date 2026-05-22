#!/usr/bin/env python3
"""Persistent Conversational Control Plane for Research Copilot.

Provides a chat interface that routes user intents directly.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

from research_copilot.state.conversation_state import ConversationState
from research_copilot.state.conversation_memory import ConversationMemory
from research_copilot.state.state_ledger import ResearchLedger
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
    conv_memory = ConversationMemory(root)
    conv_state = ConversationState(conv_memory)
    
    from research_copilot.agents.supervisor_agent import SupervisorAgent
    supervisor = SupervisorAgent(root, ledger, call_llm_fn=call_llm)
    
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

        conv_state.add_turn("user", user_msg)
        print("Supervisor is analyzing request...")
        intent = supervisor.process_request(user_msg)
        
        print(f"\n[ACTION: {intent.task_action.upper()} | GOAL: {intent.user_goal.upper()}] {intent.next_action_description}")
        conv_state.add_turn("assistant", intent.next_action_description)
        
        if intent.requires_human_input:
            print("[System paused for human input]")
            continue
            
        # In future phases, pass this intent to the Planner Agent to mutate the DAG
        # and then execute it via Execution Engine.
        
        # Phase 12 Proactive Reasoning
        from research_copilot.agents.specialized_agents import ReflectionAgent
        from research_copilot.intent_router import IntentRouter
        
        router = IntentRouter(root)
        kg = conv_state.get_state().model_dump()
        minimal_context = router.get_minimal_context(user_msg, project_state=kg, knowledge_graph=kg)
        
        reflection_agent = ReflectionAgent(call_llm)
        reflection = reflection_agent.reflect(str(minimal_context["kg_fragment"]))
        if reflection.success and reflection.output.get("gaps"):
            print("\n[PROACTIVE REASONING]")
            for gap in reflection.output["gaps"]:
                print(f" - Missing gap identified: {gap}")

if __name__ == "__main__":
    start_chat_loop()
