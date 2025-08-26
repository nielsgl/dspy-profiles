from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dspy_profiles import cli
from dspy_profiles.config import ProfileManager

runner = CliRunner()


@patch("dspy_profiles.cli.get_manager")
def test_cli_lifecycle(mock_get_manager: MagicMock):
    """Tests the full lifecycle of CLI commands with a mocked manager."""
    mock_manager = MagicMock(spec=ProfileManager)
    mock_get_manager.return_value = mock_manager

    # 1. Start with no profiles
    mock_manager.load.return_value = {}
    result = runner.invoke(cli.app, ["list"])
    assert "No profiles found" in result.stdout

    # 2. Init a profile interactively
    mock_manager.get.return_value = None
    result = runner.invoke(
        cli.app,
        ["init", "--profile", "test_profile"],
        input="openai/gpt-4o-mini\nhttp://localhost:8000\n",
    )
    assert result.exit_code == 0
    assert "OPENAI_API_KEY" in result.stdout
    mock_manager.set.assert_called_with(
        "test_profile", {"lm": {"model": "openai/gpt-4o-mini", "api_base": "http://localhost:8000"}}
    )
    mock_manager.reset_mock()

    # 3. Set a value
    mock_manager.get.return_value = {}
    result = runner.invoke(cli.app, ["set", "test_profile", "lm.model", "gpt-4"])
    assert result.exit_code == 0
    mock_manager.set.assert_called_with("test_profile", {"lm": {"model": "gpt-4"}})

    # 4. Show the profile
    mock_manager.get.return_value = {"lm": {"model": "gpt-4"}}
    result = runner.invoke(cli.app, ["show", "test_profile"])
    assert "gpt-4" in result.stdout

    # 5. List profiles
    mock_manager.load.return_value = {"test_profile": {"lm": {"model": "gpt-4"}}}
    result = runner.invoke(cli.app, ["list"])
    assert "test_profile" in result.stdout
    assert "gpt-4" in result.stdout

    # 6. Delete the profile
    mock_manager.delete.return_value = True
    result = runner.invoke(cli.app, ["delete", "test_profile"])
    assert "Success!" in result.stdout and "deleted" in result.stdout
    mock_manager.delete.assert_called_with("test_profile")


@patch("dspy_profiles.cli.get_manager")
def test_error_cases(mock_get_manager: MagicMock):
    """Tests error cases for the CLI."""
    mock_manager = MagicMock(spec=ProfileManager)
    mock_get_manager.return_value = mock_manager
    mock_manager.get.return_value = {"existing_profile": {}}

    # Show non-existent profile
    mock_manager.get.return_value = None
    result = runner.invoke(cli.app, ["show", "nonexistent"])
    assert "not found" in result.stdout
    assert result.exit_code == 1

    # Delete non-existent profile
    mock_manager.delete.return_value = False
    result = runner.invoke(cli.app, ["delete", "nonexistent"])
    assert "not found" in result.stdout
    assert result.exit_code == 1

    # Init existing profile without --force
    mock_manager.get.return_value = {"some_config"}
    result = runner.invoke(cli.app, ["init", "--profile", "existing_profile"])
    assert "already exists" in result.stdout

    # Init with a non-standard provider
    mock_manager.get.return_value = None
    result = runner.invoke(
        cli.app,
        ["init", "--profile", "custom_profile"],
        input="custom/model\n\n",
    )
    assert "Success!" in result.stdout
    assert "CUSTOM_API_KEY" in result.stdout


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
