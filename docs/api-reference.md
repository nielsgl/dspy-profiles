# API Reference

This section provides a detailed reference for the `dspy-profiles` Python API.

::: dspy_profiles

## Runtime Helpers

`lm(profile_name, **overrides)` returns a configured `dspy.LM` instance for the
given profile without entering a context manager. It supports caching and accepts
LM-specific overrides and an optional `config_path`.

Example

```python
from dspy_profiles import lm

# Get a cached LM instance for the profile
gpt = lm("default")

# Override temperature on the fly
creative = lm("default", temperature=0.9)

# Load from a specific profiles.toml if needed
custom = lm("default", config_path="/path/to/profiles.toml")
```
