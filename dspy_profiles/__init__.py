"""dspy-profiles package."""

from .core import current_profile, lm, profile, with_profile

# Attempt to load IPython extension if in an IPython environment
try:
    from IPython.core.getipython import get_ipython

    if get_ipython() is not None:
        from . import ipython

        ipython.load_ipython_extension(get_ipython())
except (ImportError, ModuleNotFoundError):
    # IPython is not installed or not in an IPython environment
    pass

__all__ = ["profile", "with_profile", "current_profile", "lm"]
