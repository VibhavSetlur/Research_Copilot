import json
from typing import List, Dict, Optional
from datetime import datetime, timezone

from research_copilot.core.state_ledger import ResearchLedger
from research_copilot.assets.schemas.state_schema import DAGNode, ExecutionDAG

class PlanMutationEngine:
    """Safely manages runtime mutations to the execution DAG."""

    def __init__(self, ledger: ResearchLedger):
        self.ledger = ledger

    def _load_dag(self) -> dict:
        return self.ledger.get_dag()

    def _save_dag(self, dag_data: dict):
        # Validate schema before saving
        ExecutionDAG(**dag_data)
        dag_path = self.ledger.get_dag_path()
        with open(dag_path, "w") as f:
            json.dump(dag_data, f, indent=2)

    def insert_node(self, node_id: str, script_path: str, depends_on: List[str] = None) -> None:
        """Insert a new node into the DAG."""
        dag = self._load_dag()
        
        if node_id in dag["nodes"]:
            raise ValueError(f"Node {node_id} already exists in the DAG.")
            
        depends_on = depends_on or []
        for dep in depends_on:
            if dep not in dag["nodes"]:
                raise ValueError(f"Dependency {dep} does not exist.")
                
        new_node = DAGNode(
            node_id=node_id,
            script_path=script_path,
            depends_on=depends_on,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="pending"
        ).model_dump()
        
        dag["nodes"][node_id] = new_node
        
        for dep in depends_on:
            dag["edges"].append({"from": dep, "to": node_id})
            
        dag["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._save_dag(dag)

    def remove_node(self, node_id: str, rewire_children: bool = True) -> None:
        """Remove a node from the DAG and optionally rewire its children to its parents."""
        dag = self._load_dag()
        
        if node_id not in dag["nodes"]:
            raise ValueError(f"Node {node_id} does not exist.")
            
        parents = [e["from"] for e in dag["edges"] if e["to"] == node_id]
        children = [e["to"] for e in dag["edges"] if e["from"] == node_id]
        
        if rewire_children:
            for child in children:
                # Remove parent dependency from child node
                if node_id in dag["nodes"][child]["depends_on"]:
                    dag["nodes"][child]["depends_on"].remove(node_id)
                # Add original parents to child node
                for parent in parents:
                    if parent not in dag["nodes"][child]["depends_on"]:
                        dag["nodes"][child]["depends_on"].append(parent)
                        dag["edges"].append({"from": parent, "to": child})
                        
        # Remove edges
        dag["edges"] = [e for e in dag["edges"] if e["from"] != node_id and e["to"] != node_id]
        
        # Remove node
        del dag["nodes"][node_id]
        
        if not rewire_children:
            # If we don't rewire, children might have dangling dependencies
            for child in children:
                if node_id in dag["nodes"][child]["depends_on"]:
                    dag["nodes"][child]["depends_on"].remove(node_id)
                    
        dag["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._save_dag(dag)

    def rewire_dependency(self, node_id: str, new_parents: List[str]) -> None:
        """Rewire a node to depend on new parents, removing old parents."""
        dag = self._load_dag()
        
        if node_id not in dag["nodes"]:
            raise ValueError(f"Node {node_id} does not exist.")
            
        for parent in new_parents:
            if parent not in dag["nodes"]:
                raise ValueError(f"New parent {parent} does not exist.")
                
        # Remove old edges
        dag["edges"] = [e for e in dag["edges"] if e["to"] != node_id]
        
        # Add new edges
        for parent in new_parents:
            dag["edges"].append({"from": parent, "to": node_id})
            
        # Update node dependencies
        dag["nodes"][node_id]["depends_on"] = new_parents
        
        dag["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._save_dag(dag)
