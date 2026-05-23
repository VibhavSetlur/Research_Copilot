from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone


class Provenance(BaseModel):
    source_id: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    description: str


class SemanticEntity(BaseModel):
    id: str
    description: str
    provenance: List[Provenance] = Field(default_factory=list)
    supporting_evidence: List[str] = Field(default_factory=list)
    opposing_evidence: List[str] = Field(default_factory=list)
    confidence: float = Field(0.5, description="Initial confidence")
    dependencies: List[str] = Field(default_factory=list)
    revision_history: List[Dict[str, str]] = Field(default_factory=list)
    branch_lineage: List[str] = Field(default_factory=list)


class Hypothesis(SemanticEntity):
    pass


class Claim(SemanticEntity):
    pass


class Evidence(SemanticEntity):
    pass


class Finding(SemanticEntity):
    pass


class Contradiction(SemanticEntity):
    related_entities: List[str] = Field(default_factory=list)


class Question(SemanticEntity):
    pass


class Experiment(SemanticEntity):
    methodology_ref: str


class Methodology(SemanticEntity):
    pass


class Citation(SemanticEntity):
    authors: List[str]
    url_or_doi: Optional[str]


class Interpretation(SemanticEntity):
    pass
