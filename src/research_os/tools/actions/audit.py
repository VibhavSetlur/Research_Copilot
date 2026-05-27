"""Back-compat shim — moved into audit/audit.py."""

from research_os.tools.actions.audit.audit import (  # noqa: F401
    audit_assumptions,
    audit_citations,
    audit_figure,
    audit_power,
    audit_reproducibility_full,
    audit_synthesis,
    get_current_path,
)
