from pathlib import Path
from typing import Any

from pydantic import ValidationError
import toml

from dspy_profiles.validation import ProfilesFile

CONFIG_DIR = Path.home() / ".dspy"
"""The default directory for storing dspy-profiles configuration."""

PROFILES_PATH = CONFIG_DIR / "profiles.toml"
"""The default path to the profiles configuration file."""

_manager = None


def get_manager():
    """Returns a singleton `ProfileManager` instance.

    This function ensures that a single instance of the `ProfileManager` is used
    throughout the application, providing a consistent point of access to the
    profile configurations.

    Returns:
        ProfileManager: The singleton `ProfileManager` instance.
    """
    global _manager
    if _manager is None:
        _manager = ProfileManager(PROFILES_PATH)
    return _manager


class ProfileManager:
    """Manages loading, saving, and updating profiles from a TOML file.

    This class provides a high-level API for interacting with the `profiles.toml`
    file, handling file creation, reading, writing, and validation.

    Attributes:
        path (Path): The file path to the `profiles.toml` being managed.
    """

    def __init__(self, path: Path):
        """Initializes the ProfileManager.

        Args:
            path (Path): The path to the `profiles.toml` file.
        """
        self.path = path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensures the profiles file and its parent directory exist."""
        self.path.parent.mkdir(exist_ok=True, parents=True)
        self.path.touch(exist_ok=True)

    def load(self) -> dict[str, Any]:
        """Loads and validates all profiles from the TOML file.

        Returns:
            dict[str, Any]: A dictionary of the loaded profiles. Returns an empty
            dictionary if the file is empty, invalid, or not found.
        """
        if not self.path.is_file():
            return {}
        with self.path.open("r") as f:
            try:
                data = toml.load(f)
                if not data or "profile" not in data:
                    return {}
                # Restructure for validation
                profiles_data = {"profiles": data.get("profile", {})}
                validated_profiles = ProfilesFile.model_validate(profiles_data)
                return validated_profiles.model_dump()["profiles"]
            except (toml.TomlDecodeError, ValidationError):
                return {}

    def save(self, profiles: dict[str, Any]):
        """Saves a dictionary of profiles to the TOML file.

        Args:
            profiles (dict[str, Any]): The dictionary of profiles to save.
        """
        with self.path.open("w") as f:
            toml.dump(profiles, f)

    def get(self, profile_name: str) -> dict[str, Any] | None:
        """Retrieves a specific profile by name.

        Args:
            profile_name (str): The name of the profile to retrieve.

        Returns:
            dict[str, Any] | None: The profile's configuration dictionary, or None
            if not found.
        """
        profiles = self.load()
        return profiles.get(profile_name)

    def set(self, profile_name: str, config: dict[str, Any]):
        """Saves or updates a single profile.

        Args:
            profile_name (str): The name of the profile to save or update.
            config (dict[str, Any]): The configuration dictionary for the profile.
        """
        profiles = self.load()
        profiles[profile_name] = config
        self.save({"profile": profiles})

    def delete(self, profile_name: str) -> bool:
        """Deletes a profile by name.

        Args:
            profile_name (str): The name of the profile to delete.

        Returns:
            bool: True if the profile was deleted, False otherwise.
        """
        profiles = self.load()
        if profile_name in profiles:
            del profiles[profile_name]
            self.save({"profile": profiles})
            return True
        return False
