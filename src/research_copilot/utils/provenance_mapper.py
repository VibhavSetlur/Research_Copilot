"""Provenance Mapper utility to trace data lineage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from research_copilot.state.state_ledger import ResearchLedger


class ProvenanceMapper:
    """Reconstructs the dependency graph for a given output file."""

    def __init__(self, ledger: ResearchLedger):
        self.ledger = ledger
        self.dag = self.ledger.get_dag()

    def _normalize_path(self, path: str) -> str:
        """Normalize path to match DAG format (typically relative to workspace root)."""
        # Paths in the DAG are typically relative to the workspace root,
        # but could have different standardizations.
        return str(Path(path).as_posix())

    def find_producing_node(self, target_file: str) -> Optional[Dict[str, Any]]:
        """Find the node that produced the given file."""
        target_norm = self._normalize_path(target_file)
        
        for node_id, node_data in self.dag.get("nodes", {}).items():
            for out_file in node_data.get("output_files", []):
                if self._normalize_path(out_file) == target_norm:
                    return node_data
                    
        return None

    def build_lineage(self, target_file: str) -> Dict[str, Any]:
        """Traverse the DAG backwards from target_file to build its lineage tree."""
        node = self.find_producing_node(target_file)
        
        if not node:
            return {
                "file": target_file,
                "type": "source_or_unknown",
                "producing_node": None,
                "inputs": []
            }
            
        result = {
            "file": target_file,
            "type": "derived",
            "producing_node": {
                "id": node.get("node_id"),
                "script": node.get("script_path"),
                "timestamp": node.get("timestamp"),
                "hash": node.get("data_hash_out", {}).get(target_file)
            },
            "inputs": []
        }
        
        for input_file in node.get("input_files", []):
            input_hash = node.get("data_hash_in", {}).get(input_file)
            input_lineage = self.build_lineage(input_file)
            input_lineage["hash"] = input_hash
            result["inputs"].append(input_lineage)
            
        return result

    def format_human_readable(self, lineage_tree: Dict[str, Any], indent_level: int = 0) -> str:
        """Convert lineage dictionary into a clean, formatted text hierarchy."""
        indent = "  " * indent_level
        lines = []
        
        file_path = lineage_tree.get("file", "Unknown")
        file_hash = lineage_tree.get("hash")
        hash_str = f" [Hash: {file_hash[:8]}...]" if file_hash else ""
        
        if indent_level == 0:
            lines.append(f"Provenance Chain for: {file_path}{hash_str}")
        else:
            prefix = "└─ " if indent_level > 0 else ""
            lines.append(f"{indent}{prefix}File: {file_path}{hash_str}")

        producing_node = lineage_tree.get("producing_node")
        if producing_node:
            script = producing_node.get("script")
            timestamp = producing_node.get("timestamp", "Unknown time")
            lines.append(f"{indent}   Produced by: Node '{producing_node.get('id')}'")
            lines.append(f"{indent}   Script: {script} at {timestamp}")
            
            inputs = lineage_tree.get("inputs", [])
            if inputs:
                lines.append(f"{indent}   Consumed:")
                for inp in inputs:
                    lines.append(self.format_human_readable(inp, indent_level + 2))
        else:
            if indent_level > 0:
                lines.append(f"{indent}   (Original Source)")
                
        return "\n".join(lines)
