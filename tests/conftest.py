import copy
from unittest.mock import patch

import dspy
from dspy.dsp.utils.settings import DEFAULT_CONFIG
from dspy.utils.dummies import DummyLM
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
    "decorator_profile": {"lm": DummyLM([{"answer": "dummy profile answer"}])},
    "env_profile_decorator": {"lm": {"model": "env_model_decorator"}},
    "other_profile_decorator": {"lm": {"model": "other_model_decorator"}},
    "forced_profile_decorator": {"lm": {"model": "forced_model_decorator"}},
    "no_lm_profile": {"rm": {"url": "http://some-rm-url"}},
}


@pytest.fixture(autouse=True)
def clear_settings():
    """Ensures that the dspy.settings are cleared after each test."""
    yield
    dspy.settings.configure(**copy.deepcopy(DEFAULT_CONFIG), inherit_config=False)


@pytest.fixture
def profile_manager():
    """
    Mocks the ProfileManager to provide a consistent, in-memory dictionary of profiles
    that can be safely manipulated by tests without affecting the filesystem.
    """
    # Use a deepcopy to ensure each test gets a fresh, isolated version of the profiles
    profiles_copy = copy.deepcopy(MOCK_PROFILES)

    def mock_save(data):
        profiles_copy.update(data)

    with patch("dspy_profiles.loader.ProfileManager") as mock:
        instance = mock.return_value
        instance.load.return_value = profiles_copy
        # Mock the save method to update our in-memory dictionary
        instance.save = mock_save
        # Also mock the path attribute to avoid filesystem interactions
        instance.path = "/tmp/dummy_profiles.toml"
        yield instance
