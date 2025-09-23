from __future__ import annotations

from typing import Any


def _deep_merge_dicts(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge two dictionaries without mutating either input."""
    merged: dict[str, Any] = existing.copy()
    for key, value in incoming.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def _assign_path(target: dict[str, Any], parts: list[str], value: Any) -> None:
    """Assign a value into a nested dictionary using a list of keys."""
    head, *tail = parts

    if tail:
        next_container = target.get(head)
        if not isinstance(next_container, dict):
            next_container = {}
        target[head] = next_container
        if isinstance(value, dict):
            value = normalize_config(value)
        _assign_path(next_container, tail, value)
        return

    normalized_value = normalize_config(value) if isinstance(value, dict) else value
    existing_value = target.get(head)
    if isinstance(existing_value, dict) and isinstance(normalized_value, dict):
        target[head] = _deep_merge_dicts(existing_value, normalized_value)
    else:
        target[head] = normalized_value


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    """Expand dotted TOML keys into nested dictionaries (recursively)."""
    normalized: dict[str, Any] = {}

    for key, value in config.items():
        if "." in key:
            _assign_path(normalized, key.split("."), value)
            continue

        normalized_value = normalize_config(value) if isinstance(value, dict) else value
        existing_value = normalized.get(key)
        if isinstance(existing_value, dict) and isinstance(normalized_value, dict):
            normalized[key] = _deep_merge_dicts(existing_value, normalized_value)
        else:
            normalized[key] = normalized_value

    return normalized
