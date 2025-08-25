import contextlib

import dspy

from dspy_profiles.loader import ProfileLoader


@contextlib.contextmanager
def profile(profile_name: str):
    """A context manager to temporarily apply a dspy-profiles configuration.

    Args:
        profile_name: The name of the profile to activate.
    """
    loader = ProfileLoader()
    resolved_profile = loader.get_config(profile_name)

    lm = None
    if resolved_profile.lm:
        lm = dspy.LM(**resolved_profile.lm)

    rm = None
    if resolved_profile.rm:
        rm = dspy.ColBERTv2(**resolved_profile.rm)

    settings = resolved_profile.settings or {}
    with dspy.context(lm=lm, rm=rm, **settings):
        yield


def with_profile(profile_name: str):
    """A decorator to apply a dspy-profiles configuration to a function.

    Args:
        profile_name: The name of the profile to activate.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            with profile(profile_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator
