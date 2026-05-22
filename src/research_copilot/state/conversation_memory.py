import os
import json
from pathlib import Path
from research_copilot.state.conversation_state import ConversationStateData
from research_copilot.utils.common import save_json_atomic, load_json

class ConversationMemory:
    """Persistent serialization backend for ConversationState."""
    def __init__(self, root: Path):
        self.root = Path(root)
        self.file_path = self.root / ".research" / "cache" / "conversation_memory.json"
        
    def load(self) -> ConversationStateData:
        if not self.file_path.exists():
            return ConversationStateData()
        data = load_json(self.file_path)
        try:
            return ConversationStateData(**data)
        except Exception:
            return ConversationStateData()

    def save(self, state_data: ConversationStateData):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        save_json_atomic(self.file_path, state_data.model_dump())
