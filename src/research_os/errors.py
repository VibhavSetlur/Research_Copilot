"""Research OS custom exceptions."""

from pathlib import Path


class WriteProtectedError(Exception):
    """Raised when a tool attempts to write to a protected directory.

    Currently enforced for:
      - inputs/        (immutable original data)
      - .os_state/     (internal OS state, should not be manually modified)
    """

    def __init__(self, path: Path | str, message: str = ""):
        self.path = str(path)
        default = (
            f"Write protection violation: '{self.path}' is read-only. "
            "The `inputs/` directory contains immutable original data "
            "and must never be modified by tools.  Write to `workspace/` instead."
        )
        super().__init__(message or default)


PROTECTED_DIRECTORIES = {"inputs", ".os_state"}


def check_write_permitted(target_path: str | Path) -> None:
    """Raise WriteProtectedError if *target_path* falls under a protected root."""
    p = Path(target_path).resolve()
    for part in p.parts:
        if part in PROTECTED_DIRECTORIES:
            raise WriteProtectedError(p)
