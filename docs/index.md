# Welcome to dspy-profiles

**A companion tool for the [DSPy framework](https://github.com/stanfordnlp/dspy) to manage configuration profiles, inspired by the AWS CLI.**

`dspy-profiles` allows you to define, switch between, and manage different DSPy configurations for various environments (e.g., development, staging, production) without cluttering your code.

## The Problem

When working with DSPy, you often need to switch between different language models, retrieval models, and settings. For example:
* Using a cheap, fast model like `gpt-4o-mini` in development.
* Using a powerful model like `claude-3-opus` in production.
* Pointing to a staging database for your retrieval model.
* Toggling settings like `track_usage`.

Managing this configuration directly in your code can be messy, error-prone, and insecure.

## The Solution

`dspy-profiles` moves this configuration out of your code and into a simple, centralized `~/.dspy/profiles.toml` file. It provides a powerful CLI and a clean Python API to manage and use these profiles seamlessly.

### Key Features Implemented
*   **Full CLI**: Manage profiles with `init`, `list`, `show`, `set`, and `delete`.
*   **Profile Activation**: Run any command under a specific profile with `dspy-profiles run`.
*   **Environment Import**: Create profiles directly from `.env` files with `dspy-profiles import`.
*   **Configuration Diffing**: Easily compare environments with `dspy-profiles diff`.
*   **Robust Precedence**: A clear and predictable activation logic ensures the right profile is always used.

**For more, see the [Quickstart](quickstart.md) guide.**
