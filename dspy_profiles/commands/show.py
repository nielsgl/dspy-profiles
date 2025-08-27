"""CLI command for showing a profile."""

from typing import Annotated

import rich
from rich.console import Console
import typer

from dspy_profiles import api

console = Console()


def show_profile(
    profile_name: Annotated[str, typer.Argument(help="The name of the profile to display.")],
):
    """Shows the full configuration details of a specific profile."""
    profile_data, error = api.get_profile(profile_name)
    if error:
        console.print(f"[bold red]Error:[/] {error}")
        raise typer.Exit(code=1)

    console.print(f"[bold]Profile: {profile_name}[/bold]")
    rich.print(profile_data)
