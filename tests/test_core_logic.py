from dspy_profiles.core import _deep_merge


def test_deep_merge_simple():
    """Test merging non-overlapping dictionaries."""
    parent = {"a": 1}
    child = {"b": 2}
    expected = {"a": 1, "b": 2}
    assert _deep_merge(parent, child) == expected


def test_deep_merge_override():
    """Test that child values override parent values."""
    parent = {"a": 1, "b": 2}
    child = {"b": 3, "c": 4}
    expected = {"a": 1, "b": 3, "c": 4}
    assert _deep_merge(parent, child) == expected


def test_deep_merge_nested():
    """Test recursive merging of nested dictionaries."""
    parent = {"a": {"x": 1, "y": 2}, "b": 10}
    child = {"a": {"y": 3, "z": 4}, "c": 20}
    expected = {"a": {"x": 1, "y": 3, "z": 4}, "b": 10, "c": 20}
    assert _deep_merge(parent, child) == expected


def test_deep_merge_child_creates_dict():
    """Test when a child value is a dict and the parent's is not."""
    parent = {"a": 1}
    child = {"a": {"x": 2}}
    expected = {"a": {"x": 2}}
    assert _deep_merge(parent, child) == expected


def test_deep_merge_parent_creates_dict():
    """Test when a parent value is a dict and the child's is not."""
    parent = {"a": {"x": 1}}
    child = {"a": 2}
    expected = {"a": 2}
    assert _deep_merge(parent, child) == expected


def test_deep_merge_empty_child():
    """Test merging with an empty child dictionary."""
    parent = {"a": 1, "b": {"x": 2}}
    child = {}
    assert _deep_merge(parent, child) == parent


def test_deep_merge_empty_parent():
    """Test merging with an empty parent dictionary."""
    parent = {}
    child = {"a": 1, "b": {"x": 2}}
    assert _deep_merge(parent, child) == child


def test_deep_merge_does_not_modify_originals():
    """Test that the original dictionaries are not modified."""
    parent = {"a": {"x": 1}}
    child = {"a": {"y": 2}}
    parent_original = parent.copy()
    child_original = child.copy()
    _deep_merge(parent, child)
    assert parent == parent_original
    assert child == child_original
