from pydantic import BaseModel, Field
from typing import List

class SemanticInsight(BaseModel):
    concept: str
    description: str
    related_nodes: List[str] = Field(default_factory=list)
    confidence: float

class SemanticMemory:
    """Long-term semantic memory for research insights and findings."""
    def __init__(self):
        self.insights: List[SemanticInsight] = []
        self.project_summary: str = ""
        self.confidence_evolution: str = ""
        
    def update_summary(self, summary: str, confidence_evolution: str):
        self.project_summary = summary
        self.confidence_evolution = confidence_evolution

    def add_insight(self, insight: SemanticInsight):
        self.insights.append(insight)
