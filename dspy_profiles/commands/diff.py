"""CLI command for diffing two profiles."""

from difflib import unified_diff
import json
from typing import Annotated

from rich.console import Console
from rich.text import Text
import typer

from dspy_profiles import api

console = Console()


def diff_profiles(
    profile_a_name: Annotated[str, typer.Argument(help="The first profile to compare.")],
    profile_b_name: Annotated[str, typer.Argument(help="The second profile to compare.")],
):
    """Compares two profiles and highlights their differences."""
    profile_a, error_a = api.get_profile(profile_a_name)
    if error_a:
        console.print(f"[bold red]Error:[/] {error_a}")
        raise typer.Exit(code=1)

    profile_b, error_b = api.get_profile(profile_b_name)
    if error_b:
        console.print(f"[bold red]Error:[/] {error_b}")
        raise typer.Exit(code=1)

    # Note: The bug with HttpUrl serialization will be fixed in a later phase.
    json_a = json.dumps(profile_a, indent=2, sort_keys=True)
    json_b = json.dumps(profile_b, indent=2, sort_keys=True)

    if json_a == json_b:
        console.print("[bold green]Profiles are identical.[/bold green]")
        return

    diff = unified_diff(
        json_a.splitlines(keepends=True),
        json_b.splitlines(keepends=True),
        fromfile=profile_a_name,
        tofile=profile_b_name,
    )

    diff_text = Text()
    for line in diff:
        if line.startswith("+"):
            diff_text.append(line, style="green")
        elif line.startswith("-"):
            diff_text.append(line, style="red")
        elif line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
            diff_text.append(line, style="cyan")
        else:
            diff_text.append(line)

    console.print(diff_text)
