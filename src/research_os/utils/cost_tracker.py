import logging
from typing import Dict

logger = logging.getLogger("research.cost_tracker")

# Approximate costs per 1K tokens
COST_RATES = {
    "google/gemini-2.5-flash": {"prompt": 0.000075, "completion": 0.00030},
    "openai/gpt-4o-mini": {"prompt": 0.00015, "completion": 0.00060},
    "anthropic/claude-haiku-3": {"prompt": 0.00025, "completion": 0.00125},
    "ollama/llama3": {"prompt": 0.0, "completion": 0.0},
}


class CostTracker:
    def __init__(self):
        self.session_cost = 0.0
        self.token_usage: Dict[str, Dict[str, int]] = {}

    def add_usage(self, model_id: str, prompt_tokens: int, completion_tokens: int):
        if model_id not in self.token_usage:
            self.token_usage[model_id] = {"prompt": 0, "completion": 0}

        self.token_usage[model_id]["prompt"] += prompt_tokens
        self.token_usage[model_id]["completion"] += completion_tokens

        rates = COST_RATES.get(model_id, {"prompt": 0.0001, "completion": 0.0002})

        cost = (prompt_tokens / 1000.0) * rates["prompt"] + (
            completion_tokens / 1000.0
        ) * rates["completion"]
        self.session_cost += cost

    def print_summary(self, notebook_path=None):
        summary = f"[Session Cost: ~${self.session_cost:.4f}]"
        logger.info(summary)

        if notebook_path:
            try:
                with open(notebook_path, "a") as f:
                    f.write(f"\n{summary}\n")
            except Exception as e:
                logger.error(f"Failed to write cost summary: {e}")


global_cost_tracker = CostTracker()
