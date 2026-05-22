from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class InterruptContext(BaseModel):
    task_id: str
    reason: str
    resumable_state: Dict[str, Any]
    timestamp: str

class ConversationStateData(BaseModel):
    """Holds the live state of the conversational continuity."""
    active_goals: List[str] = Field(default_factory=list)
    current_hypothesis: str = Field(default="None")
    unresolved_questions: List[str] = Field(default_factory=list)
    interrupt_stack: List[InterruptContext] = Field(default_factory=list)
    side_tasks: List[str] = Field(default_factory=list)
    user_corrections: List[str] = Field(default_factory=list)
    open_validations: List[str] = Field(default_factory=list)
    pending_approvals: List[str] = Field(default_factory=list)
    reasoning_trajectory: List[str] = Field(default_factory=list)
    branch_lineage: List[str] = Field(default_factory=list)
    active_thread_turns: List[Dict[str, str]] = Field(default_factory=list)

class ConversationState:
    """Manages the real-time state of the conversation."""
    def __init__(self, memory_backend):
        self.memory = memory_backend
        self.state_data = self.memory.load()

    def add_turn(self, role: str, content: str):
        self.state_data.active_thread_turns.append({"role": role, "content": content, "timestamp": datetime.now(timezone.utc).isoformat()})
        self.memory.save(self.state_data)

    def push_interrupt(self, reason: str, state_snapshot: Dict[str, Any]):
        ctx = InterruptContext(
            task_id=f"int_{len(self.state_data.interrupt_stack)}",
            reason=reason,
            resumable_state=state_snapshot,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        self.state_data.interrupt_stack.append(ctx)
        self.memory.save(self.state_data)

    def pop_interrupt(self) -> Optional[InterruptContext]:
        if not self.state_data.interrupt_stack:
            return None
        ctx = self.state_data.interrupt_stack.pop()
        self.memory.save(self.state_data)
        return ctx

    def add_goal(self, goal: str):
        self.state_data.active_goals.append(goal)
        self.memory.save(self.state_data)
        
    def add_correction(self, correction: str):
        self.state_data.user_corrections.append(correction)
        self.memory.save(self.state_data)
        
    def get_state(self) -> ConversationStateData:
        return self.state_data
