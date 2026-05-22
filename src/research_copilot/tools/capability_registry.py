from pydantic import BaseModel, Field
from typing import List, Dict, Any

class CapabilityMetadata(BaseModel):
    tool_name: str
    capabilities: List[str]
    preferred_contexts: List[str]
    failure_modes: List[str]
    cost_profile: Dict[str, str] = Field(default_factory=dict)
    risk_profile: Dict[str, str] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    validation_requirements: List[str] = Field(default_factory=list)

class CapabilityRegistry:
    """Registry where AI thinks in capabilities instead of raw tools."""
    def __init__(self):
        self.registry: Dict[str, CapabilityMetadata] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(CapabilityMetadata(
            tool_name="arxiv_search",
            capabilities=["literature_search", "citation_finding"],
            preferred_contexts=["literature_review", "evidence_gathering"],
            failure_modes=["rate_limited", "no_results"],
            cost_profile={"time": "medium", "compute": "low"},
            risk_profile={"hallucination": "low", "outdated": "medium"}
        ))
        self.register(CapabilityMetadata(
            tool_name="python_execution",
            capabilities=["data_analysis", "statistical_testing", "plotting"],
            preferred_contexts=["experimentation", "data_validation"],
            failure_modes=["syntax_error", "timeout", "missing_dependency"],
            cost_profile={"time": "variable", "compute": "high"},
            risk_profile={"security": "high", "data_corruption": "medium"}
        ))

    def register(self, meta: CapabilityMetadata):
        self.registry[meta.tool_name] = meta

    def find_by_capability(self, capability: str) -> List[CapabilityMetadata]:
        return [m for m in self.registry.values() if capability in m.capabilities]
