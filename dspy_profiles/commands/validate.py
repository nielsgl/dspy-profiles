"""CLI command for validating profiles."""

from pathlib import Path
from typing import Annotated

from pydantic import ValidationError
from rich.console import Console
import toml
import typer

from dspy_profiles.config import PROFILES_PATH
from dspy_profiles.validation import ProfilesFile

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
    try:
        with open(config_path) as f:
            data = toml.load(f)

        ProfilesFile.model_validate(data)
        console.print("[bold green]✅ Success![/bold green] All profiles are valid.")

    except FileNotFoundError:
        console.print(f"[bold red]Error:[/] Configuration file not found at '{config_path}'.")
        raise typer.Exit(1)
    except toml.TomlDecodeError as e:
        console.print(f"[bold red]Error:[/] Invalid TOML format in '{config_path}':\n  {e}")
        raise typer.Exit(1)
    except ValidationError as e:
        console.print(f"[bold red]❌ Validation Failed:[/] Found {e.error_count()} error(s).")
        for error in e.errors():
            loc = " -> ".join(map(str, error["loc"]))
            console.print(f"  - [bold cyan]{loc}[/bold cyan]: {error['msg']}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/] {e}")
        raise typer.Exit(1)
