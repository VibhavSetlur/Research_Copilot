from typing import Dict, Any, List

class PromptCompressor:
    """Compresses the reasoning trajectory, branch lineage, and evolving conclusions to save tokens."""
    
    @staticmethod
    def compress_trajectory(episodic_memory: List[Dict[str, Any]], max_items: int = 3) -> str:
        """Compress episodic memory into a dense reasoning trajectory."""
        if not episodic_memory:
            return ""
        
        # Only take the most recent
        recent = episodic_memory[-max_items:]
        
        compressed = []
        for ep in recent:
            ts = ep.get("timestamp", "")[:10]  # Just the date or short time
            summary = ep.get("summary", "")
            # Remove filler words
            compressed_summary = summary.replace("The user requested", "User:").replace("The system", "Sys:")
            compressed.append(f"[{ts}] {compressed_summary}")
            
        return " | ".join(compressed)
        
    @staticmethod
    def compress_branch_lineage(active_branch: str, all_branches: List[str]) -> str:
        """Compress branch history into a lineage string (e.g. main -> exploratory_1 -> causal_test)."""
        if not all_branches:
            return active_branch
            
        # Just show the path to the active branch if we had a tree, but for now just list them compactly
        return " -> ".join(all_branches[-3:]) if len(all_branches) > 3 else " -> ".join(all_branches)
        
    @staticmethod
    def compress_conclusions(claims: List[Dict[str, Any]]) -> str:
        """Compress evolving conclusions into a dense list of verified claims."""
        if not claims:
            return ""
            
        verified_claims = [c for c in claims if c.get("confidence", 0.0) > 0.7]
        if not verified_claims:
            return "No high-confidence conclusions yet."
            
        compressed = [f"C{i+1}: {c['description']} (cf:{c.get('confidence', 0):.2f})" for i, c in enumerate(verified_claims[-3:])]
        return "; ".join(compressed)
