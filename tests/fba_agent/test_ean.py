from __future__ import annotations

from fba_agent.ean import normalize_and_validate, validate_gtin


def test_validate_gtin_known_valid() -> None:
    assert validate_gtin("5032759031078") is True


def test_normalize_excel_float_suffix() -> None:
    info = normalize_and_validate("5032759031078.0")
    assert info.is_valid is True
    assert info.normalized == "5032759031078"


def test_invalid_gtin_rejected() -> None:
    info = normalize_and_validate("0000000000000")
    assert info.is_valid is False
    assert info.normalized is None

