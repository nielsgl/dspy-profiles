# DSPy Profiles

[![PyPI version](https://badge.fury.io/py/dspy-profiles.svg)](https://badge.fury.io/py/dspy-profiles)
[![Tests](https://github.com/nielsgl/dspy-profiles/actions/workflows/tests.yml/badge.svg)](https://github.com/nielsgl/dspy-profiles/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/codecov/c/github/your-username/dspy-profiles)](https://codecov.io/gh/your-username/dspy-profiles)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/managed%20by-uv-blue.svg)](https://github.com/astral-sh/uv)
[![Python Version](https://img.shields.io/pypi/pyversions/dspy-profiles.svg)](https://pypi.org/project/dspy-profiles/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A companion tool for the [DSPy framework](https://github.com/stanfordnlp/dspy) to manage configuration profiles, inspired by the AWS CLI.

`dspy-profiles` allows you to define, switch between, and manage different DSPy configurations for various environments (e.g., development, staging, production) without cluttering your code.

## Key Features

-   **Centralized Configuration**: Manage all your DSPy settings in a single `~/.dspy/profiles.toml` file, moving configuration out of your code.
-   **Environment Switching**: Seamlessly switch between profiles for `dev`, `staging`, and `prod` environments.
-   **Powerful Python API**: A flexible `with profile(...)` context manager and `@with_profile(...)` decorator with support for composition and inline overrides.
-   **Full-Featured CLI**: An intuitive command-line interface for initializing, managing, validating, and testing profiles.
-   **Secure Secret Management**: Load secrets from `.env` files, environment variables, or (optionally) your operating system's native keyring for enhanced security.
-   **Advanced Workflows**: Features like profile diffing, import/export, and profile-aware caching streamline complex development and team-based workflows.

## Installation

```bash
pip install dspy-profiles
```

## Quickstart

1.  **Initialize a default profile interactively:**
    ```bash
    dspy-profiles init
    ```
    This will launch an interactive prompt to help you configure your first profile.

2.  **Set configuration values:**
    ```bash
    dspy-profiles set default lm.model=openai/gpt-4o-mini
    dspy-profiles set default lm.temperature=0.7
    ```

3.  **View your profile:**
    ```bash
    dspy-profiles show default
    ```

## Python API Usage

You can activate profiles directly in your Python code using the `profile` context manager or the `with_profile` decorator.

### `with profile(...)`

The context manager is ideal for applying a profile to a specific block of code. It also supports **inline overrides** for quick experiments.

```python
import dspy
from dspy_profiles import profile

# Use the 'staging' profile, but override the temperature for this block
with profile("staging", temperature=0.9):
    response = dspy.Predict("Question -> Answer")("What is the capital of France?")

# The global settings are restored outside the block
```

### `@with_profile(...)`

The decorator is useful for applying a profile to an entire function and supports the same inline overrides. It is also fully **async-friendly**.

```python
import dspy
from dspy_profiles import with_profile

@with_profile("testing", max_tokens=4000)
async def my_async_program():
    # This async function runs with the 'testing' profile,
    # but with max_tokens overridden to 4000.
    ...

await my_async_program()
```

## CLI Usage

### `dspy-profiles list`
Lists all available profiles.

### `dspy-profiles show <profile_name>`
Displays the configuration for a specific profile.

### `dspy-profiles init --profile <name>`
Initializes a new profile interactively.

### `dspy-profiles set <profile_name> <key> <value>`
Sets a configuration value in a profile using dot notation (e.g., `lm.model`).

### `dspy-profiles delete <profile_name>`
Deletes a profile.

### `dspy-profiles diff <profile_a> <profile_b>`
Compares two profiles and shows the differences.

### `dspy-profiles import --from .env`
Creates a new profile from a `.env` file.

### `dspy-profiles run`
Executes a command with a specific profile activated.

### `dspy-profiles validate`
Validates the `profiles.toml` file against the schema.

### `dspy-profiles test <profile_name>`
Performs a live connectivity test for a given profile.

```bash
dspy-profiles run --profile prod -- python my_script.py --arg1 --arg2
```

## Roadmap

The project has a comprehensive roadmap organized into five phases. See the [PROJECT.md](PROJECT.md) file for detailed specifications.

-   **[x] Phase 1: DX, Packaging & Documentation**: Professional PyPI packaging, CI/CD for publishing, and a full documentation site with MkDocs.
-   **[x] Phase 2: Core CLI & Env Var Enhancements**: `dspy-profiles import --from .env`, `dspy-profiles diff`, and robust activation precedence rules with `DSPY_PROFILE`.
-   **[x] Phase 3: Advanced Profile Features**: Profile composition (`extends`), inline overrides, optional OS keyring support, and `validate`/`test` commands.
-   **Phase 4: Python API & Runtime Utilities**: Programmatic shortcuts like `lm("prod")`, runtime introspection with `current_profile()`, and a notebook magic command.
-   **Phase 5: QoL & Advanced Workflows**: An interactive `init` wizard, profile import/export, and async-friendly decorators.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
