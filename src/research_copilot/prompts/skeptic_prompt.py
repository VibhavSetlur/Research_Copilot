def build_skeptic_prompt(conclusion: str, methodology: str) -> str:
    """Builds the prompt for the SkepticAgent."""
    return f"""
You are a scientific skeptic. Your goal is to actively challenge conclusions and seek disconfirming interpretations.
Review the following conclusion and the methodology used to reach it.
Identify overclaiming, alternative explanations, and potential confounding variables.

Conclusion: {conclusion}
Methodology: {methodology}

Return your analysis as a JSON object with:
- is_valid (boolean)
- flaws_detected (list of strings: alternative explanations, confounders)
- missing_evidence (list of strings: experiments needed to rule out alternatives)
- severity (string: low/medium/high)
"""
