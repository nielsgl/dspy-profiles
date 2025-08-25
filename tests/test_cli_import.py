from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dspy_profiles import cli
from dspy_profiles.config import ProfileManager

runner = CliRunner()


@patch("dspy_profiles.cli.get_manager")
def test_import_profile_success(mock_get_manager: MagicMock, tmp_path):
    """Tests successfully importing a profile from a .env file."""
    mock_manager = MagicMock(spec=ProfileManager)
    mock_get_manager.return_value = mock_manager
    mock_manager.get.return_value = None  # Profile does not exist yet

    env_file = tmp_path / ".env"
    env_file.write_text(
        "DSPY_LM_MODEL=gpt-4o-mini\nDSPY_SETTINGS_TEMPERATURE=0.7\nNOT_DSPY_VAR=should_be_ignored"
    )

    result = runner.invoke(
        cli.app,
        ["import", "--profile", "imported_profile", "--from", str(env_file)],
    )

    assert result.exit_code == 0
    assert "Success!" in result.stdout
    assert "imported_profile" in result.stdout

    mock_manager.set.assert_called_once_with(
        "imported_profile",
        {
            "lm": {"model": "gpt-4o-mini"},
            "settings": {"temperature": "0.7"},
        },
    )


@patch("dspy_profiles.cli.get_manager")
def test_import_profile_already_exists(mock_get_manager: MagicMock, tmp_path):
    """Tests that import fails if the profile already exists."""
    mock_manager = MagicMock(spec=ProfileManager)
    mock_get_manager.return_value = mock_manager
    mock_manager.get.return_value = {"some_data": "exists"}  # Profile exists

    env_file = tmp_path / ".env"
    env_file.write_text("DSPY_LM_MODEL=gpt-4o-mini")

    result = runner.invoke(
        cli.app,
        ["import", "--profile", "existing_profile", "--from", str(env_file)],
    )

    assert result.exit_code == 1
    assert "already exists" in result.stdout
    mock_manager.set.assert_not_called()
