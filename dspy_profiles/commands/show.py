"""CLI command for showing a profile."""

import json
from typing import Annotated

from rich.console import Console
from rich.table import Table
import typer

from dspy_profiles import api

console = Console()


def show_profile(
    profile_name: Annotated[str, typer.Argument(help="The name of the profile to display.")],
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output the profile in JSON format."),
    ] = False,
):
    """Shows the full configuration details of a specific profile."""
    profile_data, error = api.get_profile(profile_name)
    if error:
        console.print(f"[bold red]Error:[/] {error}")
        raise typer.Exit(code=1)

    if output_json:
        from pydantic import HttpUrl

        def http_url_serializer(obj):
            if isinstance(obj, HttpUrl):
                return str(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        console.print(json.dumps(profile_data, indent=2, default=http_url_serializer))
    else:
        table = Table(
            title=f"Profile: {profile_name}", show_header=True, header_style="bold magenta"
        )
        table.add_column("Key", style="dim", width=20)
        table.add_column("Value")

        if profile_data:

            def add_rows(data, prefix=""):
                for key, value in data.items():
                    if isinstance(value, dict):
                        add_rows(value, prefix=f"{prefix}{key}.")
                    else:
                        table.add_row(f"{prefix}{key}", str(value))

            add_rows(profile_data)

        console.print(table)
