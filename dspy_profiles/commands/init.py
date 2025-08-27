"""CLI command for initializing a profile."""

from typing import Annotated

from rich.console import Console
import typer

from dspy_profiles import api

console = Console()


def init_profile(
    profile_name: Annotated[
        str,
        typer.Option(
            "--profile", "-p", help="The name for the new profile.", show_default="default"
        ),
    ] = "default",
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite the profile if it already exists.",
        ),
    ] = False,
):
    """Initializes a new profile interactively."""
    if not force:
        profile, _ = api.get_profile(profile_name)
        if profile:
            console.print(
                f"[bold red]Error:[/] Profile '{profile_name}' already exists. "
                "Use --force to overwrite."
            )
            raise typer.Exit(code=1)

    console.print(f"Configuring profile: [bold]{profile_name}[/bold]")

    model = typer.prompt("Enter the language model (e.g., openai/gpt-4o-mini)")
    api_key = typer.prompt(
        "Enter your API key (optional)", default="", show_default=False, hide_input=True
    )
    api_base = typer.prompt(
        "Enter the API base (optional, for local models)", default="", show_default=False
    )

    new_config = {"lm": {"model": model}}
    if api_key:
        new_config["lm"]["api_key"] = api_key
    if api_base:
        new_config["lm"]["api_base"] = api_base

    api.create_profile(profile_name, new_config)

    console.print(f"\n[bold green]Success![/bold green] Profile '{profile_name}' saved.")
    console.print(
        "[yellow]Warning:[/] Your API key is stored in plaintext. "
        "Ensure the configuration file is secured."
    )
    console.print(
        f"You can view your new profile with: [bold]dspy-profiles show {profile_name}[/bold]"
    )
