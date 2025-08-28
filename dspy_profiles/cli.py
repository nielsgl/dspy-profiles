"""Main CLI application for dspy-profiles."""

import typer

from dspy_profiles.commands.delete import delete_profile
from dspy_profiles.commands.diff import diff_profiles
from dspy_profiles.commands.import_profile import import_profile
from dspy_profiles.commands.init import init_profile
from dspy_profiles.commands.list import list_profiles
from dspy_profiles.commands.run import run_command
from dspy_profiles.commands.set import set_value
from dspy_profiles.commands.show import show_profile
from dspy_profiles.commands.test import test_profile
from dspy_profiles.commands.validate import validate_profiles

app = typer.Typer(
    name="dspy-profiles",
    help="A CLI for managing DSPy profiles.",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="markdown",
)

# Add command functions
app.command(name="list")(list_profiles)
app.command(name="show")(show_profile)
app.command(name="delete")(delete_profile)
app.command(name="set")(set_value)
app.command(name="init")(init_profile)
app.command(name="import")(import_profile)
app.command(name="diff")(diff_profiles)
app.command(name="validate")(validate_profiles)
app.command(name="test")(test_profile)
app.command(
    name="run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)(run_command)


def main():
    """Run the CLI application."""
    app()


if __name__ == "__main__":
    main()
