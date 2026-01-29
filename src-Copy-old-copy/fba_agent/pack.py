from __future__ import annotations

import re

from fba_agent.types import PackParseResult, SupplierNamingConvention


_DIMENSION_X_RE = re.compile(
    r"(?P<a>\d+(?:\.\d+)?)\s*[x×]\s*(?P<b>\d+(?:\.\d+)?)(?:\s*[x×]\s*\d+(?:\.\d+)?)?\s*(?P<unit>CM|MM|INCH|IN|M)\b",
    re.IGNORECASE,
)
_DIMENSION_COMPACT_RE = re.compile(r"\b\d{2,4}\s*[x×]\s*\d{2,4}\s*(CM|MM)\b", re.IGNORECASE)
_CAPACITY_MULTIPACK_RE = re.compile(
    r"\b(?P<n>\d+)\s*[x×]\s*(?P<cap>\d+(?:\.\d+)?)\s*(?P<unit>ML|L|LTR|G|KG|OZ)\b",
    re.IGNORECASE,
)
_SPEC_X_RE = re.compile(r"\b(?P<n>\d+)\s*[x×]\s*(?P<kw>MAGNIFICATION|ZOOM|TIMES)\b", re.IGNORECASE)
_LED_RE = re.compile(r"\b(?P<n>\d+)\s*LED\b", re.IGNORECASE)
_PACK_OF_RE = re.compile(r"\bPACK\s+OF\s+(?P<n>\d+)\b", re.IGNORECASE)
_N_PACK_RE = re.compile(r"\b(?P<n>\d+)\s*(PACK|PCS|PCE|UNITS?)\b", re.IGNORECASE)
_PKN_RE = re.compile(r"\bPK\s*(?P<n>\d+)\b", re.IGNORECASE)
_PAREN_NX_M_RE = re.compile(r"\((?P<a>\d+)\s*[x×]\s*(?P<b>\d+)\)", re.IGNORECASE)
_TRAILING_NUMBER_RE = re.compile(r"\b(?P<n>\d{2,4})\b\s*$")


def parse_pack_quantity(title: str, naming: SupplierNamingConvention) -> PackParseResult:
    up = title.upper()
    traps: list[str] = []

    if _DIMENSION_X_RE.search(up) or _DIMENSION_COMPACT_RE.search(up):
        traps.append("dimension_trap")
        return PackParseResult(quantity=None, evidence="dimension shield", traps=traps, ambiguous=True)

    if _SPEC_X_RE.search(up) or any(kw.upper() in up for kw in naming.spec_x_shield_keywords):
        if _SPEC_X_RE.search(up):
            traps.append("spec_x_trap")
        return PackParseResult(quantity=None, evidence="spec-x shield", traps=traps, ambiguous=True)

    if _LED_RE.search(up):
        traps.append("led_spec_trap")

    cap = _CAPACITY_MULTIPACK_RE.search(up)
    if cap and naming.capacity_pattern_as_rsu:
        n = int(cap.group("n"))
        return PackParseResult(quantity=n, evidence=f"{n}x capacity multipack", traps=traps)

    paren = _PAREN_NX_M_RE.search(up)
    if paren:
        a = int(paren.group("a"))
        b = int(paren.group("b"))
        total = a * b
        return PackParseResult(quantity=total, evidence=f"({a}x{b}) quantity-inside", traps=traps)

    m = _PACK_OF_RE.search(up)
    if m:
        n = int(m.group("n"))
        return PackParseResult(quantity=n, evidence=f"pack of {n}", traps=traps)

    m = _PKN_RE.search(up)
    if m:
        n = int(m.group("n"))
        return PackParseResult(quantity=n, evidence=f"PK{n}", traps=traps)

    m = _N_PACK_RE.search(up)
    if m:
        n = int(m.group("n"))
        return PackParseResult(quantity=n, evidence=f"{n} units", traps=traps)

    if naming.allow_trailing_number_as_qty:
        m = _TRAILING_NUMBER_RE.search(up)
        if m:
            n = int(m.group("n"))
            if 2 <= n <= 5000:
                return PackParseResult(quantity=n, evidence=f"trailing qty {n}", traps=traps)

    # Default to a single unit when no explicit pack signal exists.
    return PackParseResult(quantity=1, evidence="assume 1 (no explicit pack signal)", traps=traps, ambiguous=True)


def pack_ratio(amazon_qty: int | None, supplier_qty: int | None) -> float | None:
    if amazon_qty is None or supplier_qty is None:
        return None
    if supplier_qty <= 0:
        return None
    return amazon_qty / supplier_qty
