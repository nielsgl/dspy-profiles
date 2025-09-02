# Troubleshooting

This page lists common issues and how to resolve them quickly.

## No LM loaded / "No LM is loaded"
- Cause: Active profile has no `lm` section, or no profile is active.
- Fix: Ensure your profile includes an `[<name>.lm]` section, and that you activate the profile using the context manager, decorator, or `dspy-run`.
- Tip: Use `dspy-profiles show <name>` to verify the profile content.

## Profile not found
- Cause: The profile name is misspelled or not present in the resolved `profiles.toml`.
- Fix: Check which file is being used, then list and show its profiles.
- Commands:
  - `dspy-profiles which-config`
  - `dspy-profiles list`
  - `dspy-profiles show <name>`

## Validation errors on profiles.toml
- Cause: TOML syntax error or invalid structure.
- Fix: Run validation and address reported issues.
- Command: `dspy-profiles validate -c /path/to/profiles.toml`
- Notes:
  - Dotted keys are supported and normalized (e.g., `lm.model = "..."`).
  - Retrieval config can use `rm.class_name = "ColBERTv2"` and arbitrary kwargs.

## Which profiles.toml is being used?
- Behavior (precedence): `DSPY_PROFILES_PATH` > local discovery (CWD and parents) > global `~/.dspy/profiles.toml`.
- Command: `dspy-profiles which-config`

## `dspy-run` didn’t seem to apply my profile
- Explanation: For Python scripts, `dspy-run` wraps execution in a profile context. For non-Python commands (e.g., `pytest`), it sets the `DSPY_PROFILE` env var.
- Fix: Ensure your process or test harness respects `DSPY_PROFILE`, or run Python scripts through `dspy-run` directly.

## Retrieval model could not be imported / class not found
- Cause: `rm.class_name` points to a class that cannot be resolved.
- Fix:
  - Use `ColBERTv2`, `dspy.ColBERTv2`, or a fully-qualified import path like `my_package.retrieval.CustomRM`.
  - Ensure the package is installed and importable.

## See also
- Quickstart: installation and core concepts
- Advanced Usage: activation precedence, LM/RM configuration, and decorators
