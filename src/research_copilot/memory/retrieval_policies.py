class MemoryRetrievalPolicies:
    """Retrieves memories based on different heuristics."""
    
    @staticmethod
    def by_relevance(query: str, semantic_memory):
        # Placeholder for vector-based or keyword search
        return [insight for insight in semantic_memory.insights if query.lower() in insight.concept.lower()]
        
    @staticmethod
    def by_active_hypothesis(hypothesis_id: str, semantic_memory):
        return [insight for insight in semantic_memory.insights if hypothesis_id in insight.related_nodes]
        
    @staticmethod
    def by_contradiction_proximity(contradiction_id: str, episodic_memory):
        # Fetch recent episodes where contradictions were debated
        return [ep for ep in episodic_memory.episodes if "contradiction" in ep.summary.lower()]

import logging
from typing import Any, Dict, List

logger = logging.getLogger("research.memory.retrieval_policies")

class MemoryTier:
    """Defines memory tiers for tiered context loading."""
    TIER_1_SYSTEM = "tier_1"     # System prompt, safety rails, current DAG state (Always loaded)
    TIER_2_WORKING = "tier_2"    # Working Memory / Semantic State (Loaded by default, distillable)
    TIER_3_COLD = "tier_3"       # Cold Storage / Raw Files / Past Trajectories (Only via MCP tool)

class TieredRetrievalManager:
    """Manages memory retrieval based on context tiers."""

    @staticmethod
    def get_context_payload(state: Dict[str, Any], requested_tiers: List[str] = None) -> Dict[str, Any]:
        """Constructs a context payload by fetching memory based on requested tiers.
        
        Args:
            state: The full state ledger.
            requested_tiers: List of tiers to include. Defaults to Tier 1 and Tier 2.
            
        Returns:
            A subset of state containing only the requested tiers.
        """
        if requested_tiers is None:
            requested_tiers = [MemoryTier.TIER_1_SYSTEM, MemoryTier.TIER_2_WORKING]
            
        payload = {}
        
        if MemoryTier.TIER_1_SYSTEM in requested_tiers:
            # Core system state
            payload["phase"] = state.get("phase")
            payload["current_branch"] = state.get("current_branch")
            payload["execution_dag"] = state.get("execution_dag")
            payload["hitl_pending"] = state.get("hitl_pending")
            
        if MemoryTier.TIER_2_WORKING in requested_tiers:
            # Working memory
            memory = state.get("memory", {})
            payload["semantic_memory"] = memory.get("semantic", {})
            payload["recent_episodic"] = memory.get("episodic", [])[-3:] # Only last 3 allowed
            payload["claims"] = state.get("research_objects", {}).get("claims", [])
            
        # Tier 3 is strictly EXCLUDED from base context payload and must be fetched via MCP tools
        if MemoryTier.TIER_3_COLD in requested_tiers:
            logger.warning("Tier 3 context requested directly in payload. This should be accessed via MCP tools instead.")
            # We explicitly do not load raw files here
            
        return payload
