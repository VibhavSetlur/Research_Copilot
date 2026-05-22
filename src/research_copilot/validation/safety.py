from typing import Dict, Any, List
import logging

logger = logging.getLogger("research.safety")

class SafetyGater:
    """Handles hallucination detection, confidence-gating, and recovery policies."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.confidence_threshold = config.get("CONFIDENCE_THRESHOLD", 0.7)
        self.recovery_enabled = config.get("ENABLE_AUTONOMOUS_RECOVERY", False)

    def detect_hallucinations(self, text: str, evidence: List[str], call_llm_fn) -> bool:
        """
        Uses an LLM pass to explicitly check if any claim in 'text' is entirely
        unsupported by the provided 'evidence'.
        """
        prompt = (
            "You are a strict hallucination detector.\n"
            "Review the generated text and the exact evidence provided. "
            "Return EXACTLY 'HALLUCINATION' if the text makes factual claims or cites numbers/papers "
            "that are NOT present in the evidence. Otherwise return 'CLEAN'.\n\n"
            f"Evidence: {evidence}\n"
            f"Text: {text}"
        )
        response = call_llm_fn(prompt).strip()
        if "HALLUCINATION" in response.upper():
            logger.warning("Hallucination detected in generated text.")
            return True
        return False

    def can_publish(self, cognitive_state: Dict[str, Any]) -> bool:
        """
        Confidence-gated publishing: refuse to compile manuscript if key hypotheses 
        are active but unverified, or if confidence of core claims is below threshold.
        """
        claims = cognitive_state.get("claims", [])
        if not claims:
            logger.warning("Cannot publish: No verified claims in cognitive state.")
            return False
            
        for claim in claims:
            conf = claim.get("confidence", 0.0)
            if conf < self.confidence_threshold:
                logger.warning(f"Cannot publish: Claim '{claim.get('id')}' confidence ({conf}) is below threshold ({self.confidence_threshold}).")
                return False
                
        # Check for unresolved contradictions
        contradictions = cognitive_state.get("contradictions", [])
        unresolved = [c for c in contradictions if not c.get("resolved", False)]
        if unresolved:
            logger.warning("Cannot publish: There are unresolved contradictions in the cognitive state.")
            return False
            
        return True

    def run_recovery_policy(self, error: Exception, active_node: str, state_ledger) -> Dict[str, Any]:
        """
        Autonomous recovery policies when execution crashes.
        Returns a mutation intent to fix the graph.
        """
        if not self.recovery_enabled:
            return {"action": "fail", "reason": str(error)}
            
        error_str = str(error).lower()
        if "timeout" in error_str or "rate limit" in error_str:
            logger.info(f"Applying autonomous recovery: Backoff and retry for {active_node}")
            return {"action": "retry_with_backoff", "node_id": active_node}
            
        if "context length exceeded" in error_str or "token" in error_str:
            logger.info(f"Applying autonomous recovery: Flush context and summarize for {active_node}")
            # Mutate state ledger to trigger summarization
            state = state_ledger.get()
            state["force_memory_compression"] = True
            state_ledger.save(state)
            return {"action": "retry", "node_id": active_node}
            
        if "syntax" in error_str or "compilation" in error_str:
            logger.info(f"Applying autonomous recovery: Auto-debug mode for {active_node}")
            return {"action": "branch_for_debug", "node_id": active_node}
            
        return {"action": "escalate_to_user", "reason": str(error)}
