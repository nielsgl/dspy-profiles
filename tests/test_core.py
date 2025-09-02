import os

import dspy
from dspy.utils import DummyLM
import pytest

from dspy_profiles.core import _LM_CACHE, current_profile, lm, profile, with_profile


class MyModule(dspy.Module):
    """A simple dspy.Module for testing."""

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict("question -> answer")

    def forward(self, question):
        # In some tests, we check the profile, in others, the prediction.
        if dspy.settings.lm:
            return self.predict(question=question)
        return current_profile()


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
        return dspy.settings.lm

    result_lm = my_function()
    assert isinstance(result_lm, DummyLM)
    # The DummyLM itself doesn't have a readily accessible answer list,
    # but confirming the type proves the correct object was loaded from the profile.
    assert result_lm.model == "dummy"
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


def test_current_profile_utility(profile_manager):
    """Tests the current_profile() introspection utility."""
    # Outside any context, it should be None
    assert current_profile() is None

    with profile("test_profile", config_path=profile_manager.path, lm={"temperature": 0.9}):
        active_profile = current_profile()
        assert active_profile is not None
        assert active_profile.name == "test_profile"
        assert active_profile.config["lm"]["model"] == "test_model_context"
        assert active_profile.config["lm"]["temperature"] == 0.9  # Check override

        # Check that the LM is an instantiated object
        assert isinstance(dspy.settings.lm, dspy.LM)

    # After the context exits, it should be None again
    assert current_profile() is None


def test_lm_shortcut(profile_manager):
    """Tests the lm() shortcut utility."""
    # Clear the cache before the test
    _LM_CACHE.clear()

    # # Get a cached instance
    # lm_instance1 = lm("test_profile", config_path=profile_manager.path)
    # assert isinstance(lm_instance1, dspy.LM)
    # assert lm_instance1.model == "test_model_context"

    # # Get it again, should be the same cached object
    # lm_instance2 = lm("test_profile", config_path=profile_manager.path)
    # assert lm_instance1 is lm_instance2

    # # Force a new instance with cached=False
    # lm_instance3 = lm("test_profile", cached=False, config_path=profile_manager.path)
    # assert lm_instance1 is not lm_instance3

    # Test with overrides, which should create a new, cached instance
    lm_instance4 = lm("test_profile", temperature=0.99, config_path=profile_manager.path)
    assert lm_instance4 is not None
    assert lm_instance4.kwargs["temperature"] == 0.99

    # Getting it again with the same overrides should return the cached instance
    lm_instance5 = lm("test_profile", temperature=0.99, config_path=profile_manager.path)
    assert lm_instance4 is lm_instance5

    # A profile with no LM should return None
    assert lm("no_lm_profile", config_path=profile_manager.path) is None


def test_profile_aware_caching(profile_manager):
    """Tests that the cache_dir is set correctly based on the profile."""
    with profile("test_profile", config_path=profile_manager.path):
        expected_path = os.path.expanduser("~/.dspy/cache/test_profile")
        assert dspy.settings.cache_dir == expected_path

    # A profile with a custom cache_dir should use that value
    profile_manager.load.return_value["custom_cache"] = {
        "settings": {"cache_dir": "/tmp/my_custom_cache"}
    }
    with profile("custom_cache", config_path=profile_manager.path):
        assert dspy.settings.cache_dir == "/tmp/my_custom_cache"


def test_current_profile_with_decorator(profile_manager):
    """Tests that current_profile() works with the @with_profile decorator."""

    @with_profile("decorator_profile", config_path=profile_manager.path)
    def my_function():
        active_profile = current_profile()
        assert active_profile is not None
        assert active_profile.name == "decorator_profile"
        return active_profile

    # Before calling, no profile should be active
    assert current_profile() is None
    my_function()
    # After calling, it should be reset
    assert current_profile() is None


def test_profile_no_profile_found(profile_manager):
    """Tests that nothing happens when no profile is found."""
    with profile(config_path=profile_manager.path):
        assert dspy.settings.lm is None


def test_with_profile_decorator_on_dspy_module_with_dummy_lm(profile_manager):
    """Tests that the @with_profile decorator works on a dspy.Module class."""

    # The "decorator_profile" in the mocked conftest now contains a DummyLM instance.
    @with_profile("decorator_profile", config_path=profile_manager.path)
    class DecoratedModule(MyModule):
        pass

    module = DecoratedModule()
    result = module(question="test")

    # The answer must come from the DummyLM defined in the profile.
    assert result.answer == "dummy profile answer"


def test_current_profile_with_decorator_on_dspy_module(profile_manager):
    """Tests current_profile() with the decorator on a dspy.Module."""

    @with_profile("decorator_profile", config_path=profile_manager.path)
    class DecoratedModule(MyModule):
        def forward(self, question):
            active_profile = current_profile()
            assert active_profile is not None
            assert active_profile.name == "decorator_profile"
            return active_profile

    # Before instantiation/call, no profile should be active
    assert current_profile() is None

    module = DecoratedModule()
    module(question="test")
    # After the call, it should be reset
    assert current_profile() is None


def test_profile_with_no_lm_in_config(profile_manager):
    """Tests that a profile with no LM configured does not break the context manager."""
    with profile("no_lm_profile", config_path=profile_manager.path):
        assert dspy.settings.lm is None
    # This test now checks that calling a module without a profile doesn't crash.
    module = MyModule()
    # The forward method will return the current_profile, which should be None
    assert module(question="test") is None


def test_rm_instantiation_via_class_name(profile_manager, monkeypatch):
    """Tests that RM can be instantiated via rm.class_name."""
    import dspy

    calls = {}

    class DummyRM:
        def __init__(self, **kwargs):
            calls["kwargs"] = kwargs

    # Replace dspy.ColBERTv2 with our dummy to capture instantiation
    monkeypatch.setattr(dspy, "ColBERTv2", DummyRM, raising=True)

    profile_manager.load.return_value["rm_profile"] = {
        "rm": {"class_name": "ColBERTv2", "url": "http://localhost:8893/api/search"}
    }

    with profile("rm_profile", config_path=profile_manager.path):
        # Enter and exit should instantiate the DummyRM
        pass

    assert "kwargs" in calls
    assert calls["kwargs"]["url"].startswith("http")
