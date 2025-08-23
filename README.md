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

## Features

- **Profile Management**: A user-friendly CLI to manage your configuration profiles.
- **Centralized Configuration**: Keep all your DSPy settings in a single `~/.dspy/profiles.toml` file.
- **Secure Secret Management**: Automatically load API keys from environment variables and `.env` files.
- **Python API**: Use profiles in your code via a `with profile(...)` context manager. (Coming soon!)

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

## Roadmap

-   [x] **Core CLI**: Implement `init`, `set`, `list`, `show`, and `delete` commands.
-   [x] **Interactive `init`**: An interactive wizard for creating new profiles.
-   [x] **Secret Management**: Load API keys and other secrets from environment variables and `.env` files.
-   [ ] **Python API**: Implement `with profile(...)` and `@with_profile(...)` for using profiles in code.
-   [ ] **`run` Command**: Implement `dspy-profiles run --profile <name> -- your_script.py` to execute scripts with a specific profile.
-   [ ] **Custom Providers**: Support for configuring custom DSPy providers.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
