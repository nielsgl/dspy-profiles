# DSPy Profiles

[![PyPI version](https://badge.fury.io/py/dspy-profiles.svg)](https://badge.fury.io/py/dspy-profiles)
[![Tests](https://github.com/nielsgl/dspy-profiles/actions/workflows/tests.yml/badge.svg)](https://github.com/nielsgl/dspy-profiles/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/codecov/c/github/nielsgl/dspy-profiles)](https://codecov.io/gh/nielsgl/dspy-profiles)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/managed%20by-uv-blue.svg)](https://github.com/astral-sh/uv)
[![Python Version](https://img.shields.io/pypi/pyversions/dspy-profiles.svg)](https://pypi.org/project/dspy-profiles/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**A companion tool for the [DSPy framework](https://github.com/stanfordnlp/dspy) to manage configuration profiles, inspired by the AWS CLI.**

`dspy-profiles` allows you to define, switch between, and manage different DSPy configurations for various environments (e.g., development, staging, production) without cluttering your code.

---

## The Problem

When working with DSPy, you often need to switch between different language models, retrieval models, and settings. Managing this directly in your code can be messy, error-prone, and insecure.

## The Solution

`dspy-profiles` moves this configuration out of your code and into a simple `profiles.toml` file. It provides a powerful CLI and a clean Python API to manage and use these profiles seamlessly. The tool will automatically find your `profiles.toml` whether it's in your local project directory or in the global `~/.dspy/` folder.

---

## Key Features

-   **Declarative Profiles**: Define all your environment settings in a clear, human-readable TOML file.
-   **Powerful CLI**: A rich command-line interface lets you manage your profiles without ever leaving the terminal.
-   **Seamless Python API**: Activate profiles in your Python code with an elegant and intuitive API.
-   **Profile Inheritance**: Create base profiles and extend them for different environments to avoid repetition.
-   **Environment Precedence**: A clear and predictable activation logic ensures the right profile is always used.
-   **Validation & Testing**: `validate` and `test` commands to ensure your profiles are correct and your models are reachable.

---

## Installation

```bash
pip install dspy-profiles
```

## Quickstart

1.  **Initialize a default profile interactively:**
    ```bash
    dspy-profiles init
    ```
    This will prompt you for your language model and optionally your API key and API base.

2.  **Use it in your Python code:**
    ```python
    import dspy
    from dspy_profiles import profile

    with profile("default"):
        # Your DSPy code here, now using the settings from your 'default' profile.
        predictor = dspy.Predict("question -> answer")
        response = predictor(question="What is the capital of France?")
        print(response.answer)
    ```

3.  **Run any script with a profile:**
    ```bash
    dspy-profiles run --profile default -- python my_script.py
    ```

---

## Full Documentation

For a complete guide, including advanced features and the full API and CLI reference, please visit the **[official documentation site](https://nielsgl.github.io/dspy-profiles/)**.

---

## Project Status & Roadmap

The project is under active development. All core features are implemented and stable.

-   **[x] Phase 1: DX, Packaging & Documentation**: Professional PyPI packaging, CI/CD, and a full documentation site.
-   **[x] Phase 2: Core CLI & Env Var Enhancements**: `import`, `diff`, `run`, and robust activation precedence.
-   **[x] Phase 3: Advanced Profile Features**: Profile composition (`extends`), inline overrides, and `validate`/`test` commands.
-   **[x] Phase 4: Python API & Runtime Utilities**: Programmatic shortcuts like `lm()` and runtime introspection with `current_profile()`.
-   **[x] Phase 5: Developer Experience Overhaul**: A major refactor of the CLI, API, and documentation for clarity, stability, and ease of use.
-   **[x] Phase 6: QoL & Advanced Workflows**: An interactive `init` wizard, profile import/export, and async-friendly decorators.

See the [PROJECT.md](PROJECT.md) file for detailed specifications.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
