# API Reference

This page provides a detailed reference for the `dspy-profiles` Python API.

## `profile` Context Manager

The `profile` context manager is the primary way to activate a profile for a specific block of code.

```python
from dspy_profiles import profile

with profile(profile_name: str | None = None, *, force: bool = False, config_path=None):
    ...
```

### Parameters

-   **`profile_name` (str | None)**: The name of the profile to activate. If `None`, the manager will fall back to the `DSPY_PROFILE` environment variable, and then to the `default` profile.
-   **`force` (bool)**: If `True`, the specified `profile_name` will be activated even if the `DSPY_PROFILE` environment variable is set. This allows code to explicitly override the environment's configuration. Defaults to `False`.
-   **`config_path` (str | Path | None)**: An optional path to a `profiles.toml` file. If `None`, the default path (`~/.dspy/profiles.toml`) is used. This is primarily useful for testing.

### Activation Logic

The context manager follows a strict precedence order to determine which profile to activate:
1.  If `force=True`, the `profile_name` passed to the function is used.
2.  Otherwise, if the `DSPY_PROFILE` environment variable is set, its value is used.
3.  Otherwise, the `profile_name` passed to the function is used.
4.  If `profile_name` is `None`, it falls back to the `default` profile.

### Example

```python
import dspy
from dspy_profiles import profile

# This block will use the 'prod' profile
with profile("prod"):
    # DSPy calls inside this block will use the 'prod' configuration
    response = dspy.Predict("Question -> Answer")("What is the capital of France?")
```

## `@with_profile` Decorator

The `@with_profile` decorator applies a profile to an entire function. It is a convenient wrapper around the context manager.

```python
from dspy_profiles import with_profile

@with_profile(profile_name: str, *, force: bool = False, config_path=None)
def my_function():
    ...
```

### Parameters

The decorator accepts the exact same parameters as the `profile` context manager.

### Example

```python
import dspy
from dspy_profiles import with_profile

@with_profile("testing")
def run_test_prediction():
    predictor = dspy.Predict("question -> answer")
    return predictor(question="What is 2+2?")

# The 'testing' profile is active only for the duration of this function call
result = run_test_prediction()
```


## `current_profile`

A utility function to inspect the currently active profile.

```python
from dspy_profiles import current_profile

profile = current_profile()
```

### Return Value

-   **`ResolvedProfile` (object | None)**: Returns the `ResolvedProfile` object for the currently active profile. This object contains the profile's name and its fully resolved configuration, including any applied overrides. If no profile is active, it returns `None`.

### Example

```python
from dspy_profiles import profile, current_profile

with profile("staging", temperature=0.9):
    active_profile = current_profile()
    if active_profile:
        print(f"Active Profile: {active_profile.name}")
        print(f"Resolved LM Config: {active_profile.config['lm']}")

# Outside the context, this will print None
print(current_profile())
```


## `lm`

A shortcut function to get a pre-configured `dspy.LM` instance for a specific profile.

```python
from dspy_profiles import lm

lm_instance = lm(profile_name: str, cached: bool = True, **overrides)
```

### Parameters

-   **`profile_name` (str)**: The name of the profile to use.
-   **`cached` (bool)**: If `True` (the default), a cached LM instance will be returned if available. Set to `False` to force a new instance to be created.
-   **`**overrides`**: Keyword arguments to override any settings in the profile's `lm` section (e.g., `temperature=0.9`).

### Return Value

-   **`dspy.LM` (object | None)**: Returns a configured `dspy.LM` instance, or `None` if the profile does not have an `lm` section.

### Example

```python
from dspy_profiles import lm

# Get a cached LM instance for the 'prod' profile
prod_lm = lm("prod")

# Get a new, non-cached instance with a custom temperature
staging_lm = lm("staging", cached=False, temperature=0.8)
```
