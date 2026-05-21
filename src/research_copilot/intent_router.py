#!/usr/bin/env python3
"""Dynamic Intent Router — orthogonal routing matrix for token optimization.

Sits before DAG initialization. Maps user intent to the exact minimal subset
of tools/skills required. Identifies the null space of the request — agents
and skills that are absolutely not needed — and excludes them from context.

Compiles transient workflow YAML on-the-fly instead of forcing users into
predefined workflow templates.

Usage:
    from intent_router import IntentRouter
    router = IntentRouter()
    result = router.route("find out what's driving the variance in this dataset")
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("research.intent_router")


INTENT_CATEGORIES = {
    "exploratory": {
        "keywords": ["explore", "variance", "driving", "what", "pattern", "trend", "distribution",
                     "summary", "overview", "look at", "check", "see", "find", "describe"],
        "skills": ["profile_tabular", "detect_missingness", "descriptive_stats", "viz_basic_charts"],
        "agents": ["research_init", "data_scaffold"],
        "workflow_steps": ["intake", "scan", "data_profile", "eda", "report"],
    },
    "hypothesis_test": {
        "keywords": ["test", "hypothesis", "significant", "difference", "compare", "effect",
                     "relationship", "correlation", "association", "predict"],
        "skills": ["inferential_stats", "effect_sizes", "power_analysis", "assumption_tests"],
        "agents": ["research_init", "method_route", "execute_analysis"],
        "workflow_steps": ["intake", "method_selection", "data_pipeline", "analysis", "validate"],
    },
    "causal": {
        "keywords": ["causal", "cause", "effect", "treatment", "intervention", "confound",
                     "instrumental", "regression discontinuity", "difference in differences",
                     "propensity", "matching"],
        "skills": ["causal_inference", "dag_analysis", "confounder_detection", "sensitivity_analysis"],
        "agents": ["research_init", "method_route", "execute_analysis", "replication_validator"],
        "workflow_steps": ["intake", "causal_method", "data_pipeline", "causal_analysis", "robustness"],
    },
    "literature": {
        "keywords": ["literature", "papers", "research", "prior", "previous", "review",
                     "bibliography", "citation", "evidence", "consensus"],
        "skills": ["search_semantic_scholar", "search_pubmed", "extract_claims", "synthesize_literature"],
        "agents": ["research_init", "literature_deep"],
        "workflow_steps": ["intake", "literature_search", "evidence_matrix", "synthesis"],
    },
    "visualization": {
        "keywords": ["chart", "plot", "figure", "visualize", "graph", "dashboard", "display",
                     "show", "render", "draw"],
        "skills": ["viz_design_system", "viz_code_standards", "viz_basic_charts", "viz_advanced_plots"],
        "agents": ["research_init", "data_scaffold"],
        "workflow_steps": ["intake", "data_load", "visualization", "export"],
    },
    "manuscript": {
        "keywords": ["write", "manuscript", "paper", "draft", "section", "introduction",
                     "methods", "results", "discussion", "abstract", "compile"],
        "skills": ["imrad_structure", "apa_tables", "effect_sizes", "concise_summary"],
        "agents": ["compile_outputs", "audit_validate"],
        "workflow_steps": ["compile", "audit", "reviewer2", "finalize"],
    },
    "robustness": {
        "keywords": ["robust", "sensitivity", "check", "validate", "verify", "replicate",
                     "stability", "alternative", "specification"],
        "skills": ["robustness_checks", "sensitivity_analysis", "replication"],
        "agents": ["execute_analysis", "replication_validator", "audit_validate"],
        "workflow_steps": ["re_analyze", "robustness", "compare", "report"],
    },
    "bayesian": {
        "keywords": ["bayesian", "prior", "posterior", "mcmc", "stan", "pymc", "brms",
                     "credible interval", "bayes factor"],
        "skills": ["bayesian_analysis", "prior_specification", "mcmc_diagnostics"],
        "agents": ["research_init", "method_route", "execute_analysis"],
        "workflow_steps": ["intake", "bayesian_method", "data_pipeline", "bayesian_analysis"],
    },
    "predictive": {
        "keywords": ["predict", "model", "machine learning", "ml", "train", "test",
                     "accuracy", "cross-validation", "feature", "classification", "regression"],
        "skills": ["predictive_modeling", "cross_validation", "feature_engineering", "model_evaluation"],
        "agents": ["research_init", "method_route", "execute_analysis"],
        "workflow_steps": ["intake", "model_selection", "data_pipeline", "train", "evaluate"],
    },
    "iteration": {
        "keywords": ["try again", "different", "what if", "change", "switch", "control for",
                     "add", "remove", "alternative", "rethink"],
        "skills": [],
        "agents": ["research_iterate"],
        "workflow_steps": ["iterate"],
    },
}

NULL_SPACE_KEYWORDS = {
    "exploratory": ["causal", "bayesian", "mcmc", "manuscript", "literature", "predictive"],
    "hypothesis_test": ["bayesian", "mcmc", "literature", "manuscript", "causal"],
    "causal": ["bayesian", "predictive", "literature", "manuscript"],
    "literature": ["causal", "bayesian", "predictive", "visualization"],
    "visualization": ["causal", "bayesian", "literature", "manuscript"],
    "manuscript": ["exploratory", "causal", "bayesian", "predictive"],
    "robustness": ["literature", "visualization", "manuscript"],
    "bayesian": ["frequentist", "literature", "manuscript"],
    "predictive": ["causal", "bayesian", "literature", "manuscript"],
    "iteration": [],
}

DEPTH_PROFILES = {
    "exploratory": {
        "description": "Fast first-pass analysis for orientation and simple plots.",
        "exclude_skills": {
            "bayesian_modeling",
            "bayesian_analysis",
            "causal_inference",
            "power_analysis",
            "mixed_effects",
            "survival_analysis",
            "reviewer2_critic",
            "audit_claim_trace",
            "audit_reproducibility",
            "audit_statistical_reporting",
            "replication",
            "sensitivity_analysis",
            "cross_validation",
        },
        "exclude_agents": {
            "reviewer2_critic",
            "replication_validator",
            "audit_validate",
            "methodology_scout",
        },
        "exclude_steps": {"reviewer2", "audit", "robustness", "validate", "finalize"},
        "quality_gates": False,
        "prompt_constraint": (
            "Prioritize speed and simple descriptive statistics. "
            "Do not run adversarial audits."
        ),
    },
    "academic": {
        "description": "Balanced research workflow with method checks and lightweight validation.",
        "exclude_skills": set(),
        "exclude_agents": set(),
        "exclude_steps": set(),
        "quality_gates": True,
        "prompt_constraint": (
            "Use appropriate methodological checks and report uncertainty, "
            "but keep the workflow proportional to the question."
        ),
    },
    "publication": {
        "description": "Full rigor workflow for publication-ready outputs.",
        "exclude_skills": set(),
        "exclude_agents": set(),
        "exclude_steps": set(),
        "quality_gates": True,
        "prompt_constraint": (
            "Run full validation, adversarial critique, provenance checks, "
            "and publication-grade reporting."
        ),
    },
}


class IntentRouter:
    """Orthogonal routing matrix for minimal context loading."""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = self._find_project_root()
        self.root = Path(project_root)
        self.skill_index = self._load_skill_index()

    @staticmethod
    def _find_project_root() -> Path:
        p = Path.cwd()
        for _ in range(10):
            if (p / ".research").exists():
                return p
            if p.parent == p:
                break
            p = p.parent
        return Path.cwd()

    def _load_skill_index(self) -> dict:
        """Load the skill index for enhanced matching."""
        index_path = self.root / ".research" / "cache" / "skill_index.json"
        if index_path.exists():
            with open(index_path) as f:
                return json.load(f)
        return {"skills": []}

    def classify_intent(self, query: str) -> Dict[str, Any]:
        """Classify user query into intent categories with confidence scores.

        Args:
            query: User's natural language query

        Returns:
            Dict with primary intent, all scores, and matched keywords
        """
        query_lower = query.lower()
        scores = {}

        for category, config in INTENT_CATEGORIES.items():
            score = 0
            matched = []
            for kw in config["keywords"]:
                if kw.lower() in query_lower:
                    score += len(kw.split()) * 2
                    matched.append(kw)

            if score > 0:
                scores[category] = {"score": score, "matched_keywords": matched}

        if not scores:
            scores["exploratory"] = {"score": 1, "matched_keywords": ["default"]}

        sorted_scores = sorted(scores.items(), key=lambda x: -x[1]["score"])
        primary = sorted_scores[0][0]

        return {
            "primary_intent": primary,
            "all_scores": {k: v["score"] for k, v in sorted_scores},
            "matched_keywords": {k: v["matched_keywords"] for k, v in sorted_scores},
            "query": query,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def compute_null_space(self, primary_intent: str) -> Set[str]:
        """Identify skills/agents that are NOT needed for this intent.

        Args:
            primary_intent: The classified primary intent

        Returns:
            Set of category names that can be excluded
        """
        return set(NULL_SPACE_KEYWORDS.get(primary_intent, []))

    def get_minimal_context(self, query: str, depth: str = "academic") -> Dict[str, Any]:
        """Get the minimal context payload for a query.

        Args:
            query: User's natural language query
            depth: exploratory, academic, or publication

        Returns:
            Dict with skills, agents, and workflow steps to load
        """
        depth = self._normalize_depth(depth)
        classification = self.classify_intent(query)
        primary = classification["primary_intent"]
        profile = DEPTH_PROFILES[depth]

        if depth == "exploratory":
            # Zero-Shot Fast Path
            null_space = set(INTENT_CATEGORIES.keys()) - {"exploratory"}
            return {
                "classification": classification,
                "depth": depth,
                "depth_profile": {
                    "description": profile["description"],
                    "quality_gates": profile["quality_gates"],
                    "prompt_constraint": profile["prompt_constraint"],
                },
                "null_space": list(null_space),
                "context": {
                    "skills": ["viz_basic_charts", "descriptive_stats"],
                    "agents": ["zero_shot_analyst"],
                    "workflow_steps": ["zero_shot_analysis"],
                },
                "excluded": {
                    "skill_categories": list(null_space),
                    "depth_exclusions": sorted(
                        set(profile["exclude_skills"]) | set(profile["exclude_agents"]) | set(profile["exclude_steps"])
                    ),
                    "estimated_token_savings": self._estimate_token_savings(null_space),
                },
            }

        null_space = self.compute_null_space(primary)

        config = INTENT_CATEGORIES[primary]

        skills = list(config["skills"])
        agents = list(config["agents"])
        workflow_steps = list(config["workflow_steps"])

        enhanced_skills = self._enhance_skills_from_index(skills, query)
        enhanced_skills = [
            s for s in enhanced_skills
            if s not in profile["exclude_skills"] and not self._is_excluded_by_depth(s, profile["exclude_skills"])
        ]
        agents = [
            a for a in agents
            if a not in profile["exclude_agents"] and not self._is_excluded_by_depth(a, profile["exclude_agents"])
        ]
        workflow_steps = [s for s in workflow_steps if s not in profile["exclude_steps"]]

        if depth == "publication":
            for agent in ("replication_validator", "reviewer2_critic", "audit_validate"):
                if agent not in agents:
                    agents.append(agent)
            for step in ("robustness", "reviewer2", "audit"):
                if step not in workflow_steps:
                    workflow_steps.append(step)

        return {
            "classification": classification,
            "depth": depth,
            "depth_profile": {
                "description": profile["description"],
                "quality_gates": profile["quality_gates"],
                "prompt_constraint": profile["prompt_constraint"],
            },
            "null_space": list(null_space),
            "context": {
                "skills": enhanced_skills,
                "agents": agents,
                "workflow_steps": workflow_steps,
            },
            "excluded": {
                "skill_categories": list(null_space),
                "depth_exclusions": sorted(
                    set(profile["exclude_skills"]) | set(profile["exclude_agents"]) | set(profile["exclude_steps"])
                ),
                "estimated_token_savings": self._estimate_token_savings(null_space),
            },
        }

    @staticmethod
    def _normalize_depth(depth: str) -> str:
        depth = (depth or "academic").strip().lower()
        if depth not in DEPTH_PROFILES:
            raise ValueError(
                f"Unsupported depth '{depth}'. Use one of: {', '.join(DEPTH_PROFILES)}"
            )
        return depth

    @staticmethod
    def _is_excluded_by_depth(name: str, exclusions: Set[str]) -> bool:
        lowered = name.lower()
        return any(token in lowered for token in exclusions)

    def _enhance_skills_from_index(self, base_skills: List[str], query: str) -> List[str]:
        """Enhance skill list with matches from the skill index."""
        query_lower = query.lower()
        enhanced = list(base_skills)

        for skill in self.skill_index.get("skills", []):
            skill_id = skill.get("skill_id") or skill.get("id", "")
            if not skill_id:
                continue
            if skill_id in enhanced:
                continue

            for kw in skill.get("keywords", []):
                if kw.lower() in query_lower:
                    enhanced.append(skill_id)
                    break

        return enhanced[:8]

    def _estimate_token_savings(self, null_space: Set[str]) -> int:
        """Estimate token savings from excluding null space categories.

        Rough estimate: each skill category ~500-2000 tokens.
        """
        tokens_per_category = 1500
        return len(null_space) * tokens_per_category

    def compile_transient_workflow(self, query: str, depth: str = "academic") -> str:
        """Compile a transient workflow YAML for the query.

        Args:
            query: User's natural language query

        Returns:
            YAML string for the transient workflow
        """
        context = self.get_minimal_context(query, depth=depth)
        classification = context["classification"]
        primary = classification["primary_intent"]

        steps = []
        for i, step in enumerate(context["context"]["workflow_steps"]):
            steps.append(f"  - step: {i + 1}\n    name: {step}\n    type: {step}")

        skills_yaml = "\n".join(
            f"    - {s}" for s in context["context"]["skills"]
        )
        agents_yaml = "\n".join(
            f"    - {a}" for a in context["context"]["agents"]
        )

        yaml_content = f"""# Transient Workflow — Auto-generated
