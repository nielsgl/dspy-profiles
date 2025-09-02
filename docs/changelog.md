# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **New `dspy-run` command:** A new, ergonomic `dspy-run` command has been added as the primary way to execute scripts with a profile. It is shorter, more intuitive, and intelligently prepends `python` to script files.
- The `dspy-run` command now defaults to the "default" profile if no profile is specified.
- `dspy-run --dry-run` to preview resolved profile, config path, environment, and command without executing.
- Verbosity flags across CLIs: `-V/--verbose`, `-q/--quiet`, and `--log-level` for fine-grained logging control.
- Human-readable table output for the `show` command.
- `--json` flag for both `list` and `show` commands for machine-readable output.
- `which-config` command to print the resolved `profiles.toml` path used by the tool.

### Fixed
- **`run` command:** The `dspy-profiles run` command (and the new `dspy-run` command) now correctly activates the specified profile in the subprocess, fixing the "No LM is loaded" error.
- Data corruption bugs in `set` and `delete` commands.
- `delete default` command no longer allows deleting the default profile.
- `diff` command now correctly handles `HttpUrl` objects.
- `list` and `show` commands now correctly handle `HttpUrl` objects when using the `--json` flag.
- Incorrect rendering of the quickstart button on the index page.
