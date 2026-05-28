"""Publication-grade visualisation toolkit.

Most analysis scripts produce throw-away exploratory charts. The handful of
plots that make it into a paper, dashboard, or poster need to clear a much
higher bar — colour-blind safe palettes, journal-style typography, axis
units, error bars, accessible captions. This module provides:

* ``tool_figure_create`` (alias ``figure_create``) — declarative wrapper that
  reads a CSV/JSON table, applies a publication preset (Nature / IEEE /
  default), and writes the figure at both PNG (≥300 DPI) and SVG.
* ``tool_figure_palette`` — return the recommended palette for a given
  encoding (sequential / diverging / qualitative). Defaults: viridis,
  PuOr, Okabe-Ito (colour-blind safe).
* ``tool_figure_caption_synthesise`` — turn a technical caption + the
  step's findings into a 2-3 sentence plain-language sibling
  (``<name>.summary.md``) for W3C-style "long descriptions".
* ``tool_figure_audit_quality`` — beyond the existing DPI check: looks at
  palette, axis labels, units, error bars, font sizes.

The plotting library priority is **matplotlib + the Okabe-Ito / viridis
palette**, with SciencePlots styles applied when available (``science``,
``nature``, ``ieee``). Optional backends (plotnine, plotly, altair) are
detected at runtime; the wrapper gracefully degrades to matplotlib when
they are absent.
"""

from research_os.tools.actions.viz.dashboard_tests import (
    generate_dashboard_test_suite,
    run_dashboard_tests,
)
from research_os.tools.actions.viz.figures import (
    audit_figure_quality,
    caption_synthesise,
    figure_create,
    palette_for,
)

__all__ = [
    "audit_figure_quality",
    "caption_synthesise",
    "figure_create",
    "generate_dashboard_test_suite",
    "palette_for",
    "run_dashboard_tests",
]
