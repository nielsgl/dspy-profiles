from unittest.mock import patch

import dspy
import pytest

from dspy_profiles.core import profile, with_profile
from dspy_profiles.loader import ResolvedProfile


@pytest.fixture
def mock_profile():
    """Returns a mock ResolvedProfile for testing."""
    return ResolvedProfile(
        name="test_profile",
        config={"lm": {"model": "gpt-4o-mini"}, "settings": {"temperature": 0.7}},
        lm={"model": "gpt-4o-mini"},
        settings={"temperature": 0.7},
        rm={"url": "http://localhost:8893/api/search"},
    )


def test_profile_context_manager(mock_profile):
    """Tests that the profile context manager correctly applies settings."""
    with patch(
        "dspy_profiles.core.ProfileLoader.get_config", return_value=mock_profile
    ) as mock_get_config:
        assert dspy.settings.lm is None

        with profile("test_profile"):
            assert dspy.settings.lm is not None
            assert dspy.settings.lm.model == "gpt-4o-mini"
            assert dspy.settings.temperature == 0.7
            assert dspy.settings.rm is not None
            assert dspy.settings.rm.url == "http://localhost:8893/api/search"
            mock_get_config.assert_called_once_with("test_profile")

        assert dspy.settings.lm is None
        with pytest.raises(AttributeError):
            _ = dspy.settings.temperature


def test_with_profile_decorator(mock_profile):
    """Tests that the @with_profile decorator correctly applies settings."""

    @with_profile("test_profile")
    def my_dspy_program():
        assert dspy.settings.lm is not None
        assert dspy.settings.lm.model == "gpt-4o-mini"

    with patch(
        "dspy_profiles.core.ProfileLoader.get_config", return_value=mock_profile
    ) as mock_get_config:
        assert dspy.settings.lm is None
        my_dspy_program()
        mock_get_config.assert_called_once_with("test_profile")
        assert dspy.settings.lm is None


def test_profile_not_found():
    """Tests that a ValueError is raised for a non-existent profile."""
    with patch("dspy_profiles.loader.ProfileManager.load", return_value={}):
        with pytest.raises(ValueError, match="Profile 'non_existent_profile' not found."):
            with profile("non_existent_profile"):
                pass


def test_profile_with_no_lm_or_rm():
    """Tests that the context manager handles profiles with no lm or rm."""
    mock_profile = ResolvedProfile(name="test_profile", config={}, settings={})
    with patch("dspy_profiles.core.ProfileLoader.get_config", return_value=mock_profile):
        with profile("test_profile"):
            assert dspy.settings.lm is None
            assert dspy.settings.rm is None
