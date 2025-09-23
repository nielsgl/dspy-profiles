The `dspy-run` command runs any command with a profile activated. For Python
scripts, it wraps execution in a profile context; for non-Python commands, it
sets the `DSPY_PROFILE` environment variable.

## Notes

- Python scripts: automatically bootstraps `with profile(...)` around your script.
- Non-Python commands: use `DSPY_PROFILE` inside your tool or test harness.
- `--dry-run`: prints the resolved profile, config path, environment and final
  command without executing it (helpful for CI and debugging).
- `-V/--verbose`: prints the resolved command before executing.

```
$ dspy-run --help
Usage: dspy-run [OPTIONS] [COMMAND]... COMMAND [ARGS]...

Run a command with a dspy-profile activated.

Options:
  --profile, -p TEXT  The profile to activate. Defaults to 'default'.
  --verbose, -V       Increase verbosity (-V for INFO, -VV for DEBUG).
  --quiet, -q         Decrease verbosity (once for ERROR).
  --log-level TEXT    Explicit log level (DEBUG, INFO, WARNING, ERROR).
  --dry-run           Print the resolved command, environment, and config
                      path; then exit.
  --help              Show this message and exit.
```
