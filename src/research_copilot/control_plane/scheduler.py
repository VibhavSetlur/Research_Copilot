from typing import Dict, Any, Optional, List
import logging
from research_copilot.core.state_ledger import ResearchLedger

logger = logging.getLogger("research.scheduler")

class TaskScheduler:
    """Decides what to run next from state, instead of from CLI flags."""
    
    def __init__(self, ledger: ResearchLedger):
        self.ledger = ledger

    def get_next_executable_node(self, plan: Dict[str, Any]) -> Optional[str]:
        """Determine the next step in the workflow based on the active plan and DAG."""
        if not plan:
            return None
            
        steps = plan.get("workflow_steps", [])
        if not steps:
            return None
            
        state = self.ledger.get()
        dag = self.ledger.get_dag()
        recent_nodes = dag.get("nodes", {})
        
        # In a real DAG, we'd check dependencies. For this simple workflow list,
        # we find the first step that hasn't successfully completed in the current branch.
        # Note: A real implementation would parse the DAG properly.
        
        # Check which steps are completed
        completed_steps = set()
        for node_id, node_info in recent_nodes.items():
            if node_info.get("status") == "success":
                # Assuming node_id is <script_name>_...
                # For simplicity, extract the step name
                step_name = node_id.split("_00")[0] if "_00" in node_id else node_id
                completed_steps.add(step_name)
                
        # Find first incomplete step
        for step in steps:
            # We loosely match step names to what might be in the DAG
            match_found = False
            for completed in completed_steps:
                if step in completed or completed in step:
                    match_found = True
                    break
            
            if not match_found:
                return step
                
        return None
