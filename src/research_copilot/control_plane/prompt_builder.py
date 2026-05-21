import json
from typing import Dict, Any
from research_copilot.core.state_ledger import ResearchLedger

class PromptBuilder:
    """Assembles state-aware system prompts for every turn to ensure continuity."""
    
    def __init__(self, ledger: ResearchLedger):
        self.ledger = ledger

    def build_supervisor_prompt(self, user_msg: str) -> str:
        """Build the structured system prompt for the SupervisorAgent."""
        state = self.ledger.get()
        
        # 1. Identity / Role
        identity = "You are the SupervisorAgent for Research Copilot, a top-level orchestrator. You manage the conversation, handle interruptions, and delegate research tasks to the execution engine."
        
        # 2. Project Brief
        project_brief = state.get("project", "Research Project Workspace")
        
        # 3. Current Phase & Branch
        phase = state.get("phase", "init")
        active_branch = state.get("current_branch", state.get("active_branch", "main"))
        
        # 4. Recent Completed Nodes & Goals
        dag = self.ledger.get_dag()
        recent_nodes = dag.get("nodes", {})
        completed_nodes = [n_id for n_id, info in recent_nodes.items() if info.get("status") == "success"]
        last_few_nodes = completed_nodes[-3:] if completed_nodes else []
        
        # 5. Open Questions & Dead Ends
        open_questions = state.get("unanswered_questions", [])
        dead_ends = state.get("dead_ends", [])
        
        # 6. Conversation & Interrupt Context
        active_task = self.ledger.get_active_task_summary()
        conversation_summary = self.ledger.get_conversation_summary()
        interrupt_stack = state.get("interrupt_stack", [])
        
        # Assemble sections
        prompt = [
            f"{identity}",
            "\n--- SYSTEM STATE ---",
            f"Project: {project_brief}",
            f"Phase: {phase} | Branch: {active_branch}",
            f"Active Task:\n{active_task}",
            f"Last Completed Nodes: {last_few_nodes}",
        ]
        
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
            "\n--- INSTRUCTIONS ---",
            "Decide if this is a new task, a continuation of an existing task, or an interruption (a side question).",
            "Determine if you need to ask for clarification or approval.",
            "If it's a side question that can be answered immediately, set task_type to 'interruption', answer it in 'next_action', and set 'state_patch' to push the current task to the interrupt stack if needed.",
            "Return EXACTLY a JSON object matching this schema:",
            "{",
            '  "intent": "string",',
            '  "task_type": "new_task | continuation | interruption",',
            '  "urgency": "low | medium | high",',
            '  "needs_clarification": true/false,',
            '  "needs_approval": true/false,',
            '  "next_action": "string describing what you will do next or your direct answer",',
            '  "state_patch": {} // any key-value pairs to update in the state ledger',
            "}"
        ])
        
        return "\n".join(prompt)
