# Project: dspy-profiles

## Vision

`dspy-profiles` is a companion package for the DSPy framework that provides a robust and user-friendly system for managing configurations. Inspired by the AWS CLI, it allows developers to define, switch between, and manage different DSPy configurations (profiles) for various environments like development, staging, and production.

The core goal is to move configuration out of the code and into a centralized, manageable location, improving reproducibility, security, and developer experience.

## Core Features

1.  **Profile Management**: A CLI and Python API to manage configuration profiles.
2.  **Context Managers & Decorators**: Pythonic `with profile(...)` and `@with_profile(...)` constructs to apply profiles in code.
3.  **CLI Integration**: A `dspy-profiles` command-line interface for managing profiles and running scripts under a specific profile.
4.  **Secure Secret Management**: Seamless integration with environment variables and `.env` files for API keys and other secrets.
5.  **Configuration Validation**: Robust validation of profile schemas to prevent misconfiguration.

## Configuration (`~/.dspy/profiles.toml`)

Profiles are stored in a TOML file located at `~/.dspy/profiles.toml` (or `$XDG_CONFIG_HOME/dspy/profiles.toml`). Each profile can have `lm`, `rm`, `settings`, and `provider` sections.

### Schema Principles

*   **Direct Mapping**: All keys within the `lm`, `rm`, and `settings` sections are designed to be a direct mapping to the argument names in the corresponding DSPy classes (`dspy.LM`, `dspy.ColBERTv2`, etc.) and `dspy.settings`.
*   **Optionality**: All settings are optional. If a setting is omitted from a profile, the default value from DSPy will be used.

### Example Schema

```toml
# Default profile, used when no other is specified
[default.lm]
model = "openai/gpt-4o-mini"
temperature = 0.7
max_tokens = 4000

[default.settings]
track_usage = true

# Production profile
[prod.lm]
model = "cohere/command-r"
api_key = "${COHERE_API_KEY}" # Example of secret injection

[prod.settings]
num_threads = 32
```

## Activation Precedence Rules

The system has a clearly defined hierarchy to determine which profile is active at any given time. This ensures predictable behavior across different usage patterns, from CI/CD environments to interactive notebooks.

The order of precedence is as follows (from highest to lowest):

1.  **Forced Code (`with profile("Y", force=True)`)**: An explicit call in the code with `force=True` has the absolute highest priority. It will override any other setting, including the environment variable. This is intended for developers who need to guarantee a specific profile is used in a block of code, regardless of the execution environment.
2.  **Environment Variable (`DSPY_PROFILE`)**: If a profile is specified via the `DSPY_PROFILE` environment variable (e.g., set by `dspy-profiles run`), it will take precedence over any normal, non-forced code. This allows operators and CI/CD systems to enforce a specific configuration for a script run, ensuring operational safety.
3.  **Normal Code (`with profile("Y")`)**: A standard, non-forced call to the context manager or decorator. This will only take effect if the `DSPY_PROFILE` environment variable is *not* set.
4.  **Default Profile**: If none of the above are active, the system will look for and use the `[default]` profile in the `profiles.toml` file.
5.  **DSPy Library Defaults**: If no profiles are configured or activated, the system falls back to the standard defaults of the underlying DSPy library.

## Secret Management

*   **No Secrets in Config**: API keys and other secrets are **never** stored in the `profiles.toml` file. They are referenced via environment variable placeholders (e.g., `api_key = "${OPENAI_API_KEY}"`).
*   **Environment Loading**: Secrets are loaded on-demand from environment variables.
*   **`.env` File Support**: For local development, the library automatically detects and loads a `.env` file from the current working directory. System-level environment variables always override values in a `.env` file.
*   **OS Keyring (Optional)**: For enhanced security, secrets can be stored in the operating system's native keyring. This functionality is an optional feature (`pip install dspy-profiles[keyring]`).
    *   Secrets are referenced in profiles using a special syntax (e.g., `api_key = "keyring:service/username"`).
    *   A secure CLI command, `dspy-profiles set-secret`, will prompt interactively for credentials to store them in the keyring without exposing them in shell history.

## Python API

### `with profile(...)` Context Manager

```python
from dspy_profiles import profile

# This block will use the 'prod' profile
with profile("prod"):
    # DSPy calls inside this block will use the 'prod' configuration
    response = dspy.Predict("Question -> Answer")("What is the capital of France?")
```

### `with profile(...)` Overrides & Composition

The context manager supports powerful composition and override features:

*   **Profile Extension**: A profile can inherit from another using `extends = "basename"`. Settings are merged, with the extending profile's values taking precedence.
*   **Inline Overrides**: Provide keyword arguments to dynamically override settings for the scope of the block (e.g., `with profile("prod", temperature=0.9)`).

