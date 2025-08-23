# Project: dspy-profiles

## Vision

`dspy-profiles` is a companion package for the DSPy framework that provides a robust and user-friendly system for managing configurations. Inspired by the AWS CLI, it allows developers to define, switch between, and manage different DSPy configurations (profiles) for various environments like development, staging, and production.

The core goal is to move configuration out of the code and into a centralized, manageable location, improving reproducibility, security, and developer experience.

## Core Features

1.  **Profile Management**: A CLI and Python API to manage configuration profiles.
2.  **Context Managers & Decorators**: Pythonic `with profile(...)` and `@with_profile(...)` constructs to apply profiles in code.
3.  **CLI Integration**: A `dspy-profiles` command-line interface for managing profiles and running scripts under a specific profile.
4.  **Secure Secret Management**: Seamless integration with environment variables and `.env` files for API keys and other secrets.
5.  **Extensibility**: Support for custom providers to accommodate any DSPy setup.

## Configuration (`~/.dspy/profiles.toml`)

Profiles are stored in a TOML file located at `~/.dspy/profiles.toml` (or `$XDG_CONFIG_HOME/dspy/profiles.toml`). Each profile can have `lm`, `rm`, `settings`, and `provider` sections.

### Schema Principles

*   **Direct Mapping**: All keys within the `lm`, `rm`, and `settings` sections are designed to be a direct mapping to the argument names in the corresponding DSPy classes (`dspy.LM`, `dspy.ColBERTv2`, etc.) and `dspy.settings`.
*   **Optionality**: All settings are optional. If a setting is omitted from a profile, the default value from DSPy will be used.

### Example Schema

```toml
# Default profile, used when no other is specified
[default]
  [default.lm]
  model = "openai/gpt-4o-mini"
  temperature = 0.7
  max_tokens = 4000

  [default.settings]
  track_usage = true

# Production profile with a custom provider
[prod]
  [prod.lm]
  model = "self-hosted/llama3-70b"

  [prod.provider]
  class = "my_custom_providers.MyProvider"
  api_base = "https://my-api.com/v1"

  [prod.settings]
  num_threads = 32
```

## Precedence and Scoping Rules

The system is designed to be predictable and respect DSPy's own scoping rules. The order of precedence is as follows (from highest to lowest):

1.  **Innermost `dspy.context`**: A direct call to `with dspy.context(...)` will always have the final say, even inside a `with profile(...)` block.
2.  **`with profile(...)` / `@with_profile(...)`**: The profile applied via the context manager or decorator.
3.  **Global `dspy.configure()`**: Any global configuration set in the code.
4.  **Default Profile**: The profile designated as `default` in the `profiles.toml` file.

## Secret Management

*   **No Secrets on Disk**: API keys and other secrets are **never** stored in the `profiles.toml` file.
*   **Environment Loading**: Secrets are loaded from environment variables.
*   **`.env` File Support**: For local development, the library will automatically detect and load a `.env` file from the current working directory.
*   **Precedence**: System-level environment variables will always override any values set in a `.env` file.

## Python API

### `with profile(...)` Context Manager

```python
from dspy_profiles import profile

# This block will use the 'prod' profile
with profile("prod"):
    # DSPy calls inside this block will use the 'prod' configuration
    response = dspy.Predict("Question -> Answer")("What is the capital of France?")
```

### `@with_profile(...)` Decorator

```python
from dspy_profiles import with_profile

@with_profile("prod")
def my_dspy_function():
    # This function will run with the 'prod' profile
    ...```

## Command-Line Interface (CLI)

The CLI will be a standalone `dspy-profiles` command, built with `typer` and `rich`. The code will be structured to allow for easy integration into a parent `dspy` command in the future.

```bash
# Initialize a new profile interactively
dspy-profiles init --profile prod

# Set a value in a profile
dspy-profiles set --profile prod lm.model=openai/gpt-4o

# List all available profiles
dspy-profiles list

# Show the configuration of a specific profile
dspy-profiles show prod

# Delete a profile
dspy-profiles delete staging

# Run a Python script under a specific profile
dspy-profiles run --profile prod my_script.py
```

## Technical Design Notes

*   **Concurrency**: The `with profile(...)` context manager will be a wrapper around `dspy.context`, making it safe for use in multi-threaded and async applications by leveraging `contextvars`.
*   **`dspy-profiles run` Implementation**: This command will work by setting an environment variable (e.g., `DSPY_PROFILE=prod`) and then executing the user's script in a subprocess. The library's Python components will be designed to automatically detect and use this environment variable.
*   **Dynamic Imports**: Custom providers will be loaded dynamically using their full import path, allowing for maximum flexibility.

## Development Roadmap

1.  **Project Setup**: Initialize the project with `uv`, `typer`, `rich`, `toml`, and `python-dotenv`.
2.  **Core Logic**: Implement the profile loading, saving, and validation logic.
3.  **Secret Management**: Implement `.env` file loading.
4.  **Context Manager & Decorator**: Build the `with profile(...)` and `@with_profile(...)` features, ensuring they correctly wrap `dspy.context`.
5.  **Custom Provider Support**: Implement the dynamic class loading for providers.
6.  **CLI Implementation**: Build out all the `dspy-profiles` commands.
7.  **Testing**: Write a comprehensive test suite, including tests for precedence, concurrency, `.env` loading, and custom providers.
8.  **Documentation**: Create user-friendly documentation with clear examples.
