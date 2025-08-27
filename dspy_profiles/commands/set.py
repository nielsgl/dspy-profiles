"""CLI command for setting a profile value."""

from typing import Annotated

from rich.console import Console
import typer

from dspy_profiles.config import ProfileManager, find_profiles_path

console = Console()


def set_value(
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
