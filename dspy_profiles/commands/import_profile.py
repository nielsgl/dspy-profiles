"""CLI command for importing a profile from a .env file."""

from pathlib import Path
from typing import Annotated

from dotenv import dotenv_values
from rich.console import Console
import typer

from dspy_profiles.config import ProfileManager, find_profiles_path

console = Console()


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
