"""Passive Intent Analyzer — provides structured ResearchIntake schemas for the IDE.

The IDE (the brain) owns all routing decisions.  This module provides passive
analysis of a user's query — classifying intent, identifying relevant skills,
and building a structured intake schema — but does NOT route, plan, or decide
what to execute.  The IDE calls the next tool explicitly.

Usage:
    analyzer = IntentAnalyzer(root)
    intake = analyzer.build_bootstrap_intake("explore this dataset")
    # IDE then decides which tool to call: tool.eda.run, view.figure.show, etc.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("research.intent_analyzer")


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

_DEPTH_ALIASES: Dict[str, str] = {
    "quick": "quick", "standard": "standard", "deep": "deep",
    "exploratory": "exploratory", "academic": "academic", "publication": "publication",
}


class IntentAnalyzer:
    """Passive query analyzer — classifies intent and builds intake schema.

    This class does NOT route, plan, or execute.  It provides structured
    information about a user query that the IDE can use to decide which
    tools to call next.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = self._find_project_root()
        self.root = Path(project_root)
        self.skill_index = self._load_skill_index()

    @staticmethod
    def _find_project_root() -> Path:
        from research_os.utils.common import find_project_root
        return find_project_root()

    def _load_skill_index(self) -> dict:
        index_path = self.root / ".research" / "cache" / "skill_index.json"
        if index_path.exists():
            with open(index_path) as f:
                return json.load(f)
        return {"skills": []}

    def classify_intent(self, query: str) -> Dict[str, Any]:
        """Classify user query into an intent category with confidence scores.

        Returns information for the IDE to consume — no routing decisions are made.

        Args:
            query: User's natural language query

        Returns:
            Dict with primary_intent, all_scores, matched_keywords, and timestamp
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
        """Identify categories that are likely NOT needed for this intent.

        Informational only — the IDE decides what to exclude.
        """
        return set(NULL_SPACE_KEYWORDS.get(primary_intent, []))

    def _enhance_skills_from_index(self, base_skills: List[str], query: str) -> List[str]:
        """Enhance skill list with matches from the skill index (informational)."""
        query_lower = query.lower()
        enhanced = list(base_skills)
        for skill in self.skill_index.get("skills", []):
            skill_id = skill.get("skill_id") or skill.get("id", "")
            if not skill_id or skill_id in enhanced:
                continue
            for kw in skill.get("keywords", []):
                if kw.lower() in query_lower:
                    enhanced.append(skill_id)
                    break
        return enhanced[:8]

    def build_bootstrap_intake(self, raw_query: str) -> Dict[str, Any]:
        """Build a structured ResearchIntake schema from a raw text query.

        This is the primary public method.  It returns a passive schema that
        the IDE can inspect to decide which tools to call next.  No routing
        or auto-execution is performed.

        Args:
            raw_query: The user's unstructured request.

        Returns:
            A dict matching the intake schema (project_name, research_goal,
            primary_intent, suggested_skills, constraints, etc.).
        """
        classification = self.classify_intent(raw_query)
        primary = classification["primary_intent"]
        config = INTENT_CATEGORIES.get(primary, {})
        null_space = self.compute_null_space(primary)
        enhanced_skills = self._enhance_skills_from_index(list(config.get("skills", [])), raw_query)

        intake = {
            "project_name": "Research OS Project",
            "research_goal": raw_query,
            "primary_intent": primary,
            "classification": classification,
            "suggested_skills": enhanced_skills,
            "suggested_agents": list(config.get("agents", [])),
            "suggested_workflow_steps": list(config.get("workflow_steps", [])),
            "excluded_categories": list(null_space),
            "constraints": {
                "depth": "academic",
                "exclude_null_space": list(null_space),
            },
        }

        return intake

    def summary(self) -> str:
        """Print available intent categories and their keywords (informational)."""
        lines = ["=" * 60, "INTENT CATEGORIES (informational)", "=" * 60, ""]
        for category, config in INTENT_CATEGORIES.items():
            lines.append(f"  {category}:")
            lines.append(f"    Keywords: {', '.join(config['keywords'][:8])}...")
            lines.append(f"    Skills: {', '.join(config['skills'])}")
            lines.append("")
        return "\n".join(lines)
