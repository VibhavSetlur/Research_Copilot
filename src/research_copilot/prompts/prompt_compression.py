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


from research_copilot.runtime.hooks import hook_engine

@hook_engine.register("compress_memory")
def compress_episodic_to_semantic(state: dict, **kwargs) -> dict:
    """Rolling semantic distillation when memory exceeds 75%."""
    import logging
    logger = logging.getLogger("research.prompt_compression")
    logger.info("Token budget exceeded threshold. Distilling episodic nodes into semantic memory.")
    
    memory = state.get("memory", {})
    episodic = memory.get("episodic", [])
    semantic = memory.get("semantic", {})
    
    if not episodic:
        return state
        
    compressed_trajectory = PromptCompressor.compress_trajectory(episodic, max_items=10)
    
    # Store distilled summary in semantic memory
    old_summary = semantic.get("project_summary", "")
    new_summary = old_summary + "\n\nRecent Trajectory Summarized:\n" + compressed_trajectory
    semantic["project_summary"] = new_summary
    
    # Keep only the last 3 episodic memories to free up context
    memory["episodic"] = episodic[-3:]
    memory["semantic"] = semantic
    state["memory"] = memory
    
    return state

