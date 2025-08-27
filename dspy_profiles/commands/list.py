"""CLI command for listing profiles."""

import json
from typing import Annotated

from rich.console import Console
from rich.table import Table
import typer

from dspy_profiles import api

console = Console()


def list_profiles(
    output_json: Annotated[
        bool,
        typer.Option("--json", help="Output the list of profiles in JSON format."),
    ] = False,
):
    """Lists all available profiles and their core details."""
    all_profiles = api.list_profiles()
    if not all_profiles:
        console.print("[yellow]No profiles found. Use 'dspy-profiles init' to create one.[/yellow]")
        return

    if output_json:
        from pydantic import HttpUrl

        def http_url_serializer(obj):
            if isinstance(obj, HttpUrl):
                return str(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        console.print(json.dumps(all_profiles, indent=2, default=http_url_serializer))
    else:
        table = Table("Profile Name", "Language Model (LM)", "API Base", "API Key", "Extends")
        for name, profile_data in all_profiles.items():
            lm_section = profile_data.get("lm", {})
            model = lm_section.get("model", "[grey50]Not set[/grey50]")
            api_base_value = lm_section.get("api_base")
            api_base = str(api_base_value) if api_base_value else "[grey50]Not set[/grey50]"
            api_key = lm_section.get("api_key")
            if api_key:
                api_key_display = f"{api_key[:4]}...{api_key[-4:]}"
            else:
                api_key_display = "[grey50]Not set[/grey50]"
            extends = profile_data.get("extends", "[grey50]None[/grey50]")
            table.add_row(name, model, api_base, api_key_display, extends)

        console.print(table)
