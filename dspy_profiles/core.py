import contextlib
import os

import dspy

from dspy_profiles.loader import ProfileLoader


@contextlib.contextmanager
def profile(profile_name: str | None = None, *, force: bool = False, config_path=None):
    """A context manager to temporarily apply a dspy-profiles configuration.
    Args:
        profile_name: The name of the profile to activate.
        force: If True, this profile will override any profile set via
               the DSPY_PROFILE environment variable.
        config_path: Path to the profiles.toml file. If None, uses the default path.
    """
    env_profile = os.getenv("DSPY_PROFILE")
    profile_to_load = None

    if force:
        profile_to_load = profile_name
    elif env_profile:
        profile_to_load = env_profile
    elif profile_name:
        profile_to_load = profile_name
    else:
        profile_to_load = "default"

    if not profile_to_load:
        yield
        return

    loader = ProfileLoader(config_path=config_path) if config_path else ProfileLoader()
    resolved_profile = loader.get_config(profile_to_load)

    lm = None
    if resolved_profile.lm:
        lm_config = resolved_profile.lm.copy()
        model_name = lm_config.pop("model", None)
        lm = dspy.LM(model_name, **lm_config)

    rm = None
    if resolved_profile.rm:
        rm = dspy.ColBERTv2(**resolved_profile.rm)

    settings = resolved_profile.settings or {}
    with dspy.context(lm=lm, rm=rm, **settings):
        yield


def with_profile(profile_name: str, *, force: bool = False, config_path=None):
    """A decorator to apply a dspy-profiles configuration to a function.
    Args:
        profile_name: The name of the profile to activate.
        force: If True, this profile will override any profile set via
               the DSPY_PROFILE environment variable.
        config_path: Path to the profiles.toml file. If None, uses the default path.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            with profile(profile_name, force=force, config_path=config_path):
                return func(*args, **kwargs)

        return wrapper

    return decorator
