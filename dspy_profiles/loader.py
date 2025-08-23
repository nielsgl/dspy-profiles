from dataclasses import dataclass, field
import os
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

    def __init__(self, profile_name: str | None = None):
        self.profile_name = profile_name or os.getenv("DSPY_PROFILE") or "default"
        self._load_dotenv()
        self.profile_config = self._load_profile_config()

    def _load_dotenv(self):
        """Loads environment variables from a .env file if present."""
        load_dotenv()

    def _load_profile_config(self) -> dict[str, Any]:
        """Loads the specified profile from the config file."""
        manager = ProfileManager(PROFILES_PATH)
        all_profiles = manager.load()
        if self.profile_name not in all_profiles:
            if self.profile_name == "default":
                return {}  # It's okay if the default profile doesn't exist
            raise ValueError(f"Profile '{self.profile_name}' not found.")
        return all_profiles.get(self.profile_name, {})

    def get_config(self) -> ResolvedProfile:
        """
        Resolves and returns the final profile configuration.
        Secrets are loaded from the environment.
        """
        # For now, we'll just pass the profile through.
        # In the next step, we'll add secret injection and object instantiation.

        lm_config = self.profile_config.get("lm", {})
        rm_config = self.profile_config.get("rm", {})
        settings_config = self.profile_config.get("settings", {})

        return ResolvedProfile(
            name=self.profile_name,
            config=self.profile_config,
            lm=lm_config,
            rm=rm_config,
            settings=settings_config,
        )
