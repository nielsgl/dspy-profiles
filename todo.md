# dspy-profiles: Pre-Launch TODOs (Staff Review)

Priorities: P0 = launch blocker, P1 = launch polish, P2 = post‑launch.
Each item includes intent and acceptance criteria. Use Commitizen + gitmoji for commits.

P0 — Must Ship

- Docs: Add Configuration Reference — DONE
  - Intent: Single-page reference for `profiles.toml` schema and semantics.
  - Changes: Added `docs/config-reference.md`; wired into nav under Reference.
  - Accept: Page present and examples render correctly.

- Docs: State Requirements + .env behavior — DONE
  - Intent: Make Python/DSPy versions and .env autoload explicit.
  - Changes: Added Requirements to README and Quickstart; note on `.env` autoload/import.
  - Accept: README and Quickstart show the new sections.

- Tests: Verify suite is green locally
  - Intent: Ensure `pytest` passes with coverage ≥ 90% (configured in `pyproject.toml`).
  - Accept: `uv run pytest -q` passes; coverage gate satisfied.
  - Note: Not executed in this environment; run locally or via CI.

P1 — Launch Polish

- CI: Enforce docs build with `--strict`
  - Intent: Catch broken links/anchors before deploy.
  - Accept: Add step `uv run mkdocs build --strict` before `gh-deploy`.

- Docs: “CI & Testing” guide
  - Intent: Show using `dspy-run` in CI and tests; clarify Python vs non‑Python commands.
  - Accept: New page under User Guide with GitHub Actions and `pytest` examples.

- Docs: API examples for `profile`, `with_profile`, `current_profile`
  - Intent: Complement auto‑generated API with short, copy‑pasteable snippets.
  - Accept: Snippets added near the top of `docs/api-reference.md` with anchors.

- Docs: Examples page inline snippets (optional)
  - Intent: Showcase 2–3 key examples inline via snippet include.
  - Accept: `examples/hello_world.py` and `examples/hello_runner.py` embedded; others remain listed.

- README: Quick links to Reference pages
  - Intent: Faster navigation for new users.
  - Accept: Add links to CLI Reference and Configuration Reference.

P2 — Post‑Launch Enhancements

- Secrets: Optional keyring integration
  - Intent: Provide a `set-secret` flow backed by OS keychain (matches `keyring` extra).
  - Accept: CLI command and docs; secure prompts; tests gated behind optional extra.

- CLI: Shell completion
  - Intent: Improve UX for heavy CLI users.
  - Accept: Provide completion install instructions (Bash/Zsh/Fish) and enable Typer completion if desired.

- Docs: Provider‑specific tips
  - Intent: Add succinct guidance for common providers (OpenAI, Anthropic, local models).
  - Accept: Dedicated section with minimal examples and gotchas.

—

Suggested commit messages

- :memo: docs: add configuration reference and requirements
- :wrench: ci: add strict docs build before deploy
- :memo: docs: add CI & testing guide with dspy-run examples
