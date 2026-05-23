from pathlib import Path
from typing import Optional


class DashboardCompiler:
    """Ephemeral UI Visualization Artifacts.

    Compiles self-contained JSON payloads or static HTML from Plotly/Altair.
    Allows IDE-native rendering via MCP resources/read protocol without
    the need for persistent background web servers.
    """

    def __init__(self, root: Optional[Path] = None):
        from research_os.utils.common import find_project_root

        self.root = root or find_project_root()

    def compile_dashboard(
        self,
        dashboard_id: str,
        load_data_code: str = "pass",
        metrics_code: str = "pass",
        charts_code: str = "pass",
    ) -> Path:
        """Inject LLM-generated components into the predefined beautifully CSS-styled template.

        Args:
            dashboard_id: Unique identifier for this dashboard.
            load_data_code: Python code string to inject into load_data()
            metrics_code: Python code string to inject into render_metrics()
            charts_code: Python code string to inject into render_charts()

        Returns:
            Path to the saved Streamlit dashboard script.
        """
        template_path = (
            Path(__file__).parent.parent.parent / "core" / "dashboard_template.py"
        )

        if not template_path.exists():
            raise FileNotFoundError(f"Dashboard template not found at {template_path}")

        template = template_path.read_text()

        # Inject the components
        template = template.replace(
            "def load_data():\n    # LLM-injected slot for data loading\n    pass",
            f"def load_data():\n    # LLM-injected slot for data loading\n    {load_data_code}",
        )
        template = template.replace(
            "def render_metrics():\n    # LLM-injected slot for top level metrics\n    pass",
            f"def render_metrics():\n    # LLM-injected slot for top level metrics\n    {metrics_code}",
        )
        template = template.replace(
            "def render_charts():\n    # LLM-injected slot for charts\n    pass",
            f"def render_charts():\n    # LLM-injected slot for charts\n    {charts_code}",
        )

        out_dir = self.root / "workspace" / "dashboards"
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = out_dir / f"{dashboard_id}_dashboard.py"
        out_path.write_text(template)

        return out_path
