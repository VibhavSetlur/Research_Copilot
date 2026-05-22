import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone

class SessionReplayManager:
    """Manages deterministic snapshots of research state for replay and audit."""
    
    def __init__(self, log_dir: Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_file = self.log_dir / "replay_log.jsonl"
        
    def capture_snapshot(self, event_type: str, state: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Records a complete state snapshot at a specific point in time."""
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "metadata": metadata or {},
            "state_snapshot": state
        }
        with open(self.snapshots_file, "a") as f:
            f.write(json.dumps(snapshot) + "\n")
            
    def load_replay_log(self) -> List[Dict[str, Any]]:
        """Loads all snapshots in chronological order."""
        if not self.snapshots_file.exists():
            return []
            
        logs = []
        with open(self.snapshots_file, "r") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
        return logs
        
    def get_snapshot_at(self, index: int) -> Dict[str, Any]:
        """Retrieves a specific snapshot by index."""
        logs = self.load_replay_log()
        if not logs or index >= len(logs) or index < -len(logs):
            return {}
        return logs[index]["state_snapshot"]
        
    def format_replay_viewer(self) -> str:
        """Generates a readable trace of reasoning evolution and state transitions."""
        logs = self.load_replay_log()
        if not logs:
            return "No replay logs found."
            
        lines = ["=== Research Session Replay ==="]
        for i, log in enumerate(logs):
            ts = log.get("timestamp", "unknown")
            event = log.get("event_type", "unknown")
            meta = log.get("metadata", {})
            lines.append(f"[{i}] {ts} - {event}")
            if meta:
                lines.append(f"    Metadata: {json.dumps(meta)}")
        return "\n".join(lines)
