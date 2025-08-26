from difflib import unified_diff
import json
import os
from pathlib import Path
import subprocess
from typing import Annotated

from dotenv import dotenv_values
from pydantic import ValidationError
import rich
from rich.console import Console
from rich.table import Table
from rich.text import Text
import toml
import typer

from dspy_profiles.config import PROFILES_PATH, ProfileManager, find_profiles_path
from dspy_profiles.validation import ProfilesFile

app = typer.Typer(
    name="dspy-profiles",
    help="A CLI for managing DSPy profiles.",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="markdown",
)
console = Console()


@app.command()
def list():
    """Lists all available profiles and their core details."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    all_profiles = manager.load()
    if not all_profiles:
        console.print("[yellow]No profiles found. Use 'dspy-profiles init' to create one.[/yellow]")
        return

    table = Table("Profile Name", "Language Model (LM)", "Extends")
    for name, profile_data in all_profiles.items():
        lm = profile_data.get("lm", {}).get("model", "[grey50]Not set[/grey50]")
        extends = profile_data.get("extends", "[grey50]None[/grey50]")
        table.add_row(name, lm, extends)

    console.print(table)


@app.command()
def show(
    profile_name: Annotated[str, typer.Argument(help="The name of the profile to display.")],
):
    """Shows the full configuration details of a specific profile."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    profile_data = manager.get(profile_name)
    if not profile_data:
        console.print(f"[bold red]Error:[/] Profile '{profile_name}' not found.")
        raise typer.Exit(code=1)

    console.print(f"[bold]Profile: {profile_name}[/bold]")
    rich.print(profile_data)


@app.command()
def delete(
    profile_name: Annotated[str, typer.Argument(help="The name of the profile to delete.")],
):
    """Deletes a specified profile."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    if not manager.delete(profile_name):
        console.print(f"[bold red]Error:[/] Profile '{profile_name}' not found.")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Success![/bold green] Profile '{profile_name}' deleted.")


@app.command()
def set(
    profile_name: Annotated[str, typer.Argument(help="The name of the profile to modify.")],
    key: Annotated[str, typer.Argument(help="The configuration key to set (e.g., 'lm.model').")],
    value: Annotated[str, typer.Argument(help="The value to set for the key.")],
):
    """Sets a configuration value for a given profile."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    profile_data = manager.get(profile_name) or {}

    keys = key.split(".")
    current_level = profile_data
    for k in keys[:-1]:
        current_level = current_level.setdefault(k, {})

    current_level[keys[-1]] = value

    manager.set(profile_name, profile_data)
    console.print(f"Updated [bold cyan]{key}[/bold cyan] in profile '{profile_name}'.")


@app.command()
def init(
    profile_name: Annotated[
        str,
        typer.Option(
            "--profile", "-p", help="The name for the new profile.", show_default="default"
        ),
    ] = "default",
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite the profile if it already exists.",
        ),
    ] = False,
):
    """Initializes a new profile interactively."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    if manager.get(profile_name) and not force:
        console.print(
            f"[bold red]Error:[/] Profile '{profile_name}' already exists. "
            "Use --force to overwrite."
        )
        raise typer.Exit(code=1)

    console.print(f"Configuring profile: [bold]{profile_name}[/bold]")

    model = typer.prompt("Enter the language model (e.g., openai/gpt-4o-mini)")
    api_base = typer.prompt(
        "Enter the API base (optional, for local models)", default="", show_default=False
    )

    new_config = {"lm": {"model": model}}
    if api_base:
        new_config["lm"]["api_base"] = api_base

    manager.set(profile_name, new_config)

    provider = model.split("/")[0].upper()
    api_key_name = f"{provider}_API_KEY"

    console.print(f"\n[bold green]Success![/bold green] Profile '{profile_name}' saved.")
    console.print(
        f"To use this profile, make sure to set the [bold]{api_key_name}[/bold] "
        "environment variable."
    )
    console.print(
        f"You can view your new profile with: [bold]dspy-profiles show {profile_name}[/bold]"
    )


@app.command(name="import")
def import_profile(
    profile_name: Annotated[
        str, typer.Option(..., "--profile", "-p", help="The name for the new profile.")
    ],
    from_path: Annotated[
        Path,
        typer.Option(
            "--from",
            help="The path to the .env file to import from.",
            exists=True,
            readable=True,
            dir_okay=False,
        ),
    ] = Path(".env"),
):
    """Imports a profile from a .env file."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    if manager.get(profile_name):
        console.print(f"[bold red]Error:[/] Profile '{profile_name}' already exists.")
        raise typer.Exit(code=1)

    env_values = dotenv_values(from_path)
    if not env_values:
        console.print(f"[yellow]Warning:[/] No values found in '{from_path}'.")
        return

    new_profile = {}
    for key, value in env_values.items():
        if key.upper().startswith("DSPY_"):
            parts = key.upper().split("_")[1:]
            if len(parts) < 2:
                continue

            section = parts[0].lower()
            config_key = "_".join(parts[1:]).lower()

            if section not in new_profile:
                new_profile[section] = {}
            new_profile[section][config_key] = value

    if not new_profile:
        console.print(
            f"[yellow]Warning:[/] No variables with the 'DSPY_' prefix found in '{from_path}'."
        )
        return

    manager.set(profile_name, new_profile)
    console.print(
        f"[bold green]Success![/bold green] Profile '{profile_name}' imported from '{from_path}'."
    )
    console.print(f"You can view it with: [bold]dspy-profiles show {profile_name}[/bold]")


