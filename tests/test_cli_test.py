from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from dspy_profiles.cli import app
from dspy_profiles.config import ProfileManager

runner = CliRunner()

MOCK_PROFILES = {
    "test_profile": {"lm": {"model": "mock-model"}},
    "no_lm_profile": {"rm": {"model": "some-rm"}},
}


@pytest.fixture
def profile_manager(tmp_path):
    """Fixture to create a ProfileManager with a temporary config file."""
    config_path = tmp_path / "profiles.toml"
    manager = ProfileManager(config_path)
    for name, data in MOCK_PROFILES.items():
        manager.set(name, data)
    return manager


@patch("dspy_profiles.config.get_manager")
def test_test_command_success(mock_get_manager, profile_manager):
    """Test the 'test' command with a profile that should succeed."""
    mock_get_manager.return_value = profile_manager

    # We patch the profile context manager in the core module
    with patch("dspy_profiles.core.profile"):
        # And we patch dspy.settings.lm to mock the "network call"
        with patch("dspy.settings") as mock_settings:
            mock_lm = MagicMock()
            mock_lm.return_value = "ok"
            mock_settings.lm = mock_lm

            result = runner.invoke(app, ["test", "test_profile"])

    assert result.exit_code == 0, result.stdout
    assert "✅ Success!" in result.stdout
    mock_lm.assert_called_once_with("Say 'ok'")


@patch("dspy_profiles.config.get_manager")
def test_test_command_failure(mock_get_manager, profile_manager):
    """Test the 'test' command with a profile that should fail."""
    mock_get_manager.return_value = profile_manager

    with patch("dspy_profiles.core.profile"):
        with patch("dspy.settings") as mock_settings:
            mock_lm = MagicMock()
            mock_lm.side_effect = ConnectionError("Could not connect")
            mock_settings.lm = mock_lm

            result = runner.invoke(app, ["test", "test_profile"])

    assert result.exit_code == 1, result.stdout
    assert "❌ Test Failed" in result.stdout
    assert "Could not connect" in result.stdout


@patch("dspy_profiles.config.get_manager")
def test_test_command_no_lm(mock_get_manager, profile_manager):
    """Test the 'test' command with a profile that has no LM configured."""
    mock_get_manager.return_value = profile_manager

    with patch("dspy_profiles.core.profile"):
        with patch("dspy.settings") as mock_settings:
            mock_settings.lm = None
            result = runner.invoke(app, ["test", "no_lm_profile"])

    assert result.exit_code == 1, result.stdout
    assert "No language model configured" in result.stdout


@patch("dspy_profiles.config.get_manager")
def test_test_command_profile_not_found(mock_get_manager, profile_manager):
    """Test the 'test' command with a profile that does not exist."""
    mock_get_manager.return_value = profile_manager

    result = runner.invoke(app, ["test", "nonexistent_profile"])

    assert result.exit_code == 1
    assert "Profile 'nonexistent_profile' not found" in result.stdout
