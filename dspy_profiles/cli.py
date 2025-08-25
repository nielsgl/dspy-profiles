from pathlib import Path
import subprocess

from dotenv import dotenv_values
from pydantic import ValidationError
import rich
from rich.console import Console
from rich.table import Table
import toml
import typer

from dspy_profiles.config import PROFILES_PATH, get_manager
from dspy_profiles.validation import ProfilesFile

app = typer.Typer()
console = Console()


@app.command()
def list():
    """Lists all available profiles."""
    manager = get_manager()
    all_profiles = manager.load()
    if not all_profiles:
        console.print("No profiles found.")
        return

    table = Table("Profile Name", "Details")
    for name, profile_data in all_profiles.items():
        details = f"LM: {profile_data.get('lm', {}).get('model', 'Not set')}"
        table.add_row(name, details)

    console.print(table)


@app.command()
def show(profile_name: str):
    """Shows the details of a specific profile."""
    manager = get_manager()
    profile_data = manager.get(profile_name)
    if not profile_data:
        console.print(f"Profile '{profile_name}' not found.")
        raise typer.Exit(code=1)

    console.print(f"[bold]Profile: {profile_name}[/bold]")
    rich.print(profile_data)


@app.command()
def delete(profile_name: str):
    """Deletes a profile."""
    manager = get_manager()
    if not manager.delete(profile_name):
        console.print(f"Profile '{profile_name}' not found.")
        raise typer.Exit(code=1)

    console.print(f"Profile '{profile_name}' deleted successfully.")


@app.command()
def set(profile_name: str, key: str, value: str):
    """Sets a configuration value in a profile."""
    manager = get_manager()
    profile_data = manager.get(profile_name) or {}

    keys = key.split(".")
    current_level = profile_data
    for k in keys[:-1]:
        current_level = current_level.setdefault(k, {})

    current_level[keys[-1]] = value

    manager.set(profile_name, profile_data)
    console.print(f"Updated '{key}' in profile '{profile_name}'.")


@app.command()
def init(
    profile_name: str = typer.Option(
        "default", "--profile", "-p", prompt="Enter a name for the new profile"
    ),
    force: bool = typer.Option(False, "--force", "-f"),
):
    """Initializes a new profile interactively."""
    manager = get_manager()
    if manager.get(profile_name) and not force:
        console.print(f"Profile '{profile_name}' already exists. Use --force to overwrite.")
        return

    console.print(f"Configuring profile: [bold]{profile_name}[/bold]")

    model = typer.prompt("Enter the language model (e.g., openai/gpt-4o-mini)")
    api_base = typer.prompt(
        "Enter the API base (optional, for local models)", default="", show_default=False
    )

    new_config = {"lm": {"model": model}}
    if api_base:
        new_config["lm"]["api_base"] = api_base

    manager.set(profile_name, new_config)

    # Provide guidance on setting the API key
    provider = model.split("/")[0].upper()
    if provider not in ["OPENAI", "ANTHROPIC", "COHERE"]:  # Add more as needed
        console.print(
            f"\n[yellow]Warning:[/] Could not determine the API key for provider '{provider}'."
        )
        console.print(
            "Please consult your provider's documentation and set the appropriate"
            " environment variable."
        )
    else:
        console.print(f"\n[bold green]Success![/bold green] Profile '{profile_name}' saved.")
        console.print(
            f"To use this profile, make sure to set the [bold]{provider}_API_KEY[/bold]"
            " environment variable."
        )

    console.print(f"You can view your new profile with: dspy-profiles show {profile_name}")


def main():
    app()


@app.command(name="import")
def import_profile(
    profile_name: str = typer.Option(..., "--profile", "-p", help="The name for the new profile."),
    from_path: Path = typer.Option(
        ".env",
        "--from",
        help="The path to the .env file to import from.",
        exists=True,
        readable=True,
        dir_okay=False,
    ),
):
    """Imports a profile from a .env file."""
    manager = get_manager()
    if manager.get(profile_name):
        console.print(f"[bold red]Error:[/] Profile '{profile_name}' already exists.")
        raise typer.Exit(code=1)

    env_values = dotenv_values(from_path)
    if not env_values:
        console.print(f"No values found in '{from_path}'.")
        return

    new_profile = {}
    for key, value in env_values.items():
        if key.upper().startswith("DSPY_"):
            parts = key.upper().split("_")[1:]  # Remove DSPY_ and split
            if len(parts) < 2:
                continue  # Must have at least a section and a key (e.g., LM_MODEL)

            section = parts[0].lower()
            config_key = "_".join(parts[1:]).lower()

            if section not in new_profile:
                new_profile[section] = {}
            new_profile[section][config_key] = value

    if not new_profile:
        console.print(f"No variables with the 'DSPY_' prefix found in '{from_path}'.")
        return

    manager.set(profile_name, new_profile)
    console.print(
        f"[bold green]Success![/bold green] Profile '{profile_name}' imported from '{from_path}'."
    )
    console.print(f"You can view the new profile with: dspy-profiles show {profile_name}")


