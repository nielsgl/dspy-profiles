# dspy-profiles Roadmap

_Last updated: 2025-09-01_

## Current Focus (v0.3)

- Keep the CLI and Python API stable while incorporating early post-release feedback.
- Raise coverage on CLI-heavy paths so we can lock the global `fail_under` at 95%.
- Ship developer-experience polish (shell completion docs, provider guides, export workflow).
- Maintain a zero-regression policy: lint, tests, docs, and packaging must stay green on every merge.

## Quality Gates (every PR and release)

| Layer           | What it covers                                                     | Command / Tooling                     |
|-----------------|---------------------------------------------------------------------|---------------------------------------|
| Unit            | Pure helpers, normalization, deep merge behaviour                   | `uv run pytest --cov`                 |
| Integration     | Profile loading, inheritance, CLI workflows via `CliRunner`         | `uv run pytest --cov`                 |
| End-to-end      | `dspy-run` wrapping, env propagation, async decorator paths          | `uv run pytest --cov` + helper script |
| Documentation   | Navigation, snippets, API docs, reference consistency               | `uv run mkdocs build --strict`        |
| Packaging (tag) | Build integrity before publishing                                   | `uv build`                            |

## Manual Smoke Checklist (before tagging)

1. `dspy-profiles init --profile demo` (cancel + force flows).
2. `dspy-profiles list/show/set/delete` with a temporary config.
3. `dspy-run --profile demo --dry-run python hello.py` to validate bootstrap messaging.
4. `dspy-profiles validate` and `dspy-profiles test demo` against a stub LM.
5. Run `./run-examples.zsh` or the per-example commands to ensure every sample works with the expected profiles.
6. Preview docs locally: `uv run mkdocs serve`.

## Near-Term Priorities (P1)

1. **Raise coverage on CLI surfaces & tighten fail-under**
   - Add targeted tests for `dspy_profiles/commands/run.py` (error handling, verbose echo) and `dspy_profiles/api.py` retrieval helpers.
   - Once coverage is ≥95% across modules, raise `pyproject.toml`'s `fail_under` accordingly.
   - Acceptance: Coverage report ≥95%; fail-under lifted without flake regressions.

## Backlog (P2)

- Secrets: optional keyring integration with `dspy-profiles set-secret` and loader fallback.
- Shell completion documentation/install helpers for Bash/Zsh/Fish.
- Provider-specific guides and recipes (OpenAI, Anthropic, Ollama, local models).
- `dspy-profiles export` command plus conflict-aware import UX.
- Notebook ergonomics (investigate `%profile` magic).

## Completed Highlights (v0.3)

- Recursive dotted-key normalization with deep merge semantics.
- Profile inheritance cycle detection.
- Async-aware `@with_profile` decorator.
- `run-examples.zsh` helper and refreshed example docs.
- CI enforces `mkdocs build --strict`; docs upgraded with CI/testing and usage guides.

## Reporting

- Coverage reports (`coverage.json`) uploaded from CI; ratchet the fail-under after coverage work lands.
- Release notes sourced from `CHANGELOG.md` and the docs changelog page.
- Capture any deviations or flaky tests in issues or this roadmap before tagging.

---

Need more detail? Check the documentation site for tutorials and API references: https://nielsgl.github.io/dspy-profiles/
