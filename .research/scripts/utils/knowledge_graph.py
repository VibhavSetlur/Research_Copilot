#!/usr/bin/env python3
"""Local Knowledge Graph — lightweight NetworkX-based graph for research context.

Replaces dense text CTMs with graph-based retrieval. When the literature agent
reads a paper, it extracts triplets and writes them to the graph. Agents query
the graph instead of reading 10,000-token literature summaries.

Storage: .research/cache/knowledge_graph.pkl (NetworkX pickle)
         .research/cache/knowledge_graph.json (JSON export for inspection)

Usage:
    from knowledge_graph import ResearchKnowledgeGraph
    kg = ResearchKnowledgeGraph()
    kg.add_triplet("Variable X", "confounded_by", "Variable Y", source="Smith et al., 2023")
    results = kg.query("confounded_by", subject="Variable X")
"""

import json
import logging
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

logger = logging.getLogger("research.knowledge_graph")


class ResearchKnowledgeGraph:
    """Lightweight knowledge graph for research context management."""

    def __init__(self, graph_path: Optional[Path] = None):
        if not HAS_NETWORKX:
            raise ImportError(
                "networkx is required for the knowledge graph. "
                "Install with: pip install networkx"
            )

        if graph_path is None:
            project_root = self._find_project_root()
            cache_dir = project_root / ".research" / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.pkl_path = cache_dir / "knowledge_graph.pkl"
            self.json_path = cache_dir / "knowledge_graph.json"
        else:
            self.pkl_path = Path(graph_path)
            self.json_path = self.pkl_path.with_suffix(".json")

        self.graph = self._load_or_init()

    @staticmethod
    def _find_project_root() -> Path:
        p = Path.cwd()
        for _ in range(10):
            if (p / ".research").exists():
                return p
            if p.parent == p:
                break
            p = p.parent
        return Path.cwd()

    def _load_or_init(self) -> nx.DiGraph:
        """Load existing graph or create a new one."""
        if self.pkl_path.exists():
            try:
                with open(self.pkl_path, "rb") as f:
                    g = pickle.load(f)
                logger.info("Loaded knowledge graph: %d nodes, %d edges", g.number_of_nodes(), g.number_of_edges())
                return g
            except Exception as e:
                logger.warning("Failed to load knowledge graph, creating new: %s", e)

        g = nx.DiGraph()
        g.graph["created_at"] = datetime.now(timezone.utc).isoformat()
        g.graph["schema_version"] = "1.0.0"
        g.graph["triplet_count"] = 0
        return g

    def save(self) -> None:
        """Persist graph to disk (both pickle and JSON)."""
        self.pkl_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.pkl_path, "wb") as f:
            pickle.dump(self.graph, f)

        self._export_json()
        logger.debug("Saved knowledge graph: %d nodes, %d edges",
                     self.graph.number_of_nodes(), self.graph.number_of_edges())

    def _export_json(self) -> None:
        """Export graph as JSON for human inspection."""
        data = {
            "schema_version": self.graph.graph.get("schema_version", "1.0.0"),
            "created_at": self.graph.graph.get("created_at", ""),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "nodes": [],
            "edges": [],
            "statistics": {
                "total_nodes": self.graph.number_of_nodes(),
                "total_edges": self.graph.number_of_edges(),
                "relation_types": list(set(
                    self.graph.edges[e].get("relation", "")
                    for e in self.graph.edges
                )),
            },
        }

        for node, attrs in self.graph.nodes(data=True):
            data["nodes"].append({
                "id": str(node),
                "type": attrs.get("node_type", "entity"),
                "source": attrs.get("source", ""),
                "metadata": {k: v for k, v in attrs.items() if k not in ("node_type", "source")},
            })

        for u, v, attrs in self.graph.edges(data=True):
            data["edges"].append({
                "source": str(u),
                "target": str(v),
                "relation": attrs.get("relation", ""),
                "source_paper": attrs.get("source", ""),
                "confidence": attrs.get("confidence", "unknown"),
                "metadata": {k: v for k, v in attrs.items() if k not in ("relation", "source", "confidence")},
            })

        with open(self.json_path, "w") as f:
            json.dump(data, f, indent=2)

    def add_triplet(
        self,
        subject: str,
        relation: str,
        obj: str,
        source: str = "",
        confidence: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a knowledge triplet to the graph.

        Args:
            subject: Subject entity (e.g., "Variable X")
            relation: Relationship type (e.g., "confounded_by", "mediates", "causes")
            obj: Object entity (e.g., "Variable Y")
            source: Source paper or reference
            confidence: Confidence level (high, medium, low, unknown)
            metadata: Additional metadata
        """
        self.graph.add_node(subject, node_type="entity", source=source)
        self.graph.add_node(obj, node_type="entity", source=source)

        edge_attrs = {
            "relation": relation,
            "source": source,
            "confidence": confidence,
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        if metadata:
            edge_attrs.update(metadata)

        self.graph.add_edge(subject, obj, **edge_attrs)
        self.graph.graph["triplet_count"] = self.graph.graph.get("triplet_count", 0) + 1

    def add_paper_nodes(
        self,
        paper_id: str,
        title: str,
        authors: str,
        year: int,
        doi: str = "",
        claims: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Add a paper as a node with its extracted claims.

        Args:
            paper_id: Unique paper identifier
            title: Paper title
            authors: Author string
            year: Publication year
            doi: DOI if available
            claims: List of extracted claims as triplets
        """
        paper_node = f"paper:{paper_id}"
        self.graph.add_node(
            paper_node,
            node_type="paper",
            title=title,
            authors=authors,
            year=year,
            doi=doi,
            added_at=datetime.now(timezone.utc).isoformat(),
        )

        if claims:
            for claim in claims:
                subject = claim.get("subject", "")
                relation = claim.get("relation", "")
                obj = claim.get("object", "")
                confidence = claim.get("confidence", "unknown")

                if subject and relation and obj:
                    self.add_triplet(subject, relation, obj, source=paper_node, confidence=confidence)
                    self.graph.add_edge(paper_node, subject, relation="claims_about")

    def query(
        self,
        relation: Optional[str] = None,
        subject: Optional[str] = None,
        obj: Optional[str] = None,
        confidence_min: str = "unknown",
    ) -> List[Dict[str, str]]:
        """Query the knowledge graph for matching triplets.

        Args:
            relation: Filter by relation type (e.g., "confounded_by")
            subject: Filter by subject entity
            obj: Filter by object entity
            confidence_min: Minimum confidence level

        Returns:
            List of matching triplet dicts
        """
        confidence_order = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
        min_conf = confidence_order.get(confidence_min, 0)

        results = []
        for u, v, attrs in self.graph.edges(data=True):
            edge_conf = confidence_order.get(attrs.get("confidence", "unknown"), 0)
            if edge_conf < min_conf:
                continue

            if relation and attrs.get("relation") != relation:
                continue
            if subject and str(u) != subject:
                continue
            if obj and str(v) != obj:
                continue

            results.append({
                "subject": str(u),
                "relation": attrs.get("relation", ""),
                "object": str(v),
                "source": attrs.get("source", ""),
                "confidence": attrs.get("confidence", "unknown"),
            })

        return results

    def get_confounders(self, variable: str) -> List[Dict[str, str]]:
        """Get known confounders for a specific variable.

        Args:
            variable: Variable name to find confounders for

        Returns:
            List of confounder triplets
        """
        confounders = self.query(relation="confounded_by", subject=variable)
        confounders += self.query(relation="confounds", obj=variable)
        return confounders

    def get_mediators(self, variable: str) -> List[Dict[str, str]]:
        """Get known mediators for a specific variable."""
        return self.query(relation="mediates", subject=variable)

    def get_causal_paths(self, start: str, end: str, max_depth: int = 3) -> List[List[str]]:
        """Find causal paths between two variables.

        Args:
            start: Starting variable
            end: Ending variable
            max_depth: Maximum path length

        Returns:
            List of paths (each path is a list of node names)
        """
        if not self.graph.has_node(start) or not self.graph.has_node(end):
            return []

        paths = []
        for path in nx.all_simple_paths(self.graph, start, end, cutoff=max_depth):
            paths.append(path)

        return paths

    def get_neighbors(self, node: str, relation: Optional[str] = None) -> List[Dict[str, str]]:
        """Get all neighbors of a node, optionally filtered by relation.

        Args:
            node: Node to find neighbors for
            relation: Optional relation filter

        Returns:
            List of neighbor dicts with relation info
        """
        neighbors = []
        for _, neighbor, attrs in self.graph.out_edges(node, data=True):
            if relation and attrs.get("relation") != relation:
                continue
            neighbors.append({
                "node": str(neighbor),
                "relation": attrs.get("relation", ""),
                "source": attrs.get("source", ""),
                "confidence": attrs.get("confidence", "unknown"),
            })
        return neighbors

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        relation_counts = {}
        for _, _, attrs in self.graph.edges(data=True):
            rel = attrs.get("relation", "unknown")
            relation_counts[rel] = relation_counts.get(rel, 0) + 1

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "relation_types": relation_counts,
            "paper_nodes": sum(
                1 for _, attrs in self.graph.nodes(data=True)
                if attrs.get("node_type") == "paper"
            ),
            "entity_nodes": sum(
                1 for _, attrs in self.graph.nodes(data=True)
                if attrs.get("node_type") == "entity"
            ),
        }

    def summary(self) -> str:
        """Generate a human-readable summary of the knowledge graph."""
        stats = self.get_statistics()
        lines = [
            "=" * 60,
            "RESEARCH KNOWLEDGE GRAPH",
            "=" * 60,
            "",
            f"  Nodes: {stats['total_nodes']}",
            f"    - Papers: {stats['paper_nodes']}",
            f"    - Entities: {stats['entity_nodes']}",
            f"  Edges: {stats['total_edges']}",
            "",
            "  Relation Types:",
        ]

        for rel, count in sorted(stats["relation_types"].items(), key=lambda x: -x[1]):
            lines.append(f"    - {rel}: {count}")

        lines.append("")
        lines.append(f"  Storage: {self.pkl_path}")
        lines.append(f"  JSON Export: {self.json_path}")
        lines.append("")
        return "\n".join(lines)

    def merge_graph(self, other_graph_path: Path) -> None:
        """Merge another knowledge graph into this one.

        Args:
            other_graph_path: Path to the other graph pickle file
        """
        with open(other_graph_path, "rb") as f:
            other = pickle.load(f)

        self.graph = nx.compose(self.graph, other)
        self.graph.graph["triplet_count"] = self.graph.number_of_edges()
        self.graph.graph["last_merged"] = datetime.now(timezone.utc).isoformat()
        self.save()

        logger.info("Merged knowledge graph from %s", other_graph_path)

    def clear(self) -> None:
        """Clear all nodes and edges from the graph."""
        self.graph = nx.DiGraph()
        self.graph.graph["created_at"] = datetime.now(timezone.utc).isoformat()
        self.graph.graph["schema_version"] = "1.0.0"
        self.graph.graph["triplet_count"] = 0
        self.save()
        logger.info("Cleared knowledge graph")
