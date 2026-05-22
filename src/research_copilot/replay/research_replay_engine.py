import json
from pathlib import Path
from typing import Dict, Any, List

class StateSnapshot:
    def __init__(self, step_id: str, semantic_state: Dict[str, Any], memory_state: Dict[str, Any], graph_state: Dict[str, Any]):
        self.step_id = step_id
        self.semantic_state = semantic_state
        self.memory_state = memory_state
        self.graph_state = graph_state

class ResearchReplayEngine:
    """Enables time-travel debugging and replay of reasoning trajectories."""
    def __init__(self, root: Path):
        self.replay_dir = root / ".research" / "replay_logs"
        self.replay_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots: List[StateSnapshot] = []

    def save_snapshot(self, step_id: str, semantic_state: Dict[str, Any], memory_state: Dict[str, Any], graph_state: Dict[str, Any]):
        snapshot = StateSnapshot(step_id, semantic_state, memory_state, graph_state)
        self.snapshots.append(snapshot)
        
        file_path = self.replay_dir / f"snapshot_{step_id}.json"
        with open(file_path, "w") as f:
            json.dump({
                "step_id": step_id,
                "semantic_state": semantic_state,
                "memory_state": memory_state,
                "graph_state": graph_state
            }, f, indent=2)

    def load_snapshot(self, step_id: str) -> StateSnapshot:
        file_path = self.replay_dir / f"snapshot_{step_id}.json"
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)
                return StateSnapshot(
                    data["step_id"],
                    data["semantic_state"],
                    data["memory_state"],
                    data["graph_state"]
                )
        return None

    def rollback_to(self, step_id: str) -> StateSnapshot:
        """Loads a previous snapshot to branch from."""
        return self.load_snapshot(step_id)
