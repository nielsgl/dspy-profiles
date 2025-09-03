## Contributing to dspy-profiles

Thank you for your interest in contributing! This guide explains how to set up your environment, run tests, follow the style, and propose changes.

## Getting Started

- Prerequisites: Python 3.12+, uv recommended
- Clone the repo and install dev dependencies:

```
uv sync --all-extras --group dev
pre-commit install
```

## Running Tests

- Run all tests with coverage:

```
uv run pytest -q
```

- Aim to keep coverage high (≥ 90%); critical changes should include tests.

## Style & Tooling

- Formatting & linting: ruff + black (configured in `pyproject.toml`)
- Commit style: Commitizen conventional commits with gitmoji (used in CI)
- Pre-commit hooks enforce formatting and lint; please follow them.

## Documentation

- Docs use MkDocs Material. To preview locally:

```
uv run mkdocs serve
```

- Docs sources live under `docs/`. CLI and API docs are generated with `mkdocs-typer2` and `mkdocstrings`.

## Making Changes

- Keep PRs focused and scoped. Include tests and docs updates where relevant.
- For user-visible changes, update the Unreleased section in `CHANGELOG.md`.
- Use `dspy-run --dry-run` and verbosity flags for debugging workflows.

## Releases

- Versioning: Semantic, pre-1.0 (0.x) with Commitizen.
- Changelog: Maintained in the root `CHANGELOG.md` and surfaced on the docs site.

## Questions

- Open an issue for feature requests or bugs. Be specific and include repro steps.

Thanks again for helping improve dspy-profiles!
