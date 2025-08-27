"""CLI command for deleting a profile."""

from typing import Annotated

from rich.console import Console
import typer

from dspy_profiles import api

console = Console()


def delete_profile(
    profile_name: Annotated[str, typer.Argument(help="The name of the profile to delete.")],
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Delete the profile without prompting for confirmation.",
        ),
    ] = False,
):
    """Deletes a specified profile."""
    if profile_name == "default":
        console.print("[bold red]Error:[/] The 'default' profile cannot be deleted.")
        raise typer.Exit(code=1)

    if not force:
        profile, error = api.get_profile(profile_name)
        if error:
            console.print(f"[bold red]Error:[/] {error}")
            raise typer.Exit(code=1)
        if not typer.confirm(f"Are you sure you want to delete the profile '{profile_name}'?"):
            console.print("Deletion cancelled.")
            raise typer.Exit()

    error = api.delete_profile(profile_name)
    if error:
        console.print(f"[bold red]Error:[/] {error}")
        raise typer.Exit(code=1)

    console.print(f"Profile '{profile_name}' deleted successfully.")
