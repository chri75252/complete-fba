from __future__ import annotations

from fba_agent.pack import parse_pack_quantity
from fba_agent.types import SupplierNamingConvention


def test_dimension_not_treated_as_pack() -> None:
    naming = SupplierNamingConvention()
    res = parse_pack_quantity("TRAY 9 x 9 inch", naming)
    assert res.quantity is None
    assert "dimension" in res.evidence


def test_capacity_multipack_rsu() -> None:
    naming = SupplierNamingConvention()
    res = parse_pack_quantity("3 x 400ml Spray Paint", naming)
    assert res.quantity == 3


def test_quantity_inside_parentheses() -> None:
    naming = SupplierNamingConvention()
    res = parse_pack_quantity("200 bags (4 x 50)", naming)
    assert res.quantity == 200

