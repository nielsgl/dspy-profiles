from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dspy_profiles.cli import app
from dspy_profiles.loader import ResolvedProfile

runner = CliRunner()

MOCK_PROFILES = {
    "test_profile": {"lm": {"model": "mock-model"}},
    "no_lm_profile": {"rm": {"url": "http://some-rm-url"}},
}


def mock_get_config(profile_name):
    """A side_effect function to mock ProfileLoader.get_config."""
    config = MOCK_PROFILES.get(profile_name)
    if config is None:
        raise ValueError(f"Profile '{profile_name}' not found.")
    return ResolvedProfile(
        name=profile_name, config=config, lm=config.get("lm"), rm=config.get("rm")
    )


def test_test_command_success():
    """Test the 'test' command with a profile that should succeed."""
    mock_manager = MagicMock()
    mock_manager.get.return_value = MOCK_PROFILES["test_profile"]

    with (
        patch("dspy_profiles.commands.test.ProfileManager", return_value=mock_manager),
        patch("dspy_profiles.core.ProfileLoader") as mock_loader,
    ):
        mock_loader.return_value.get_config.side_effect = mock_get_config

        with patch("dspy.settings") as mock_settings:
            mock_lm = MagicMock()
            mock_lm.return_value = "ok"
            mock_settings.lm = mock_lm

            result = runner.invoke(app, ["test", "test_profile"])

    assert result.exit_code == 0, result.stdout
    assert "✅ Success!" in result.stdout
    mock_lm.assert_called_once_with("Say 'ok'")


def test_test_command_failure():
    """Test the 'test' command with a profile that should fail."""
    mock_manager = MagicMock()
    mock_manager.get.return_value = MOCK_PROFILES["test_profile"]

    with (
        patch("dspy_profiles.commands.test.ProfileManager", return_value=mock_manager),
        patch("dspy_profiles.core.ProfileLoader") as mock_loader,
    ):
        mock_loader.return_value.get_config.side_effect = mock_get_config

        with patch("dspy.settings") as mock_settings:
            mock_lm = MagicMock()
            mock_lm.side_effect = ConnectionError("Could not connect")
            mock_settings.lm = mock_lm

            result = runner.invoke(app, ["test", "test_profile"])

    assert result.exit_code == 1, result.stdout
    assert "❌ Test Failed" in result.stdout
    assert "Could not connect" in result.stdout


def test_test_command_no_lm():
    """Test the 'test' command with a profile that has no LM configured."""
    mock_manager = MagicMock()
    mock_manager.get.return_value = MOCK_PROFILES["no_lm_profile"]

    with (
        patch("dspy_profiles.commands.test.ProfileManager", return_value=mock_manager),
        patch("dspy_profiles.core.ProfileLoader") as mock_loader,
    ):
        mock_loader.return_value.get_config.side_effect = mock_get_config

        with patch("dspy.settings") as mock_settings:
            mock_settings.lm = None
            result = runner.invoke(app, ["test", "no_lm_profile"])

    assert result.exit_code == 1, result.stdout
    assert "No language model configured" in result.stdout


def test_test_command_profile_not_found():
    """Test the 'test' command with a profile that does not exist."""
    mock_manager = MagicMock()
    mock_manager.get.return_value = None

    with patch("dspy_profiles.commands.test.ProfileManager", return_value=mock_manager):
        result = runner.invoke(app, ["test", "nonexistent_profile"])

    assert result.exit_code == 1
    assert "Profile 'nonexistent_profile' not found" in result.stdout
