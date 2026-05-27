"""Back-compat shim — moved into exec/scripts.py."""

from research_os.tools.actions.exec.scripts import (  # noqa: F401
    execute_bash_script,
    execute_julia_script,
    execute_r_script,
)
