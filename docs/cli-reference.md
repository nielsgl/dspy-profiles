# CLI Reference

This page provides a detailed reference for all commands available in the `dspy-profiles` command-line interface.

## `dspy-profiles init`

Initializes a new profile through an interactive wizard. This is the recommended way to create your first profile.

```bash
dspy-profiles init
```

### Options

-   `--profile <profile_name>`: The name of the profile to create. If not provided, it will default to `default`.
-   `--force`: Overwrite the profile if it already exists.

### Interactive Prompts

The wizard will guide you through setting up the essential components of your profile, such as the language model and API base. It will also provide guidance on setting the necessary environment variables for API keys.

**Example:**
```bash
$ dspy-profiles init --profile staging
Configuring profile: staging
Enter the language model (e.g., openai/gpt-4o-mini): anthropic/claude-3-opus
Enter the API base (optional, for local models):

Success! Profile 'staging' saved.
To use this profile, make sure to set the ANTHROPIC_API_KEY environment variable.
```

## `dspy-profiles list`

Lists all available profiles found in your `~/.dspy/profiles.toml` file, providing a quick overview of your configured environments.

```bash
dspy-profiles list
```

**Example Output:**
```
 Profile Name   Details
────────────────────────────────────────
 default        LM: openai/gpt-4o-mini
 staging        LM: anthropic/claude-3-opus
 prod           LM: cohere/command-r
```

## `dspy-profiles show`

Displays the fully resolved configuration for a specific profile, showing all the settings that will be applied.

```bash
dspy-profiles show <profile_name>
```

### Arguments

-   `<profile_name>`: The name of the profile to display.

**Example:**
```bash
$ dspy-profiles show default
Profile: default
{
    "lm": {
        "model": "openai/gpt-4o-mini",
        "temperature": 0.7
    }
}
```

## `dspy-profiles set`

Sets or updates a single configuration value within a profile using dot notation. This is useful for making quick adjustments without manually editing the TOML file.

```bash
dspy-profiles set <profile_name> <key> <value>```

### Arguments

-   `<profile_name>`: The name of the profile to modify.
-   `<key>`: The configuration key to set (e.g., `lm.model`, `settings.temperature`).
-   `<value>`: The new value to set.

**Example:**
```bash
$ dspy-profiles set default lm.temperature=0.8
Updated 'lm.temperature' in profile 'default'.
```

## `dspy-profiles delete`

Permanently deletes a profile from your configuration file.

```bash
dspy-profiles delete <profile_name>
```

### Arguments

-   `<profile_name>`: The name of the profile to delete.

## `dspy-profiles diff`

Compares two profiles and shows a color-coded, line-by-line diff of their configurations. This is extremely useful for identifying differences between environments (e.g., `staging` vs. `prod`).

```bash
dspy-profiles diff <profile_a> <profile_b>```

### Arguments

-   `<profile_a>`: The first profile to compare.
-   `<profile_b>`: The second profile to compare.

## `dspy-profiles import`

Creates a new profile by reading variables from a `.env` file. The command looks for variables with a `DSPY_` prefix and maps them to the profile's configuration.

The mapping follows the convention `DSPY_{SECTION}_{KEY}` -> `section.key`. For example, `DSPY_LM_MODEL` becomes `lm.model`.

```bash
dspy-profiles import --profile <new_profile_name> --from <path_to_env_file>
```

### Options

-   `--profile <new_profile_name>`: **(Required)** The name for the new profile being created.
-   `--from <path_to_env_file>`: The path to the `.env` file to import from. Defaults to `.env` in the current directory.

**Example `.env` file:**
```dotenv
# .env
DSPY_LM_MODEL=openai/gpt-4o-mini
DSPY_SETTINGS_TEMPERATURE=0.7
```

**Example command:**
```bash
$ dspy-profiles import --profile from_env
Success! Profile 'from_env' imported from '.env'.
```

## `dspy-profiles run`

Executes a command with a specific profile activated. It works by setting the `DSPY_PROFILE` environment variable for the subprocess, which ensures that any DSPy application run by the command will use the specified profile.

```bash
dspy-profiles run --profile <profile_name> -- <command_to_run> [args...]
```

### Options

-   `--profile <profile_name>`: **(Required)** The name of the profile to activate for the command.

### The `--` Separator

It is crucial to use the `--` separator between the `run` command's options and the command you want to execute. This tells `dspy-profiles` to treat everything after `--` as the command to be run.

**Examples:**

```bash
# Run a python script with the 'prod' profile
dspy-profiles run --profile prod -- python my_app.py --input data.json

# Run pytest for your DSPy tests with a dedicated 'test' profile
dspy-profiles run --profile test -- pytest -v tests/
```
