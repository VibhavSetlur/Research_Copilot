"""Smoke tests for the new viz renderers.

We don't validate pixel output — just that each registered chart kind
can be invoked end-to-end without raising and produces a PNG + caption
+ summary + provenance sidecar.
"""

from pathlib import Path

import pytest

from research_os.project_ops import (
    create_numbered_experiment,
    scaffold_minimal_workspace,
)

# Matplotlib is a viz prerequisite. Skip the whole module when absent
# so the test suite still runs on minimal environments.
try:
    import matplotlib  # noqa: F401

    HAS_MPL = True
except ImportError:
    HAS_MPL = False

pytestmark = pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")


@pytest.fixture
def step_root(tmp_path: Path):
    scaffold_minimal_workspace(tmp_path, project_name="V", git_init=False, ide_flags=[])
    create_numbered_experiment(tmp_path, "eda")
    return tmp_path


def _assert_outputs(res: dict, root: Path) -> None:
    assert res["status"] == "success", res
    assert res["figure_png"]
    assert (root / res["figure_png"]).exists()
    # caption + provenance sidecars
    assert (root / res["caption_path"]).exists()
    assert res.get("provenance_path")


def test_bar(step_root: Path):
    from research_os.tools.actions.viz import figure_create

    res = figure_create(
        root=step_root, step_id="01_eda", name="bar_x",
        kind="bar",
        data=[{"g": "A", "v": 10}, {"g": "B", "v": 14}, {"g": "C", "v": 7}],
        x="g", y="v",
    )
    _assert_outputs(res, step_root)


def test_line_with_color_by(step_root: Path):
    from research_os.tools.actions.viz import figure_create

    rows = [
        {"t": i, "y": i * 1.1, "site": "A"} for i in range(10)
    ] + [
        {"t": i, "y": i * 0.9 + 2, "site": "B"} for i in range(10)
    ]
    res = figure_create(
        root=step_root, step_id="01_eda", name="line_trend",
        kind="line", data=rows, x="t", y="y", color_by="site",
    )
    _assert_outputs(res, step_root)


def test_scatter_with_regression(step_root: Path):
    from research_os.tools.actions.viz import figure_create

    rows = [{"x": i, "y": i * 2 + (i % 3)} for i in range(40)]
    res = figure_create(
        root=step_root, step_id="01_eda", name="scatter_fit",
        kind="scatter", data=rows, x="x", y="y", regression=True,
    )
    _assert_outputs(res, step_root)


def test_hist(step_root: Path):
    from research_os.tools.actions.viz import figure_create

    rows = [{"v": (i * 7) % 23} for i in range(120)]
    res = figure_create(
        root=step_root, step_id="01_eda", name="hist_v",
        kind="hist", data=rows, x="v",
    )
    _assert_outputs(res, step_root)


def test_box(step_root: Path):
    from research_os.tools.actions.viz import figure_create

    rows = (
        [{"g": "A", "v": i} for i in range(10)]
        + [{"g": "B", "v": 2 * i} for i in range(10)]
    )
    res = figure_create(
        root=step_root, step_id="01_eda", name="box_v",
        kind="box", data=rows, x="g", y="v",
    )
    _assert_outputs(res, step_root)


def test_forest(step_root: Path):
    from research_os.tools.actions.viz import figure_create

    rows = [
        {"label": "S1", "effect": 0.5, "ci_lo": 0.1, "ci_hi": 0.9},
        {"label": "S2", "effect": 0.2, "ci_lo": -0.1, "ci_hi": 0.5},
        {"label": "S3", "effect": 0.7, "ci_lo": 0.4, "ci_hi": 1.0},
    ]
    res = figure_create(
        root=step_root, step_id="01_eda", name="forest_meta",
        kind="forest", data=rows, x="label", y="effect",
    )
    _assert_outputs(res, step_root)


def test_ridgeline(step_root: Path):
    from research_os.tools.actions.viz import figure_create

    rows = (
        [{"g": "A", "v": (i * 7) % 50} for i in range(80)]
        + [{"g": "B", "v": ((i * 3) + 10) % 50} for i in range(80)]
    )
    res = figure_create(
        root=step_root, step_id="01_eda", name="ridge_v",
        kind="ridgeline", data=rows, x="g", y="v",
    )
    _assert_outputs(res, step_root)


def test_hexbin(step_root: Path):
    from research_os.tools.actions.viz import figure_create

    rows = [{"x": i, "y": (i * 7) % 50} for i in range(200)]
    res = figure_create(
        root=step_root, step_id="01_eda", name="hexbin_xy",
        kind="hexbin", data=rows, x="x", y="y",
    )
    _assert_outputs(res, step_root)
