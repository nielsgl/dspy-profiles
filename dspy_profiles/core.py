from collections.abc import Callable, Generator
import contextlib
from contextvars import ContextVar
from functools import wraps
import inspect
import os
from typing import Any

import dspy

from dspy_profiles.loader import ProfileLoader, ResolvedProfile

_CURRENT_PROFILE: ContextVar[ResolvedProfile | None] = ContextVar("current_profile", default=None)


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
    profile_to_load = profile_name if force or not env_profile else env_profile or "default"

    if not profile_to_load:
        yield
        return

    loader = ProfileLoader(config_path=config_path) if config_path else ProfileLoader()
    loaded_profile = loader.get_config(profile_to_load)
    # print(f"DEBUG: Loaded profile config: {loaded_profile.config}")
    print(f"[DEBUG] Initial loaded_profile.config: {loaded_profile.config}")
    print(f"[DEBUG] Overrides received: {overrides}")
    final_config = _deep_merge(loaded_profile.config, overrides)
    print(f"[DEBUG] final_config after merge: {final_config}")
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
        print(f"[DEBUG] resolved_profile.lm is type: {type(resolved_profile.lm)}")
        if isinstance(resolved_profile.lm, dspy.LM):
            print("[DEBUG] resolved_profile.lm is a dspy.LM instance. Using it directly.")
            lm_instance = resolved_profile.lm
        else:
            print("[DEBUG] resolved_profile.lm is a dict. Instantiating new LM.")
            lm_config = resolved_profile.lm.copy()
            model = lm_config.pop("model", None)
            provider = lm_config.pop("provider", "openai").capitalize()
            lm_class = getattr(dspy, provider, dspy.LM)
            lm_instance = lm_class(model=model, **lm_config) if model else dspy.LM(**lm_config)
        print(f"[DEBUG] lm_instance created: {lm_instance}")

    if resolved_profile.rm:
        rm_config = resolved_profile.rm.copy()
        provider = rm_config.pop("provider", "ColBERTv2")
        # Fallback for legacy dspy versions might be needed if RM names change.
        rm_class = getattr(dspy, provider, dspy.ColBERTv2)
        rm_instance = rm_class(**rm_config)

    token = _CURRENT_PROFILE.set(resolved_profile)
    try:
        # print(
        #     f"DEBUG: Configuring dspy.context with lm={lm_instance},"
        #     f"rm={rm_instance}, settings={settings}"
        # )
        dspy_settings = settings.copy()
        if resolved_profile.lm and isinstance(resolved_profile.lm, dict):
            dspy_settings.update(resolved_profile.lm)

        dspy.settings.configure(**dspy_settings)

        print(f"[DEBUG] Entering dspy.context with lm_instance: {lm_instance}")
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


def lm(profile_name: str, cached: bool = True, **overrides: Any) -> dspy.LM | None:
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
    print(f"\n[DEBUG] lm(profile_name='{profile_name}', cached={cached}, overrides={overrides})")

    # Separate LM-specific overrides from other function kwargs like 'config_path'
    known_non_lm_kwargs = {"config_path"}
    lm_overrides = {k: v for k, v in overrides.items() if k not in known_non_lm_kwargs}
    print(f"[DEBUG] Separated lm_overrides: {lm_overrides}")

    cache_key = (profile_name, tuple(sorted(lm_overrides.items())))
    print(f"[DEBUG] Generated cache_key: {cache_key}")
    if cached and cache_key in _LM_CACHE:
        print(f"[DEBUG] Cache hit. Returning cached instance for key: {cache_key}")
        return _LM_CACHE[cache_key]
    print("[DEBUG] Cache miss. Proceeding to create new LM instance.")

    loader = ProfileLoader()
    loaded_profile = loader.get_config(profile_name)
    print(f"[DEBUG] Loaded profile '{loaded_profile.name}' with config: {loaded_profile.config}")
    final_config = loaded_profile.config.copy()

    if lm_overrides:
        print("[DEBUG] Overrides detected. Merging lm_overrides into config...")
        lm_config_before_merge = final_config.get("lm", {}).copy()
        print(f"[DEBUG] lm_config before merge: {lm_config_before_merge}")
        lm_config = final_config.setdefault("lm", {})
        final_config["lm"] = _deep_merge(lm_config, lm_overrides)
        print(f"[DEBUG] lm_config after merge: {final_config.get('lm')}")

    lm_config = final_config.get("lm")
    if not lm_config:
        print("[DEBUG] No lm_config found after processing. Returning None.")
        return None
    print(f"[DEBUG] Final lm_config to be used for instantiation: {lm_config}")

    lm_config = lm_config.copy()
    model = lm_config.pop("model", None)
    provider = lm_config.pop("provider", "openai").capitalize()
    lm_class = getattr(dspy, provider, dspy.LM)
    print(
        f"[DEBUG] Preparing to instantiate lm_class '{lm_class.__name__}' "
        f"with model='{model}' and kwargs={lm_config}"
    )

    instance = lm_class(model=model, **lm_config)
    print(f"[DEBUG] Instantiated LM: {instance}")
    print(f"[DEBUG] Instantiated LM kwargs: {getattr(instance, 'kwargs', 'N/A')}")

    if cached:
        _LM_CACHE[cache_key] = instance

    return instance
