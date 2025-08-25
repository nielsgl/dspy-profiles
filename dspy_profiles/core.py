import contextlib
from contextvars import ContextVar
import os

import dspy

from dspy_profiles.loader import ProfileLoader, ResolvedProfile

# Context variable to hold the currently active ResolvedProfile.
_CURRENT_PROFILE: ContextVar[ResolvedProfile | None] = ContextVar("current_profile", default=None)


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

    # Profile-aware caching
    # If cache_dir is not set in the profile, default to ~/.dspy/cache/<profile_name>
    if "settings" not in final_config:
        final_config["settings"] = {}
    if "cache_dir" not in final_config["settings"]:
        final_config["settings"]["cache_dir"] = os.path.expanduser(
            f"~/.dspy/cache/{loaded_profile.name}"
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
    # Ensure the profile-aware cache directory is part of the settings
    if "cache_dir" in final_config.get("settings", {}):
        settings["cache_dir"] = final_config["settings"]["cache_dir"]

    token = _CURRENT_PROFILE.set(resolved_profile)
    try:
        with dspy.context(lm=lm, rm=rm, **settings):
            # Also configure the cache_dir directly
            if "cache_dir" in settings:
                dspy.settings.configure(cache_dir=settings["cache_dir"])
            yield
    finally:
        _CURRENT_PROFILE.reset(token)


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


def current_profile() -> ResolvedProfile | None:
    """Returns the currently active profile, if any.

    This function provides an introspection utility to see the fully resolved
    settings of the profile that is currently active via the `profile`

    context manager or `@with_profile` decorator.

    Returns:
        The active ResolvedProfile, or None if no profile is active.
    """
    return _CURRENT_PROFILE.get()


_LM_CACHE = {}


def lm(profile_name: str, cached: bool = True, **overrides) -> dspy.LM | None:
    """Gets a pre-configured dspy.LM instance for a given profile.

    This is a convenience utility to quickly get a language model instance
    without needing the full context manager.

    Args:
        profile_name: The name of the profile to use.
        cached: If True, a cached LM instance will be returned if available.
                Set to False to force a new instance to be created.
        **overrides: Keyword arguments to override profile settings.

    Returns:
        A configured dspy.LM instance, or None if the profile has no LM.
    """
    cache_key = (profile_name, tuple(sorted(overrides.items())))

    if cached and cache_key in _LM_CACHE:
        return _LM_CACHE[cache_key]

    loader = ProfileLoader()
    loaded_profile = loader.get_config(profile_name)
    final_config = loaded_profile.config.copy()

    if overrides:
        # We need to be careful to merge the overrides into the 'lm' section
        # if they are LM-specific parameters. A simple heuristic is to assume
        # that any kwarg not in the other main sections is an LM parameter.
        known_sections = {"rm", "settings", "config_path"}
        lm_overrides = {k: v for k, v in overrides.items() if k not in known_sections}
        if lm_overrides:
            if "lm" not in final_config:
                final_config["lm"] = {}
            final_config["lm"] = _deep_merge(final_config["lm"], lm_overrides)

    lm_config = final_config.get("lm")
    if not lm_config:
        return None

    lm_config = lm_config.copy()
    model_name = lm_config.pop("model", None)
    provider = lm_config.pop("provider", None)

    lm_class = dspy.LM
    if provider:
        lm_class_name = provider.capitalize()
        lm_class = getattr(dspy, lm_class_name, dspy.LM)

    instance = lm_class(model=model_name, **lm_config) if model_name else dspy.LM(**lm_config)

    if cached:
        _LM_CACHE[cache_key] = instance

    return instance
