"""CLI command for setting a profile value."""

from typing import Annotated

import rich
from rich.console import Console
import typer

from dspy_profiles import api

console = Console()


def set_value(
    profile_name: Annotated[str, typer.Argument(help="The name of the profile to modify.")],
    key: Annotated[str, typer.Argument(help="The configuration key to set (e.g., 'lm.model').")],
    value: Annotated[str, typer.Argument(help="The value to set for the key.")],
):
    """Sets or updates a configuration value for a given profile."""
    # Note: The underlying API function is currently bugged and will be fixed in a later phase.
    updated_profile, error = api.update_profile(profile_name, key, value)
    if error:
        console.print(f"[bold red]Error:[/] {error}")
        raise typer.Exit(code=1)

    console.print(f"Profile '{profile_name}' updated successfully.")
    rich.print(updated_profile)
