from pathlib import Path
from typing import Any

import toml

CONFIG_DIR = Path.home() / ".dspy"
PROFILES_PATH = CONFIG_DIR / "profiles.toml"

_manager = None


def get_manager():
    """Returns a singleton ProfileManager instance."""
    global _manager
    if _manager is None:
        _manager = ProfileManager(PROFILES_PATH)
    return _manager


class ProfileManager:
    """Manages loading, saving, and updating profiles from a TOML file."""

    def __init__(self, path: Path):
        self.path = path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensures the profiles file and its directory exist."""
        self.path.parent.mkdir(exist_ok=True, parents=True)
        self.path.touch(exist_ok=True)

    def load(self) -> dict[str, Any]:
        """Loads all profiles from the file."""
        with self.path.open("r") as f:
            try:
                return toml.load(f)
            except toml.TomlDecodeError:
                return {}

    def save(self, profiles: dict[str, Any]):
        """Saves all profiles to the file."""
        with self.path.open("w") as f:
            toml.dump(profiles, f)

    def get(self, profile_name: str) -> dict[str, Any] | None:
        """Retrieves a specific profile by name."""
        profiles = self.load()
        return profiles.get(profile_name)

    def set(self, profile_name: str, config: dict[str, Any]):
        """Saves or updates a single profile."""
        profiles = self.load()
        profiles[profile_name] = config
        self.save(profiles)

    def delete(self, profile_name: str) -> bool:
        """Deletes a profile by name."""
        profiles = self.load()
        if profile_name in profiles:
            del profiles[profile_name]
            self.save(profiles)
            return True
        return False
