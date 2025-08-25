# API Reference

This page provides a detailed reference for the `dspy-profiles` Python API.

## `profile` Context Manager

```python
with profile(profile_name: str, force: bool = False, **overrides)
```

**Parameters:**

*   **`profile_name` (str)**: The name of the profile to activate.
*   **`force` (bool)**: If `True`, this profile will override the `DSPY_PROFILE` environment variable. Defaults to `False`.
*   **`**overrides`**: Keyword arguments to dynamically override settings from the loaded profile.

## `@with_profile` Decorator

```python
@with_profile(profile_name: str, force: bool = False, **overrides)
```

**Parameters:**

*   **`profile_name` (str)**: The name of the profile to activate for the decorated function.
*   **`force` (bool)**: If `True`, this profile will override the `DSPY_PROFILE` environment variable. Defaults to `False`.
*   **`**overrides`**: Keyword arguments to dynamically override settings from the loaded profile.

*(More API documentation will be added here)*
