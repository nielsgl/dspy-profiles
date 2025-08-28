from pathlib import Path

from dspy_profiles.config import PROFILES_PATH, ProfileManager, find_profiles_path


def test_find_profiles_path_hierarchy(tmp_path: Path, monkeypatch):
    """Tests the hierarchical search logic of find_profiles_path."""
    # 1. Test fallback to global default
    assert find_profiles_path() == PROFILES_PATH

    # 2. Test finding local `profiles.toml`
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    local_config = project_dir / "profiles.toml"
    local_config.touch()
    monkeypatch.chdir(project_dir)
    assert find_profiles_path() == local_config

    # 3. Test environment variable override
    env_config_path = tmp_path / "env_profiles.toml"
    monkeypatch.setenv("DSPY_PROFILES_PATH", str(env_config_path))
    assert find_profiles_path() == env_config_path


def test_profile_manager_crud(tmp_path: Path, monkeypatch):
    """Tests the CRUD operations of the ProfileManager."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.config.find_profiles_path", lambda: config_path)
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


def test_profile_manager_isolated_ops(tmp_path: Path, monkeypatch):
    """Tests the ProfileManager's methods in isolation."""
    config_path = tmp_path / "profiles.toml"
    monkeypatch.setattr("dspy_profiles.config.find_profiles_path", lambda: config_path)

    # Test set
    manager1 = ProfileManager(config_path)
    manager1.set("prof1", {"lm": {"model": "model1"}})

    # Test get
    manager2 = ProfileManager(config_path)
    profile = manager2.get("prof1")
    assert profile is not None
    assert profile["lm"]["model"] == "model1"

    # Test delete
    manager3 = ProfileManager(config_path)
    assert manager3.delete("prof1") is True

    # Test get after delete
    manager4 = ProfileManager(config_path)
    assert manager4.get("prof1") is None


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
lm = { model = "gpt-4o-mini", temperature = "not-a-float" }
"""
    config_path.write_text(invalid_profile)
    manager = ProfileManager(config_path)
    assert manager.load() != {}


def test_load_dotted_keys(tmp_path: Path):
    """Tests that profiles with dotted keys are correctly parsed."""
    config_path = tmp_path / "profiles.toml"
    dotted_key_profile = """
[prof1]
lm.model = "model1"
lm.temperature = 0.7

[prof2.lm]
model = "model2"
temperature = 0.8
"""
    config_path.write_text(dotted_key_profile)
    manager = ProfileManager(config_path)
    profiles = manager.load()

    assert "prof1" in profiles
    assert "prof2" in profiles
    assert profiles["prof1"]["lm"]["model"] == "model1"
    assert profiles["prof1"]["lm"]["temperature"] == 0.7
    assert profiles["prof2"]["lm"]["model"] == "model2"
    assert profiles["prof2"]["lm"]["temperature"] == 0.8
