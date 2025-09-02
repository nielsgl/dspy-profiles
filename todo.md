# dspy-profiles: Staff-Level Review TODOs

This is a prioritized, actionable checklist derived from a thorough code and docs review. Each item includes intent, proposed change, affected files, and suggested tests or acceptance criteria. Priorities: P0 = must fix, P1 = important polish, P2 = nice-to-have.

1) P0 — Fix profile precedence and default fallback
- Intent: Ensure `profile()` follows documented precedence and always falls back to "default" when nothing is provided.
- Change: Compute final profile name as: use `DSPY_PROFILE` unless `force=True`; otherwise use explicit `profile_name` or "default". Remove early return path.
- Files: `dspy_profiles/core.py:62–68`
- Tests: Add case where `profile(None)` with no env activates empty default (no LM), not a no-op; retain current test expectations.

2) P0 — Correct `dspy.settings.configure` usage (don’t merge LM dict)
- Intent: Avoid polluting DSPy settings with LM keys; rely on `lm`/`rm` parameters to `dspy.context`.
- Change: Do not merge `resolved_profile.lm` into `settings` before calling `configure`. Only configure settings (e.g., `cache_dir`, `retries`). Pass `lm=lm_instance`, `rm=rm_instance` to `dspy.context`.
- Files: `dspy_profiles/core.py:117–125`
- Tests: Validate that settings keys remain only settings and LM is provided via context; predictive calls still work.

3) P0 — Remove production debug prints
- Intent: Prevent noisy stdout in normal use.
- Change: Replace `print("[DEBUG] ...")` with `logging.getLogger(__name__).debug(...)` or remove entirely. Default logger level remains INFO.
- Files: `dspy_profiles/core.py:72–75, 91–103, 123, 236–281`; `dspy_profiles/config.py:43`
- Tests: None (behavioral), verify clean CLI outputs manually.

4) P0 — `lm()` should accept and respect `config_path`
- Intent: Parity with context manager and tests that pass `config_path`.
- Change: Add explicit `config_path: str | Path | None` param to `lm()` and pass to `ProfileLoader(config_path=...)`.
- Files: `dspy_profiles/core.py:218–253`
- Tests: Add a test loading from a temporary config file via `lm(..., config_path=tmp_path)`.

5) P0 — Unify LM instantiation to `dspy.LM(...)`
- Intent: Align with DSPy v3 unified LM; simplify provider heuristics.
- Change: Always instantiate `dspy.LM(model=model, **lm_config)` for both context manager and `lm()` helper.
- Files: `dspy_profiles/core.py:97–103, 269–279`
- Tests: Existing tests using DummyLM and kwargs should continue to pass.

6) P0 — Normalize before validation in API
- Intent: Keep `validate` behavior consistent with loader behavior on dotted keys.
- Change: Apply `normalize_config(data)` before `ProfilesFile.model_validate(data)`.
- Files: `dspy_profiles/api.py:98–116`
- Tests: Add a validation test for dotted keys using `validate_profiles_file`.

7) P0 — Align Retrieval Model schema with docs (or vice versa)
- Intent: Avoid validation failures for documented RM examples (`class_name`, `url`).
- Option A (recommended): Make `RetrievalModelSettings` permissive (optional `model`, allow `class_name`, `url`, and extra keys). Update core to instantiate RM by `class_name` if provided, else by `provider` fallback, else leave RM unset.
- Option B: Require `model` string in docs and code; update docs accordingly and keep schema strict.
- Files: `dspy_profiles/validation.py:24–45`; `dspy_profiles/core.py:104–109`; docs noted below
- Tests: Add unit tests for RM config variants and instantiation.

8) P0 — Remove stray debug print from path resolution
- Intent: Prevent stdout noise in `find_profiles_path` fallback.
- Change: Remove `print(f"{PROFILES_PATH=}")`.
- Files: `dspy_profiles/config.py:43`
- Tests: None.

9) P1 — Fix CLI usage typo in docs (diff command)
- Intent: Correct argument placeholders.
- Change: Replace `dspy-profiles diff <a a> <b b>` with `dspy-profiles diff <a> <b>`.
- Files: `docs/index.md:65`
- Tests: Docs only.

10) P1 — Fix `uvx` invocation in Quickstart
- Intent: Correct usage for `uvx`.
- Change: Use `uvx dspy-profiles --version` (not `uvx run dspy-profiles --version`).
- Files: `docs/quickstart.md:31–38`
- Tests: Docs only.

