import logging
from pathlib import Path
from typing import Any, Dict, Optional

from research_copilot.core.hooks import hook_engine
from research_copilot.core.state_ledger import ResearchLedger
from research_copilot.intent_router import IntentRouter
from research_copilot.project_ops import create_experiment_branch, log_decision, save_artifact
from research_copilot.utils.asset_manager import AssetManager
from research_copilot.utils.dag_manager import ExecutionDAGManager

logger = logging.getLogger("research.engine")

class ResearchEngine:
    """Unified headless execution engine for Research Copilot.
    
    This class serves as the central orchestration point for both the CLI
    and the MCP server. It manages state, routing, hooks, and execution.
    """

    def __init__(self, project_root: Optional[Path] = None, depth: str = "academic"):
        self.root = project_root or AssetManager.find_project_root()
        if not self.root:
            raise ValueError("Not in a Research Copilot workspace.")
            
        self.assets = AssetManager(self.root)
        self.ledger = ResearchLedger(self.root / "03_synthesis" / "state_ledger.json")
        self.hooks = hook_engine
        self.router = IntentRouter(self.root)
        self.dag = ExecutionDAGManager(self.root)
        self.depth = depth

    def execute_node(self, node_id: str, **kwargs) -> Dict[str, Any]:
        """Execute a single execution node directly."""
        logger.info(f"Executing node {node_id}")
        self.hooks.trigger_sync("pre_execution", {"node_id": node_id, "kwargs": kwargs})
        
        # In a full implementation, this would dynamically load and run the skill/agent.
        # For now we simulate execution.
        result = {"status": "success", "node": node_id, "output": "Execution completed"}
        
        self.hooks.trigger_sync("post_execution", {"node_id": node_id, "result": result})
        return result

    def route_and_execute(self, query: str, depth: Optional[str] = None) -> Dict[str, Any]:
        """Route a natural language query and execute the corresponding workflow."""
        target_depth = depth or self.depth
        self.hooks.trigger_sync("pre_routing", {"query": query, "depth": target_depth})
        
        workflow = self.router.route_intent(query, target_depth)
        
        # Execute workflow steps...
        results = []
        for step in workflow.get("steps", []):
            res = self.execute_node(step)
            results.append(res)
            
        return {"workflow": workflow, "results": results}

    def create_branch(self, name: str, hypothesis: str) -> Dict[str, Any]:
        """Create a new experimental branch."""
        branch_dir = create_experiment_branch(self.root, name, hypothesis)
        self.ledger.branch_state(name)
        return {"status": "success", "branch": name, "directory": str(branch_dir)}

    def log_decision(self, context: str, selected_option: str, rationale: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """Log a methodological decision."""
        log_decision(self.root, context, selected_option, rationale, branch)
        return {"status": "success", "message": "Decision logged successfully."}

    def save_artifact(self, filepath: str, content: str, artifact_type: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """Save a generated artifact."""
        path = save_artifact(self.root, filepath, content, artifact_type, branch)
        return {"status": "success", "path": str(path)}
