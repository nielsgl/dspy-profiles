# dspy-profiles: Backlog

Priorities: P0 = urgent, P1 = next-up, P2 = queued. Each item includes intent, proposed changes, affected files, and acceptance criteria.

—

P0 — Urgent

_No open P0 items._

—

P1 — Next Up

1) P1 — Raise coverage on CLI surfaces & tighten fail-under
- Intent: Ratchet the coverage floor to ≥95% once remaining CLI edges are exercised.
- Changes:
  - Add targeted tests for `dspy_profiles/commands/run.py` (error handling, verbose echo) and `dspy_profiles/api.py` retrieval helpers.
  - Update `pyproject.toml` coverage threshold to 95 after new tests land.
- Files: `tests/test_cli_run.py`, `tests/test_api.py`, `pyproject.toml`.
- Acceptance: Coverage report shows ≥95% across modules; fail-under raised without flake regressions.
- Commit: :white_check_mark: test(cli): cover run error paths and raise coverage gate

—

P2 — Queued Enhancements

3) P2 — Secrets: optional keyring integration
- Intent: Support secure storage of secrets.
- Changes: Add `set-secret` CLI backed by OS keychain (`keyring` extra); loader lookup fallback to env.
- Files: `dspy_profiles/commands/set_secret.py`, wiring in `cli.py`; docs page.
- Tests: Mark as optional (skip if `keyring` unavailable); basic roundtrip.
- Commit: :sparkles: feat(secrets): add set-secret command with keyring optional extra

4) P2 — CLI shell completion
- Intent: Better UX for heavy CLI users.
- Changes: Document Typer completion; add install instructions (Bash/Zsh/Fish).
- Files: `docs/cli-reference.md` or new `docs/completion.md`.
- Acceptance: Instructions validated locally.
- Commit: :memo: docs: add shell completion instructions for dspy-profiles

5) P2 — Provider‑specific tips
- Intent: Succinct guidance for OpenAI, Anthropic, local models (Ollama), etc.
- Changes: New doc section with minimal examples and gotchas (rate limits, api_base, timeouts).
- Files: `docs/advanced-usage.md` or new `docs/providers.md`.
- Acceptance: Strict build passes; links valid.
- Commit: :memo: docs: add provider-specific tips and examples

6) P2 — Export command & import UX polish
- Intent: Round out profile portability tooling.
- Changes: Implement `dspy-profiles export`; improve conflict resolution prompts on import.
- Files: `dspy_profiles/commands/export.py`, CLI wiring, docs.
- Tests: CLI integration tests covering export/import round-trips.
- Commit: :sparkles: feat(cli): add export command with conflict-aware import flow

—

Completed (for reference)
- Recursive dotted-key normalization with deep merge semantics.
- Cycle detection for profile inheritance chains.
- Async-aware `@with_profile` decorator and tests.
- CI strictly builds docs; docs refreshed with CI guide, examples, API snippets.
- Release readiness plan captured in `plan.md` and changelog updated.

—

Quality checklist (v0.3)
- [x] Deep dotted-key normalization implemented and tested
- [x] Precedence guard test present
- [x] CI runs `mkdocs build --strict`
- [x] CI & Testing guide added and linked in nav
- [x] API examples added for `profile`/`with_profile`/`current_profile`
- [x] Examples page inlines 2 key snippets (or consciously deferred)
