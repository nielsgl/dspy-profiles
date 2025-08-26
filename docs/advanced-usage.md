# Advanced Usage

This section covers more advanced features and use cases for `dspy-profiles`.

## Complex Profile Examples

While the `init` command is great for getting started, your `profiles.toml` file can grow to handle much more complex scenarios.

### Configuring Different LMs

You can configure any language model that DSPy supports. Here's an example of configuring a local Ollama model:

```toml title="~/.dspy/profiles.toml"
[local_mistral]
[local_mistral.lm]
class_name = "dspy.OllamaLocal"
model = "mistral"
max_tokens = 4096
```

### Configuring Retrieval Models

Configuring a retrieval model like `ColBERTv2` is just as easy. This is where profiles become incredibly powerful, as you can switch your entire retrieval backend with a single word.

```toml title="~/.dspy/profiles.toml"
[dev_retrieval]
[dev_retrieval.rm]
class_name = "dspy.ColBERTv2"
url = "http://localhost:8893/api/search"
```

## Activation Precedence

`dspy-profiles` uses a clear and predictable order of precedence to determine which profile is active. This ensures that you always know which configuration is being used.

The order is as follows:

1.  **`profile()` Context Manager / `@with_profile` Decorator**: The most specific and highest precedence.
2.  **`DSPY_PROFILE` Environment Variable**: If set, this profile will be used. This is what the `dspy-profiles run` command uses internally.
3.  **Default DSPy Configuration**: If neither of the above is present, the standard DSPy environment variables (`OPENAI_API_KEY`, etc.) or manually configured settings will be used.

```mermaid
graph TD
    subgraph "Activation Logic"
        A{Code Execution} --> B{Is it inside a `profile()` block?};
        B -- Yes --> C[Activate Profile from Context];
        B -- No --> D{Is `DSPY_PROFILE` env var set?};
        D -- Yes --> E[Activate Profile from Env Var];
        D -- No --> F[Use Default DSPy Settings];
    end
```

## Programmatic Access

You can programmatically access profile information, which is useful for introspection or for building more complex workflows.

### Getting the Current Profile

The `current_profile()` function returns the name of the currently active profile, if any.

```python
from dspy_profiles import profile, current_profile

print(f"Outside context: {current_profile()}")

with profile("my_profile"):
    print(f"Inside context: {current_profile()}")

# Output:
# Outside context: None
# Inside context: my_profile
```

### Loading a Profile's Configuration

The `get_profile()` function allows you to load the fully resolved configuration of any profile as a dictionary.

```python
from dspy_profiles import get_profile

config = get_profile("my_profile")
print(config)

# Output:
# {'lm': {'model': 'gpt-4o-mini'}, 'settings': {'temperature': 0.7}}
```
