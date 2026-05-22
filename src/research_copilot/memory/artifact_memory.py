from pydantic import BaseModel
from typing import List

class ArtifactRecord(BaseModel):
    artifact_id: str
    file_path: str
    artifact_type: str
    description: str
    generated_by: str

class ArtifactMemory:
    """Tracks generated papers, datasets, charts, experiments."""
    def __init__(self):
        self.artifacts: List[ArtifactRecord] = []
        
    def add_artifact(self, record: ArtifactRecord):
        self.artifacts.append(record)
