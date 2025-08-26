import pytest

# Mark all tests in this file as IPython tests
pytestmark = pytest.mark.ipython


@pytest.fixture
def ipython_shell(profile_manager):
    """Fixture to get a clean IPython shell instance with our extension loaded."""
    from IPython.terminal.interactiveshell import TerminalInteractiveShell

    from dspy_profiles.ipython import ProfileMagics

    shell = TerminalInteractiveShell.instance()
    # This is the key: instantiate the magics with our mock loader,
    # and register that specific instance.
    magics = ProfileMagics(shell, loader=profile_manager)
    shell.register_magics(magics)
    return shell


def test_profile_magic_loads(ipython_shell):
    """Test that the %profile magic command is loaded."""
    assert "profile" in ipython_shell.magics_manager.magics["line"]


def test_profile_magic_activates_profile(ipython_shell, profile_manager, monkeypatch):
    """Test that %profile magic activates a profile and configures dspy."""
    profile_manager.create("test_magic", {"model": "test_model", "api_key": "test_magic_key"})

    from unittest.mock import MagicMock

    configure_mock = MagicMock()
    # We need to patch configure where it's used, inside the core module.
    monkeypatch.setattr("dspy_profiles.core.dspy.configure", configure_mock)

    ipython_shell.run_line_magic("profile", "test_magic")

    configure_mock.assert_called_once()
    call_args, call_kwargs = configure_mock.call_args
    assert call_kwargs["lm"].kwargs["api_key"] == "test_magic_key"


def test_profile_magic_with_overrides(ipython_shell, profile_manager, monkeypatch):
    """Test that %profile magic works with inline overrides."""
    profile_manager.create(
        "test_magic_override", {"model": "override_model", "api_key": "override_key"}
    )

    from unittest.mock import MagicMock

    configure_mock = MagicMock()
    monkeypatch.setattr("dspy_profiles.core.dspy.configure", configure_mock)

    ipython_shell.run_line_magic("profile", "test_magic_override model=gpt-4")

    configure_mock.assert_called_once()
    call_args, call_kwargs = configure_mock.call_args
    assert call_kwargs["lm"].kwargs["api_key"] == "override_key"
    assert call_kwargs["lm"].kwargs["model"] == "gpt-4"


def test_profile_magic_not_found(ipython_shell, capsys):
    """Test that %profile magic handles a non-existent profile."""
    ipython_shell.run_line_magic("profile", "non_existent_profile")
    captured = capsys.readouterr()
    assert "Profile 'non_existent_profile' not found." in captured.out
