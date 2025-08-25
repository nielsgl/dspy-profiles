from pathlib import Path

import pytest
from typer.testing import CliRunner

from dspy_profiles.cli import app

runner = CliRunner()


@pytest.fixture
def valid_profiles_file(tmp_path: Path) -> Path:
    """Creates a valid profiles.toml file."""
    content = """
[profile.default]
lm.model = "gpt-4o-mini"
lm.api_base = "https://api.openai.com/v1"

[profile.ollama]
extends = "default"
lm.model = "ollama/llama3"
lm.api_base = "http://localhost:11434/v1"
rm.model = "colbertv2.0"
cache.enabled = true
"""
    file_path = tmp_path / "profiles.toml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def invalid_profiles_file(tmp_path: Path) -> Path:
    """Creates an invalid profiles.toml file."""
    content = """
[profile.bad_lm]
lm.model = 123  # Invalid type

[profile.bad_rm]
rm.model = false # Invalid type

[profile.unknown_toplevel]
cache.enabled = true
storage.type = "local"
"""
    file_path = tmp_path / "profiles.toml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def malformed_toml_file(tmp_path: Path) -> Path:
    """Creates a malformed profiles.toml file."""
    content = """
[profile.default]
  model = "missing_section"
  is_malformed =
"""
    file_path = tmp_path / "profiles.toml"
    file_path.write_text(content)
    return file_path


def test_validate_valid_file(valid_profiles_file: Path):
    """Test validation with a valid profiles.toml file."""
    result = runner.invoke(app, ["validate", "--config", str(valid_profiles_file)])
    assert result.exit_code == 0
    assert "✅ Success!" in result.stdout
    assert "All profiles are valid" in result.stdout


def test_validate_invalid_file(invalid_profiles_file: Path):
    """Test validation with an invalid profiles.toml file."""
    result = runner.invoke(app, ["validate", "--config", str(invalid_profiles_file)])
    assert result.exit_code == 1
    assert "❌ Validation Failed" in result.stdout
    assert "profiles -> bad_lm -> lm -> model" in result.stdout
    assert "Input should be a valid string" in result.stdout
    assert "profiles -> bad_rm -> rm -> model" in result.stdout


def test_validate_nonexistent_file():
    """Test validation with a nonexistent file."""
    result = runner.invoke(app, ["validate", "--config", "nonexistent.toml"])
    assert result.exit_code == 2  # typer exit code for file not found
    assert "does not exist" in result.stderr


def test_validate_malformed_toml(malformed_toml_file: Path):
    """Test validation with a malformed TOML file."""
    result = runner.invoke(app, ["validate", "--config", str(malformed_toml_file)])
    assert result.exit_code == 1
    assert "Invalid TOML format" in result.stdout