@app.command()
def diff(
    profile_a_name: Annotated[str, typer.Argument(help="The first profile to compare.")],
    profile_b_name: Annotated[str, typer.Argument(help="The second profile to compare.")],
):
    """Compares two profiles and highlights their differences."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    profile_a = manager.get(profile_a_name)
    profile_b = manager.get(profile_b_name)

    if not profile_a:
        console.print(f"[bold red]Error:[/] Profile '{profile_a_name}' not found.")
        raise typer.Exit(code=1)
    if not profile_b:
        console.print(f"[bold red]Error:[/] Profile '{profile_b_name}' not found.")
        raise typer.Exit(code=1)

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
    for line in diff:
        if line.startswith("+"):
            diff_text.append(line, style="green")
        elif line.startswith("-"):
            diff_text.append(line, style="red")
        elif line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
            diff_text.append(line, style="cyan")
        else:
            diff_text.append(line)

    console.print(diff_text)


@app.command()
def validate(
    config_path: Annotated[
        Path,
        typer.Option(
            "--config",
            "-c",
            help="Path to the profiles.toml file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ] = PROFILES_PATH,
):
    """Validates the structure and content of the profiles.toml file."""
    console.print(f"Validating profiles at: [cyan]{config_path}[/cyan]")
    try:
        with open(config_path) as f:
            data = toml.load(f)

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
        console.print(f"[bold red]Error:[/] Invalid TOML format in '{config_path}':\n  {e}")
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
    profile_name: Annotated[str, typer.Argument(help="The name of the profile to test.")],
):
    """Tests connectivity to the language model for a given profile."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    if not manager.get(profile_name):
        console.print(f"[bold red]Error:[/] Profile '{profile_name}' not found.")
        raise typer.Exit(code=1)

    from dspy_profiles.core import profile as activate_profile

    console.print(f"Testing profile: [bold cyan]{profile_name}[/bold cyan]...")

    try:
        with activate_profile(profile_name):
            import dspy

            lm = dspy.settings.lm
            if not lm:
                console.print(
                    f"[bold red]Error:[/] No language model configured for profile "
                    f"'{profile_name}'."
                )
                raise typer.Exit(1)

            console.print(f"  - Using model: [yellow]{lm.model}[/yellow]")
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
    profile_name: Annotated[
        str,
        typer.Option(..., "--profile", "-p", help="The profile to activate for the command."),
    ],
):
    """Executes a command with the specified profile's environment variables."""
    command = ctx.args
    if not command:
        console.print("[bold red]Error:[/] No command provided to run.")
        raise typer.Exit(1)

    env = os.environ.copy()
    env["DSPY_PROFILE"] = profile_name

    try:
        result = subprocess.run(command, env=env, check=False, capture_output=True, text=True)
        if result.stdout:
            console.print(result.stdout, end="")
        if result.stderr:
            console.print(result.stderr, style="bold red", end="")
        if result.returncode != 0:
            raise typer.Exit(result.returncode)
    except FileNotFoundError:
        cmd_str = " ".join(command)
        console.print(f"[bold red]Error:[/] Command not found: '{cmd_str}'")
        raise typer.Exit(1)


def main():
    app()
