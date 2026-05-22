from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime, timezone

class EpisodicMemoryData(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    trigger: str
    summary: str
    decisions_made: List[str] = Field(default_factory=list)
    rejected_alternatives: List[str] = Field(default_factory=list)
    context_snapshot: Dict[str, Any] = Field(default_factory=dict)

class EpisodicMemory:
    """Stores recent conversation + execution context."""
    def __init__(self):
        self.episodes: List[EpisodicMemoryData] = []
        
    def add_episode(self, data: EpisodicMemoryData):
        self.episodes.append(data)
