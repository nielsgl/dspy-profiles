"""dspy-profiles package."""

import importlib.metadata

from .core import current_profile, profile, with_profile

try:
    __version__ = importlib.metadata.version("dspy-profiles")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


__all__ = ["profile", "with_profile", "current_profile"]
