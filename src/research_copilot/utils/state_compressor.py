import sqlite3
import os
import json
from pathlib import Path
from research_copilot.core.hooks import hook_engine
from research_copilot.utils.asset_manager import AssetManager

def compress_output(output_text):
    # Condense the node's output into a short summary.
    # In a full implementation, this would call a fast LLM.
    if len(output_text) > 150:
        return output_text[:147] + "..."
    return output_text

@hook_engine.register("post_execution")
def compress_state_hook(state, **kwargs):
    node_id = kwargs.get("node_id")
    if not node_id:
        return state
        
    output_text = state.get("last_output", "")
    summary = compress_output(output_text)
    
    root = AssetManager.find_project_root()
    db_path = root / ".research" / "cache" / "state_cache.sqlite"
    
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS outputs (node_id TEXT PRIMARY KEY, raw_output TEXT)")
    cursor.execute("INSERT OR REPLACE INTO outputs (node_id, raw_output) VALUES (?, ?)", (node_id, output_text))
    conn.commit()
    conn.close()
    
    # Update global context summary
    current_summary = state.get("global_context_summary", "")
    state["global_context_summary"] = current_summary + f"\nNode {node_id}: {summary}"
    
    # Flush raw output, keeping only immediate previous output
    if "last_output" in state:
        state["immediate_previous_output"] = state["last_output"]
        state["last_output"] = summary
        
    return state
