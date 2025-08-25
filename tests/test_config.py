from pathlib import Path

from dspy_profiles.config import ProfileManager


def test_profile_manager_crud(tmp_path: Path):
    """Tests the CRUD operations of the ProfileManager."""
    config_path = tmp_path / "profiles.toml"
    manager = ProfileManager(config_path)

    # 1. Load from non-existent file
    assert manager.load() == {}

    # 2. Set a profile
    manager.set("prof1", {"lm": {"model": "model1"}})
    profile = manager.get("prof1")
    assert profile is not None
    assert profile["lm"]["model"] == "model1"

    # 3. Set another profile
    manager.set("prof2", {"lm": {"model": "model2"}})
    assert len(manager.load()) == 2

    # 4. Delete a profile
    assert manager.delete("prof1") is True
    assert manager.get("prof1") is None
    assert len(manager.load()) == 1

    # 5. Delete non-existent profile
    assert manager.delete("nonexistent") is False


def test_load_corrupt_file(tmp_path: Path):
    """Tests that loading a corrupt TOML file returns an empty dict."""
    config_path = tmp_path / "profiles.toml"
    config_path.write_text("this is not valid toml")
    manager = ProfileManager(config_path)
    assert manager.load() == {}


def test_load_invalid_schema(tmp_path: Path):
    """Tests that loading a file with an invalid schema returns an empty dict."""
    config_path = tmp_path / "profiles.toml"
    invalid_profile = """
[default]
  [default.lm]
  model = "gpt-4o-mini"
  temperature = "not-a-float"
"""
    config_path.write_text(invalid_profile)
    manager = ProfileManager(config_path)
    assert manager.load() == {}


def test_get_manager_singleton():
    """Tests that get_manager returns a singleton instance."""
    from dspy_profiles import config

    manager1 = config.get_manager()
    manager2 = config.get_manager()
    assert manager1 is manager2
