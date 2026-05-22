from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json

class CritiqueResult(BaseModel):
    is_valid: bool = Field(..., description="Whether the claim/conclusion stands up to scrutiny")
    flaws_detected: List[str] = Field(default_factory=list, description="Specific logical, statistical, or methodological flaws")
    missing_evidence: List[str] = Field(default_factory=list, description="What evidence is missing to support the claim")
    severity: str = Field(..., description="low, medium, high")

class CriticAgent:
    """Agent responsible for checking statistical misuse, unsupported claims, and causality assumptions."""
    def __init__(self, call_llm):
        self.call_llm = call_llm

    def critique_claim(self, claim: str, evidence: List[str]) -> CritiqueResult:
        prompt = f"""
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
        
        raw_response = self.call_llm(prompt)
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        try:
            data = json.loads(raw_response.strip())
            return CritiqueResult(**data)
        except Exception:
            return CritiqueResult(is_valid=False, flaws_detected=["Failed to parse critique"], severity="high")


class SkepticAgent:
    """Agent responsible for seeking disconfirming evidence and challenging overarching interpretations."""
    def __init__(self, call_llm):
        self.call_llm = call_llm

    def challenge_conclusion(self, conclusion: str, methodology: str) -> CritiqueResult:
        prompt = f"""
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
        
        raw_response = self.call_llm(prompt)
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:]
        if raw_response.endswith("```"):
            raw_response = raw_response[:-3]
            
        try:
            data = json.loads(raw_response.strip())
            return CritiqueResult(**data)
        except Exception:
            return CritiqueResult(is_valid=False, flaws_detected=["Failed to parse critique"], severity="high")
