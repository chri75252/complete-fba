from __future__ import annotations

from copy import deepcopy
from typing import Any


def deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = deepcopy(base)

    for key, override_value in overrides.items():
        if key not in merged:
            merged[key] = deepcopy(override_value)
            continue

        base_value = merged[key]

        if isinstance(base_value, dict) and isinstance(override_value, dict):
            merged[key] = deep_merge(base_value, override_value)
            continue

        merged[key] = deepcopy(override_value)

    return merged
