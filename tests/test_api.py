"""Tests for the core API for managing dspy-profiles."""

from unittest.mock import patch

import pytest

from dspy_profiles.api import (
    ProfileNotFound,
    delete_profile,
    get_profile,
    list_profiles,
    update_profile,
)


@pytest.fixture
def mock_profile_manager():
    """Fixture to mock the ProfileManager."""
    with patch("dspy_profiles.api.ProfileManager") as mock:
        yield mock


def test_list_profiles(mock_profile_manager):
    """Test that list_profiles returns the correct data."""
    mock_instance = mock_profile_manager.return_value
    mock_instance.load.return_value = {"default": {"lm": {"model": "gpt-4"}}}

    profiles = list_profiles()

    assert "default" in profiles
    assert profiles["default"]["lm"]["model"] == "gpt-4"
    mock_instance.load.assert_called_once()


def test_get_profile_found(mock_profile_manager):
    """Test retrieving an existing profile."""
    mock_instance = mock_profile_manager.return_value
    mock_instance.get.return_value = {"lm": {"model": "gpt-4"}}

    profile = get_profile("default")

    assert profile["lm"]["model"] == "gpt-4"
    mock_instance.get.assert_called_once_with("default")


def test_get_profile_not_found(mock_profile_manager):
    """Test that getting a non-existent profile raises ProfileNotFound."""
    mock_instance = mock_profile_manager.return_value
    mock_instance.get.return_value = None

    with pytest.raises(ProfileNotFound):
        get_profile("non_existent")


def test_delete_profile_found(mock_profile_manager):
    """Test deleting an existing profile."""
    mock_instance = mock_profile_manager.return_value
    mock_instance.delete.return_value = True

    delete_profile("default")

    mock_instance.delete.assert_called_once_with("default")


def test_delete_profile_not_found(mock_profile_manager):
    """Test that deleting a non-existent profile raises ProfileNotFound."""
    mock_instance = mock_profile_manager.return_value
    mock_instance.delete.return_value = False

    with pytest.raises(ProfileNotFound):
        delete_profile("non_existent")


def test_update_profile(mock_profile_manager):
    """Test updating a profile's key."""
    mock_instance = mock_profile_manager.return_value
    mock_instance.get.return_value = {"lm": {"model": "gpt-3.5"}}

    updated_profile = update_profile("default", "lm.model", "gpt-4-turbo")

    assert updated_profile["lm"]["model"] == "gpt-4-turbo"
    mock_instance.set.assert_called_once_with("default", {"lm": {"model": "gpt-4-turbo"}})


def test_update_profile_new_profile(mock_profile_manager):
    """Test updating a key for a new profile."""
    mock_instance = mock_profile_manager.return_value
    mock_instance.get.return_value = None  # Profile doesn't exist yet

    updated_profile = update_profile("new_profile", "lm.api_key", "12345")

    assert updated_profile["lm"]["api_key"] == "12345"
    mock_instance.set.assert_called_once_with("new_profile", {"lm": {"api_key": "12345"}})
