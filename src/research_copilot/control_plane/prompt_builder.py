import json
from typing import Dict, Any
from research_copilot.core.state_ledger import ResearchLedger
from research_copilot.core.cognitive_tracker import CognitiveStateTracker

class PromptBuilder:
    """Assembles state-aware system prompts for every turn to ensure continuity."""
    
    def __init__(self, ledger: ResearchLedger, cognitive_tracker: CognitiveStateTracker = None):
        self.ledger = ledger
        self.cognitive_tracker = cognitive_tracker or CognitiveStateTracker(ledger)

    def build_supervisor_prompt(self, user_msg: str, mode: str = "exploratory") -> str:
        """Build the structured system prompt for the SupervisorAgent."""
        state = self.ledger.get()
        
        # 1. Identity / Role
        identity = "You are the SupervisorAgent for Research Copilot, a top-level orchestrator. You manage the conversation, handle interruptions, and delegate research tasks to the execution engine."
        
        # 2. Project Brief
        project_brief = state.get("project", "Research Project Workspace")
        
        # 3. Current Phase & Branch
        phase = state.get("phase", "init")
        active_branch = state.get("current_branch", state.get("active_branch", "main"))

        # 4. Cognitive / Semantic State
        cognitive_summary = self.cognitive_tracker.get_context_summary()

        # Memory Context
        memory_state = state.get("memory", {})
        semantic_memory = memory_state.get("semantic", {})
        episodic_memory = memory_state.get("episodic", [])
        
        memory_context = ""
        if semantic_memory:
            memory_context += f"Project Semantic Summary: {semantic_memory.get('project_summary', '')}\n"
            memory_context += f"Confidence Evolution: {semantic_memory.get('confidence_evolution', '')}\n"
        if episodic_memory:
            recent_episodes = episodic_memory[-3:]
            memory_context += "Recent Episodic Memories:\n"
            for ep in recent_episodes:
                memory_context += f"- [{ep.get('timestamp')}] {ep.get('summary')}\n"

        # 5. Recent Completed Nodes & Goals
        recent_nodes = [n for n in state.get("execution_dag", {}).get("nodes", {}).values() if n.get("status") == "complete"]
        recent_nodes = sorted(recent_nodes, key=lambda x: x.get("timestamp", ""))[-3:]

        prompt = [
            identity,
            f"Project: {project_brief}",
            f"Phase: {phase}",
            f"Active Branch: {active_branch}",
            "\n--- CONVERSATIONAL MEMORY ---",
            memory_context if memory_context else "(No memory established yet)",
            "\n--- COGNITIVE STATE ---",
            cognitive_summary,
        ]
        
        # 5. Open Questions & Dead Ends
        open_questions = state.get("unanswered_questions", [])
        dead_ends = state.get("dead_ends", [])
        
        # 6. Conversation & Interrupt Context
        active_task = self.ledger.get_active_task_summary()
        conversation_summary = self.ledger.get_conversation_summary()
        interrupt_stack = state.get("interrupt_stack", [])
        
        # Assemble sections
        prompt.extend([
            "\n--- SYSTEM STATE ---",
            f"Active Task:\n{active_task}",
            f"Last Completed Nodes: {recent_nodes}",
        ])
        
        if open_questions:
            prompt.append(f"Open Questions: {json.dumps(open_questions)}")
        if dead_ends:
            prompt.append(f"Dead Ends (Avoid these): {json.dumps(dead_ends[-3:])}")
        if interrupt_stack:
            prompt.append(f"Paused Tasks (Interrupt Stack depth): {len(interrupt_stack)}")
            
        prompt.extend([
            "\n--- RECENT CONVERSATION ---",
            conversation_summary if conversation_summary else "(No recent turns)",
            "\n--- USER MESSAGE ---",
            f"User says: {user_msg}",
            "\n--- CONVERSATIONAL RESPONSE STRATEGY ---",
            f"Current Mode: {mode.upper()}",
        ])
        
        if mode == "exploratory":
            prompt.append("Focus on brainstorming, generating ideas, and suggesting new directions. Be open to all possibilities.")
        elif mode == "skeptical":
            prompt.append("Act as a skeptic. Challenge assumptions, demand evidence, and point out logical flaws.")
        elif mode == "publication-grade":
            prompt.append("Ensure high rigor, formal tone, precise citations, and methodological soundness.")
        
        prompt.extend([
            "Act as a senior research collaborator, not just a procedural tool.",
            "Choose a conversational mode based on the user's intent: exploratory, publication-grade, skeptical, brainstorming, audit mode, or replication mode.",
            "Response patterns:",
            "  - Explain rationale briefly.",
            "  - Communicate uncertainty when findings are preliminary.",
            "  - Proactively identify risks (methodological, statistical).",
            "  - Suggest next research directions.",
            "  - Ask clarifying questions ONLY when strictly necessary to proceed.",
            "\n--- INSTRUCTIONS ---",
            "You are the autonomous Operator. Decide exactly how to handle the user's intent.",
            "Determine the task_type from these options:",
            "  - new_task: starting a fresh workflow",
            "  - continuation: normal progression of the active plan",
            "  - interruption: side question that doesn't mutate the DAG",
            "  - modify: user wants to change a hypothesis or assumption mid-analysis without branching",
            "  - branch: user wants to explore a new direction while preserving the current one",
            "  - replan: user uploaded contradictory evidence or changed research direction entirely",
            "  - repair: execution failed or user corrected a mistake requiring rollback",
            "  - answer: answer a spontaneous question directly",
            "  - pause: wait for user action or data",
            "  - request_approval: explicit safety gate needed",
            "",
            "If branching or repairing, populate the 'execution_intent' field with details (e.g. branch_name_override, rollback_target).",
            "Return EXACTLY a JSON object matching this schema:",
            "{",
            '  "intent": "string",',
            '  "task_type": "new_task | continuation | interruption | modify | branch | answer | pause | replan | repair | request_approval",',
            '  "urgency": "low | medium | high",',
            '  "needs_clarification": true/false,',
            '  "needs_approval": true/false,',
            '  "next_action": "string describing what you will do next or your direct answer",',
            '  "state_patch": {}, // any key-value pairs to update in the state ledger',
            '  "execution_intent": { // Optional',
            '    "target_nodes": [],',
            '    "branch_name_override": "string | null",',
            '    "rollback_target": "string | null",',
            '    "suspend_execution": true/false',
            '  }',
            "}"
        ])
        
        return "\n".join(prompt)
