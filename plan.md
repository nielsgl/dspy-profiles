# Post-0.3 Improvement Plan

Version 0.3.0 is out. This plan captures the quality bars and focus areas for the next iteration of `dspy-profiles`.

## Objectives

1. Keep the CLI and Python API rock solid while we iterate on post-launch feedback.
2. Raise test coverage above 95% and lock the fail-under so regressions surface immediately.
3. Ship the next wave of developer-experience polish (docs, shell completion, provider guides).
4. Maintain a zero-regression policy on CI: lint, tests, docs, and packaging must stay green on every merge.

## Quality Gates (for every merge to `main`)

- ✅ Tests: `uv run pytest --cov` (soon raising `fail_under` to 95 once CLI gaps are covered).
- ✅ Lint: `uv run ruff check .`.
- ✅ Docs: `uv run mkdocs build --strict`.
- ✅ Packaging sanity: `uv build` on demand before release tags.
- 🔄 Backlog in `todo.md` reflects new work or defers it explicitly.

## Verification Strategy (unchanged)

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

## Manual Smoke Checklist (run before tagging a release)

1. `dspy-profiles init --profile demo` (cancel + force flows).
2. `dspy-profiles list/show/set/delete` with a temporary config.
3. `dspy-run --profile demo --dry-run python hello.py` to validate bootstrap messaging.
4. `dspy-profiles validate` and `dspy-profiles test demo` against a stub LM.
5. Review docs site locally (`uv run mkdocs serve`) for copy accuracy.

## High-Priority Enhancements

- Keyring-backed secrets management (`dspy-profiles set-secret`).
- Shell completion instructions and auto-generation helpers.
- Provider-specific guides (OpenAI, Anthropic, Ollama, local models).
- `dspy-profiles export` command and import conflict resolution UX.
- Raise coverage fail-under to 95% once CLI edge cases are exercised.

## Reporting

- Coverage reports (`coverage.json`) uploaded from CI; ratchet the fail-under after coverage work lands.
- Release notes sourced from `CHANGELOG.md` and the docs changelog page.
- Any deviations or flaky tests must be captured in `todo.md` (or an issue) before tagging.
