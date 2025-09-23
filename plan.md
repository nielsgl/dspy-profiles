# Release Readiness Plan

This plan captures the final checks required before cutting the first public release of `dspy-profiles`.

## Objectives

1. Ship a developer-friendly CLI and Python API with accurate, discoverable documentation.
2. Guarantee stable configuration behaviour (profiles, inheritance, overrides, async flows).
3. Exceed 95% statement coverage with meaningful automated tests (unit, integration, CLI).
4. Keep the release pipeline green: lint, tests, docs build, packaging.

## Release Gates

- ✅ Tests: `uv run pytest --cov` (target ≥95% coverage; fail-under currently 90%).
- ✅ Lint: `uv run ruff check .` with zero warnings.
- ✅ Docs: `uv run mkdocs build --strict` without broken references.
- ✅ Packaging: `uv build` succeeds; optional dry-run publish to TestPyPI.
- ✅ CI: GitHub Actions workflow mirrors the commands above and must pass on `main`.
- 🔄 Backlog tracked in `todo.md` stays in sync with any follow-up items.

## Verification Strategy

| Layer        | What we cover                                                         | Tooling                                  |
|--------------|------------------------------------------------------------------------|-------------------------------------------|
| Unit         | Pure helpers, normalization, deep merge behaviour                      | `pytest`, focused fixtures & parametrised |
| Integration  | Profile loading, inheritance, CLI workflows via `CliRunner`           | `pytest`, Typer `CliRunner`               |
| End-to-end   | `dspy-run` wrapping, subprocess env propagation, async decorator paths | `pytest`, live subprocess invocation      |
| Documentation| Navigation, snippets, API docs, reference consistency                 | `mkdocs build --strict`                   |

## Regression Focus

- Dotted-key handling (arbitrary depth, idempotency).
- Profile inheritance precedence and cycle detection.
- Async `@with_profile` decorator correctness.
- CLI commands (`set`, `run`, `import`, `diff`, `test`) covering success and failure paths.
- Cache directory behaviour and environment precedence (`DSPY_PROFILE`, discovery).

## Manual Smoke Checklist

1. `dspy-profiles init --profile demo` (cancel + force flows).
2. `dspy-profiles list/show/set/delete` with a temporary config.
3. `dspy-run --profile demo --dry-run python hello.py` to validate bootstrap messaging.
4. `dspy-profiles validate` and `dspy-profiles test demo` against a stub LM.
5. Review docs site locally (`uv run mkdocs serve`) for copy accuracy.

## Outstanding Enhancements (Post-Launch Candidates)

- Keyring-backed secrets management (`dspy-profiles set-secret`).
- Shell completion instructions and auto-generation helpers.
- Provider-specific guides (OpenAI, Anthropic, Ollama, local models).
- `dspy-profiles export` command and import conflict resolution UX.

## Reporting

- Coverage (`coverage.json`) uploaded from CI; fail builds if future coverage drops below target after ratcheting.
- Release notes derived from `CHANGELOG.md` and docs “Changelog” page.
- Any deviations or flaky tests must be captured in `todo.md` before tagging.
