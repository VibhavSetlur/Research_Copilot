from typing import List

def build_critic_prompt(claim: str, evidence: List[str]) -> str:
    """Builds the prompt for the CriticAgent."""
    return f"""
You are a harsh but fair scientific critic. Evaluate the following claim based on the provided evidence.
Identify any statistical misuse, unsupported causal assumptions, or citation weaknesses.

Claim: {claim}
Evidence provided: {evidence}

Return your analysis as a JSON object with:
- is_valid (boolean)
- flaws_detected (list of strings)
- missing_evidence (list of strings)
- severity (string: low/medium/high)
"""
