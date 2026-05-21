#!/usr/bin/env python3
"""Interpretative Coupling — auto-generates .interpret.md files for all figures.

Every figure generated must be accompanied by an auto-generated .interpret.md
file in docs/decisions/. This ensures users aren't just handed a dashboard,
but rather a curated gallery of visual evidence paired with explicit
statistical interpretations.

Usage (as interceptor):
    from interpretative_coupling import generate_interpretation
    state = generate_interpretation(state, figure_path="reports/figures/scatter.png")
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("research.interpretative_coupling")


class InterpretativeCoupler:
    """Generates statistical interpretations for all generated figures."""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = self._find_project_root()
        self.root = Path(project_root)

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

    def generate_interpretation(
        self,
        figure_path: Path,
        figure_type: str = "unknown",
        statistical_results: Optional[Dict[str, Any]] = None,
        research_question: str = "",
        hypothesis: str = "",
        branch_id: str = "main",
    ) -> Path:
        """Generate an .interpret.md file for a figure.

        Args:
            figure_path: Path to the figure file
            figure_type: Type of figure (scatter, bar, line, heatmap, etc.)
            statistical_results: Dict of statistical results associated with figure
            research_question: Research question this figure addresses
            hypothesis: Hypothesis being tested
            branch_id: Current branch

        Returns:
            Path to the generated interpretation file
        """
        figure_path = Path(figure_path)
        if not figure_path.exists():
            logger.warning("Figure not found: %s", figure_path)
            return figure_path

        interp_path = self._resolve_interpretation_path(figure_path, branch_id)

        content = self._build_interpretation(
            figure_path, figure_type, statistical_results,
            research_question, hypothesis, branch_id,
        )

        with open(interp_path, "w") as f:
            f.write(content)

        logger.info("Generated interpretation: %s", interp_path)
        return interp_path

    def _resolve_interpretation_path(self, figure_path: Path, branch_id: str) -> Path:
        """Resolve the path for the interpretation file."""
        decisions_dir = self.root / "docs" / "decisions"
        if branch_id != "main":
            decisions_dir = decisions_dir / branch_id
        decisions_dir.mkdir(parents=True, exist_ok=True)

        stem = figure_path.stem
        return decisions_dir / f"{stem}.interpret.md"

    def _build_interpretation(
        self,
        figure_path: Path,
        figure_type: str,
        statistical_results: Optional[Dict[str, Any]],
        research_question: str,
        hypothesis: str,
        branch_id: str,
    ) -> str:
        """Build the interpretation markdown content."""
        now = datetime.now(timezone.utc).isoformat()

        relative_path = figure_path.relative_to(self.root) if figure_path.is_absolute() else figure_path

        sections = [
            f"# Figure Interpretation: {figure_path.stem}",
            "",
            f"**Generated**: {now}",
            f"**Figure**: `{relative_path}`",
            f"**Type**: {figure_type}",
            f"**Branch**: {branch_id}",
            "",
        ]

        if research_question:
            sections.append(f"## Research Question")
            sections.append(f"{research_question}")
            sections.append("")

        if hypothesis:
            sections.append(f"## Hypothesis")
            sections.append(f"{hypothesis}")
            sections.append("")

        sections.extend([
            "## Visual Description",
            "",
            self._generate_visual_description(figure_type, figure_path.stem),
            "",
        ])

        if statistical_results:
            sections.extend([
                "## Statistical Interpretation",
                "",
                self._generate_statistical_interpretation(statistical_results),
                "",
            ])

        sections.extend([
            "## Key Takeaways",
            "",
            self._generate_key_takeaways(figure_type, statistical_results),
            "",
            "## Caveats & Limitations",
            "",
            self._generate_caveats(figure_type, statistical_results),
            "",
            "---",
            f"*Auto-generated by Research Copilot Interpretative Coupling*",
        ])

        return "\n".join(sections)

    def _generate_visual_description(self, figure_type: str, stem: str) -> str:
        """Generate a visual description based on figure type."""
        descriptions = {
            "scatter": "This scatter plot displays the relationship between two continuous variables. "
                       "Each point represents an observation. The pattern of points reveals the direction, "
                       "strength, and form of the association.",
            "bar": "This bar chart compares values across categorical groups. "
                   "The height of each bar represents the magnitude of the measured variable for that category.",
            "line": "This line plot shows how a variable changes over a continuous dimension (typically time). "
                    "The trajectory of the line reveals trends, cycles, and structural breaks.",
            "histogram": "This histogram displays the distribution of a single continuous variable. "
                         "The shape reveals central tendency, spread, skewness, and potential outliers.",
            "boxplot": "This box plot summarizes the distribution of a variable across groups. "
                       "The box shows the interquartile range (IQR), the line is the median, "
                       "and whiskers extend to 1.5×IQR. Points beyond are potential outliers.",
            "heatmap": "This heatmap displays a matrix of values using color intensity. "
                       "Warmer colors indicate higher values, cooler colors indicate lower values.",
            "forest": "This forest plot displays effect estimates with confidence intervals for multiple "
                      "variables or studies. The vertical line represents the null effect.",
            "violin": "This violin plot combines a box plot with a kernel density estimate, "
                      "showing both summary statistics and the full distribution shape.",
            "residual": "This residual plot displays the difference between observed and predicted values. "
                        "A random scatter around zero indicates good model fit; patterns suggest misspecification.",
        }

        return descriptions.get(figure_type,
                                f"This figure ({figure_type}) visualizes the data related to '{stem}'. "
                                f"Refer to the statistical interpretation below for quantitative findings.")

    def _generate_statistical_interpretation(self, results: Dict[str, Any]) -> str:
        """Generate statistical interpretation from results dict."""
        lines = []

        if "effect_size" in results:
            es = results["effect_size"]
            ci = results.get("ci", [None, None])
            lines.append(f"- **Effect size**: β = {es:.3f} "
                         f"[{ci[0]:.3f}, {ci[1]:.3f}]")

        if "p_value" in results:
            p = results["p_value"]
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            lines.append(f"- **p-value**: {p:.4f} ({sig})")

        if "r_squared" in results:
            lines.append(f"- **R²**: {results['r_squared']:.3f}")

        if "n" in results:
            lines.append(f"- **Sample size**: N = {results['n']}")

        if "test_statistic" in results:
            lines.append(f"- **Test statistic**: {results.get('test_name', 't')} = "
                         f"{results['test_statistic']:.3f}")

        if "confidence_level" in results:
            lines.append(f"- **Confidence level**: {results['confidence_level']}%")

        if not lines:
            lines.append("- Statistical results not available in metadata. "
                         "Run the associated analysis script for quantitative interpretation.")

        return "\n".join(lines)

    def _generate_key_takeaways(
        self, figure_type: str, results: Optional[Dict[str, Any]]
    ) -> str:
        """Generate key takeaways based on figure type and results."""
        takeaways = []

        if results:
            p = results.get("p_value", 1.0)
            es = results.get("effect_size", 0)

            if p < 0.05:
                takeaways.append(
                    f"- The relationship is statistically significant (p = {p:.4f})."
                )
                if abs(es) > 0.5:
                    takeaways.append(
                        f"- The effect size (β = {es:.3f}) is substantively meaningful."
                    )
                elif abs(es) > 0.2:
                    takeaways.append(
                        f"- The effect size (β = {es:.3f}) is moderate."
                    )
                else:
                    takeaways.append(
                        f"- The effect size (β = {es:.3f}) is small but statistically significant."
                    )
            else:
                takeaways.append(
                    f"- The relationship is not statistically significant (p = {p:.4f})."
                )
                takeaways.append(
                    "- Non-significant results are reported with the same rigor as significant findings."
                )

        if figure_type == "residual":
            takeaways.append(
                "- Check for patterns in residuals: funnel shapes suggest heteroskedasticity, "
                "curves suggest nonlinearity."
            )
        elif figure_type == "scatter":
            takeaways.append(
                "- Assess the direction (positive/negative), strength (tight/loose), "
                "and form (linear/nonlinear) of the relationship."
            )

        if not takeaways:
            takeaways.append(
                "- Interpret the visual pattern in the context of the research question."
            )
            takeaways.append(
                "- Note any outliers, clusters, or unexpected patterns."
            )

        return "\n".join(takeaways)

    def _generate_caveats(
        self, figure_type: str, results: Optional[Dict[str, Any]]
    ) -> str:
        """Generate caveats and limitations."""
        caveats = [
            "- This interpretation is auto-generated and should be verified by a domain expert.",
            "- Visual patterns alone do not establish causation.",
        ]

        if results and results.get("p_value", 1.0) < 0.05:
            caveats.append(
                "- Statistical significance does not imply practical significance. "
                "Consider the effect size in context."
            )

        if figure_type in ("scatter", "line"):
            caveats.append(
                "- Correlation does not imply causation. Unobserved confounders may explain the pattern."
            )

        if figure_type == "histogram":
            caveats.append(
                "- The shape depends on bin width. Try different bin sizes to verify robustness."
            )

        return "\n".join(caveats)


def generate_figure_interpretation(state: dict, *args, **kwargs) -> dict:
    """Interceptor: auto-generate interpretation for newly created figures.

    Called as a post_execution hook. Checks if state contains figure output
    and generates an accompanying .interpret.md file.
    """
    figure_path = state.get("generated_figure", "")
    if not figure_path:
        return state

    project_root = _find_project_root()
    coupler = InterpretativeCoupler(project_root)

    try:
        fig_path = Path(figure_path)
        if fig_path.exists():
            figure_type = state.get("figure_type", _infer_figure_type(fig_path.stem))
            stat_results = state.get("statistical_results", {})
            research_question = state.get("research_question", "")
            hypothesis = state.get("hypothesis", "")
            branch_id = state.get("active_branch", "main")

            interp_path = coupler.generate_interpretation(
                fig_path, figure_type, stat_results,
                research_question, hypothesis, branch_id,
            )
            state["interpretation_generated"] = str(interp_path)
            logger.info("Interpretation generated for: %s", figure_path)
        else:
            state["interpretation_error"] = f"Figure not found: {figure_path}"
    except Exception as e:
        state["interpretation_error"] = str(e)
        logger.error("Interpretation generation failed: %s", e)

    return state


def _infer_figure_type(stem: str) -> str:
    """Infer figure type from filename stem."""
    stem_lower = stem.lower()
    type_map = {
        "scatter": "scatter", "correlation": "scatter",
        "bar": "bar", "comparison": "bar",
        "line": "line", "trend": "line", "time_series": "line",
        "histogram": "histogram", "distribution": "histogram",
        "boxplot": "boxplot", "box": "boxplot",
        "heatmap": "heatmap", "matrix": "heatmap",
        "forest": "forest", "effect": "forest",
        "violin": "violin",
        "residual": "residual", "diagnostic": "residual",
    }
    for key, fig_type in type_map.items():
        if key in stem_lower:
            return fig_type
    return "unknown"


def _find_project_root() -> Path:
    p = Path.cwd()
    for _ in range(10):
        if (p / ".research").exists():
            return p
        if p.parent == p:
            break
        p = p.parent
    return Path.cwd()
