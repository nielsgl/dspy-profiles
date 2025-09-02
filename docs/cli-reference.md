The `dspy-profiles` CLI manages profiles and includes global verbosity
controls. Use `-V/--verbose` (once for INFO, twice for DEBUG), `-q/--quiet`
for ERROR, or `--log-level` to set an explicit level. Use `which-config` to
print the resolved `profiles.toml` path.

::: mkdocs-typer2
    :module: dspy_profiles.cli
    :name: dspy-profiles
