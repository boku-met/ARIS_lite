"""Deprecation helpers for legacy ARIS-lite APIs and CLI entry points."""

from __future__ import annotations

import sys
import warnings

LEGACY_REMOVAL_VERSION = "0.4.0"


class ArisDeprecationWarning(FutureWarning):
    """Project-specific deprecation warning category."""


def _build_message(kind: str, old: str, new: str, removal_version: str) -> str:
    return (
        f"{kind} '{old}' is deprecated; use '{new}' instead. "
        f"It will be removed in {removal_version}."
    )


def warn_legacy_python_api(
    old: str,
    new: str,
    removal_version: str = LEGACY_REMOVAL_VERSION,
) -> str:
    """Emit a standardized deprecation warning for Python APIs."""
    message = _build_message("Python API", old, new, removal_version)
    warnings.warn(message, ArisDeprecationWarning, stacklevel=2)
    return message


def warn_legacy_cli(
    old: str,
    new: str,
    removal_version: str = LEGACY_REMOVAL_VERSION,
) -> str:
    """Emit a standardized deprecation warning for CLI entries."""
    message = _build_message("CLI entry", old, new, removal_version)
    print(f"WARNING: {message}", file=sys.stderr)
    warnings.warn(message, ArisDeprecationWarning, stacklevel=2)
    return message

