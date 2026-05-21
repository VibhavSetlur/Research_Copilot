import logging

logger = logging.getLogger("research.token_budget")

class TokenBudgetTracker:
    """Tracks token usage and triggers emergency synthesis when budget is near exhaustion."""
    
    def __init__(self, max_tokens: int = 200000):
        self.max_tokens = max_tokens
        self.used_tokens = 0
        self.limit_reached = False

    def add_usage(self, prompt_tokens: int, completion_tokens: int):
        total = prompt_tokens + completion_tokens
        self.used_tokens += total
        
        if self.used_tokens >= 0.9 * self.max_tokens and not self.limit_reached:
            self.limit_reached = True
            logger.warning("WARNING: Token budget reached 90%. Triggering force_synthesize interceptor.")
            self._trigger_force_synthesize()

    def _trigger_force_synthesize(self):
        from research_copilot.core.hooks import hook_engine
        hook_engine.trigger_sync("emergency_synthesize", {"status": "budget_exhausted"})

    def get_remaining(self) -> int:
        return max(0, self.max_tokens - self.used_tokens)
