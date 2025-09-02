from collections.abc import Callable, Generator
import contextlib
from contextvars import ContextVar
from functools import wraps
import importlib
import inspect
import logging
import os
from typing import Any

import dspy

from dspy_profiles.loader import ProfileLoader, ResolvedProfile

_CURRENT_PROFILE: ContextVar[ResolvedProfile | None] = ContextVar("current_profile", default=None)
logger = logging.getLogger(__name__)


def _deep_merge(parent: dict, child: dict) -> dict:
    """Recursively merges two dictionaries, with child values overriding parent values."""
    merged = parent.copy()
    for key, value in child.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


@contextlib.contextmanager
def profile(
    profile_name: str | None = None,
    *,
    force: bool = False,
    config_path: str | None = None,
    **overrides: Any,
) -> Generator[None, None, None]:
    """A context manager to temporarily apply a dspy-profiles configuration.

    This context manager activates a specified profile, configuring `dspy.settings`
    with the language model (LM), retrieval model (RM), and other settings defined
    in the profile. It also handles profile precedence and allows for inline overrides.

    Args:
        profile_name (str | None, optional): The name of the profile to activate. If not
            provided, it falls back to the `DSPY_PROFILE` environment variable, and then
            to "default". Defaults to None.
        force (bool, optional): If True, this profile will override any profile set via
            the `DSPY_PROFILE` environment variable. Defaults to False.
        config_path (str | None, optional): Path to the `profiles.toml` file. If None,
            uses the default search paths. Defaults to None.
        **overrides: Keyword arguments to override profile settings (e.g., `lm`, `rm`).
            These are deeply merged into the loaded profile's configuration.

    Yields:
        None: The context manager does not yield a value.

    Example:
        ```python
        with dspy_profiles.profile("my-profile", lm={"temperature": 0.7}):
            # DSPy calls within this block will use 'my-profile' with overridden temperature.
            response = dspy.Predict("question -> answer")("What is DSPy?")
        ```
    """
    env_profile = os.getenv("DSPY_PROFILE")
    if env_profile and not force:
        profile_to_load = env_profile
    else:
        profile_to_load = profile_name or "default"
    logger.debug(
        "Activating profile=%s (env_var=%s, force=%s, config_path=%s, overrides_keys=%s)",
        profile_to_load,
        bool(env_profile),
        force,
        config_path,
        list(overrides.keys()),
    )

    loader = ProfileLoader(config_path=config_path) if config_path else ProfileLoader()
    loaded_profile = loader.get_config(profile_to_load)
    final_config = _deep_merge(loaded_profile.config, overrides)
    logger.debug(
        "Resolved config sections: lm=%s rm=%s settings=%s",
        "yes" if final_config.get("lm") else "no",
        "yes" if final_config.get("rm") else "no",
        "yes" if final_config.get("settings") else "no",
    )
    resolved_profile = ResolvedProfile(
        name=loaded_profile.name,
        config=final_config,
        lm=final_config.get("lm"),
        rm=final_config.get("rm"),
        settings=final_config.get("settings"),
    )

    # Profile-aware caching setup
    settings = final_config.setdefault("settings", {})
    if "cache_dir" not in settings:
        settings["cache_dir"] = os.path.expanduser(f"~/.dspy/cache/{loaded_profile.name}")

    lm_instance, rm_instance = None, None
    if resolved_profile.lm:
        if isinstance(resolved_profile.lm, dspy.LM):
            lm_instance = resolved_profile.lm
        else:
            lm_config = resolved_profile.lm.copy()
            model = lm_config.pop("model", None)
            # Use unified LM instantiation
            lm_instance = dspy.LM(model=model, **lm_config) if model else dspy.LM(**lm_config)
            logger.debug("Instantiated LM for model=%s", model)

    if resolved_profile.rm:
        rm_config = resolved_profile.rm.copy()
        rm_class = None

        class_name = rm_config.pop("class_name", None)
        if class_name:
            try:
                if class_name.startswith("dspy."):
                    cls_name = class_name.split(".", 1)[1]
                    rm_class = getattr(dspy, cls_name, None)
                elif "." in class_name:
                    module_path, _, clsname = class_name.rpartition(".")
                    module = importlib.import_module(module_path)
                    rm_class = getattr(module, clsname, None)
                else:
                    rm_class = getattr(dspy, class_name, None)
            except Exception as e:  # pragma: no cover
                logger.debug("Failed to resolve RM class '%s': %s", class_name, e)

        if rm_class is None:
            provider = rm_config.pop("provider", "ColBERTv2")
            rm_class = getattr(dspy, provider, dspy.ColBERTv2)
            logger.debug("Instantiated RM via provider=%s", provider)
        else:
            logger.debug("Instantiated RM via class_name=%s", class_name)

        rm_instance = rm_class(**rm_config)

    token = _CURRENT_PROFILE.set(resolved_profile)
    try:
        # Configure only DSPy settings (not LM dict keys)
        dspy.settings.configure(**settings)
        logger.debug(
            "Entering dspy.context (lm=%s, rm=%s, settings_keys=%s)",
            type(lm_instance).__name__ if lm_instance else None,
            type(rm_instance).__name__ if rm_instance else None,
            list(settings.keys()),
        )
        with dspy.context(lm=lm_instance, rm=rm_instance, **settings):
            yield
    finally:
        _CURRENT_PROFILE.reset(token)


