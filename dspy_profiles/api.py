"""Core API for managing dspy-profiles."""

from typing import Any

from dspy_profiles.config import ProfileManager, find_profiles_path


class ProfileNotFound(Exception):
    """Raised when a requested profile is not found."""

    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        super().__init__(f"Profile '{profile_name}' not found.")


def list_profiles() -> dict[str, Any]:
    """Lists all available profiles.

    Returns:
        A dictionary of all profiles.
    """
    manager = ProfileManager(find_profiles_path())
    return manager.load()


def get_profile(profile_name: str) -> dict[str, Any]:
    """Retrieves a specific profile by name.

    Args:
        profile_name: The name of the profile to retrieve.

    Returns:
        The profile's configuration dictionary.

    Raises:
        ProfileNotFound: If the profile does not exist.
    """
    manager = ProfileManager(find_profiles_path())
    profile = manager.get(profile_name)
    if profile is None:
        raise ProfileNotFound(profile_name)
    return profile


def delete_profile(profile_name: str) -> None:
    """Deletes a specified profile.

    Args:
        profile_name: The name of the profile to delete.

    Raises:
        ProfileNotFound: If the profile does not exist.
    """
    manager = ProfileManager(find_profiles_path())
    if not manager.delete(profile_name):
        raise ProfileNotFound(profile_name)


def update_profile(profile_name: str, key: str, value: Any) -> dict[str, Any]:
    """Sets or updates a configuration value for a given profile.

    This function will be improved later to handle the `set` command bug correctly.

    Args:
        profile_name: The name of the profile to modify.
        key: The configuration key to set (e.g., 'lm.model').
        value: The value to set for the key.

    Returns:
        The updated profile data.
    """
    manager = ProfileManager(find_profiles_path())
    profile_data = manager.get(profile_name) or {}

    keys = key.split(".")
    current_level = profile_data
    for k in keys[:-1]:
        current_level = current_level.setdefault(k, {})

    current_level[keys[-1]] = value

    manager.set(profile_name, profile_data)
    return profile_data
