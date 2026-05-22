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
        from research_copilot.prompts.critic_prompt import build_critic_prompt
        prompt = build_critic_prompt(claim, evidence)
        
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
        from research_copilot.prompts.skeptic_prompt import build_skeptic_prompt
        prompt = build_skeptic_prompt(conclusion, methodology)
        
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
