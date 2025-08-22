from rich.console import Console
from rich.table import Table
import typer

from dspy_profiles import profiles

app = typer.Typer()
console = Console()


@app.command()
def list():
    """Lists all available profiles."""
    all_profiles = profiles.load_profiles()
    if not all_profiles:
        console.print("No profiles found.")
        return

    table = Table("Profile Name", "Details")
    for name, config in all_profiles.items():
        # For now, just show a simple summary. We can make this more detailed later.
        details = f"LM: {config.get('lm', {}).get('model', 'Not set')}"
        table.add_row(name, details)

    console.print(table)


@app.command()
def show(profile_name: str = typer.Argument(..., help="The name of the profile to show.")):
    """Shows the details of a specific profile."""
    profile_config = profiles.get_profile(profile_name)
    if not profile_config:
        console.print(f"Profile '{profile_name}' not found.")
        raise typer.Exit(code=1)

    console.print(f"[bold]Profile: {profile_name}[/bold]")

    # We can use rich's print to render the dict nicely
    import rich

    rich.print(profile_config)


@app.command()
def delete(profile_name: str = typer.Argument(..., help="The name of the profile to delete.")):
    """Deletes a profile."""
    if profiles.delete_profile(profile_name):
        console.print(f"Profile '{profile_name}' deleted successfully.")
    else:
        console.print(f"Profile '{profile_name}' not found.")
        raise typer.Exit(code=1)


@app.command()
def set(
    profile_name: str = typer.Argument(..., help="The name of the profile to update."),
    key: str = typer.Argument(..., help="The key to set (e.g., 'lm.model')."),
    value: str = typer.Argument(..., help="The value to set."),
):
    """Sets a configuration value in a profile."""
    config = profiles.get_profile(profile_name) or {}

    # Handle dot notation for nested keys
    keys = key.split(".")
    current_level = config
    for k in keys[:-1]:
        current_level = current_level.setdefault(k, {})

    # TODO: We should probably handle type casting here (e.g., for numbers, booleans)
    current_level[keys[-1]] = value

    profiles.save_profile(profile_name, config)
    console.print(f"Updated '{key}' in profile '{profile_name}'.")


@app.command()
def init(
    profile_name: str = typer.Option(
        "default", "--profile", "-p", help="The name of the profile to initialize."
    )
):
    """Initializes a new profile."""
    if profiles.get_profile(profile_name):
        overwrite = typer.confirm(f"Profile '{profile_name}' already exists. Overwrite?")
        if not overwrite:
            console.print("Initialization cancelled.")
            raise typer.Exit()

    # For now, just create an empty profile. We can add interactive prompts later.
    profiles.save_profile(profile_name, {})
    console.print(f"Profile '{profile_name}' initialized successfully.")
    console.print(f"You can now set values using: dspy-profiles set {profile_name} <key> <value>")


# Add other commands here as we implement them


def main():
    app()


if __name__ == "__main__":
    main()
