import importlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import toml
from typer.testing import CliRunner

from dspy_profiles import cli

runner = CliRunner()


@patch("dspy_profiles.commands.list.api")
def test_list_command(mock_api: MagicMock):
    """Tests the list command by mocking the API layer."""
    # 1. Test with no profiles
    mock_api.list_profiles.return_value = {}
    result = runner.invoke(cli.app, ["list"])
    assert "No profiles found" in result.stdout

    # 2. Test with a profile
    mock_profiles = {
        "test_profile": {
            "lm": {
                "model": "gpt-4",
                "api_key": "sk-1234567890abcdef1234567890abcdef",
                "api_base": "https://api.openai.com/v1",
            }
        }
    }
    mock_api.list_profiles.return_value = mock_profiles
    result = runner.invoke(cli.app, ["list"])
    assert "test_profile" in result.stdout
    assert "gpt-4" in result.stdout
    assert "sk-1...cdef" in result.stdout
    assert "https://api.open" in result.stdout

    # 3. Test with --json flag
    result = runner.invoke(cli.app, ["list", "--json"])
    assert result.exit_code == 0
    import json

    assert json.loads(result.stdout) == mock_profiles


@patch("dspy_profiles.commands.show.api")
def test_show_command(mock_api: MagicMock):
    """Tests the show command by mocking the API layer."""
    # 1. Test showing an existing profile
    mock_profile_data = {"lm": {"model": "gpt-4"}}
    mock_api.get_profile.return_value = mock_profile_data, None
    result = runner.invoke(cli.app, ["show", "test_profile"])
    assert result.exit_code == 0
    assert "gpt-4" in result.stdout
    mock_api.get_profile.assert_called_with("test_profile")

    # 2. Test showing a non-existent profile
    mock_api.get_profile.return_value = None, "Profile 'nonexistent' not found."
    result = runner.invoke(cli.app, ["show", "nonexistent"])
    assert result.exit_code == 1
    assert "Error: Profile 'nonexistent' not found." in result.stdout

    # 3. Test with --json flag
    mock_api.get_profile.return_value = mock_profile_data, None
    result = runner.invoke(cli.app, ["show", "test_profile", "--json"])
    assert result.exit_code == 0
    import json

    assert json.loads(result.stdout) == mock_profile_data


@patch("dspy_profiles.commands.delete.api")
def test_delete_command(mock_api: MagicMock):
    """Tests the delete command by mocking the API layer."""
    # 1. Test deleting an existing profile
    mock_api.delete_profile.return_value = None
    result = runner.invoke(cli.app, ["delete", "test_profile", "--force"])
    assert result.exit_code == 0
    assert "deleted successfully" in result.stdout
    mock_api.delete_profile.assert_called_with("test_profile")

    # 2. Test deleting a non-existent profile
    mock_api.delete_profile.return_value = "Profile 'nonexistent' not found."
    result = runner.invoke(cli.app, ["delete", "nonexistent", "--force"])
    assert result.exit_code == 1
    assert "Error: Profile 'nonexistent' not found." in result.stdout

    # 3. Test deleting the 'default' profile, which should fail
    result = runner.invoke(cli.app, ["delete", "default", "--force"])
    assert result.exit_code == 1
    assert "cannot be deleted" in result.stdout


@patch("dspy_profiles.commands.init.api")
def test_init_command_interactive(mock_api: MagicMock):
    """Tests the interactive init command by mocking the API layer."""
    # Mock get_profile to indicate the profile doesn't exist yet
    mock_api.get_profile.return_value = None, None

    result = runner.invoke(
        cli.app,
        ["init", "--profile", "test_profile"],
        input="openai/gpt-4o-mini\nsk-my-secret-key\nhttp://localhost:8000\n",
    )
    assert result.exit_code == 0
    assert "Success!" in result.stdout

    # Verify that the create_profile function was called with the correct data
    mock_api.create_profile.assert_called_once()
    mock_api.create_profile.assert_called_with(
        "test_profile",
        {
            "lm": {
                "model": "openai/gpt-4o-mini",
                "api_key": "sk-my-secret-key",
                "api_base": "http://localhost:8000",
            }
        },
    )


