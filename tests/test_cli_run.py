import sys
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dspy_profiles import cli
from dspy_profiles.commands import run as run_cli

runner = CliRunner()


@patch("dspy_profiles.commands.run.subprocess.run")
def test_run_command_success(mock_subprocess_run: MagicMock):
    """Tests that the run command executes a subprocess with the correct environment."""
    mock_subprocess_run.return_value.returncode = 0

    result = runner.invoke(
        cli.app,
        ["run", "--profile", "test_profile", "--", "echo", "hello"],
    )

    assert result.exit_code == 0
    mock_subprocess_run.assert_called_once()

    # Check the environment passed to the subprocess
    call_args, call_kwargs = mock_subprocess_run.call_args
    assert "env" in call_kwargs
    env = call_kwargs["env"]
    assert env["DSPY_PROFILE"] == "test_profile"
    assert call_args == (["echo", "hello"],)


def test_run_command_actually_runs():
    """
    Tests that the run command can actually execute a real command.
    We'll use python to print an env var.
    """
    # A simple python script to print the env var
    command_to_run = [
        sys.executable,
        "-c",
        "import os; print(os.environ.get('DSPY_PROFILE', ''))",
    ]

    result = runner.invoke(
        cli.app,
        ["run", "--profile", "real_run_profile", "--", *command_to_run],
    )

    assert result.exit_code == 0
    assert "real_run_profile" in result.stdout


@patch("dspy_profiles.commands.run.subprocess.run")
def test_run_command_propagates_exit_code(mock_subprocess_run: MagicMock):
    """Tests that the exit code from the subprocess is propagated."""
    mock_subprocess_run.return_value.returncode = 123

    result = runner.invoke(
        cli.app,
        ["run", "--profile", "test_profile", "--", "some-command"],
    )

    assert result.exit_code == 123


def test_run_no_command_provided():
    """Tests that the command exits if no command is provided to run."""
    result = runner.invoke(cli.app, ["run", "--profile", "test_profile"])

    assert result.exit_code == 1
    assert "No command provided" in result.stdout


@patch("dspy_profiles.commands.run.subprocess.run", side_effect=FileNotFoundError)
def test_run_command_not_found(mock_subprocess_run: MagicMock):
    """Tests that the command exits if the command is not found."""
    result = runner.invoke(
        cli.app,
        ["run", "--profile", "test_profile", "--", "nonexistent-command"],
    )

    assert result.exit_code == 1
    assert "Command not found" in result.stdout


def test_dspy_run_app_with_verbose_executes_python():
    """Covers dspy-run app callback with verbosity flags and real python."""
    runner_local = CliRunner()
    result = runner_local.invoke(
        run_cli.app,
        [
            "--profile",
            "default",
            "-V",
            "--",
            sys.executable,
            "-c",
            "print('ok')",
        ],
    )
    assert result.exit_code == 0
    assert "ok" in result.stdout


def test_dspy_run_dry_run_python():
    """Dry-run prints resolved command and exits without executing."""
    runner_local = CliRunner()
    result = runner_local.invoke(
        cli.app,
        [
            "run",
            "--profile",
            "default",
            "--dry-run",
            "--",
            "script.py",
            "--flag",
        ],
    )
    assert result.exit_code == 0
    assert "Resolved command:" in result.stdout
    assert "-c" in result.stdout  # python -c bootstrap is used for .py


def test_dspy_run_dry_run_non_python():
    runner_local = CliRunner()
    result = runner_local.invoke(
        cli.app,
        ["run", "--profile", "default", "--dry-run", "--", "echo", "hello"],
    )
    assert result.exit_code == 0
    assert "Resolved command:" in result.stdout
    assert "echo hello" in result.stdout
