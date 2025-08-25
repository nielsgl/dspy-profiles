import contextlib
import os

import dspy

from dspy_profiles.loader import ProfileLoader, ResolvedProfile


def _deep_merge(parent: dict, child: dict) -> dict:
    """Recursively merges two dictionaries. Child values override parent values."""
    merged = parent.copy()
    for key, value in child.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


@contextlib.contextmanager
def profile(profile_name: str | None = None, *, force: bool = False, config_path=None, **overrides):
    """A context manager to temporarily apply a dspy-profiles configuration.
    Args:
        profile_name: The name of the profile to activate.
        force: If True, this profile will override any profile set via
               the DSPY_PROFILE environment variable.
        config_path: Path to the profiles.toml file. If None, uses the default path.
        **overrides: Keyword arguments to override profile settings (e.g., lm, rm).
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
    loaded_profile = loader.get_config(profile_to_load)

    # Apply inline overrides
    final_config = loaded_profile.config.copy()
    if overrides:
        final_config = _deep_merge(final_config, overrides)

    resolved_profile = ResolvedProfile(
        name=loaded_profile.name,
        config=final_config,
        lm=final_config.get("lm"),
        rm=final_config.get("rm"),
        settings=final_config.get("settings"),
    )

    lm = None
    if resolved_profile.lm:
        lm_config = resolved_profile.lm.copy()
        model_name = lm_config.pop("model", None)
        # DSPy expects the provider to be part of the model name if not openai
        # but we handle that in the profile. Let's be robust.
        provider = lm_config.pop("provider", None)
        if provider and provider != "openai" and model_name and provider not in model_name:
            # Simple heuristic, may need refinement
            pass  # For now, assume model name is correct

        # Dynamically find the correct LM class if specified
        lm_class = dspy.LM
        if provider:
            lm_class_name = provider.capitalize()
            lm_class = getattr(dspy, lm_class_name, dspy.LM)

        lm = lm_class(model=model_name, **lm_config) if model_name else dspy.LM(**lm_config)

    rm = None
    if resolved_profile.rm:
        # A simple heuristic to select RM class. Can be expanded.
        rm_model_name = resolved_profile.rm.get("model", "").lower()
        rm_class = dspy.ColBERTv2
        if "rag" in rm_model_name:
            # This is a placeholder for more advanced RM selection.
            # For now, we default to ColBERTv2 as it's the most common.
            rm_class = dspy.ColBERTv2
        rm = rm_class(**resolved_profile.rm)

    settings = resolved_profile.settings or {}
    with dspy.context(lm=lm, rm=rm, **settings):
        yield


def with_profile(profile_name: str, *, force: bool = False, config_path=None, **overrides):
    """A decorator to apply a dspy-profiles configuration to a function.
    Args:
        profile_name: The name of the profile to activate.
        force: If True, this profile will override any profile set via
               the DSPY_PROFILE environment variable.
        config_path: Path to the profiles.toml file. If None, uses the default path.
        **overrides: Keyword arguments to override profile settings.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Overrides from the decorator can be further overridden by kwargs
            # passed to the decorated function.
            final_overrides = overrides.copy()
            # A bit of a hack to separate profile kwargs from function kwargs
            profile_keys = {"lm", "rm", "settings"}
            func_overrides = {k: v for k, v in kwargs.items() if k in profile_keys}
            func_args = {k: v for k, v in kwargs.items() if k not in profile_keys}

            if func_overrides:
                final_overrides = _deep_merge(final_overrides, func_overrides)

            with profile(profile_name, force=force, config_path=config_path, **final_overrides):
                return func(*args, **func_args)

        return wrapper

    return decorator