# Query: {query}
# Intent: {primary}
# Depth: {context['depth']}
# Generated: {datetime.now(timezone.utc).isoformat()}
# Token savings: ~{context['excluded']['estimated_token_savings']} tokens excluded

transient: true
intent: {primary}
depth: {context['depth']}
null_space_excluded: {context['null_space']}
depth_exclusions: {context['excluded']['depth_exclusions']}

prompt_constraints:
  - "{context['depth_profile']['prompt_constraint']}"

steps:
{chr(10).join(steps)}

skills_to_load:
{skills_yaml}

agents_to_invoke:
{agents_yaml}

quality_gates:
  - enabled: {str(context['depth_profile']['quality_gates']).lower()}
    checks: [data_grounding, method_appropriateness]
"""
        return yaml_content

    def route(self, query: str, save: bool = True, depth: str = "academic") -> Dict[str, Any]:
        """Full routing pipeline: classify, compute null space, get minimal context.

        Args:
            query: User's natural language query
            save: Whether to save the routing decision
            depth: exploratory, academic, or publication

        Returns:
            Full routing result dict
        """
        result = self.get_minimal_context(query, depth=depth)
        result["transient_workflow"] = self.compile_transient_workflow(query, depth=depth)

        if save:
            self._save_routing_decision(result)

        return result

    def _save_routing_decision(self, result: Dict[str, Any]) -> None:
        """Save routing decision for auditability."""
        routing_dir = self.root / "01_workspace" / "scratchpad" / "routing_decisions"
        routing_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        routing_path = routing_dir / f"routing_{timestamp}.json"

        with open(routing_path, "w") as f:
            json.dump(result, f, indent=2)

        logger.info("Routing decision saved to %s", routing_path)

    def summary(self) -> str:
        """Print available intent categories and their keywords."""
        lines = [
            "=" * 60,
            "INTENT ROUTING MATRIX",
            "=" * 60,
            "",
        ]

        for category, config in INTENT_CATEGORIES.items():
            lines.append(f"  {category}:")
            lines.append(f"    Keywords: {', '.join(config['keywords'][:8])}...")
            lines.append(f"    Skills: {', '.join(config['skills'])}")
            lines.append(f"    Agents: {', '.join(config['agents'])}")
            lines.append("")

        return "\n".join(lines)
