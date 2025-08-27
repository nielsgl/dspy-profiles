from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dspy_profiles import cli
from dspy_profiles.config import ProfileManager

runner = CliRunner()


def test_list_command(tmp_path: Path, monkeypatch):
    """Tests the list command with an isolated profile manager."""
    config_path = tmp_path / "profiles.toml"

    # Patch find_profiles_path to return our temp path
    monkeypatch.setattr("dspy_profiles.commands.list.find_profiles_path", lambda: config_path)

    # 1. Test with no profiles
    result = runner.invoke(cli.app, ["list"])
    assert "No profiles found" in result.stdout

    # 2. Add a profile and test again
    manager = ProfileManager(config_path)
    manager.set(
        "test_profile",
        {
            "lm": {
                "model": "gpt-4",
                "api_key": "sk-1234567890abcdef1234567890abcdef",
                "api_base": "https://api.openai.com/v1",
            }
        },
    )
    result = runner.invoke(cli.app, ["list"])
    assert "test_profile" in result.stdout
    assert "gpt-4" in result.stdout
    assert "sk-1...cdef" in result.stdout
    assert "https://api.open" in result.stdout


def test_show_command(tmp_path: Path, monkeypatch):
    """Tests the show command with an isolated profile manager."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.commands.show.find_profiles_path", lambda: config_path)
    manager = ProfileManager(config_path)
    manager.set("test_profile", {"lm": {"model": "gpt-4"}})

    # 1. Test showing an existing profile
    result = runner.invoke(cli.app, ["show", "test_profile"])
    assert result.exit_code == 0
    assert "gpt-4" in result.stdout

    # 2. Test showing a non-existent profile
    result = runner.invoke(cli.app, ["show", "nonexistent"])
    assert "not found" in result.stdout
    assert result.exit_code == 1


def test_delete_command(tmp_path: Path, monkeypatch):
    """Tests the delete command with an isolated profile manager."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.commands.delete.find_profiles_path", lambda: config_path)
    manager = ProfileManager(config_path)
    manager.set("test_profile", {"lm": {"model": "gpt-4"}})

    # 1. Test deleting an existing profile
    result = runner.invoke(cli.app, ["delete", "test_profile"])
    assert result.exit_code == 0
    assert "Success!" in result.stdout
    assert manager.get("test_profile") is None

    # 2. Test deleting a non-existent profile
    result = runner.invoke(cli.app, ["delete", "nonexistent"])
    assert "not found" in result.stdout
    assert result.exit_code == 1


def test_init_command_interactive(tmp_path: Path, monkeypatch):
    """Tests the interactive init command."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.commands.init.find_profiles_path", lambda: config_path)

    # Run the init command
    result = runner.invoke(
        cli.app,
        ["init", "--profile", "test_profile"],
        input="openai/gpt-4o-mini\nsk-my-secret-key\nhttp://localhost:8000\n",
    )
    assert result.exit_code == 0
    assert "Success!" in result.stdout

    # Verify the profile was created correctly
    manager = ProfileManager(config_path)
    profile = manager.get("test_profile")
    assert profile is not None
    assert profile.get("lm", {}).get("model") == "openai/gpt-4o-mini"
    assert profile.get("lm", {}).get("api_key") == "sk-my-secret-key"
    assert str(profile.get("lm", {}).get("api_base")) == "http://localhost:8000/"


def test_init_command_no_optional_values(tmp_path: Path, monkeypatch):
    """Tests the init command without providing optional values."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.commands.init.find_profiles_path", lambda: config_path)

    result = runner.invoke(
        cli.app,
        ["init", "--profile", "test_profile_no_key"],
        input="openai/gpt-4o-mini\n\n\n",
    )
    assert result.exit_code == 0
    assert "Success!" in result.stdout

    manager = ProfileManager(config_path)
    profile = manager.get("test_profile_no_key")
    assert profile is not None
    assert profile.get("lm", {}).get("model") == "openai/gpt-4o-mini"
    assert profile.get("lm", {}).get("api_key") is None
    assert profile.get("lm", {}).get("api_base") is None


def test_init_command_force(tmp_path: Path, monkeypatch):
    """Tests the --force option of the init command."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.commands.init.find_profiles_path", lambda: config_path)
    manager = ProfileManager(config_path)
    manager.set("test_profile", {"lm": {"model": "old/model"}})

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
    profile = manager.get("test_profile")
    assert profile is not None
    assert profile.get("lm", {}).get("model") == "new/model"
    assert profile.get("lm", {}).get("api_key") == "new-key"


def test_set_command(tmp_path: Path, monkeypatch):
    """Tests the set command with an isolated profile manager."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.commands.set.find_profiles_path", lambda: config_path)
    manager = ProfileManager(config_path)

    # 1. Set a value in a new profile
    result = runner.invoke(cli.app, ["set", "new_profile", "lm.model", "gpt-4o"])
    assert result.exit_code == 0
    profile = manager.get("new_profile")
    assert profile is not None
    assert profile.get("lm", {}).get("model") == "gpt-4o"

    # 2. Set a nested value in an existing profile
    result = runner.invoke(cli.app, ["set", "new_profile", "lm.temperature", "0.7"])
    assert result.exit_code == 0
    profile = manager.get("new_profile")
    assert profile is not None
    assert profile.get("lm", {}).get("temperature") == "0.7"
    assert profile.get("lm", {}).get("model") == "gpt-4o"  # Ensure old value is kept


@patch("dspy_profiles.commands.run.subprocess.run")
def test_run_command_success(mock_subprocess_run: MagicMock):
    """Tests a successful run command."""
    mock_subprocess_run.return_value = MagicMock(returncode=0)
    result = runner.invoke(
        cli.app, ["run", "--profile", "test_profile", "--", "python", "my_script.py"]
    )
    assert result.exit_code == 0
    mock_subprocess_run.assert_called_once()
    args, kwargs = mock_subprocess_run.call_args
    assert args == (["python", "my_script.py"],)
    assert kwargs["env"]["DSPY_PROFILE"] == "test_profile"


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


@patch("dspy_profiles.cli.app")
def test_main(mock_app: MagicMock):
    """Tests the main function."""
    cli.main()
    mock_app.assert_called_once()
