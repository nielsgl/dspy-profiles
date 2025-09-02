"""Logging utilities for dspy-profiles.

Library modules emit logs via module loggers. CLI entrypoints control
verbosity and formatting by configuring the root logger.
"""

from __future__ import annotations

import logging
import os


def compute_level(verbose: int = 0, quiet: int = 0, log_level: str | None = None) -> int:
    """Compute the effective logging level from CLI flags and env.

    Priority: explicit --log-level > DSPY_PROFILES_LOG_LEVEL > -q/-v flags.
    """
    if log_level:
        return getattr(logging, log_level.upper(), logging.INFO)

    env_level = os.getenv("DSPY_PROFILES_LOG_LEVEL")
    if env_level:
        return getattr(logging, env_level.upper(), logging.INFO)

    # Base WARNING; -v => INFO, -vv => DEBUG; -q => ERROR
    level = logging.WARNING
    if quiet >= 1:
        level = logging.ERROR
    if verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    return level


def setup_logging(level: int) -> None:
    """Configure the root logger once with a simple stderr handler.

    Safe to call multiple times; it won't duplicate handlers.
    """
    root = logging.getLogger()
    if not root.handlers:  # pragma: no cover
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        root.addHandler(handler)
    root.setLevel(level)
