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
