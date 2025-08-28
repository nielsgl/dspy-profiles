from unittest.mock import patch

import toml
from typer.testing import CliRunner

from dspy_profiles.cli import app

runner = CliRunner()


@patch("dspy_profiles.api.find_profiles_path")
def test_delete_profile_not_found(mock_find_path, tmp_path):
    """Test deleting a profile that does not exist."""
    profiles_path = tmp_path / "profiles.toml"
    profiles_path.touch()
    mock_find_path.return_value = profiles_path

    result = runner.invoke(app, ["delete", "non_existent_profile"], input="y\n")
    assert result.exit_code == 1
    assert "Profile 'non_existent_profile' not found." in result.stdout


@patch("dspy_profiles.api.find_profiles_path")
def test_delete_profile_found(mock_find_path, tmp_path):
    """Test deleting an existing profile."""
    profiles_path = tmp_path / "profiles.toml"
    profiles_path.write_text('[my_profile]\nlm = {model = "gpt-4"}')
    mock_find_path.return_value = profiles_path

    # WHEN the delete command is called
    result = runner.invoke(app, ["delete", "my_profile"], input="y\n")

    # THEN the command should succeed and the profile should be removed
    assert result.exit_code == 0
    assert "Profile 'my_profile' deleted successfully." in result.stdout

    with open(profiles_path) as f:
        remaining_profiles = toml.load(f)

    assert "my_profile" not in remaining_profiles
