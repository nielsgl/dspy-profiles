import logging

from dspy_profiles.logging_utils import compute_level, setup_logging


def test_compute_level_precedence():
    # Explicit log-level overrides flags
    assert compute_level(verbose=2, quiet=1, log_level="error") == logging.ERROR
    # Verbose beats default
    assert compute_level(verbose=1, quiet=0, log_level=None) == logging.INFO
    # Double verbose -> DEBUG
    assert compute_level(verbose=2, quiet=0, log_level=None) == logging.DEBUG
    # Quiet -> ERROR
    assert compute_level(verbose=0, quiet=1, log_level=None) == logging.ERROR


def test_setup_logging_idempotent(monkeypatch):
    # Ensure setup_logging can be safely called multiple times
    setup_logging(logging.DEBUG)
    root = logging.getLogger()
    handler_count = len(root.handlers)
    setup_logging(logging.INFO)
    # No extra handlers added
    assert len(root.handlers) == handler_count
