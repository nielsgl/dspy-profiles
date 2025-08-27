from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dspy_profiles import cli

runner = CliRunner()


@patch("dspy_profiles.commands.import_profile.api")
def test_import_profile(mock_api: MagicMock, tmp_path: Path):
    """Tests the import command by mocking the API layer."""
    env_file = tmp_path / ".env"
    env_file.write_text("DSPY_LM_MODEL=gpt-4o-mini")

    # 1. Test successful import
    mock_api.import_profile.return_value = None
    result = runner.invoke(
        cli.app,
        ["import", "--profile", "imported_profile", "--from", str(env_file)],
    )
    assert result.exit_code == 0
    assert "Success!" in result.stdout
    mock_api.import_profile.assert_called_with("imported_profile", env_file)

    # 2. Test import when profile already exists
    mock_api.import_profile.return_value = "Profile 'imported_profile' already exists."
    result = runner.invoke(
        cli.app,
        ["import", "--profile", "imported_profile", "--from", str(env_file)],
    )
    assert result.exit_code == 1
    assert "Error: Profile 'imported_profile' already exists." in result.stdout

    # 3. Test import with a non-existent file
    result = runner.invoke(
        cli.app,
        ["import", "--profile", "any_profile", "--from", "nonexistent.env"],
    )
    assert result.exit_code == 2  # Typer's exit code for file not found
    assert "Invalid value" in result.stderr
