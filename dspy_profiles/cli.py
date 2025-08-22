import rich
from rich.console import Console
from rich.table import Table
import typer

from dspy_profiles.config import get_manager

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
    profile_name: str = typer.Option("default", "--profile", "-p"),
    force: bool = typer.Option(False, "--force", "-f"),
):
    """Initializes a new profile."""
    manager = get_manager()
    if manager.get(profile_name) and not force:
        console.print(f"Profile '{profile_name}' already exists. Use --force to overwrite.")
        return

    manager.set(profile_name, {})
    console.print(f"Profile '{profile_name}' initialized successfully.")


def main():
    app()
