from typing import List, Dict
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
