from dspy_profiles.utils import normalize_config


def test_normalize_config_empty():
    """Test that an empty config remains empty."""
    assert normalize_config({}) == {}


def test_normalize_config_no_dots():
    """Test that a config with no dotted keys remains unchanged."""
    config = {"key1": "value1", "key2": 42}
    assert normalize_config(config) == config


def test_normalize_config_simple_dotted_key():
    """Test expansion of a single dotted key."""
    config = {"lm.model": "gpt-4"}
    expected = {"lm": {"model": "gpt-4"}}
    assert normalize_config(config) == expected


def test_normalize_config_multiple_dotted_keys_same_parent():
    """Test expansion of multiple dotted keys under the same parent."""
    config = {"lm.model": "gpt-4", "lm.temperature": 0.7}
    expected = {"lm": {"model": "gpt-4", "temperature": 0.7}}
    assert normalize_config(config) == expected


def test_normalize_config_mixed_keys():
    """Test a mix of dotted and non-dotted keys."""
    config = {
        "lm.model": "gpt-4",
        "rm.url": "http://localhost:8000",
        "max_tokens": 100,
    }
    expected = {
        "lm": {"model": "gpt-4"},
        "rm": {"url": "http://localhost:8000"},
        "max_tokens": 100,
    }
    assert normalize_config(config) == expected


def test_normalize_config_with_nested_dict():
    """Test that existing nested dictionaries are handled correctly."""
    config = {
        "lm": {"model": "gpt-3.5-turbo"},
        "lm.temperature": 0.9,
    }
    # The implementation merges the dotted key into the existing dictionary.
    expected = {"lm": {"model": "gpt-3.5-turbo", "temperature": 0.9}}
    assert normalize_config(config) == expected


def test_normalize_config_deeper_nesting_in_value():
    """Test that nested dictionaries in values are recursively normalized."""
    config = {"profile1": {"lm.model": "gpt-4", "temperature": 0.5}}
    expected = {"profile1": {"lm": {"model": "gpt-4"}, "temperature": 0.5}}
    assert normalize_config(config) == expected
