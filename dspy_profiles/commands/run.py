"""CLI command for running a command with a profile."""

import os
import subprocess
import sys
from typing import Annotated

from rich.console import Console
import typer

console = Console()
app = typer.Typer(
    name="dspy-run",
    help="Run a command with a dspy-profile activated.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="markdown",
)


def _execute_with_profile(command: list[str], profile_name: str):
    """Core logic to execute a command with an activated profile."""

    is_python_command = False
    if command:
        executable = command[0].lower()
        if (
            executable == "python"
            or executable.endswith("/python")
            or executable.endswith("\\python.exe")
            or executable.endswith(".py")
        ):
            is_python_command = True

    if is_python_command:
        script_path_index = -1
        for i, arg in enumerate(command):
            if arg.endswith(".py"):
                script_path_index = i
                break

        if script_path_index != -1:
            script_path = command[script_path_index]
            script_args = command[script_path_index + 1 :]

            bootstrap_code = f"""
import sys
import runpy
from dspy_profiles.core import profile as activate_profile

sys.argv = [{script_path!r}] + {script_args!r}

with activate_profile('{profile_name}'):
    runpy.run_path({script_path!r}, run_name='__main__')
"""
            python_executable = sys.executable or "python"
            new_command = [python_executable, "-c", bootstrap_code]
            command = new_command

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


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    profile_name: Annotated[
        str,
        typer.Option("--profile", "-p", help="The profile to activate. Defaults to 'default'."),
    ] = "default",
    command: Annotated[
        list[str] | None,
        typer.Argument(help="The command to run.", rich_help_panel="Command"),
    ] = None,
):
    """
    Run a command with a dspy-profile activated.
    """
    if command is None:
        console.print("[bold red]Error:[/] No command provided to run.")
        raise typer.Exit(1)

    # If the user did not explicitly provide a profile, inform them of the default.
    raw_args = " ".join(sys.argv)
    if "--profile" not in raw_args and " -p " not in raw_args:
        console.print(f"[dim]No profile specified. Using default profile: '{profile_name}'[/dim]")

    run_command_list = list(command)

    if (
        run_command_list
        and run_command_list[0].endswith(".py")
        and not run_command_list[0].startswith("-")
    ):
        run_command_list.insert(0, "python")

    _execute_with_profile(run_command_list, profile_name)


# This is for the original `dspy-profiles run` subcommand
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

    _execute_with_profile(command, profile_name)


def cli_app():
    """The entry point for the dspy-run command."""
    app()


if __name__ == "__main__":
    cli_app()
