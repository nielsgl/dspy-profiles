# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Human-readable table output for the `show` command.
- `--json` flag for both `list` and `show` commands for machine-readable output.

### Fixed
- Data corruption bugs in `set` and `delete` commands.
- `delete default` command no longer allows deleting the default profile.
- `diff` command now correctly handles `HttpUrl` objects.
- `list` and `show` commands now correctly handle `HttpUrl` objects when using the `--json` flag.
- Incorrect rendering of the quickstart button on the index page.