11) P1 — Fix broken indentation in advanced example
- Intent: Make copy-pasteable Python.
- Change: Indent `__init__` and `forward` inside class in the AdaptiveAgent example.
- Files: `docs/advanced-usage.md:268–297`
- Tests: Docs only.

12) P1 — Clarify `dspy-run` behavior for non-Python commands
- Intent: Set correct expectations for users running tools like `pytest`.
- Change: Explicit note: for non-Python commands, `dspy-run` sets `DSPY_PROFILE` env var; your program should honor it. For Python scripts, `dspy-run` bootstraps via a `profile(...)` wrapper automatically.
- Files: `docs/quickstart.md` (CLI section), `docs/cli-run-reference.md`
- Tests: Add a CLI test asserting env var is set and visible to subprocess (already exists, keep).

13) P1 — Document the `lm()` helper in API Reference
- Intent: Improve discoverability of runtime helpers.
- Change: Add “Runtime helpers” section with examples and caching notes.
- Files: `docs/api-reference.md`
- Tests: Docs only.

14) P1 — Add a Troubleshooting page
- Intent: Reduce support friction for common issues.
- Change: New doc covering: “No LM loaded”, “Profile not found”, “Validation errors”, “Which profiles.toml is used?”, and commands to diagnose.
- Files: `docs/troubleshooting.md` (new), `mkdocs.yml` nav entry
- Tests: Docs only.

15) P1 — Expose the resolved config path for UX
- Intent: Help users understand which file is being used.
- Change: Add `--show-config-path` flag to `list`/`show` or add `dspy-profiles which-config` command that prints resolved path from `find_profiles_path()`.
- Files: `dspy_profiles/cli.py`, new command or options; docs update
- Tests: Unit test that prints the path; patch `find_profiles_path` in tests.

16) P1 — Security guidance for secrets
- Intent: Encourage safe handling of API keys.
- Change: Add docs section recommending env vars, `.env` + `import`, or optional `keyring` extra. Provide example flows.
- Files: `docs/advanced-usage.md` (Security), link from Quickstart
- Tests: Docs only.

17) P1 — Make dotted-key normalization fully recursive
- Intent: Robust handling for arbitrarily deep TOML dotted keys.
- Change: Implement recursive expansion for nested dotted keys in `normalize_config`.
- Files: `dspy_profiles/utils.py`
- Tests: Add tests for 2+ nested levels (e.g., `a.b.c = 1`).

18) P2 — `dspy-run` quality-of-life flags
- Intent: Improve transparency when executing.
- Change: Add `--dry-run` (print command, profile, and path to config) and `--verbose` (echo resolved profile, selected bootstrap path).
- Files: `dspy_profiles/commands/run.py`, docs updates
- Tests: CLI tests for flags.

19) P0 — Decide and document LM provider strategy (policy decision)
- Intent: Consistency between code and docs.
- Choice: Adopt `dspy.LM(...)` universally and remove provider-class dynamic lookup; update docs to reflect the unified LM pattern.
- Files: Code (as in #5), docs (Advanced Usage “Integrating with Any Language Model”).
- Tests: Existing tests remain valid.

20) P0 — Decide and document RM schema and instantiation (policy decision)
- Intent: Consistent RM configuration and validation.
- Choice: Prefer a permissive schema supporting `class_name`/`url` (docs-friendly), or a strict `model`-string schema. Implement instantiation accordingly and document clearly with examples for ColBERTv2 and others.
- Files: `dspy_profiles/validation.py`, `dspy_profiles/core.py` (RM creation), `docs/advanced-usage.md`
- Tests: Add coverage for both accepted config shapes.

21) P1 — Fix example quoting bug
- Intent: Prevent syntax errors in examples.
- Change: Replace `print(f"{os.getenv("DSPY_PROFILE")=}")` with `print(f"{os.getenv('DSPY_PROFILE')=}")`.
- Files: `examples/hello_runner.py:5`
- Tests: Manual run; optional doctest.

22) P1 — Add a minimal RM example aligned with schema
- Intent: Show a working retrieval model configuration users can copy.
- Change: New section in Advanced Usage with a tested config snippet; optionally add a simple example script.
- Files: `docs/advanced-usage.md`, maybe `examples/retrieval_example.py`
- Tests: Docs/example only.

