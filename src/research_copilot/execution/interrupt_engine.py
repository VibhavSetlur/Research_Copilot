import logging
from typing import Dict, Any, Optional
from research_copilot.state.state_ledger import ResearchLedger

logger = logging.getLogger(__name__)

class InterruptEngine:
    """Handles deep interruptions and state preservation during nested tasks."""
    def __init__(self, ledger: ResearchLedger, conversation_state=None):
        self.ledger = ledger
        self.conversation_state = conversation_state

    def trigger_interrupt(self, interrupt_type: str, context: Dict[str, Any]):
        """Types: informational, corrective, branching, speculative, destructive, exploratory"""
        state = self.ledger.get()
        active_node = state.get("active_node")
        
        # Save snapshot
        snapshot = {
            "active_node": active_node,
            "execution_context": state.get("execution_context", {}),
            "pending_validations": state.get("pending_validations", []),
            "active_hypothesis": state.get("active_hypothesis")
        }
        
        interrupt_stack = state.get("interrupt_stack", [])
        interrupt_stack.append({
            "type": interrupt_type,
            "context": context,
            "snapshot": snapshot
        })
        
        self.ledger.update(interrupt_stack=interrupt_stack, active_node=None)
        
        if self.conversation_state:
            self.conversation_state.push_interrupt(interrupt_type, snapshot)
            
        logger.info(f"Triggered {interrupt_type} interrupt. State saved.")

    def recover(self) -> Optional[Dict[str, Any]]:
        state = self.ledger.get()
        interrupt_stack = state.get("interrupt_stack", [])
        if not interrupt_stack:
            return None
            
        last_interrupt = interrupt_stack.pop()
        snapshot = last_interrupt["snapshot"]
        
        self.ledger.update(
            interrupt_stack=interrupt_stack,
            active_node=snapshot["active_node"],
            execution_context=snapshot["execution_context"],
            pending_validations=snapshot["pending_validations"],
            active_hypothesis=snapshot["active_hypothesis"]
        )
        
        if self.conversation_state:
            self.conversation_state.pop_interrupt()
            
        logger.info("Recovered from interrupt. Restored previous state.")
        return snapshot
