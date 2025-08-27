"""CLI command for diffing two profiles."""

from difflib import unified_diff
import json
from typing import Annotated

from rich.console import Console
from rich.text import Text
import typer

from dspy_profiles.config import ProfileManager, find_profiles_path

console = Console()


def diff_profiles(
    profile_a_name: Annotated[str, typer.Argument(help="The first profile to compare.")],
    profile_b_name: Annotated[str, typer.Argument(help="The second profile to compare.")],
):
    """Compares two profiles and highlights their differences."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    profile_a = manager.get(profile_a_name)
    profile_b = manager.get(profile_b_name)

    if not profile_a:
        console.print(f"[bold red]Error:[/] Profile '{profile_a_name}' not found.")
        raise typer.Exit(code=1)
    if not profile_b:
        console.print(f"[bold red]Error:[/] Profile '{profile_b_name}' not found.")
        raise typer.Exit(code=1)

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
