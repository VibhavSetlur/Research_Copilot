import json
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class Revision(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    author_agent: str
    changes: Dict[str, Any]
    reasoning: str

class ResearchObject(BaseModel):
    id: str
    object_type: str
    content: Dict[str, Any]
    revisions: List[Revision] = Field(default_factory=list)
    linked_objects: List[str] = Field(default_factory=list)
    confidence: float = 0.5
    provenance_chain: List[str] = Field(default_factory=list)
    branch: str = "main"

    def revise(self, agent: str, changes: Dict[str, Any], reasoning: str):
        self.revisions.append(Revision(author_agent=agent, changes=changes, reasoning=reasoning))
        self.content.update(changes)

    def link(self, target_id: str):
        if target_id not in self.linked_objects:
            self.linked_objects.append(target_id)

class HypothesisObject(ResearchObject):
    object_type: str = "hypothesis"

class ClaimObject(ResearchObject):
    object_type: str = "claim"

class EvidenceObject(ResearchObject):
    object_type: str = "evidence"

class CitationObject(ResearchObject):
    object_type: str = "citation"

class DatasetObject(ResearchObject):
    object_type: str = "dataset"

class ExperimentObject(ResearchObject):
    object_type: str = "experiment"

class InterpretationObject(ResearchObject):
    object_type: str = "interpretation"

class ResearchObjectStore:
    def __init__(self, root: Path):
        self.store_dir = root / ".research" / "objects"
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.objects: Dict[str, ResearchObject] = {}

    def save(self, obj: ResearchObject):
        self.objects[obj.id] = obj
        file_path = self.store_dir / f"{obj.id}.json"
        with open(file_path, "w") as f:
            f.write(obj.model_dump_json(indent=2))

    def load(self, obj_id: str) -> Optional[ResearchObject]:
        file_path = self.store_dir / f"{obj_id}.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)
                return ResearchObject(**data)
        return None
