# API Reference

This section provides a detailed reference for the `dspy-profiles` Python API.

## Usage Examples

```python title="Activate a profile"
from dspy_profiles import profile

with profile("prod"):
    predictor = dspy.Predict("question -> answer")
    result = predictor(question="What is the latest build status?")
```

```python title="Decorate a function"
from dspy_profiles import with_profile

@with_profile("staging", settings={"cache_dir": ".cache/staging"})
def run_evaluation(prompt: str) -> str:
    return dspy.Predict("prompt -> answer")(prompt=prompt).answer
```

```python title="Inspect the active profile"
from dspy_profiles import current_profile, profile

with profile("analysis"):
    active = current_profile()
    assert active and active.name == "analysis"
```

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
