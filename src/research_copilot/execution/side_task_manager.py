import uuid
from typing import Dict, Any
from research_copilot.execution.interrupt_engine import InterruptEngine

class SideTask:
    def __init__(self, description: str, context: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.description = description
        self.context = context
        self.status = "running"
        self.findings = {}

class SideTaskManager:
    """Spawns temporary tasks to answer side questions without destroying main context."""
    def __init__(self, interrupt_engine: InterruptEngine):
        self.interrupt_engine = interrupt_engine
        self.active_tasks: Dict[str, SideTask] = {}

    def spawn(self, description: str, context: Dict[str, Any]) -> str:
        # Suspend main thread
        self.interrupt_engine.trigger_interrupt("exploratory", context={"side_task": description})
        
        # Isolate context window from main thread
        isolated_context = dict(context)
        isolated_context["active_thread_turns"] = []
        
        task = SideTask(description, isolated_context)
        self.active_tasks[task.id] = task
        return task.id

    def complete(self, task_id: str, findings: Dict[str, Any]):
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = "completed"
            task.findings = findings
            
            # Merge findings
            # In a real system, this would write to the Semantic Memory
            
            # Resume main thread
            self.interrupt_engine.recover()

    def handle_stuck_loop(self, exception: Exception, context: Dict[str, Any]) -> str:
        """Called when StuckLoopException is caught. Spawns CriticAgent to break the loop."""
        description = f"Stuck in execution loop. Need CriticAgent to suggest alternatives. Error: {str(exception)}"
        return self.spawn(description, context)
