import dspy
from dspy.utils.dummies import DummyLM
import pytest

from dspy_profiles.core import profile, with_profile
from dspy_profiles.loader import ProfileLoader


def test_simple_inheritance(profile_manager):
    """Tests that a child profile correctly inherits and overrides from a base profile."""
    loader = ProfileLoader()
    resolved = loader.get_config("child")

    assert resolved.name == "child"
    assert resolved.lm is not None
    assert resolved.rm is not None
    assert resolved.settings is not None
    assert resolved.lm["model"] == "child_model"  # Overridden
    assert resolved.lm["temperature"] == 0.7  # Inherited
    assert resolved.rm["url"] == "http://child_rm_url"  # From child
    assert resolved.settings["retries"] == 2  # Inherited


def test_multi_level_inheritance(profile_manager):
    """Tests that settings are correctly inherited through multiple levels."""
    loader = ProfileLoader()
    resolved = loader.get_config("grandchild")

    assert resolved.name == "grandchild"
    assert resolved.lm is not None
    assert resolved.rm is not None
    assert resolved.settings is not None
    assert resolved.lm["model"] == "child_model"  # Inherited from 'child'
    assert resolved.lm["temperature"] == 0.7  # Inherited from 'base'
    assert resolved.rm["url"] == "http://child_rm_url"  # Inherited from 'child'
    assert resolved.settings["retries"] == 5  # Overridden by 'grandchild'
    assert resolved.settings["timeout"] == 60  # From 'grandchild'


def test_circular_dependency_error(profile_manager):
    """Tests that a circular 'extends' reference raises a ValueError."""
    loader = ProfileLoader()
    with pytest.raises(ValueError, match="cannot extend itself"):
        loader.get_config("circular")


def test_context_manager_with_inline_overrides(profile_manager):
    """Tests that the profile context manager applies inline overrides."""
    # This DummyLM will be overridden by the profile context.
    dspy.settings.configure(lm=DummyLM([{"answer": "Should not be called"}]))

    with profile("child", lm={"temperature": 0.9, "max_tokens": 100}, settings={"retries": 10}):
        # The LM configured inside the context should be a dspy.LM instance
        # Let's inspect it to ensure our settings were applied.
        configured_lm = dspy.settings.lm
        assert isinstance(configured_lm, dspy.LM)
        assert configured_lm.model == "child_model"
        assert configured_lm.kwargs["temperature"] == 0.9
        assert configured_lm.kwargs["max_tokens"] == 100

        # Check dspy.settings
        assert dspy.settings.retries == 10


def test_decorator_with_inline_overrides(profile_manager):
    """Tests that the @with_profile decorator applies inline overrides."""

    @with_profile("base", lm={"model": "decorator_override"})
    def my_function():
        return dspy.settings.lm

    lm_instance = my_function()
    assert isinstance(lm_instance, dspy.LM)
    assert lm_instance.model == "decorator_override"
    assert lm_instance.kwargs["temperature"] == 0.7


def test_decorator_with_function_kwargs_overrides_with_dummy_lm(profile_manager):
    """Tests that kwargs passed to the decorated function take precedence, using DummyLM."""
    # This DummyLM, when passed as a kwarg, should override any profile settings.
    override_lm = DummyLM([{"answer": "override dummy"}])

    @with_profile("base", config_path=profile_manager.path)
    def my_function(question, lm=None):
        # The 'lm' kwarg is handled by the decorator.
        return dspy.Predict("question -> answer")(question=question)

    # Pass the DummyLM instance directly in the function call.
    result = my_function(question="test", lm=override_lm)

    # The result's answer must come from our override_lm, proving it was used.
    assert result.answer == "override dummy"
