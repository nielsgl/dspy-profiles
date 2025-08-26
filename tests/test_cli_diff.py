from pathlib import Path

from typer.testing import CliRunner

from dspy_profiles import cli
from dspy_profiles.config import ProfileManager

runner = CliRunner()


def test_diff_command(tmp_path: Path, monkeypatch):
    """Tests the diff command with an isolated profile manager."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.cli.find_profiles_path", lambda: config_path)
    manager = ProfileManager(config_path)

    # Setup profiles
    manager.set("profile_a", {"lm": {"model": "gpt-4o-mini"}})
    manager.set("profile_b", {"lm": {"model": "claude-3-opus"}})
    manager.set("profile_c", {"lm": {"model": "gpt-4o-mini"}})

    # 1. Test diff between different profiles
    result = runner.invoke(cli.app, ["diff", "profile_a", "profile_b"])
    assert result.exit_code == 0
    assert "gpt-4o-mini" in result.stdout
    assert "claude-3-opus" in result.stdout
    assert "+" in result.stdout
    assert "-" in result.stdout

    # 2. Test diff between identical profiles
    result = runner.invoke(cli.app, ["diff", "profile_a", "profile_c"])
    assert result.exit_code == 0
    assert "Profiles are identical" in result.stdout

    # 3. Test diff with a non-existent profile
    result = runner.invoke(cli.app, ["diff", "profile_a", "nonexistent"])
    assert result.exit_code == 1
    assert "Profile 'nonexistent' not found" in result.stdout
