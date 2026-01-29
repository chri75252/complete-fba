from __future__ import annotations

import re

from fba_agent.constants import COLORS, SCENTS
from fba_agent.types import VariantParseResult


_CAPACITY_RE = re.compile(r"(?P<value>\\d+(?:\\.\\d+)?)\\s*(?P<unit>ML|L|LTR|G|KG|OZ)\\b")


def _to_base(value: float, unit: str) -> float:
    unit = unit.upper()
    if unit in {"ML"}:
        return value
    if unit in {"L", "LTR"}:
        return value * 1000.0
    if unit in {"G"}:
        return value
    if unit in {"KG"}:
        return value * 1000.0
    if unit in {"OZ"}:
        return value * 28.3495
    return value


def parse_variant(title: str) -> VariantParseResult:
    up = title.upper()
    match = _CAPACITY_RE.search(up)
    if match:
        value = float(match.group("value"))
        unit = match.group("unit").upper()
        base = _to_base(value, unit)
    else:
        value = None
        unit = None
        base = None

    color = next((c for c in COLORS if f" {c} " in f" {up} "), None)
    scent = next((s for s in SCENTS if f" {s} " in f" {up} "), None)

    return VariantParseResult(capacity_value=value, capacity_unit=unit, capacity_base=base, color=color, scent=scent)


def capacity_delta_pct(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    if a <= 0 or b <= 0:
        return None
    return abs(a - b) / max(a, b) * 100.0


def capacity_gate(delta_pct: float | None) -> str:
    if delta_pct is None:
        return "unknown"
    if delta_pct <= 10.0:
        return "ok_0_10"
    if delta_pct <= 25.0:
        return "nv_10_25"
    if delta_pct <= 50.0:
        return "fo_25_50"
    return "fo_gt_50"

