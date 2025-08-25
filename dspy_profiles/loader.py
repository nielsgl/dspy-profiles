from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from dspy_profiles.config import PROFILES_PATH, ProfileManager


@dataclass
class ResolvedProfile:
    """A dataclass to hold the fully resolved profile configuration."""

    name: str
    config: dict[str, Any] = field(default_factory=dict)
    lm: dict[str, Any] | None = None
    rm: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None


class ProfileLoader:
    """Resolves a profile by merging settings from files and the environment."""

    def __init__(self, config_path: str | Path = PROFILES_PATH):
        self.config_path = Path(config_path)
        self._load_dotenv()

    def _load_dotenv(self):
        """Loads environment variables from a .env file if present."""
        load_dotenv()

    def _load_profile_config(self, profile_name: str) -> dict[str, Any]:
        """Loads the specified profile from the config file."""
        manager = ProfileManager(self.config_path)
        all_profiles = manager.load()
        if profile_name not in all_profiles:
            if profile_name == "default":
                return {}  # It's okay if the default profile doesn't exist
            raise ValueError(f"Profile '{profile_name}' not found.")
        return all_profiles.get(profile_name, {})

    def get_config(self, profile_name: str | None = None) -> ResolvedProfile:
        """
        Resolves and returns the final profile configuration.
        The precedence is: provided name -> DSPY_PROFILE env var -> 'default'.
        """
        final_profile_name = profile_name or os.getenv("DSPY_PROFILE") or "default"
        profile_config = self._load_profile_config(final_profile_name)

        lm_config = profile_config.get("lm")
        rm_config = profile_config.get("rm")
        settings_config = profile_config.get("settings")

        return ResolvedProfile(
            name=final_profile_name,
            config=profile_config,
            lm=lm_config,
            rm=rm_config,
            settings=settings_config,
        )
