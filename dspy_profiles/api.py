"""Core API for managing dspy-profiles."""

from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from pydantic import ValidationError
import toml

from dspy_profiles.config import ProfileManager, find_profiles_path
from dspy_profiles.validation import ProfilesFile


class ProfileNotFound(Exception):
    """Raised when a requested profile is not found."""

    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        super().__init__(f"Profile '{profile_name}' not found.")


class ProfileExistsError(Exception):
    """Raised when attempting to create a profile that already exists."""

    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        super().__init__(f"Profile '{profile_name}' already exists.")


def list_profiles() -> dict[str, Any]:
    """Lists all available profiles.

    Returns:
        A dictionary of all profiles.
    """
    manager = ProfileManager(find_profiles_path())
    return manager.load()


def get_profile(profile_name: str) -> tuple[dict[str, Any] | None, str | None]:
    """Retrieves a specific profile by name.

    Args:
        profile_name: The name of the profile to retrieve.

    Returns:
        A tuple containing the profile data and an error message, if any.
    """
    manager = ProfileManager(find_profiles_path())
    profile = manager.get(profile_name)
    if profile is None:
        return None, f"Profile '{profile_name}' not found."
    return profile, None


def delete_profile(profile_name: str) -> str | None:
    """Deletes a specified profile.

    Args:
        profile_name: The name of the profile to delete.

    Returns:
        An error message if the profile was not found, otherwise None.
    """
    manager = ProfileManager(find_profiles_path())
    profiles = manager.load()
    if profile_name not in profiles:
        return f"Profile '{profile_name}' not found."

    del profiles[profile_name]
    manager.save(profiles)
    return None


def update_profile(
    profile_name: str, key: str, value: Any
) -> tuple[dict[str, Any] | None, str | None]:
    """Sets or updates a configuration value for a given profile.

    Args:
        profile_name: The name of the profile to modify.
        key: The configuration key to set (e.g., 'lm.model').
        value: The value to set for the key.

    Returns:
        A tuple containing the updated profile data and an error message, if any.
    """
    manager = ProfileManager(find_profiles_path())
    profile_data = manager.get(profile_name)
    if profile_data is None:
        profile_data = {}

    keys = key.split(".")
    current_level = profile_data
    for k in keys[:-1]:
        current_level = current_level.setdefault(k, {})

    current_level[keys[-1]] = value

    manager.set(profile_name, profile_data)
    return profile_data, None


def create_profile(profile_name: str, profile_data: dict[str, Any]) -> None:
    """Creates a new profile.

    Args:
        profile_name: The name for the new profile.
        profile_data: The configuration data for the profile.
    """
    manager = ProfileManager(find_profiles_path())
    manager.set(profile_name, profile_data)


def import_profile(profile_name: str, from_path: "Path") -> str | None:
    """Imports a profile from a .env file.

    Args:
        profile_name: The name for the new profile.
        from_path: The path to the .env file.

    Returns:
        An error message if the import fails, otherwise None.
    """
    manager = ProfileManager(find_profiles_path())
    if manager.get(profile_name):
        return f"Profile '{profile_name}' already exists."

    env_values = dotenv_values(from_path)
    if not env_values:
        return f"No values found in '{from_path}'."

    new_profile = {}
    for key, value in env_values.items():
        if key.upper().startswith("DSPY_"):
            parts = key.upper().split("_")[1:]
            if len(parts) < 2:
                continue

            section = parts[0].lower()
            config_key = "_".join(parts[1:]).lower()

            if section not in new_profile:
                new_profile[section] = {}
            new_profile[section][config_key] = value

    if not new_profile:
        return f"No variables with the 'DSPY_' prefix found in '{from_path}'."

    manager.set(profile_name, new_profile)
    return None


def validate_profiles_file(config_path: Path) -> Exception | None:
    """Validates the structure and content of a profiles.toml file.

    Args:
        config_path: The path to the profiles.toml file.

    Returns:
        An exception object if validation fails, otherwise None.
    """
    try:
        with open(config_path) as f:
            data = toml.load(f)
        ProfilesFile.model_validate(data)
        return None
    except (FileNotFoundError, toml.TomlDecodeError, ValidationError) as e:
        return e