23) P1 — Improve docs on configuration precedence and discovery
- Intent: Make precedence behavior crystal-clear and consistent.
- Change: Consolidate hierarchy details in Quickstart and Index; reference `DSPY_PROFILES_PATH`, parent search, and fallback.
- Files: `docs/index.md`, `docs/quickstart.md`
- Tests: Docs only.

24) P1 — Add acceptance tests for precedence and defaults
- Intent: Guard against regressions in `profile()` precedence.
- Change: Add tests where env var and `force=True` interact; assert default fallback path still yields empty config but not a no-op.
- Files: `tests/test_core.py` (new/modified tests)

25) P1 — Add tests for validation normalization path
- Intent: Ensure `validate_profiles_file` matches loader behavior.
- Change: New tests invoking `validate_profiles_file` on dotted-key TOML.
- Files: `tests/test_api.py` or new test file

26) P1 — Add tests for `lm(config_path=...)`
- Intent: Ensure LM helper respects explicit file paths.
- Change: Construct temp profiles.toml and assert `lm()` reads it.
- Files: `tests/test_core.py`

27) P1 — Update docs build and navigation
- Intent: Keep docs site coherent after new pages.
- Change: Add `troubleshooting.md` to nav, update references, verify `mkdocs.yml` builds cleanly.
- Files: `mkdocs.yml`, new doc
- Tests: Run `mkdocs build` locally.

28) P1 — Update CHANGELOG for upcoming release
- Intent: Communicate changes and fixes.
- Change: Add entries under “Unreleased” or bump version section: core precedence fix, LM config handling, validation normalization, docs fixes, example fixes.
- Files: `CHANGELOG.md`

29) P1 — Bump version after changes
- Intent: Align PyPI and docs.
- Change: Update `pyproject.toml` version and release metadata.
- Files: `pyproject.toml`

30) P2 — Optional: add `which-config` command (ergonomic helper)
- Intent: One-stop command for discovering the active config file.
- Change: Implement `dspy-profiles which-config` printing resolved path, and optionally whether it exists.
- Files: `dspy_profiles/cli.py`, new command; docs update
- Tests: Small CLI test that asserts printed path matches patched resolver.

---

Notes
- Items 5, 19 are coupled: choosing `dspy.LM(...)` as the only LM path simplifies code and aligns with docs.
- Items 7, 20 are coupled: agree on RM shape, then update validation, core instantiation, and docs together.
- Where tests already exist for related behavior, prefer enhancing them rather than duplicating coverage.

---

Decision Update: Config Discovery Precedence (env > local > global)

31) P0 — Align Python API config discovery with CLI (Principle of Least Surprise)
- Intent: Ensure both CLI and Python API resolve `profiles.toml` with the same precedence: `DSPY_PROFILES_PATH` > local discovery (CWD/parents) > global (`~/.dspy/profiles.toml`).
- Change: In `ProfileLoader.__init__`, accept `config_path: Path | None = None`; when None, set `self.config_path = find_profiles_path()` (import from `dspy_profiles.config`). Keep `config_path` override behavior intact. In `core.profile()`/`core.lm()`, rely on loader’s default unless `config_path` is explicitly passed.
- Files: `dspy_profiles/loader.py` (constructor), `dspy_profiles/core.py` (call sites pass-through only), `dspy_profiles/config.py` (no change in precedence implementation).
- Tests: Add/adjust tests verifying API code uses env var when set, local file when present, else global fallback (mirror existing `tests/test_config.py` behavior, but for `ProfileLoader`/`profile()`/`lm()`).

32) P0 — Fix documentation to state env > local > global
- Intent: Make the documented precedence match the implementation and common conventions.
- Change: Update the “Configuration Hierarchy” sections to list: (1) Environment Variable `DSPY_PROFILES_PATH`, (2) Project-Specific File search in CWD and parents, (3) Global default `~/.dspy/profiles.toml`.
- Files: `docs/index.md` and `docs/quickstart.md` (the hierarchy bullet lists).
- Tests: Docs only.

33) P1 — Add `which-config` CLI helper (supersedes item 30 and complements item 15)
- Intent: Improve discoverability by showing the resolved path used by the tool.
- Change: Implement `dspy-profiles which-config` that prints the resolved `profiles.toml` path from `find_profiles_path()`, and whether it exists. Prefer this over adding flags to `list`/`show` (item 15 becomes optional supplement).
- Files: `dspy_profiles/cli.py` (new command), docs (`docs/cli-reference.md`, mention in Quickstart/Index as needed).
- Tests: Add CLI test asserting output matches a patched resolver and correct existence status.
