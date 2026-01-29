from __future__ import annotations

from fba_agent.text import clamp
from fba_agent.types import MatchChecks, RowDecisionRecord


def compute_confidence(record: RowDecisionRecord) -> int:
    checks: MatchChecks = record.checks

    if checks.strict_exact_ean:
        score = 95
        if record.traps:
            score -= 1
        if checks.capacity_delta_pct is not None and checks.capacity_delta_pct > 5:
            score -= 2
        if record.pack_ratio is not None and record.pack_ratio > 1 and (record.adjusted_profit or 0) < 5:
            score -= 2
        return clamp(score, 85, 95)

    score = 0
    
    # Brand evidence (updated with partial brand support)
    if checks.brand_match:
        score += 40  # Both brands detected + equal (strong signal)
    else:
        # Check for partial brand (brand in one title only)
        # We can infer this from supplier_ean_valid and amazon_ean_missing
        # Partial brand gets moderate boost
        # Note: This is a simplification; ideally we'd pass partial_brand_match from analysis.py
        # For now, use a proxy: if strong product match but no brand match
        if checks.product_type_match and not checks.brand_match:
            score += 15  # Moderate boost for potential partial brand scenario
    
    score += 25 if checks.product_type_match else 0
    score += 15 if checks.variant_within_tolerance else 0
    score += 10 if record.pack_ratio == 1 else 0
    score += 5 if (record.sales or 0) > 0 else 0
    
    # EAN evidence quality (NEW)
    supplier_has_ean = checks.supplier_ean_valid
    amazon_has_ean = checks.amazon_ean_valid
    
    if supplier_has_ean and checks.amazon_ean_missing:
        # 1 EAN (Amazon missing) - GOOD signal (missing ≠ different)
        score += 5
    elif supplier_has_ean and amazon_has_ean and not checks.strict_exact_ean:
        # 2 Different EANs - BAD signal (conflicting evidence)
        score -= 10

    if record.pack_ratio is None:
        score -= 20

    if checks.capacity_gate == "nv_10_25":
        score -= 30
    if checks.capacity_gate in {"fo_25_50", "fo_gt_50"}:
        score -= 60

    return clamp(score, 0, 100)
