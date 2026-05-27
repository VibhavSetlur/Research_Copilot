"""Back-compat shim — moved into state/config.py."""

from research_os.tools.actions.state.config import (  # noqa: F401
    explain_config,
    get_config,
    init_config,
    set_config,
    validate_config,
)
