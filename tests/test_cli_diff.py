from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dspy_profiles import cli
from dspy_profiles.config import ProfileManager

runner = CliRunner()


@patch("dspy_profiles.cli.get_manager")
def test_diff_identical_profiles(mock_get_manager: MagicMock):
    """Tests diffing two identical profiles."""
    mock_manager = MagicMock(spec=ProfileManager)
    mock_get_manager.return_value = mock_manager
    mock_manager.get.return_value = {"lm": {"model": "gpt-4"}}

    result = runner.invoke(cli.app, ["diff", "profile_a", "profile_b"])

    assert result.exit_code == 0
    assert "Profiles are identical" in result.stdout


@patch("dspy_profiles.cli.get_manager")
def test_diff_different_profiles(mock_get_manager: MagicMock):
    """Tests diffing two different profiles."""
    mock_manager = MagicMock(spec=ProfileManager)
    mock_get_manager.return_value = mock_manager

    def get_side_effect(profile_name):
        if profile_name == "profile_a":
            return {"lm": {"model": "gpt-4o-mini"}}
        if profile_name == "profile_b":
            return {"lm": {"model": "claude-3-opus"}}
        return None

    mock_manager.get.side_effect = get_side_effect

    result = runner.invoke(cli.app, ["diff", "profile_a", "profile_b"])

    assert result.exit_code == 0
    assert "gpt-4o-mini" in result.stdout
    assert "claude-3-opus" in result.stdout
    assert "+" in result.stdout  # Should have additions
    assert "-" in result.stdout  # Should have deletions


@patch("dspy_profiles.cli.get_manager")
def test_diff_profile_a_not_found(mock_get_manager: MagicMock):
    """Tests diffing when the first profile does not exist."""
    mock_manager = MagicMock(spec=ProfileManager)
    mock_get_manager.return_value = mock_manager

    def get_side_effect(profile_name):
        if profile_name == "nonexistent":
            return None
        return {"lm": {"model": "claude-3-opus"}}

    mock_manager.get.side_effect = get_side_effect

    result = runner.invoke(cli.app, ["diff", "nonexistent", "existent"])

    assert result.exit_code == 1
    assert "Profile 'nonexistent' not found" in result.stdout


@patch("dspy_profiles.cli.get_manager")
def test_diff_profile_b_not_found(mock_get_manager: MagicMock):
    """Tests diffing when the second profile does not exist."""
    mock_manager = MagicMock(spec=ProfileManager)
    mock_get_manager.return_value = mock_manager
    mock_manager.get.return_value = None

    result = runner.invoke(cli.app, ["diff", "existent", "nonexistent"])

    assert result.exit_code == 1
    assert "not found" in result.stdout
