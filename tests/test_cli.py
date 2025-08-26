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
    monkeypatch.setattr("dspy_profiles.cli.find_profiles_path", lambda: config_path)

    # 1. Test with no profiles
    result = runner.invoke(cli.app, ["list"])
    assert "No profiles found" in result.stdout

    # 2. Add a profile and test again
    manager = ProfileManager(config_path)
    manager.set("test_profile", {"lm": {"model": "gpt-4"}})
    result = runner.invoke(cli.app, ["list"])
    assert "test_profile" in result.stdout
    assert "gpt-4" in result.stdout


def test_show_command(tmp_path: Path, monkeypatch):
    """Tests the show command with an isolated profile manager."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.cli.find_profiles_path", lambda: config_path)
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
    monkeypatch.setattr("dspy_profiles.cli.find_profiles_path", lambda: config_path)
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


def test_init_command(tmp_path: Path, monkeypatch):
    """Tests the init command with an isolated profile manager."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.cli.find_profiles_path", lambda: config_path)
    manager = ProfileManager(config_path)

    # 1. Test interactive init
    result = runner.invoke(
        cli.app,
        ["init", "--profile", "test_profile"],
        input="openai/gpt-4o-mini\nhttp://localhost:8000\n",
    )
    assert result.exit_code == 0
    assert "Success!" in result.stdout
    profile = manager.get("test_profile")
    assert profile is not None
    assert profile.get("lm", {}).get("model") == "openai/gpt-4o-mini"
    assert str(profile.get("lm", {}).get("api_base")) == "http://localhost:8000/"

    # 2. Test init with existing profile without --force
    result = runner.invoke(cli.app, ["init", "--profile", "test_profile"])
    assert "already exists" in result.stdout
    assert result.exit_code == 1

    # 3. Test init with --force
    result = runner.invoke(
        cli.app,
        ["init", "--profile", "test_profile", "--force"],
        input="new/model\n\n",
    )
    assert result.exit_code == 0
    profile = manager.get("test_profile")
    assert profile is not None
    assert profile.get("lm", {}).get("model") == "new/model"


def test_set_command(tmp_path: Path, monkeypatch):
    """Tests the set command with an isolated profile manager."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.cli.find_profiles_path", lambda: config_path)
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


@patch("dspy_profiles.cli.subprocess.run")
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


@patch("dspy_profiles.cli.subprocess.run")
def test_run_no_command_provided(mock_subprocess_run: MagicMock):
    """Tests that the run command exits if no command is provided."""
    result = runner.invoke(cli.app, ["run", "--profile", "test_profile"])
    assert "No command provided" in result.stdout
    assert result.exit_code == 1
    mock_subprocess_run.assert_not_called()


@patch("dspy_profiles.cli.subprocess.run")
def test_run_command_not_found(mock_subprocess_run: MagicMock):
    """Tests the run command when the executable is not found."""
    mock_subprocess_run.side_effect = FileNotFoundError
    result = runner.invoke(
        cli.app, ["run", "--profile", "test_profile", "--", "nonexistent_command"]
    )
    assert "Command not found" in result.stdout
    assert result.exit_code == 1


@patch("dspy_profiles.cli.subprocess.run")
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
