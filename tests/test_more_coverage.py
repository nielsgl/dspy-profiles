from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dspy_profiles import cli
from dspy_profiles.api import ProfileExistsError, ProfileNotFound
from dspy_profiles.commands import run as run_cli
from dspy_profiles.logging_utils import compute_level, setup_logging

runner = CliRunner()


def test_dspy_run_app_no_profile_default_message():
    """Invoking dspy-run without --profile should print default profile notice."""
    result = runner.invoke(
        run_cli.app,
        ["--", sys.executable, "-c", "print('ok')"],
    )
    assert result.exit_code == 0
    assert "No profile specified. Using default profile: 'default'" in result.stdout
    assert "ok" in result.stdout


def test_cli_import_warning_when_no_vars(tmp_path: Path):
    """Importing from a .env with no DSPY_ variables should warn and exit 0."""
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\n")
    result = runner.invoke(
        cli.app,
        ["import", "--profile", "empty", "--from", str(env_file)],
    )
    assert result.exit_code == 0
    assert "Warning:" in result.stdout


def test_cli_delete_cancelled(tmp_path: Path):
    """Interactive delete without --force; user cancels (answers 'n')."""
    profiles_path = tmp_path / "profiles.toml"
    profiles_path.write_text('[my_profile]\nlm = {model = "gpt-4"}')
    with patch("dspy_profiles.api.find_profiles_path", return_value=profiles_path):
        res = runner.invoke(cli.app, ["delete", "my_profile"], input="n\n")
    assert res.exit_code == 0
    assert "Deletion cancelled." in res.stdout
    # Ensure profile remains
    import toml

    data = toml.load(profiles_path)
    assert "my_profile" in data


@patch("dspy_profiles.commands.diff.api")
def test_diff_command_error_on_first_profile(mock_api: MagicMock):
    """Diff should error when the first profile cannot be loaded."""
    mock_api.get_profile.side_effect = [
        (None, "Profile 'missing' not found."),
        ({}, None),
    ]
    result = runner.invoke(cli.app, ["diff", "missing", "other"])
    assert result.exit_code == 1
    assert "Error: Profile 'missing' not found." in result.stdout


@patch("dspy_profiles.commands.list.api")
def test_list_json_httpurl_serialization(mock_api: MagicMock):
    """Ensure HttpUrl values are serialized to strings in --json."""
    from pydantic import HttpUrl

    mock_api.list_profiles.return_value = {
        "test": {"lm": {"model": "gpt-4", "api_base": HttpUrl("http://localhost:8080")}}
    }
    result = runner.invoke(cli.app, ["list", "--json"])
    assert result.exit_code == 0
    assert "http://localhost:8080" in result.stdout


@patch("dspy_profiles.commands.show.api")
def test_show_json_httpurl_serialization(mock_api: MagicMock):
    from pydantic import HttpUrl

    mock_api.get_profile.return_value = (
        {"lm": {"api_base": HttpUrl("http://localhost:9999")}},
        None,
    )
    result = runner.invoke(cli.app, ["show", "test", "--json"])
    assert result.exit_code == 0
    assert "http://localhost:9999" in result.stdout


def test_api_exceptions_and_logging_env(monkeypatch):
    """Cover exception __init__ and env-level path for logging setup."""
    # Exercise exception constructors
    e1 = ProfileNotFound("abc")
    e2 = ProfileExistsError("xyz")
    assert "abc" in str(e1)
    assert "xyz" in str(e2)

    # Ensure setup_logging creates a handler when none exists
    import logging

    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    setup_logging(logging.INFO)
    assert root.handlers

    # Env variable level should override flags
    monkeypatch.setenv("DSPY_PROFILES_LOG_LEVEL", "ERROR")
    assert compute_level(verbose=2, quiet=0, log_level=None) == logging.ERROR
    monkeypatch.delenv("DSPY_PROFILES_LOG_LEVEL", raising=False)