The layering logic is applied in a specific order:
1.  The base profile (from `extends`) is loaded.
2.  The main profile's settings are merged on top.
3.  The inline keyword arguments are applied as the final override.

### `@with_profile(...)` Decorator

The decorator supports the same override and composition features as the context manager.

```python
from dspy_profiles import with_profile

@with_profile("prod", temperature=0.9)
async def my_async_dspy_function():
    # This function will run with the 'prod' profile, but with temperature=0.9
    ...
```
*   **Async Support**: The decorator is designed to be fully compatible with `async def` functions.

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

### Additional CLI Commands

*   **`dspy-profiles diff <A> <B>`**: Provides a color-coded diff of two profiles to easily compare configurations.
*   **`dspy-profiles import --from .env`**: Creates a new profile by mapping variables from a `.env` file using a `DSPY_` prefix convention (e.g., `DSPY_LM_MODEL` -> `lm.model`).
*   **`dspy-profiles export/import`**: Allows users to share profile configurations. The `import` command will interactively prompt on conflicts (overwrite/skip/rename). `export` will scrub secrets by default.
*   **`dspy-profiles validate`**: Lints the `profiles.toml` file, checking for schema errors, unknown keys, and deprecated keys (suggesting alternatives).
*   **`dspy-profiles test <profile>`**: Performs a live dry run by loading a profile and attempting a minimal API call to verify connectivity and credentials.

## Technical Design Notes

*   **Concurrency**: The `with profile(...)` context manager will be a wrapper around `dspy.context`, making it safe for use in multi-threaded and async applications by leveraging `contextvars`.
*   **`dspy-profiles run` Implementation**: This command will set the `DSPY_PROFILE` environment variable and execute the user's script in a subprocess, enabling the precedence rules described above.
*   **Schema Validation**: Pydantic models will be used to validate the structure of `profiles.toml`.
*   **Programmatic Shortcuts**:
    *   `lm("prod")`: A cached factory function to get a pre-configured `dspy.LM` instance. Can be disabled with `lm("prod", cached=False)`.
    *   `current_profile()`: An introspection utility to see the currently active profile and its resolved settings.
*   **Notebook Integration**: A session-wide `%profile <name>` magic command will be available for interactive use in IPython/Jupyter.

## Developer Experience & Publishing

*   **PyPI Packaging**: The project will be packaged and distributed via PyPI, making it easily installable with `pip`.
*   **Automated Publishing**: A GitHub Actions workflow will automate the process of building and publishing the package to PyPI whenever a new version tag is pushed.
*   **Official Documentation**: A documentation site will be built using MkDocs with the Material theme, providing comprehensive guides, tutorials, and API references. It will be hosted on GitHub Pages.
*   **Contribution-Friendly**: With clear documentation, automated testing, and a well-defined project structure, the goal is to make it easy for the community to contribute.

## Development Roadmap

### Phase 1: DX, Packaging & Documentation

1.  **Packaging**: [x] Configure `pyproject.toml` for PyPI publishing.
2.  **CI/CD**: [x] Implement a GitHub Actions workflow for automated publishing to PyPI.
3.  **Documentation Setup**: [x] Add and configure MkDocs with the Material theme.
4.  **Content Scaffolding**: [x] Create the initial documentation structure and placeholder pages.
5.  **Project Vision Alignment**: [x] Update `README.md` and `PROJECT.md` to reflect the full scope.

### Phase 2: Core CLI & Env Var Enhancements

6.  **`.env` Import**: [x] Implement `dspy profiles import --from .env`.
7.  **Profile Diffing**: [x] Implement `dspy profiles diff <profile_a> <profile_b>`.
8.  **`DSPY_PROFILE` Env Var**: [x] Add support for the `DSPY_PROFILE` environment variable.
9.  **`run` Command**: [x] Enhance the `dspy-profiles run` command.

### Phase 3: Advanced Profile Features

10. **Profile Composition**: Implement `extends` functionality for profile inheritance.
11. **Inline Overrides**: Allow `with profile("name", key=value)` overrides.
12. **Keyring Support**: Integrate optional OS keyring support for secrets.
13. **Validation & Testing**: [x] Add `dspy profiles validate` and `dspy profiles test` commands.

### Phase 4: Python API & Runtime Utilities

14. **Runtime Introspection**: Create a `current_profile()` utility.
15. **LM Shortcuts**: Implement `from dspy_profiles import lm`.
16. **Profile-Aware Caching**: Isolate cache directories per profile.

### Phase 5: Quality-of-Life and Final Touches

17. **Interactive Wizard**: Enhance `dspy profiles init` into a full setup wizard.
18. **Decorator Enhancements**: Add `async` and `kwargs` support to `@with_profile`.
19. **Export/Import**: Implement `dspy profiles export` and `import`.
