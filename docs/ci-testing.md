# CI & Testing

This guide shows how to run automated tests and continuous integration workflows with `dspy-profiles`.

## Local & CI Test Runs

Use `dspy-run` to activate profiles around your test suite without touching application code:

```bash
# Run pytest with the "ci" profile
uv run dspy-run --profile ci -- pytest -q --maxfail=1
```

- Python entry points (`*.py`) are wrapped automatically; non-Python commands receive the `DSPY_PROFILE` environment variable.
- Combine `--dry-run` with `--profile` to inspect the resolved command and configuration before executing.
- If your tests rely on `.env` files, keep them next to the project root—`dspy-profiles` auto-loads them before activating a profile.

## Setting Profiles in Other Tools

Some tools read `DSPY_PROFILE` directly. Export it once and run the tool normally:

```bash
export DSPY_PROFILE=ci
pytest -q
```

`dspy-run` keeps both approaches consistent: the CLI sets `DSPY_PROFILE` for subprocesses while Python scripts are wrapped in the context manager.

## Example GitHub Actions Workflow

```yaml
ame: ci

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true

      - name: Install dependencies
        run: uv sync --group dev --all-extras

      - name: Run tests with profiles
        run: uv run dspy-run --profile ci -- pytest --cov --cov-report=xml

      - name: Build docs (strict)
        run: uv run mkdocs build --strict
```

### Tips

- Keep a lightweight `ci` profile in `profiles.toml` with service stubs or dummy API keys for tests.
- Use `dspy-profiles which-config` inside CI to confirm which configuration file is resolved.
- Cache the `.uv` directory between workflow runs to speed up installs.
