import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional

import networkx as nx

from research_copilot.utils.common import find_project_root


class KnowledgeGraph:
    """Localized Knowledge Graph for Literature Triplets.
    
    Replaces dense text Context Transfer Memos (CTMs) with graph-based retrieval.
    Literature agent extracts triplets: [Variable X] -> [relation] -> [Variable Y].
    Analysis agents query this graph instead of reading 10,000-token summaries.
    """

    def __init__(self, root: Optional[Path] = None):
        self.root = root or find_project_root()
        if not self.root:
            raise ValueError("Not in a Research Copilot workspace.")
        
        self.db_path = self.root / "01_workspace" / "knowledge_graph.pkl"
        self.graph = nx.DiGraph()
        self._load()

    def _load(self) -> None:
        if self.db_path.exists():
            try:
                with open(self.db_path, "rb") as f:
                    self.graph = pickle.load(f)
            except Exception:
                self.graph = nx.DiGraph()

    def _save(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, "wb") as f:
            pickle.dump(self.graph, f)

    def add_triplet(self, subject: str, relation: str, obj: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a literature triplet to the knowledge graph."""
        self.graph.add_edge(subject, obj, relation=relation, **(metadata or {}))
        self._save()

    def query_confounders(self, variable: str) -> List[str]:
        """Find all variables that confound the given variable."""
        confounders = []
        if variable in self.graph:
            for pred in self.graph.predecessors(variable):
                edge_data = self.graph.get_edge_data(pred, variable)
                if edge_data and edge_data.get("relation") == "confounds":
                    confounders.append(pred)
        return confounders

    def query_by_relation(self, relation: str) -> List[Dict[str, str]]:
        """Find all edges with a specific relation."""
        results = []
        for u, v, data in self.graph.edges(data=True):
            if data.get("relation") == relation:
                results.append({"subject": u, "relation": relation, "object": v})
        return results

    def add_ctm(self, text: str) -> None:
        """Serialize a CTM into the local vector store."""
        ctm_path = self.root / ".research" / "cache" / "ctm_store.pkl"
        ctm_path.parent.mkdir(parents=True, exist_ok=True)
        ctms = []
        if ctm_path.exists():
            try:
                with open(ctm_path, "rb") as f:
                    ctms = pickle.load(f)
            except Exception:
                pass
        ctms.append(text)
        with open(ctm_path, "wb") as f:
            pickle.dump(ctms, f)

    def query_research_context(self, question: str) -> str:
        """Retrieve the most relevant ~200 tokens from the CTM store for a given question."""
        ctm_path = self.root / ".research" / "cache" / "ctm_store.pkl"
        if not ctm_path.exists():
            return "No research context available."
        try:
            with open(ctm_path, "rb") as f:
                ctms = pickle.load(f)
        except Exception:
            return "Error reading research context."

        # Simple keyword-based chunk retrieval (mocking FAISS/ChromaDB for template)
        keywords = set(question.lower().split())
        best_chunk = "No highly relevant context found."
        best_score = -1
        
        for ctm in ctms:
            # Simulate chunking
            chunks = [ctm[i:i+800] for i in range(0, len(ctm), 800)]
            for chunk in chunks:
                score = sum(1 for kw in keywords if kw in chunk.lower())
                if score > best_score and score > 0:
                    best_score = score
                    best_chunk = chunk
                    
        return best_chunk

    def summary(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "relations": len(set(data.get("relation") for _, _, data in self.graph.edges(data=True))),
        }