@app.command()
def diff(
    profile_a_name: str = typer.Argument(..., help="The first profile to compare."),
    profile_b_name: str = typer.Argument(..., help="The second profile to compare."),
):
    """Compares two profiles and shows the differences."""
    manager = get_manager()
    profile_a = manager.get(profile_a_name)
    profile_b = manager.get(profile_b_name)

    if not profile_a:
        console.print(f"[bold red]Error:[/] Profile '{profile_a_name}' not found.")
        raise typer.Exit(code=1)
    if not profile_b:
        console.print(f"[bold red]Error:[/] Profile '{profile_b_name}' not found.")
        raise typer.Exit(code=1)

    from difflib import unified_diff
    import json

    from rich.text import Text

    json_a = json.dumps(profile_a, indent=2, sort_keys=True)
    json_b = json.dumps(profile_b, indent=2, sort_keys=True)

    if json_a == json_b:
        console.print("[bold green]Profiles are identical.[/bold green]")
        return

    diff = unified_diff(
        json_a.splitlines(keepends=True),
        json_b.splitlines(keepends=True),
        fromfile=profile_a_name,
        tofile=profile_b_name,
    )

    diff_text = Text()
    diff_iterator = iter(diff)
    try:
        # Skip the '---' and '+++' header lines
        next(diff_iterator)
        next(diff_iterator)
    except StopIteration:
        pass  # Handle cases with very short diffs

    for line in diff_iterator:
        if line.startswith("+"):
            diff_text.append(line, style="green")
        elif line.startswith("-"):
            diff_text.append(line, style="red")
        elif line.startswith("?"):
            continue  # Skip the line number info
        else:
            diff_text.append(line)

    console.print(diff_text)


@app.command()
def validate(
    config_path: Path = typer.Option(
        PROFILES_PATH,
        "--config",
        "-c",
        help="Path to the profiles.toml file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
):
    """Validate the profiles.toml file against the schema."""
    console.print(f"Validating profiles at: [cyan]{config_path}[/cyan]")
    try:
        with open(config_path) as f:
            data = toml.load(f)

        # Pydantic model expects a top-level key, let's call it 'profiles'
        # The TOML file structure is [profile.name], which toml loads as {'profile': {'name': ...}}
        # We need to restructure it for the model.
        if "profile" in data:
            profiles_data = {"profiles": data["profile"]}
        else:
            profiles_data = {"profiles": {}}

        ProfilesFile.model_validate(profiles_data)
        console.print("[bold green]✅ Success![/bold green] All profiles are valid.")

    except FileNotFoundError:
        console.print(f"[bold red]Error:[/] Configuration file not found at '{config_path}'.")
        raise typer.Exit(1)
    except toml.TomlDecodeError as e:
        console.print(f"[bold red]Error:[/] Invalid TOML format in '{config_path}':")
        console.print(f"  {e}")
        raise typer.Exit(1)
    except ValidationError as e:
        console.print(f"[bold red]❌ Validation Failed:[/] Found {e.error_count()} error(s).")
        for error in e.errors():
            loc = " -> ".join(map(str, error["loc"]))
            console.print(f"  - [bold cyan]{loc}[/bold cyan]: {error['msg']}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/] {e}")
        raise typer.Exit(1)


@app.command()
def test(
    profile_name: str = typer.Argument(..., help="The name of the profile to test."),
):
    """Tests the connectivity for a given profile."""
    from dspy_profiles.core import profile as activate_profile

    console.print(f"Testing profile: [bold cyan]{profile_name}[/bold cyan]...")

    try:
        with activate_profile(profile_name):
            import dspy

            lm = dspy.settings.lm
            if not lm:
                console.print(
                    f"[bold red]Error:[/] No language model (LM) configured for profile "
                    f"'{profile_name}'."
                )
                raise typer.Exit(1)

            console.print(f"  - Using model: [yellow]{lm.model}[/yellow]")
            # A simple, low-token request to test connectivity
            lm("Say 'ok'")

        console.print("[bold green]✅ Success![/bold green] Connectivity test passed.")

    except Exception as e:
        console.print(
            f"\n[bold red]❌ Test Failed:[/] Could not connect using profile '{profile_name}'."
        )
        console.print(f"  [bold]Reason:[/] {e}")
        raise typer.Exit(1)


@app.command(
    name="run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def run_command(
    ctx: typer.Context,
    profile_name: str = typer.Option(..., "--profile", "-p", help="The profile to activate."),
):
    """Executes a command with the specified profile activated."""
    command = ctx.args
    if not command:
        console.print("[bold red]Error:[/bold red] No command provided to run.")
        raise typer.Exit(1)

    import os

    env = os.environ.copy()
    env["DSPY_PROFILE"] = profile_name

    try:
        result = subprocess.run(command, env=env, check=False, capture_output=True, text=True)
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(result.stderr, style="bold red")
        if result.returncode != 0:
            raise typer.Exit(result.returncode)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/] Command not found: '{command}'")
        raise typer.Exit(1)
