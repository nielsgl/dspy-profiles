The `dspy-run` command runs any command with a profile activated. For Python
scripts, it wraps execution in a profile context; for non-Python commands, it
sets the `DSPY_PROFILE` environment variable.

Notes

- Python scripts: automatically bootstraps `with profile(...)` around your script.
- Non-Python commands: use `DSPY_PROFILE` inside your tool or test harness.
- `--dry-run`: prints the resolved profile, config path, environment and final
  command without executing it (helpful for CI and debugging).
- `-V/--verbose`: prints the resolved command before executing.

::: mkdocs-typer2
    :module: dspy_profiles.commands.run
    :name: dspy-run
