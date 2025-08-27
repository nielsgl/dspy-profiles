"""CLI command for importing a profile from a .env file."""

from pathlib import Path
from typing import Annotated

from rich.console import Console
import typer

from dspy_profiles import api

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
    error = api.import_profile(profile_name, from_path)
    if error:
        if "already exists" in error:
            console.print(f"[bold red]Error:[/] {error}")
            raise typer.Exit(code=1)
        else:
            console.print(f"[yellow]Warning:[/] {error}")
            return

    console.print(
        f"[bold green]Success![/bold green] Profile '{profile_name}' imported from '{from_path}'."
    )
    console.print(f"You can view it with: [bold]dspy-profiles show {profile_name}[/bold]")
