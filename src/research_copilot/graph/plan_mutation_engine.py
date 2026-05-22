from typing import List, Dict, Any
from research_copilot.planning.dynamic_planner import ExecutionNode, PlanMutation

class PlanMutationEngine:
    """Applies runtime operations to the Execution Graph."""
    
    def __init__(self, ledger):
        self.ledger = ledger

    def apply_mutations(self, mutations: List[PlanMutation]):
        state = self.ledger.get()
        dag = state.get("execution_dag", {"nodes": {}})
        
        for mut in mutations:
            if mut.action == "insert" and mut.new_node:
                dag["nodes"][mut.target_node] = mut.new_node.model_dump()
            elif mut.action == "remove":
                if mut.target_node in dag["nodes"]:
                    del dag["nodes"][mut.target_node]
            elif mut.action == "rewire" and mut.new_dependencies is not None:
                if mut.target_node in dag["nodes"]:
                    dag["nodes"][mut.target_node]["dependencies"] = mut.new_dependencies
            elif mut.action == "pause":
                if mut.target_node in dag["nodes"]:
                    dag["nodes"][mut.target_node]["status"] = "paused"
            elif mut.action == "retry":
                if mut.target_node in dag["nodes"]:
                    dag["nodes"][mut.target_node]["status"] = "pending"
                    
        self.ledger.update(execution_dag=dag)

    def build_dag_from_intake(self, intake: Dict[str, Any]):
        """Constructs a ConversationDAG dynamically without disk files from an intake schema."""
        state = self.ledger.get()
        dag = state.get("execution_dag", {"nodes": {}})
        
        # Simple heuristic mapping to DAG nodes based on primary_intent
        primary = intake.get("primary_intent", "exploratory")
        
        nodes = {}
        if primary == "exploratory":
            nodes["intake"] = {"id": "intake", "status": "pending", "dependencies": []}
            nodes["scan"] = {"id": "scan", "status": "pending", "dependencies": ["intake"]}
            nodes["data_profile"] = {"id": "data_profile", "status": "pending", "dependencies": ["scan"]}
            nodes["report"] = {"id": "report", "status": "pending", "dependencies": ["data_profile"]}
        else:
            nodes["intake"] = {"id": "intake", "status": "pending", "dependencies": []}
            nodes["analysis"] = {"id": "analysis", "status": "pending", "dependencies": ["intake"]}
            nodes["validate"] = {"id": "validate", "status": "pending", "dependencies": ["analysis"]}
            
        dag["nodes"] = nodes
        self.ledger.update(execution_dag=dag, phase="initialized")
