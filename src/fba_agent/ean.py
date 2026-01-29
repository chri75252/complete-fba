from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class EanInfo:
    raw: str
    digits: str
    is_valid: bool
    normalized: str | None


def _digits_only(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def normalize_ean(raw: object) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if s in {"", "nan", "NaN", "None"}:
        return None

    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]

    if "e" in s.lower():
        try:
            d = Decimal(s)
            if d.is_finite():
                s = format(int(d), "d")
        except (InvalidOperation, ValueError, OverflowError):
            pass

    digits = _digits_only(s)
    return digits or None


def compute_check_digit(number_without_check: str) -> int:
    total = 0
    reverse = list(reversed(number_without_check))
    for i, ch in enumerate(reverse, start=1):
        n = int(ch)
        weight = 3 if i % 2 == 1 else 1
        total += n * weight
    return (10 - (total % 10)) % 10


def validate_gtin(digits: str) -> bool:
    if not digits.isdigit():
        return False
    if set(digits) == {"0"}:
        return False
    if len(digits) not in {8, 12, 13, 14}:
        return False
    expected = compute_check_digit(digits[:-1])
    return expected == int(digits[-1])


def normalize_and_validate(raw: object) -> EanInfo:
    digits = normalize_ean(raw) or ""
    if not digits:
        return EanInfo(raw=str(raw), digits="", is_valid=False, normalized=None)

    if validate_gtin(digits):
        return EanInfo(raw=str(raw), digits=digits, is_valid=True, normalized=digits)

    for target_len in (12, 13, 14):
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if validate_gtin(padded):
                return EanInfo(raw=str(raw), digits=digits, is_valid=True, normalized=padded)

    return EanInfo(raw=str(raw), digits=digits, is_valid=False, normalized=None)
