import copy

import dspy
from dspy.dsp.utils.settings import DEFAULT_CONFIG
import pytest

# Sample profiles for testing, now globally available
MOCK_PROFILES = {
    "base": {
        "lm": {"model": "base_model", "temperature": 0.7},
        "settings": {"retries": 2},
    },
    "child": {
        "extends": "base",
        "lm": {"model": "child_model"},
        "rm": {"url": "http://child_rm_url"},
    },
    "grandchild": {
        "extends": "child",
        "settings": {"retries": 5, "timeout": 60},
    },
    "circular": {"extends": "circular"},
    "dev": {"lm": {"model": "dev_model"}},
    "prod": {"lm": {"model": "prod_model"}},
    # Profiles for test_core.py
    "test_profile": {"lm": {"model": "test_model_context"}},
    "env_profile": {"lm": {"model": "env_model"}},
    "other_profile": {"lm": {"model": "other_model"}},
    "forced_profile": {"lm": {"model": "forced_model"}},
    "decorator_profile": {"lm": {"model": "decorator_model"}},
    "env_profile_decorator": {"lm": {"model": "env_model_decorator"}},
    "other_profile_decorator": {"lm": {"model": "other_model_decorator"}},
    "forced_profile_decorator": {"lm": {"model": "forced_model_decorator"}},
    "no_lm_profile": {"rm": {"model": "some-rm"}},
    "default": {"lm": {"model": "default_model"}},
}


@pytest.fixture(autouse=True)
def clear_settings():
    """Ensures that the dspy.settings are cleared after each test."""
    yield
    dspy.settings.configure(**copy.deepcopy(DEFAULT_CONFIG), inherit_config=False)


@pytest.fixture
def profile_manager(monkeypatch):
    """
    Provides a stateful, in-memory mock of ProfileLoader and ProfileManager
    that can be safely manipulated by tests without affecting the filesystem.
    """

    class MockProfileManager:
        def __init__(self, initial_profiles):
            self.profiles = copy.deepcopy(initial_profiles)
            self.path = "/tmp/dummy_path_for_tests"

        def load(self):
            return self.profiles

        def _load_profile_config(self, profile_name, history=None):
            if history is None:
                history = set()
            if profile_name in history:
                raise ValueError("Circular dependency detected")
            history.add(profile_name)

            if profile_name not in self.profiles:
                raise ValueError(f"Profile '{profile_name}' not found.")

            config = copy.deepcopy(self.profiles[profile_name])
            if "extends" in config:
                if config["extends"] == profile_name:
                    raise ValueError(f"Profile '{profile_name}' cannot extend itself.")
                base_config = self._load_profile_config(config.pop("extends"), history)
                # A simplified deep merge for tests
                for key, value in config.items():
                    if (
                        key in base_config
                        and isinstance(base_config[key], dict)
                        and isinstance(value, dict)
                    ):
                        base_config[key].update(value)
                    else:
                        base_config[key] = value
                config = base_config
            return config

        def get_config(self, profile_name, **overrides):
            from dspy_profiles.loader import ResolvedProfile

            config = self._load_profile_config(profile_name)
            if overrides:
                if "lm" in overrides and "lm" in config:
                    config["lm"].update(overrides)
                else:
                    config.update(overrides)
            return ResolvedProfile(
                name=profile_name,
                config=config,
                lm=config.get("lm"),
                rm=config.get("rm"),
                settings=config.get("settings"),
            )

        def create(self, profile_name, data):
            self.profiles[profile_name] = data

    mock_instance = MockProfileManager(MOCK_PROFILES)

    # Patch both ProfileLoader and ProfileManager to return our mock instance
    monkeypatch.setattr(
        "dspy_profiles.loader.ProfileLoader", lambda config_path=None: mock_instance
    )
    monkeypatch.setattr(
        "dspy_profiles.loader.ProfileManager", lambda config_path=None: mock_instance
    )
    monkeypatch.setattr("dspy_profiles.core.ProfileLoader", lambda config_path=None: mock_instance)

    return mock_instance
