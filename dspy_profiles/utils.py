from collections import defaultdict
from typing import Any


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a dictionary to expand dotted keys into nested dictionaries.

    This function is designed to handle TOML configurations where nested
    structures might be represented with dotted keys. For example, a key
    'lm.model' would be transformed into a nested dictionary
    {'lm': {'model': ...}}.

    Args:
        config: The dictionary to normalize.

    Returns:
        A new dictionary with dotted keys expanded into nested structures.
    """
    normalized = defaultdict(dict)
    for key, value in config.items():
        if "." in key:
            parts = key.split(".", 1)
            # This is a simplified implementation that assumes one level of nesting
            # which is sufficient for the current use case (e.g., 'lm.model').
            # A more complex recursive solution would be needed for deeper nesting.
            parent_key, child_key = parts
            if parent_key not in normalized:
                normalized[parent_key] = {}
            normalized[parent_key][child_key] = value
        else:
            # If the value is a dictionary, it could be a sub-profile that also needs normalization
            if isinstance(value, dict):
                normalized[key] = normalize_config(value)
            else:
                normalized[key] = value
    return dict(normalized)