@patch("dspy_profiles.commands.init.api")
def test_init_command_no_optional_values(mock_api: MagicMock):
    """Tests the init command without providing optional values."""
    mock_api.get_profile.return_value = None, None

    result = runner.invoke(
        cli.app,
        ["init", "--profile", "test_profile_no_key"],
        input="openai/gpt-4o-mini\n\n\n",
    )
    assert result.exit_code == 0
    assert "Success!" in result.stdout

    mock_api.create_profile.assert_called_with(
        "test_profile_no_key", {"lm": {"model": "openai/gpt-4o-mini"}}
    )


@patch("dspy_profiles.commands.init.api")
def test_init_command_force(mock_api: MagicMock):
    """Tests the --force option of the init command."""
    # Mock get_profile to indicate the profile already exists
    mock_api.get_profile.return_value = {"lm": {"model": "old/model"}}, None

    # Test without --force first
    result = runner.invoke(cli.app, ["init", "--profile", "test_profile"])
    assert "already exists" in result.stdout
    assert result.exit_code == 1

    # Test with --force
    result = runner.invoke(
        cli.app,
        ["init", "--profile", "test_profile", "--force"],
        input="new/model\nnew-key\n\n",
    )
    assert result.exit_code == 0
    mock_api.create_profile.assert_called_with(
        "test_profile", {"lm": {"model": "new/model", "api_key": "new-key"}}
    )


@patch("dspy_profiles.commands.set.api")
def test_set_command(mock_api: MagicMock):
    """Tests the set command by mocking the API layer."""
    mock_api.update_profile.return_value = (
        {"lm": {"model": "gpt-4o", "temperature": "0.7"}},
        None,
    )

    result = runner.invoke(cli.app, ["set", "new_profile", "lm.model", "gpt-4o"])
    assert result.exit_code == 0
    mock_api.update_profile.assert_called_with("new_profile", "lm.model", "gpt-4o")

    result = runner.invoke(cli.app, ["set", "new_profile", "lm.temperature", "0.7"])
    assert result.exit_code == 0
    mock_api.update_profile.assert_called_with("new_profile", "lm.temperature", "0.7")


@patch("dspy_profiles.commands.run.subprocess.run")
def test_run_no_command_provided(mock_subprocess_run: MagicMock):
    """Tests that the run command exits if no command is provided."""
    result = runner.invoke(cli.app, ["run", "--profile", "test_profile"])
    assert "No command provided" in result.stdout
    assert result.exit_code == 1
    mock_subprocess_run.assert_not_called()


@patch("dspy_profiles.commands.run.subprocess.run")
def test_run_command_not_found(mock_subprocess_run: MagicMock):
    """Tests the run command when the executable is not found."""
    mock_subprocess_run.side_effect = FileNotFoundError
    result = runner.invoke(
        cli.app, ["run", "--profile", "test_profile", "--", "nonexistent_command"]
    )
    assert "Command not found" in result.stdout
    assert result.exit_code == 1


@patch("dspy_profiles.commands.run.subprocess.run")
def test_run_command_fails(mock_subprocess_run: MagicMock):
    """Tests the run command when the subprocess fails."""
    mock_subprocess_run.return_value = MagicMock(returncode=123)
    result = runner.invoke(cli.app, ["run", "--profile", "test_profile", "--", "failing_command"])
    assert result.exit_code == 123


def test_delete_command_corruption_bug(tmp_path: Path):
    """Test that the delete command does not corrupt other profiles."""
    profiles_file = tmp_path / "profiles.toml"
    # GIVEN a profiles file with two profiles
    profiles_content = {
        "default": {"lm": {"model": "gpt-4"}},
        "testing": {"lm": {"model": "gpt-3.5-turbo"}},
    }
    with open(profiles_file, "w") as f:
        toml.dump(profiles_content, f)

    # WHEN the delete command is called on one profile
    importlib.import_module("dspy_profiles.api")

    # Temporarily patch find_profiles_path to point to our test file
    with patch("dspy_profiles.api.find_profiles_path", return_value=profiles_file):
        runner.invoke(cli.app, ["delete", "default", "--force"])

    # THEN the remaining profile should still be intact in the file
    with open(profiles_file) as f:
        remaining_profiles = toml.load(f)

    assert "default" in remaining_profiles
    assert "testing" in remaining_profiles
    assert remaining_profiles["testing"] == {"lm": {"model": "gpt-3.5-turbo"}}
