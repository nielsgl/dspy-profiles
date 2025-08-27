"""CLI command for showing a profile."""

from typing import Annotated

import rich
from rich.console import Console
import typer

from dspy_profiles.config import ProfileManager, find_profiles_path

console = Console()


def show_profile(
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
