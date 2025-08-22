from pathlib import Path
from typing import Any, Dict, Optional

import toml

# Define the path for the profiles file
DSPY_DIR = Path.home() / ".dspy"
PROFILES_PATH = DSPY_DIR / "profiles.toml"


def ensure_profiles_file_exists():
    """Ensures the profiles.toml file and its directory exist."""
    DSPY_DIR.mkdir(exist_ok=True)
    PROFILES_PATH.touch(exist_ok=True)


def load_profiles() -> Dict[str, Any]:
    """Loads all profiles from the profiles.toml file."""
    ensure_profiles_file_exists()
    with open(PROFILES_PATH, "r") as f:
        return toml.load(f)


def get_profile(profile_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a specific profile by name.

    Args:
        profile_name: The name of the profile to retrieve.

    Returns:
        A dictionary containing the profile's configuration, or None if not found.
    """
    profiles = load_profiles()
    return profiles.get(profile_name)


def save_profile(profile_name: str, config: Dict[str, Any]):
    """
    Saves or updates a profile in the profiles.toml file.

    Args:
        profile_name: The name of the profile to save.
        config: The configuration dictionary for the profile.
    """
    profiles = load_profiles()
    profiles[profile_name] = config
    with open(PROFILES_PATH, "w") as f:
        toml.dump(profiles, f)


def delete_profile(profile_name: str) -> bool:
    """
    Deletes a profile by name.

    Args:
        profile_name: The name of the profile to delete.

    Returns:
        True if the profile was deleted, False otherwise.
    """
    profiles = load_profiles()
    if profile_name in profiles:
        del profiles[profile_name]
        with open(PROFILES_PATH, "w") as f:
            toml.dump(profiles, f)
        return True
    return False
