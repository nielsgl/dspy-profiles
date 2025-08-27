"""CLI command for deleting a profile."""

from typing import Annotated

from rich.console import Console
import typer

from dspy_profiles.config import ProfileManager, find_profiles_path

console = Console()


def delete_profile(
    profile_name: Annotated[str, typer.Argument(help="The name of the profile to delete.")],
):
    """Deletes a specified profile."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    if not manager.delete(profile_name):
        console.print(f"[bold red]Error:[/] Profile '{profile_name}' not found.")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Success![/bold green] Profile '{profile_name}' deleted.")
