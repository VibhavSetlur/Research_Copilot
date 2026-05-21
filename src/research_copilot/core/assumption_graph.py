from pathlib import Path
from typing import Any, Dict, List, Optional

import networkx as nx

from research_copilot.utils.common import find_project_root, load_json, save_json_atomic


class AssumptionDAG:
    """Hierarchical Assumption Invalidation Graph.
    
    Tracks assumptions made during analysis. If an assumption is violated,
    backward traversal marks all dependent nodes as 'Tainted'.
    """

    def __init__(self, root: Optional[Path] = None):
        self.root = root or find_project_root()
        if not self.root:
            raise ValueError("Not in a Research Copilot workspace.")
            
        self.db_path = self.root / "03_synthesis" / "assumption_graph.json"
        self.graph = nx.DiGraph()
        self._load()

    def _load(self) -> None:
        data = load_json(self.db_path, default={"nodes": [], "edges": []})
        for node in data.get("nodes", []):
            self.graph.add_node(node["id"], **node)
        for edge in data.get("edges", []):
            self.graph.add_edge(edge["source"], edge["target"])

    def _save(self) -> None:
        nodes = [{"id": n, **d} for n, d in self.graph.nodes(data=True)]
        edges = [{"source": u, "target": v} for u, v in self.graph.edges()]
        save_json_atomic(self.db_path, {"nodes": nodes, "edges": edges})

    def add_assumption(self, assumption_id: str, description: str, depends_on: Optional[List[str]] = None) -> None:
        """Add a new assumption and its dependencies."""
        self.graph.add_node(assumption_id, description=description, status="valid")
        if depends_on:
            for dep in depends_on:
                self.graph.add_edge(dep, assumption_id)
        self._save()

    def mark_violated(self, assumption_id: str, reason: str) -> List[str]:
        """Mark an assumption as violated and taint all dependencies.
        
        Returns:
            List of node IDs that were tainted as a result.
        """
        if assumption_id not in self.graph:
            return []
            
        self.graph.nodes[assumption_id]["status"] = "violated"
        self.graph.nodes[assumption_id]["reason"] = reason
        
        # Taint all downstream nodes (descendants)
        tainted = []
        for desc in nx.descendants(self.graph, assumption_id):
            self.graph.nodes[desc]["status"] = "tainted"
            self.graph.nodes[desc]["tainted_by"] = assumption_id
            tainted.append(desc)
            
        self._save()
        return tainted

    def get_tainted(self) -> List[Dict[str, Any]]:
        """Get all tainted or violated assumptions."""
        return [
            {"id": n, **d} 
            for n, d in self.graph.nodes(data=True) 
            if d.get("status") in ("violated", "tainted")
        ]
