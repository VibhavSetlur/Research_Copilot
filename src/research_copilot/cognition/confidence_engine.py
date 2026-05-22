from pydantic import BaseModel, Field

class ConfidenceScore(BaseModel):
    value: float = Field(..., description="Overall confidence (0-1)")
    evidence_strength: float = Field(..., description="Strength of supporting evidence (0-1)")
    contradiction_penalty: float = Field(..., description="Penalty for contradictions (0-1)")
    methodological_quality: float = Field(..., description="Rigor of methodology used (0-1)")
    recency_score: float = Field(..., description="Freshness of findings (0-1)")

class ConfidenceEngine:
    """Dynamically evolves confidence based on graph state."""
    
    @staticmethod
    def calculate_confidence(
        evidence_strength: float,
        contradiction_penalty: float,
        methodological_quality: float,
        recency_score: float
    ) -> ConfidenceScore:
        
        # Simple weighted sum for Phase 2 demonstration
        base_value = (evidence_strength * 0.4) + (methodological_quality * 0.4) + (recency_score * 0.2)
        final_value = max(0.0, base_value - contradiction_penalty)
        
        return ConfidenceScore(
            value=round(final_value, 2),
            evidence_strength=evidence_strength,
            contradiction_penalty=contradiction_penalty,
            methodological_quality=methodological_quality,
            recency_score=recency_score
        )
