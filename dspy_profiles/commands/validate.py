"""CLI command for validating profiles."""

from pathlib import Path
from typing import Annotated

from pydantic import ValidationError
from rich.console import Console
import typer

from dspy_profiles import api
from dspy_profiles.config import PROFILES_PATH

console = Console()


def validate_profiles(
    config_path: Annotated[
        Path,
        typer.Option(
            "--config",
            "-c",
            help="Path to the profiles.toml file.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ] = PROFILES_PATH,
):
    """Validates the structure and content of the profiles.toml file."""
    console.print(f"Validating profiles at: [cyan]{config_path}[/cyan]")
    error = api.validate_profiles_file(config_path)
    if error:
        if isinstance(error, ValidationError):
            console.print(
                f"[bold red]❌ Validation Failed:[/] Found {error.error_count()} error(s)."
            )
            for e_ in error.errors():
                loc = " -> ".join(map(str, e_["loc"]))
                console.print(f"  - [bold cyan]{loc}[/bold cyan]: {e_['msg']}")
        else:
            console.print(f"[bold red]Error:[/] {error}")
        raise typer.Exit(1)

    console.print("[bold green]✅ Success![/bold green] All profiles are valid.")
