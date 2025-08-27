from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from dspy_profiles.config import PROFILES_PATH, ProfileManager


@dataclass
class ResolvedProfile:
    """A dataclass holding the fully resolved and merged profile configuration.

    This object represents the final state of a profile after inheritance
    (`extends`) and any runtime overrides have been applied.

    Attributes:
        name (str): The name of the resolved profile.
        config (dict[str, Any]): The complete, merged configuration dictionary.
        lm (dict[str, Any] | None): The specific configuration for the language model.
        rm (dict[str, Any] | None): The specific configuration for the retrieval model.
        settings (dict[str, Any] | None): Any other global settings for `dspy.settings`.
    """

    name: str
    config: dict[str, Any] = field(default_factory=dict)
    lm: dict[str, Any] | None = None
    rm: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None


class ProfileLoader:
    """Resolves a profile by loading, merging, and processing configurations.

    This class handles the logic of finding a `profiles.toml` file, loading a
    specific profile, resolving its inheritance chain using the `extends` key,
    and producing a final, flattened `ResolvedProfile`.

    Attributes:
        config_path (Path): The path to the `profiles.toml` file being used.
    """

    def __init__(self, config_path: str | Path = PROFILES_PATH):
        """Initializes the ProfileLoader.

        Args:
            config_path (str | Path, optional): The path to the `profiles.toml` file.
                If not provided, it uses the default path resolution.
                Defaults to `PROFILES_PATH`.
        """
        self.config_path = Path(config_path)
        self._load_dotenv()

    def _load_dotenv(self):
        """Loads environment variables from a .env file if present."""
        load_dotenv()

    def _deep_merge(self, parent: dict, child: dict) -> dict:
        """Recursively merges two dictionaries. Child values override parent values."""
        merged = parent.copy()
        for key, value in child.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _load_profile_config(
        self, profile_name: str, all_profiles: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Loads and recursively merges the specified profile from the config."""
        if all_profiles is None:
            manager = ProfileManager(self.config_path)
            all_profiles = manager.load()

        if profile_name not in all_profiles:
            if profile_name == "default":
                return {}  # It's okay if the default profile doesn't exist
            raise ValueError(f"Profile '{profile_name}' not found.")

        profile_data = all_profiles.get(profile_name, {})
        parent_name = profile_data.get("extends")

        if parent_name:
            if parent_name == profile_name:
                raise ValueError(f"Profile '{profile_name}' cannot extend itself.")

            parent_config = self._load_profile_config(parent_name, all_profiles)

            # Create copies to avoid modifying the original loaded profiles
            merged_config = parent_config.copy()
            child_config = profile_data.copy()
            child_config.pop("extends", None)  # Remove extends from child before merging

            return self._deep_merge(merged_config, child_config)

        return profile_data

    def get_config(self, profile_name: str | None = None) -> ResolvedProfile:
        """Resolves and returns the final configuration for a given profile name.

        The profile name is determined with the following precedence:
        1. The `profile_name` argument if provided.
        2. The `DSPY_PROFILE` environment variable.
        3. The literal string "default".

        Args:
            profile_name (str | None, optional): The name of the profile to load.
                Defaults to None.

        Returns:
            ResolvedProfile: The fully resolved and merged profile configuration.
        """
        final_profile_name = profile_name or os.getenv("DSPY_PROFILE") or "default"
        profile_config = self._load_profile_config(final_profile_name)

        return ResolvedProfile(
            name=final_profile_name,
            config=profile_config,
            lm=profile_config.get("lm"),
            rm=profile_config.get("rm"),
            settings=profile_config.get("settings"),
        )
