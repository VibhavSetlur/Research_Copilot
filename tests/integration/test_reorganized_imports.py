"""Verify both the new subfolder layout and the back-compat shims work."""


def test_new_layout_imports():
    """The new subfolder layout exposes everything cleanly."""
    from research_os.tools.actions.state import config, path, checkpoint
    from research_os.tools.actions.data import data, intake, profiling
    from research_os.tools.actions.exec import scripts, notebook, tasks, environment
    from research_os.tools.actions.search import search, literature
    from research_os.tools.actions.research import research, planning
    from research_os.tools.actions.audit import audit, md_audit
    from research_os.tools.actions.synthesis import synthesize, latex, citations
    from research_os.tools.actions.memory import memory

    assert callable(config.get_config)
    assert callable(planning.plan_next_step)
    assert callable(citations.collect_for_section)
    assert callable(scripts.execute_r_script)
    assert callable(notebook.execute_notebook)
    assert callable(tasks.task_run)
    assert callable(intake.intake_autofill)


def test_backcompat_shims_resolve():
    """Old imports keep working after the reorganization."""
    from research_os.tools.actions.config import get_config            # noqa: F401
    from research_os.tools.actions.checkpoint import create_checkpoint  # noqa: F401
    from research_os.tools.actions.path import create_path              # noqa: F401
    from research_os.tools.actions.interaction import session_handoff   # noqa: F401
    from research_os.tools.actions.data import data_profile              # noqa: F401
    from research_os.tools.actions.intake import intake_autofill         # noqa: F401
    from research_os.tools.actions.profiling import _profile_inputs       # noqa: F401
    from research_os.tools.actions.web_search import search_web          # noqa: F401
    from research_os.tools.actions.literature_retrieval import (         # noqa: F401
        search_semantic_scholar,
    )
    from research_os.tools.actions.search import search_arxiv             # noqa: F401
    from research_os.tools.actions.research import research_method        # noqa: F401
    from research_os.tools.actions.audit import audit_synthesis           # noqa: F401
    from research_os.tools.actions.md_audit import validate_md_template   # noqa: F401
    from research_os.tools.actions.environment import env_snapshot        # noqa: F401
    from research_os.tools.actions.execution import execute_r_script      # noqa: F401
    from research_os.tools.actions.notebook import execute_notebook       # noqa: F401
    from research_os.tools.actions.tasks import task_run                  # noqa: F401
    from research_os.tools.actions.synthesize import synthesize_workspace  # noqa: F401
    from research_os.tools.actions.latex import latex_compile             # noqa: F401
    from research_os.tools.actions.memory import hypothesis_add           # noqa: F401
