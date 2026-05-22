from pydantic import BaseModel, Field
from typing import List, Dict, Any

class WorkflowSuccessRate(BaseModel):
    workflow_name: str
    success_count: int = 0
    failure_count: int = 0
    common_errors: List[str] = Field(default_factory=list)

class ProceduralMemory:
    """Stores execution history and tool performance patterns."""
    def __init__(self):
        self.success_rates: Dict[str, WorkflowSuccessRate] = {}
        
    def record_execution(self, workflow: str, success: bool, error: str = None):
        if workflow not in self.success_rates:
            self.success_rates[workflow] = WorkflowSuccessRate(workflow_name=workflow)
        
        record = self.success_rates[workflow]
        if success:
            record.success_count += 1
        else:
            record.failure_count += 1
            if error:
                record.common_errors.append(error)
