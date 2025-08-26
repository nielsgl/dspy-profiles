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


def test_test_command_success(profile_manager):
    """Test the 'test' command with a profile that should succeed."""
    with patch("dspy_profiles.cli.find_profiles_path", return_value=profile_manager.path):
        with patch("dspy_profiles.core.profile") as mock_profile_context:
            with patch("dspy.settings") as mock_settings:
                mock_lm = MagicMock()
                mock_lm.return_value = "ok"
                mock_settings.lm = mock_lm

                result = runner.invoke(app, ["test", "test_profile"])

    assert result.exit_code == 0, result.stdout
    assert "✅ Success!" in result.stdout
    mock_profile_context.assert_called_once_with("test_profile")
    mock_lm.assert_called_once_with("Say 'ok'")


def test_test_command_failure(profile_manager):
    """Test the 'test' command with a profile that should fail."""
    with patch("dspy_profiles.cli.find_profiles_path", return_value=profile_manager.path):
        with patch("dspy_profiles.core.profile"):  # as mock_profile_context:
            with patch("dspy.settings") as mock_settings:
                mock_lm = MagicMock()
                mock_lm.side_effect = ConnectionError("Could not connect")
                mock_settings.lm = mock_lm

                result = runner.invoke(app, ["test", "test_profile"])

    assert result.exit_code == 1, result.stdout
    assert "❌ Test Failed" in result.stdout
    assert "Could not connect" in result.stdout


def test_test_command_no_lm(profile_manager):
    """Test the 'test' command with a profile that has no LM configured."""
    with patch("dspy_profiles.cli.find_profiles_path", return_value=profile_manager.path):
        with patch("dspy_profiles.core.profile"):  # as mock_profile_context:
            with patch("dspy.settings") as mock_settings:
                mock_settings.lm = None
                result = runner.invoke(app, ["test", "no_lm_profile"])

    assert result.exit_code == 1, result.stdout
    assert "No language model configured" in result.stdout


def test_test_command_profile_not_found(profile_manager):
    """Test the 'test' command with a profile that does not exist."""
    # This test doesn't need to patch activate_profile because it should fail before that.
    # We need to patch find_profiles_path to use our isolated manager.
    with patch("dspy_profiles.cli.find_profiles_path", return_value=profile_manager.path):
        result = runner.invoke(app, ["test", "nonexistent_profile"])

    assert result.exit_code == 1
    assert "Profile 'nonexistent_profile' not found" in result.stdout
