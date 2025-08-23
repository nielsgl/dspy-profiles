from unittest.mock import patch

import pytest

from dspy_profiles.loader import ProfileLoader


@pytest.fixture
def mock_profiles():
    return {
        "default": {"lm": {"model": "default_model"}},
        "prod": {
            "lm": {"model": "prod_model"},
            "settings": {"track_usage": True},
        },
    }


@patch("dspy_profiles.loader.ProfileManager")
def test_load_default_profile(mock_profile_manager, mock_profiles):
    """Tests that the 'default' profile is loaded when none is specified."""
    mock_manager_instance = mock_profile_manager.return_value
    mock_manager_instance.load.return_value = mock_profiles
    loader = ProfileLoader()
    config = loader.get_config()
    assert config.name == "default"
    assert config.lm is not None
    assert config.lm["model"] == "default_model"


@patch("dspy_profiles.loader.ProfileManager")
def test_load_named_profile(mock_profile_manager, mock_profiles):
    """Tests loading a specifically named profile."""
    mock_manager_instance = mock_profile_manager.return_value
    mock_manager_instance.load.return_value = mock_profiles
    loader = ProfileLoader(profile_name="prod")
    config = loader.get_config()
    assert config.name == "prod"
    assert config.lm is not None
    assert config.lm["model"] == "prod_model"
    assert config.settings is not None
    assert config.settings["track_usage"] is True


@patch("dspy_profiles.loader.ProfileManager")
def test_load_profile_from_env(mock_profile_manager, mock_profiles, monkeypatch):
    """Tests that the profile name is taken from the DSPY_PROFILE env var."""
    monkeypatch.setenv("DSPY_PROFILE", "prod")
    mock_manager_instance = mock_profile_manager.return_value
    mock_manager_instance.load.return_value = mock_profiles
    loader = ProfileLoader()
    config = loader.get_config()
    assert config.name == "prod"
    assert config.lm is not None
    assert config.lm["model"] == "prod_model"


@patch("dspy_profiles.loader.ProfileManager")
def test_profile_not_found(mock_profile_manager):
    """Tests that a ValueError is raised for a non-existent profile."""
    mock_manager_instance = mock_profile_manager.return_value
    mock_manager_instance.load.return_value = {}
    with pytest.raises(ValueError, match="Profile 'nonexistent' not found"):
        ProfileLoader(profile_name="nonexistent")


@patch("dspy_profiles.loader.ProfileManager")
@patch("dspy_profiles.loader.load_dotenv")
def test_dotenv_loading(mock_load_dotenv, mock_profile_manager):
    """Tests that load_dotenv is called."""
    mock_manager_instance = mock_profile_manager.return_value
    mock_manager_instance.load.return_value = {}
    ProfileLoader()
    mock_load_dotenv.assert_called_once()
