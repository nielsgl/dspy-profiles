import os
from pathlib import Path
from typing import Any

from pydantic import ValidationError
import toml

from dspy_profiles.utils import normalize_config
from dspy_profiles.validation import ProfilesFile

CONFIG_DIR = Path.home() / ".dspy"
"""The default directory for storing dspy-profiles configuration."""

PROFILES_PATH = CONFIG_DIR / "profiles.toml"
"""The default path to the profiles configuration file."""

_manager = None


def find_profiles_path() -> Path:
    """Finds the path to the profiles.toml file with a hierarchical search.

    The search order is as follows:
    1.  `DSPY_PROFILES_PATH` environment variable.
    2.  Search for `profiles.toml` in the current directory and parent directories.
    3.  Fall back to the global default path (`~/.dspy/profiles.toml`).

    Returns:
        Path: The resolved path to the `profiles.toml` file.
    """
    # 1. Check environment variable
    if env_path_str := os.getenv("DSPY_PROFILES_PATH"):
        return Path(env_path_str)

    # 2. Search current and parent directories
    current_dir = Path.cwd()
    for directory in [current_dir, *current_dir.parents]:
        local_path = directory / "profiles.toml"
        if local_path.exists():
            return local_path

    # 3. Fallback to global default
    print(f"{PROFILES_PATH=}")
    return PROFILES_PATH


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
                if not data:
                    return {}

                normalized_data = normalize_config(data)
                ProfilesFile.model_validate(normalized_data)
                return normalized_data
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
        self.save(profiles)

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
            self.save(profiles)
            return True
        return False
