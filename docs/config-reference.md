# Configuration Reference

This page provides a concise reference for authoring `profiles.toml`.
It complements the Quickstart and Advanced Usage guides with a single place
to look up supported sections and keys.

## Structure

A `profiles.toml` file defines one or more named profiles. Each profile may
optionally extend another profile. Sections are grouped by concern:

- `lm`: Language Model configuration
- `rm`: Retrieval Model configuration
- `settings`: Additional DSPy settings (passed to `dspy.settings.configure(...)`)

Example

```toml title="~/.dspy/profiles.toml"
[default]

[default.lm]
model = "openai/gpt-4o-mini"
api_base = "https://api.openai.com/v1"
# Consider using env vars for secrets
api_key = "${OPENAI_API_KEY}"

[default.settings]
cache_dir = "~/.cache/dspy/default"

[prod]
extends = "default"

[prod.lm]
model = "anthropic/claude-3-opus"
```

## Inheritance

- Use `extends = "<parent>"` to inherit values from another profile.
- Child values override parent values (deep merge of nested tables).
- A profile cannot extend itself.

## Language Model (lm)

- `model: str | None` — Model identifier (e.g., `openai/gpt-4o-mini`).
- `api_base: str | None` — API base URL when required by a provider.
- `api_key: str | None` — API key. Prefer environment variables over plaintext.
- Extra keys are passed as keyword args to `dspy.LM(...)`.

Example

```toml
[dev.lm]
model = "openai/gpt-4o-mini"
api_key = "${OPENAI_API_KEY}"
# Any other kwargs supported by dspy.LM
temperature = 0.7
```

## Retrieval Model (rm)

Two equivalent ways to specify the retrieval model class:

- `class_name: str | None` — Fully-qualified or `dspy.*` class (e.g., `ColBERTv2`).
- `model: str | None` — Optional shorthand if your workflow uses a named model.
- Extra keys are forwarded as kwargs to the RM constructor.

Examples

```toml
[dev.rm]
class_name = "ColBERTv2"
url = "http://localhost:8893/api/search"
```

```toml
[dev.rm]
class_name = "my_package.retrieval.CustomRM"
index = "my-index"
```

## DSPy Settings (settings)

Everything under `settings` is passed to `dspy.settings.configure(**settings)`.
Common keys include `cache_dir` and any other runtime flags supported by DSPy.

```toml
[dev.settings]
cache_dir = "~/.cache/dspy/dev"
```

## Dotted Keys

Dotted TOML syntax is supported and normalized internally. These are equivalent:

```toml
[dev.lm]
model = "openai/gpt-4o-mini"
```

```toml
[dev]
lm.model = "openai/gpt-4o-mini"
```

> Nested dotted keys are fully recursive, so paths like `retrieval.settings.timeout.limit` resolve to the expected nested dictionaries.

## Discovery & Precedence

When resolving the configuration file, precedence is:

1. `DSPY_PROFILES_PATH` environment variable
2. Local discovery: `profiles.toml` in the current directory or its parents
3. Global default: `~/.dspy/profiles.toml`

Use `dspy-profiles which-config` to see which file is used.

## Environment Variables and .env

- `dspy-profiles` automatically loads variables from a local `.env` if present.
- You can import a profile directly from a `.env` using:

```bash
dspy-profiles import --profile from_env --from .env
```

## Security Tips

- Prefer environment variables to store secrets (`${OPENAI_API_KEY}`) and avoid
  committing plaintext keys in `profiles.toml`.
- Keep `profiles.toml` out of version control if it contains secrets.
- Optional: consider installing with the `keyring` extra and storing secrets in
  your OS keychain for improved security.
