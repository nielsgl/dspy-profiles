from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from dspy_profiles import cli

runner = CliRunner()


@patch("dspy_profiles.commands.diff.api")
def test_diff_command(mock_api: MagicMock):
    """Tests the diff command by mocking the API layer."""
    profile_a = {"lm": {"model": "gpt-4o-mini"}}
    profile_b = {"lm": {"model": "claude-3-opus"}}
    profile_c = {"lm": {"model": "gpt-4o-mini"}}

    # 1. Test diff between different profiles
    mock_api.get_profile.side_effect = [(profile_a, None), (profile_b, None)]
    result = runner.invoke(cli.app, ["diff", "profile_a", "profile_b"])
    assert result.exit_code == 0
    assert "gpt-4o-mini" in result.stdout
    assert "claude-3-opus" in result.stdout
    assert "+" in result.stdout
    assert "-" in result.stdout

    # 2. Test diff between identical profiles
    mock_api.get_profile.side_effect = [(profile_a, None), (profile_c, None)]
    result = runner.invoke(cli.app, ["diff", "profile_a", "profile_c"])
    assert result.exit_code == 0
    assert "Profiles are identical" in result.stdout

    # 3. Test diff with a non-existent profile
    mock_api.get_profile.side_effect = [
        (profile_a, None),
        (None, "Profile 'nonexistent' not found."),
    ]
    result = runner.invoke(cli.app, ["diff", "profile_a", "nonexistent"])
    assert result.exit_code == 1
    assert "Error: Profile 'nonexistent' not found." in result.stdout


@patch("dspy_profiles.commands.diff.api")
def test_diff_command_with_http_url(mock_api: MagicMock):
    """Tests the diff command with a profile containing an HttpUrl."""
    mock_api.get_profile.side_effect = [
        ({"lm": {"api_base": "HttpUrl('http://localhost:8080')"}}, None),
        ({"lm": {"api_base": "HttpUrl('http://localhost:8888')"}}, None),
    ]

    result = runner.invoke(cli.app, ["diff", "profile1", "profile2"])
    assert result.exit_code == 0
    assert 'api_base": "HttpUrl(\'http://localhost:8080\')"' in result.stdout
    assert 'api_base": "HttpUrl(\'http://localhost:8888\')"' in result.stdout
