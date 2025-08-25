import os

import dspy
import pytest

from dspy_profiles.core import profile, with_profile


# Fixture to manage environment variables
@pytest.fixture
def manage_env_var():
    original_value = os.environ.get("DSPY_PROFILE")
    yield
    if original_value is not None:
        os.environ["DSPY_PROFILE"] = original_value
    elif "DSPY_PROFILE" in os.environ:
        del os.environ["DSPY_PROFILE"]


def test_profile_context_manager_activates_profile(profile_manager):
    """Tests that the profile() context manager correctly activates a profile."""
    with profile("test_profile", config_path=profile_manager.path):
        assert dspy.settings.lm.model == "test_model_context"

    assert dspy.settings.lm is None


def test_dspy_profile_env_var_has_precedence(profile_manager, manage_env_var):
    """Tests that DSPY_PROFILE environment variable overrides the context manager."""
    os.environ["DSPY_PROFILE"] = "env_profile"

    # When DSPY_PROFILE is set, calling profile() should load that profile
    with profile("other_profile", config_path=profile_manager.path):
        assert dspy.settings.lm.model == "env_model"


def test_force_overrides_dspy_profile_env_var(profile_manager, manage_env_var):
    """Tests that force=True in the context manager overrides DSPY_PROFILE."""
    os.environ["DSPY_PROFILE"] = "env_profile"

    with profile("forced_profile", force=True, config_path=profile_manager.path):
        assert dspy.settings.lm.model == "forced_model"


def test_with_profile_decorator(profile_manager):
    """Tests that the @with_profile decorator works."""

    @with_profile("decorator_profile", config_path=profile_manager.path)
    def my_function():
        return dspy.settings.lm.model

    assert my_function() == "decorator_model"
    assert dspy.settings.lm is None


def test_with_profile_decorator_respects_env_var(profile_manager, manage_env_var):
    """Tests that the @with_profile decorator respects DSPY_PROFILE."""
    os.environ["DSPY_PROFILE"] = "env_profile"

    @with_profile("other_profile", config_path=profile_manager.path)
    def my_function():
        return dspy.settings.lm.model

    assert my_function() == "env_model"


def test_with_profile_decorator_force_overrides_env_var(profile_manager, manage_env_var):
    """Tests that force=True in the decorator overrides DSPY_PROFILE."""
    os.environ["DSPY_PROFILE"] = "env_profile"

    @with_profile("forced_profile", force=True, config_path=profile_manager.path)
    def my_function():
        return dspy.settings.lm.model

    assert my_function() == "forced_model"


def test_profile_no_profile_found(profile_manager):
    """Tests that nothing happens when no profile is found."""
    with profile(config_path=profile_manager.path):
        assert dspy.settings.lm is None
