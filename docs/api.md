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
