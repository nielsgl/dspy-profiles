"""CLI command for running a command with a profile."""

import os
import subprocess
from typing import Annotated

from rich.console import Console
import typer

console = Console()


def run_command(
    ctx: typer.Context,
    profile_name: Annotated[
        str,
        typer.Option(..., "--profile", "-p", help="The profile to activate for the command."),
    ],
):
    """Executes a command with the specified profile's environment variables."""
    command = ctx.args
    if not command:
        console.print("[bold red]Error:[/] No command provided to run.")
        raise typer.Exit(1)

    env = os.environ.copy()
    env["DSPY_PROFILE"] = profile_name

    try:
        result = subprocess.run(command, env=env, check=False, capture_output=True, text=True)
        if result.stdout:
            console.print(result.stdout, end="")
        if result.stderr:
            console.print(result.stderr, style="bold red", end="")
        if result.returncode != 0:
            raise typer.Exit(result.returncode)
    except FileNotFoundError:
        cmd_str = " ".join(command)
        console.print(f"[bold red]Error:[/] Command not found: '{cmd_str}'")
        raise typer.Exit(1)
