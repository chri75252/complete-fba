"""
Scoring Tools for FBA Agent.

Implements deterministic confidence scoring based on the PRD scoring rubric.
Scores are computed by code, not LLM estimation.
"""

from ..models.schemas import RowDecisionRecord, MatchChecks, TrapDetection
from typing import List


def compute_confidence(record: RowDecisionRecord) -> int:
    """
    Compute deterministic confidence score for a row decision.
    
    Based on PRD Section 5 scoring rubric:
    - VERIFIED base: 95, range 85-95
    - HIGHLY_LIKELY base: 80, range 70-90
    - NEEDS_VERIFICATION base: 60, range 40-79
    - FILTERED_OUT: returns what score would have been
    
    Args:
        record: Row decision record with match checks
        
    Returns:
        Confidence score 0-100
    """
    bucket = record.bucket
    checks = record.match_checks
    
    if bucket == "VERIFIED":
        return _score_verified(record)
    elif bucket == "HIGHLY_LIKELY":
        return _score_highly_likely(record)
    elif bucket == "NEEDS_VERIFICATION":
        return _score_needs_verification(record)
    else:  # FILTERED_OUT
        # Return score it would have had if not filtered
        base = 80 if checks.is_exact_ean_strict else 70
        return base


def _score_verified(record: RowDecisionRecord) -> int:
    """Score for VERIFIED bucket (exact EAN match)."""
    score = 95  # Base score
    checks = record.match_checks
    
    # Deductions
    if checks.capacity_delta_percent and checks.capacity_delta_percent > 5:
        score -= 2  # Minor capacity variance
    
    if len(record.trap_detections) > 0:
        score -= 1  # Had to apply trap logic
    
    if record.rsu > 1 and record.adjusted_profit < 5:
        score -= 2  # Marginal profit after adjustment
    
    if record.rsu > 1:
        score -= 1  # Pack adjustment required
    
    # Clamp to range
    return max(85, min(95, score))


def _score_highly_likely(record: RowDecisionRecord) -> int:
    """Score for HIGHLY_LIKELY bucket."""
    score = 80  # Base score
    checks = record.match_checks
    
    # Additions
    if checks.brand_match and checks.product_type_match:
        score += 5  # Strong evidence
    
    if not checks.ean_strict_valid_amazon:
        # Missing Amazon EAN is more forgiving than different EAN
        score += 2
    
    if checks.variant_match == "true":
        score += 2  # Variant confirmed
    
    if checks.pack_match:
        score += 1  # Pack sizes align
    
    # Deductions
    if checks.ean_strict_valid_amazon and not checks.is_exact_ean_strict:
        # Different EAN (not missing) requires stronger evidence
        score -= 5
    
    if checks.variant_match == "ambiguous":
        score -= 3  # Uncertain variant
    
    if record.rsu > 1:
        score -= 2  # Pack adjustment needed
    
    if checks.capacity_delta_percent and checks.capacity_delta_percent > 10:
        score -= 2  # Notable capacity difference
    
    # Clamp to range
    return max(70, min(90, score))


def _score_needs_verification(record: RowDecisionRecord) -> int:
    """Score for NEEDS_VERIFICATION bucket."""
    score = 60  # Base score
    checks = record.match_checks
    
    # Additions for stronger evidence
    if checks.brand_match:
        score += 10  # Brand gives confidence
    
    if checks.product_type_match:
        score += 5  # Product type matches
    
    if checks.ean_strict_valid_supplier:
        score += 2  # At least supplier EAN is valid
    
    # Deductions
    if not checks.brand_match and not checks.product_type_match:
        score -= 10  # Very weak evidence
    
    if checks.variant_match == "false":
        score -= 5  # Possible variant mismatch
    
    # Clamp to range
    return max(40, min(79, score))


def compute_pack_verdict(
    supplier_pack: int, 
    amazon_total: int, 
    rsu: float, 
    adjusted_profit: float,
    trap_notes: List[str] = None
) -> str:
    """
    Compute pack verdict string for display.
    
    Args:
        supplier_pack: Pack count from supplier
        amazon_total: Total items in Amazon listing
        rsu: Required Supplier Units
        adjusted_profit: Profit after adjustment
        trap_notes: Optional notes about trap detections
        
    Returns:
        Pack verdict string for table display
    """
    trap_notes = trap_notes or []
    
    if rsu == 1.0 or (supplier_pack == amazon_total):
        if trap_notes:
            note = trap_notes[0] if len(trap_notes[0]) < 30 else trap_notes[0][:27] + "..."
            return f"1:1 ({note})"
        return "1:1 Match"
    
    if rsu > 1.0:
        if adjusted_profit > 0:
            return f"BUNDLE ({int(rsu)}x) - OK"
        else:
            return f"BUNDLE ({int(rsu)}x) - LOSS"
    
    if rsu < 1.0:
        ratio = int(1 / rsu)
        if adjusted_profit > 0:
            return f"SPLIT (1/{ratio}) - OK"
        else:
            return f"SPLIT (1/{ratio}) - LOSS"
    
    return "1:1 Match"


def compute_evidence_string(record: RowDecisionRecord) -> str:
    """
    Compute key match evidence string for table display.
    
    Args:
        record: Row decision record
        
    Returns:
        Concise evidence string
    """
    evidence_parts = []
    checks = record.match_checks
    
    # EAN evidence
    if checks.is_exact_ean_strict:
        evidence_parts.append("Exact EAN match")
    elif checks.ean_strict_valid_supplier and not checks.ean_strict_valid_amazon:
        evidence_parts.append("Amazon EAN missing")
    elif checks.ean_strict_valid_supplier and checks.ean_strict_valid_amazon:
        evidence_parts.append("Different EANs")
    
    # Brand evidence
    if checks.brand_match:
        if record.supplier_attributes.brand:
            evidence_parts.append(f"Brand: {record.supplier_attributes.brand}")
        else:
            evidence_parts.append("Brand match")
    
    # Product evidence
    if checks.product_type_match:
        if record.supplier_attributes.product_type:
            evidence_parts.append(f"Type: {record.supplier_attributes.product_type}")
    
    # Pack evidence
    if checks.pack_match:
        evidence_parts.append("Pack aligned")
    
    return "; ".join(evidence_parts) if evidence_parts else "-"
