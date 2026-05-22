import json
from pathlib import Path
from typing import Dict, Any, List

class ResearchKnowledgeGraph:
    """Represents the evolving research process as a cognitive graph."""
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.nodes = {}
        self.edges = []
        self._load()

    def _load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.nodes = data.get("nodes", {})
                    self.edges = data.get("edges", [])
            except Exception:
                pass

    def _save(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump({"nodes": self.nodes, "edges": self.edges}, f, indent=2)

    def add_node(self, entity_id: str, entity_type: str, data: Dict[str, Any]):
        self.nodes[entity_id] = {"type": entity_type, "data": data}
        self._save()

    def add_edge(self, source_id: str, target_id: str, relationship: str):
        """Relationships: supports, contradicts, derived_from, validates, invalidates, supersedes, depends_on"""
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "relationship": relationship
        })
        self._save()

    def get_related(self, entity_id: str, relationship: str) -> List[str]:
        return [e["target"] for e in self.edges if e["source"] == entity_id and e["relationship"] == relationship]
