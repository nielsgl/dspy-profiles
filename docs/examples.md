# Examples

Run these examples with `dspy-run` (or the helper script `./run-examples.zsh`) to activate profiles without modifying the scripts. Most examples can also be executed directly with `uv run python …` when you want tighter control.

## Hello World

```python title="examples/hello_world.py"
--8<-- "examples/hello_world.py"
```

## Hello Runner

```python title="examples/hello_runner.py"
--8<-- "examples/hello_runner.py"
```

## More Samples

- `hello_decorator.py`: Applying `@with_profile` to a function (`uv run python examples/hello_decorator.py`)
- `decorator_usage.py`: Decorator-focused walkthrough (`uv run python examples/decorator_usage.py`)
- `multiple_profiles.py`: Switching profiles and printing the active one (requires `default` and `creative` profiles)
- `extended_profiles.py`: Profile inheritance using `extends` (expects `creative_child` extending `base_model`)
- `profile_overrides.py`: Overriding profile settings at runtime (`uv run python examples/profile_overrides.py`)
- `adaptive_agent.py`: Advanced agent pattern with runtime escalation (use `uv run dspy-run --profile creative_agent -- python examples/adaptive_agent.py`; also defines a `technical_agent` profile for task overrides)
- `retrieval_example.py`: Configuring and using a retrieval model via `rm.class_name` (needs a `search` profile with an `rm` section)
