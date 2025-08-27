from pathlib import Path

from typer.testing import CliRunner

from dspy_profiles import cli
from dspy_profiles.config import ProfileManager

runner = CliRunner()


def test_import_profile(tmp_path: Path, monkeypatch):
    """Tests the import command with an isolated profile manager."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr(
        "dspy_profiles.commands.import_profile.find_profiles_path", lambda: config_path
    )
    manager = ProfileManager(config_path)

    # 1. Test successful import
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
    profile = manager.get("imported_profile")
    assert profile is not None
    assert profile.get("lm", {}).get("model") == "gpt-4o-mini"
    assert profile.get("settings", {}).get("temperature") == "0.7"

    # 2. Test import when profile already exists
    result = runner.invoke(
        cli.app,
        ["import", "--profile", "imported_profile", "--from", str(env_file)],
    )
    assert result.exit_code == 1
    assert "already exists" in result.stdout

    # 3. Test import with a non-existent file
    result = runner.invoke(
        cli.app,
        ["import", "--profile", "any_profile", "--from", "nonexistent.env"],
    )
    assert result.exit_code == 2  # Typer's exit code for file not found
    assert "Invalid value" in result.stderr
