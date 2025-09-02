# Welcome to dspy-profiles

**A companion tool for the [DSPy framework](https://github.com/stanfordnlp/dspy) to manage configuration profiles, inspired by the AWS CLI.**

`dspy-profiles` allows you to define, switch between, and manage different DSPy configurations for various environments (e.g., development, staging, production) without cluttering your code.

!!! abstract "The Problem"

    When working with DSPy, you often need to switch between different language models, retrieval models, and settings. For example:

    -   Using a cheap, fast model like `gpt-4o-mini` in development.
    -   Using a powerful model like `claude-3-opus` in production.
    -   Pointing to a staging database for your retrieval model.
    -   Toggling settings like `track_usage`.

    Managing this configuration directly in your code can be messy, error-prone, and insecure.

!!! success "The Solution"

    `dspy-profiles` moves this configuration out of your code and into a simple, centralized `profiles.toml` file. It provides a powerful CLI and a clean Python API to manage and use these profiles seamlessly.

---

## Configuration Hierarchy

`dspy-profiles` locates your configuration file with a clear, `git`-like precedence:

1.  **Environment Variable**: Set `DSPY_PROFILES_PATH` to point to a specific configuration file.
2.  **Project-Specific File**: Search for a `profiles.toml` in the current directory and its parent directories. This allows you to commit project-specific profiles directly to your repository.
3.  **Global File**: If neither of the above is found, fall back to the global default at `~/.dspy/profiles.toml`.

---

## Key Features

`dspy-profiles` is designed to be a comprehensive solution for DSPy configuration management.

=== "Declarative Profiles"

    Define all your environment settings in a clear, human-readable TOML file.

    ```toml title="~/.dspy/profiles.toml"
    [dev.lm]
    model = "openai/gpt-4o-mini"
    temperature = 0.7

    [dev.settings]
    cache_dir = ".cache"

    [prod]
    extends = "dev"

    [prod.lm]
    model = "anthropic/claude-3-opus"
    temperature = 0.0
    ```

=== "Powerful CLI"

    A rich command-line interface lets you manage your profiles without ever leaving the terminal.

    -   `dspy-profiles init`: Interactively create a new profile.
    -   `dspy-profiles list`: See all your available profiles.
    -   `dspy-profiles show <name>`: View the full configuration of a profile.
    -   `dspy-profiles diff <a> <b>`: Compare two profiles.
    -   `dspy-run ...`: The star of the show. Execute any script with a profile, no code changes needed.

=== "Seamless Python API"

    Keep your DSPy code completely clean of configuration. Use `dspy-run` to activate profiles from the command line, or use the elegant context manager for fine-grained control.

    ```python
    # Your script remains pure DSPy, with no mention of profiles.
    # my_script.py
    import dspy

    predictor = dspy.Predict("question -> answer")
    result = predictor(question="What is the capital of Spain?")
    print(f"The capital of Spain is {result.answer}.")
    ```

    ```bash
    # Activate the profile from the outside!
    $ dspy-run --profile production my_script.py
    ```

=== "Advanced Features"

    -   **Profile Inheritance**: Create base profiles and extend them for different environments.
    -   **Environment Precedence**: A clear and predictable activation logic ensures the right profile is always used.
    -   **Validation**: `dspy-profiles validate` checks your configuration file for correctness.
    -   **Connectivity Testing**: `dspy-profiles test <name>` ensures your settings are correct and your models are reachable.

---

## Get Started

Ready to streamline your DSPy workflow?

<a href="quickstart" class="md-button md-button--primary">Get Started with the Quickstart Guide</a>
