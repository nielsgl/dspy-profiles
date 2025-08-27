"""CLI command for testing a profile."""

from typing import Annotated

from rich.console import Console
import typer

from dspy_profiles.config import ProfileManager, find_profiles_path
from dspy_profiles.core import profile as activate_profile

console = Console()


def test_profile(
    profile_name: Annotated[str, typer.Argument(help="The name of the profile to test.")],
):
    """Tests connectivity to the language model for a given profile."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    if not manager.get(profile_name):
        console.print(f"[bold red]Error:[/] Profile '{profile_name}' not found.")
        raise typer.Exit(code=1)

    console.print(f"Testing profile: [bold cyan]{profile_name}[/bold cyan]...")

    try:
        with activate_profile(profile_name):
            import dspy

            lm = dspy.settings.lm
            if not lm:
                console.print(
                    f"[bold red]Error:[/] No language model configured for profile "
                    f"'{profile_name}'."
                )
                raise typer.Exit(1)

            console.print(f"  - Using model: [yellow]{lm.model}[/yellow]")
            lm("Say 'ok'")

        console.print("[bold green]✅ Success![/bold green] Connectivity test passed.")

    except Exception as e:
        console.print(
            f"\n[bold red]❌ Test Failed:[/] Could not connect using profile '{profile_name}'."
        )
        console.print(f"  [bold]Reason:[/] {e}")
        raise typer.Exit(1)