def with_profile(
    profile_name: str, *, force: bool = False, config_path: str | None = None, **overrides: Any
) -> Callable:
    """A decorator to apply a dspy-profiles configuration to a function or dspy.Module.

    This decorator wraps a function or a `dspy.Module` class, activating the
    specified profile before the decorated object is called.

    When applied to a function, it wraps the function directly. When applied to a
    class (like a `dspy.Module`), it wraps the `__call__` method, ensuring the
    profile is active during its execution.

    Args:
        profile_name (str): The name of the profile to activate.
        force (bool, optional): If True, this profile will override any profile set via
            the `DSPY_PROFILE` environment variable. Defaults to False.
        config_path (str | None, optional): Path to the `profiles.toml` file.
            Defaults to None.
        **overrides: Keyword arguments to override profile settings.

    Returns:
        Callable: The decorated function or class.

    Example (Function):
        ```python
        @dspy_profiles.with_profile("testing", temperature=0)
        def my_dspy_program(question):
            return dspy.Predict("question -> answer")(question=question)
        ```

    Example (dspy.Module):
        ```python
        @dspy_profiles.with_profile("agent-profile")
        class MyAgent(dspy.Module):
            def __init__(self):
                super().__init__()
                self.predict = dspy.Predict("question -> answer")

            def __call__(self, question):
                return self.predict(question=question)
        ```"""

    def decorator(target: Callable) -> Callable:
        # This is the wrapper that will be applied to the function or __call__ method.
        def profile_wrapper(func_to_wrap: Callable) -> Callable:
            @wraps(func_to_wrap)
            def wrapper(*args, **kwargs):
                final_overrides = overrides.copy()
                profile_keys = {"lm", "rm", "settings"}
                func_overrides = {k: v for k, v in kwargs.items() if k in profile_keys}
                func_args = {k: v for k, v in kwargs.items() if k not in profile_keys}

                if func_overrides:
                    final_overrides = _deep_merge(final_overrides, func_overrides)

                with profile(profile_name, force=force, config_path=config_path, **final_overrides):
                    return func_to_wrap(*args, **func_args)

            return wrapper

        # Check if the target is a class or a function/method
        if inspect.isclass(target):
            # It's a class, so we need to wrap its __call__ method.
            original_call = target.__call__
            target.__call__ = profile_wrapper(original_call)
            return target
        # It's a function, wrap it directly.
        return profile_wrapper(target)

    return decorator


def current_profile() -> ResolvedProfile | None:
    """Returns the currently active `dspy-profiles` profile.

    This utility function provides introspection to see the fully resolved settings
    of the profile that is currently active via the `profile` context manager
    or `@with_profile` decorator.

    Returns:
        ResolvedProfile | None: The active ResolvedProfile, or None if no profile is active.
    """
    return _CURRENT_PROFILE.get()


_LM_CACHE: dict[tuple, dspy.LM] = {}


def lm(
    profile_name: str,
    cached: bool = True,
    config_path: str | os.PathLike | None = None,
    **overrides: Any,
) -> dspy.LM | None:
    """Gets a pre-configured `dspy.LM` instance for a given profile.

    This is a convenience utility to quickly get a language model instance
    without needing the full context manager. It's useful for lightweight tasks
    or when you need an LM instance outside of a DSPy program flow.

    Args:
        profile_name (str): The name of the profile to use.
        cached (bool, optional): If True, a cached LM instance will be returned if
            available. Set to False to force a new instance to be created.
            Defaults to True.
        **overrides: Keyword arguments to override profile settings for the LM.

    Returns:
        dspy.LM | None: A configured `dspy.LM` instance, or None if the profile
            has no language model configured.
    """
    # Separate LM-specific overrides from other function kwargs like 'config_path'
    known_non_lm_kwargs = {"config_path"}
    lm_overrides = {k: v for k, v in overrides.items() if k not in known_non_lm_kwargs}
    logger.debug(
        "lm() requested for profile=%s cached=%s override_keys=%s config_path=%s",
        profile_name,
        cached,
        list(lm_overrides.keys()),
        config_path,
    )

    cache_key = (profile_name, tuple(sorted(lm_overrides.items())))
    if cached and cache_key in _LM_CACHE:
        return _LM_CACHE[cache_key]

    loader = ProfileLoader(config_path=config_path) if config_path else ProfileLoader()
    loaded_profile = loader.get_config(profile_name)
    final_config = loaded_profile.config.copy()

    if lm_overrides:
        lm_config = final_config.setdefault("lm", {})
        final_config["lm"] = _deep_merge(lm_config, lm_overrides)

    lm_config = final_config.get("lm")
    if not lm_config:
        return None

    lm_config = lm_config.copy()
    model = lm_config.pop("model", None)
    instance = dspy.LM(model=model, **lm_config)
    logger.debug("lm() instantiated LM for model=%s", model)

    if cached:
        _LM_CACHE[cache_key] = instance

    return instance
