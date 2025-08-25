import pytest

from dspy_profiles.config import ProfileManager


@pytest.fixture
def profile_manager(tmp_path):
    """Fixture to create a temporary profiles.toml file and a ProfileManager."""
    profiles_file = tmp_path / "profiles.toml"
    manager = ProfileManager(profiles_file)

    # Ensure the file exists for the manager to read/write
    profiles_file.touch()

    return manager
