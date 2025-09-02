"""Tests for the core API for managing dspy-profiles."""

from pathlib import Path

import pytest

from dspy_profiles.api import (
    delete_profile,
    get_profile,
    import_profile,
    list_profiles,
    update_profile,
    validate_profiles_file,
)


@pytest.fixture
def mock_profile_manager(monkeypatch):
    """Fixture to mock the ProfileManager."""
    profiles = {}

    class MockProfileManager:
        def __init__(self, path: Path):
            pass

        def load(self):
            return profiles

        def save(self, data):
            nonlocal profiles
            profiles = data

        def get(self, name):
            return profiles.get(name)

        def set(self, name, config):
            profiles[name] = config

        def delete(self, name):
            if name in profiles:
                del profiles[name]
                return True
            return False

    monkeypatch.setattr("dspy_profiles.api.ProfileManager", MockProfileManager)
    monkeypatch.setattr("dspy_profiles.api.find_profiles_path", lambda: Path("/fake/path"))

    # Reset profiles before each test
    profiles.clear()

    return MockProfileManager


def test_list_profiles(mock_profile_manager):
    """Test that list_profiles returns the correct data."""
    manager = mock_profile_manager(None)
    manager.set("default", {"lm": {"model": "gpt-4"}})

    profiles = list_profiles()

    assert "default" in profiles
    assert profiles["default"]["lm"]["model"] == "gpt-4"


def test_get_profile_found(mock_profile_manager):
    """Test retrieving an existing profile."""
    manager = mock_profile_manager(None)
    manager.set("default", {"lm": {"model": "gpt-4"}})

    profile, error = get_profile("default")

    assert error is None
    assert profile is not None
    assert profile["lm"]["model"] == "gpt-4"


def test_get_profile_not_found(mock_profile_manager):
    """Test that getting a non-existent profile returns an error."""
    profile, error = get_profile("non_existent")
    assert profile is None
    assert error == "Profile 'non_existent' not found."


def test_delete_profile_found(mock_profile_manager):
    """Test deleting an existing profile."""
    manager = mock_profile_manager(None)
    manager.set("default", {"lm": {"model": "gpt-4"}})

    delete_profile("default")

    assert manager.get("default") is None


def test_delete_profile_not_found(mock_profile_manager):
    """Test that deleting a non-existent profile returns an error."""
    error = delete_profile("non_existent")
    assert error is not None


def test_update_profile(mock_profile_manager):
    """Test updating a profile's key."""
    manager = mock_profile_manager(None)
    manager.set("default", {"lm": {"model": "gpt-3.5"}})

    updated_profile, error = update_profile("default", "lm.model", "gpt-4-turbo")

    assert error is None
    assert updated_profile is not None
    assert updated_profile["lm"]["model"] == "gpt-4-turbo"


def test_update_profile_new_profile(mock_profile_manager):
    """Test updating a key for a new profile."""
    updated_profile, error = update_profile("new_profile", "lm.api_key", "12345")

    assert error is None
    assert updated_profile is not None
    assert updated_profile["lm"]["api_key"] == "12345"


def test_update_profile_with_nested_key(mock_profile_manager):
    """Tests that `set` command correctly handles nested keys without overwriting the structure."""
    manager = mock_profile_manager(None)
    # GIVEN a profile with a nested structure
    initial_profile = {
        "lm": {
            "model": "openai/hola",
            "api_base": "HttpUrl('http://base-url/')",
            "api_key": "bla123",
        }
    }
    manager.set("default", initial_profile)

    # WHEN we update a nested key
    update_profile("default", "lm.api_key", "newkey456")

    # THEN the updated profile should be set with the full nested structure preserved
    expected_profile = {
        "lm": {
            "model": "openai/hola",
            "api_base": "HttpUrl('http://base-url/')",
            "api_key": "newkey456",
        }
    }
    assert manager.get("default") == expected_profile


def test_import_profile(mock_profile_manager, tmp_path):
    """Test importing a profile from a .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("DSPY_LM_MODEL=model1\nDSPY_RM_PROVIDER=colbert")
    err = import_profile("imported_prof", env_file)
    assert err is None

    manager = mock_profile_manager(None)
    assert manager.get("imported_prof") is not None


def test_validate_profiles_file(tmp_path):
    """Test validating a profiles.toml file."""
    valid_file = tmp_path / "valid.toml"
    valid_file.write_text('[default]\nlm = {model = "gpt-4"}')
    assert validate_profiles_file(valid_file) is None

    invalid_file = tmp_path / "invalid.toml"
    invalid_file.write_text("this is not toml")
    assert validate_profiles_file(invalid_file) is not None


def test_validate_profiles_file_rm_class_name(tmp_path):
    """Validation should allow rm.class_name based configs."""
    valid_rm = tmp_path / "valid_rm.toml"
    valid_rm.write_text(
        """
[default.rm]
class_name = "ColBERTv2"
url = "http://localhost:8893/api/search"
        """.strip()
    )
    assert validate_profiles_file(valid_rm) is None
