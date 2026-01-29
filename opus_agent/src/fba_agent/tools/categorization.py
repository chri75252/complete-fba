"""
Categorization Tools for FBA Agent.

Core logic for categorizing products into VERIFIED, HIGHLY_LIKELY, 
NEEDS_VERIFICATION, or FILTERED_OUT buckets.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from ..models.schemas import (
    RowDecisionRecord, 
    ParsedAttributes, 
    TrapDetection, 
    MatchChecks,
    Bucket
)
from .ean_validation import check_ean_match, format_ean_for_display
from .pack_detection import (
    extract_pack_count, 
    extract_multipack_total, 
    calculate_rsu,
    detect_dimension_trap,
    detect_quantity_inside_trap
)
from .title_parsing import (
    parse_title_attributes, 
    check_brand_match, 
    check_product_type_match,
    calculate_title_similarity
)
from .profit_calculation import calculate_adjusted_profit, extract_row_financials
from .scoring import compute_confidence, compute_pack_verdict, compute_evidence_string


def analyze_row(row: Dict[str, Any], config: Optional[Dict] = None) -> RowDecisionRecord:
    """
    Analyze a single row and produce a decision record.
    
    This is the core deterministic analysis function that:
    1. Validates EANs
    2. Parses titles for attributes
    3. Detects pack sizes with trap shields
    4. Calculates RSU and adjusted profit
    5. Assigns bucket based on rules from Main.txt
    6. Computes deterministic confidence score
    
    Args:
        row: Row dictionary from DataFrame
        config: Optional calibration config
        
    Returns:
        Complete RowDecisionRecord
    """
    config = config or {}
    
    # Extract basic info
    row_id = int(row.get('RowID', 0))
    
    # Get EAN values
    supplier_ean = str(row.get('EAN_clean', row.get('EAN', '')))
    amazon_ean = str(row.get('EAN_OnPage_clean', row.get('EAN_OnPage', '')))
    
    # Validate EANs
    sup_valid, amz_valid, is_exact_ean, amz_present = check_ean_match(supplier_ean, amazon_ean)
    
    # Parse titles
    supplier_title = str(row.get('SupplierTitle', ''))
    amazon_title = str(row.get('AmazonTitle', ''))
    
    supplier_attrs = parse_title_attributes(supplier_title)
    amazon_attrs = parse_title_attributes(amazon_title)
    
    # Check brand and product type matches
    brand_match = check_brand_match(supplier_attrs.brand, amazon_attrs.brand)
    product_match = check_product_type_match(supplier_attrs.product_type, amazon_attrs.product_type)
    
    # Extract pack counts with trap detection
    trap_detections: List[TrapDetection] = []
    
    sup_pack, sup_traps = extract_pack_count(supplier_title)
    trap_detections.extend(sup_traps)
    
    amz_outer, amz_inner, amz_total, amz_traps = extract_multipack_total(amazon_title)
    trap_detections.extend(amz_traps)
    
    # Check for quantity-inside traps
    qty_trap = detect_quantity_inside_trap(supplier_title)
    if qty_trap:
        trap_detections.append(qty_trap)
    
    # Update attributes with detected pack counts
    supplier_attrs.pack_count = sup_pack
    amazon_attrs.pack_count = amz_total
    
    # Calculate RSU
    rsu = calculate_rsu(sup_pack, amz_total)
    
    # Extract financials and calculate adjusted profit
    supplier_price, selling_price, net_profit, roi = extract_row_financials(row)
    adjusted_profit = calculate_adjusted_profit(net_profit, supplier_price, rsu)
    
    # Determine pack match
    pack_match = (rsu == 1.0) or (sup_pack == amz_total)
    
    # Check variant match
    variant_match = _check_variant_match(supplier_attrs, amazon_attrs)
    
    # Build match checks
    match_checks = MatchChecks(
        ean_strict_valid_supplier=sup_valid,
        ean_strict_valid_amazon=amz_valid,
        is_exact_ean_strict=is_exact_ean,
        brand_match=brand_match,
        product_type_match=product_match,
        variant_match=variant_match,
        pack_match=pack_match,
        capacity_delta_percent=_calculate_capacity_delta(supplier_attrs, amazon_attrs)
    )
    
    # Categorize the row
    bucket, filter_reason = categorize_row(
        match_checks=match_checks,
        adjusted_profit=adjusted_profit,
        rsu=rsu,
        trap_detections=trap_detections
    )
    
    # Build pack verdict with trap notes
    trap_notes = [t.pattern_matched for t in trap_detections if t.action_taken.startswith("ignored")]
    pack_verdict = compute_pack_verdict(sup_pack, amz_total, rsu, adjusted_profit, trap_notes)
    
    # Build the decision record
    record = RowDecisionRecord(
        row_id=row_id,
        bucket=bucket,
        confidence=0,  # Will be computed below
        pack_verdict=pack_verdict,
        adjusted_profit=adjusted_profit,
        rsu=rsu,
        supplier_attributes=supplier_attrs,
        amazon_attributes=amazon_attrs,
        trap_detections=trap_detections,
        match_checks=match_checks,
        key_match_evidence="",  # Will be computed below
        filter_reason=filter_reason,
        required_next_action=_get_required_action(bucket, match_checks),
        raw_row=dict(row)
    )
    
    # Compute confidence score (deterministic)
    record.confidence = compute_confidence(record)
    
    # Compute evidence string
    record.key_match_evidence = compute_evidence_string(record)
    
    return record


def categorize_row(
    match_checks: MatchChecks,
    adjusted_profit: float,
    rsu: float,
    trap_detections: List[TrapDetection]
) -> tuple:
    """
    Categorize a row into the appropriate bucket.
    
    Decision tree from Main.txt:
    1. Exact EAN + no pack contradiction + profit > 0 → VERIFIED
    2. Exact EAN + pack/profit issue → FILTERED_OUT
    3. Brand + Product match + profit > 0 → HIGHLY_LIKELY  
    4. Plausible match needing confirmation → NEEDS_VERIFICATION
    5. Otherwise → FILTERED_OUT or not included
    
    Args:
        match_checks: Results of all match verification checks
        adjusted_profit: Profit after RSU adjustment
        rsu: Required Supplier Units
        trap_detections: List of trap detections
        
    Returns:
        Tuple of (bucket, filter_reason)
    """
    # Step 1: Check for exact EAN match
    if match_checks.is_exact_ean_strict:
        # EAN match - check for pack contradiction or profit issue
        if adjusted_profit <= 0:
            return Bucket.FILTERED_OUT.value, f"RSU={int(rsu)}; adjusted profit negative"
        
        # Check for explicit pack contradiction (not dimension traps)
        has_real_pack_issue = False
        for trap in trap_detections:
            if trap.trap_type == "capacity_multipack" and rsu > 1:
                has_real_pack_issue = True
        
        if has_real_pack_issue and adjusted_profit <= 0:
            return Bucket.FILTERED_OUT.value, f"Pack multipack requires {int(rsu)} units; unprofitable"
        
        # Valid VERIFIED
        return Bucket.VERIFIED.value, "-"
    
    # Step 2: Check for HIGHLY_LIKELY (brand + product match)
    if match_checks.brand_match and match_checks.product_type_match:
        if adjusted_profit <= 0:
            return Bucket.FILTERED_OUT.value, "Brand/product match but adjusted profit negative"
        
        # Check variant mismatch
        if match_checks.variant_match == "false":
            return Bucket.FILTERED_OUT.value, "Variant mismatch (size/color/scent)"
        
        # Check capacity difference
        if match_checks.capacity_delta_percent and match_checks.capacity_delta_percent > 50:
            return Bucket.FILTERED_OUT.value, f"Capacity difference {int(match_checks.capacity_delta_percent)}% - different product"
        
        if match_checks.capacity_delta_percent and match_checks.capacity_delta_percent > 25:
            return Bucket.NEEDS_VERIFICATION.value, f"Capacity difference {int(match_checks.capacity_delta_percent)}% - verify SKU"
        
        # Valid HIGHLY_LIKELY
        return Bucket.HIGHLY_LIKELY.value, "-"
    
    # Step 3: Check for NEEDS_VERIFICATION
    if match_checks.brand_match or match_checks.product_type_match:
        if adjusted_profit <= 0:
            return Bucket.FILTERED_OUT.value, "Partial match but adjusted profit negative"
        
        # Has some match evidence - needs verification
        reasons = []
        if not match_checks.brand_match:
            reasons.append("verify brand")
        if not match_checks.product_type_match:
            reasons.append("verify product type")
        if match_checks.variant_match == "ambiguous":
            reasons.append("check variant")
        
        return Bucket.NEEDS_VERIFICATION.value, "; ".join(reasons) if reasons else "verify match details"
    
    # Step 4: Not enough evidence for any positive bucket
    if adjusted_profit <= 0:
        return Bucket.FILTERED_OUT.value, "No match evidence and unprofitable"
    
    # Weak evidence but profitable - route to NEEDS_VERIFICATION with low confidence
    # Per Main.txt: "if a row is not clearly unrelated, route to NEEDS VERIFICATION"
    return Bucket.NEEDS_VERIFICATION.value, "weak evidence - manual review needed"


def _check_variant_match(sup_attrs: ParsedAttributes, amz_attrs: ParsedAttributes) -> str:
    """Check if variants (color, scent, size) match."""
    if sup_attrs.variant and amz_attrs.variant:
        if sup_attrs.variant.lower() == amz_attrs.variant.lower():
            return "true"
        else:
            return "false"
    
    if sup_attrs.size_capacity and amz_attrs.size_capacity:
        # Compare capacities if both present
        # This is a simple check; capacity delta is calculated separately
        if sup_attrs.size_capacity.lower() == amz_attrs.size_capacity.lower():
            return "true"
    
    return "ambiguous"


def _calculate_capacity_delta(sup_attrs: ParsedAttributes, amz_attrs: ParsedAttributes) -> Optional[float]:
    """Calculate percentage difference in capacity/size."""
    import re
    
    sup_cap = sup_attrs.size_capacity
    amz_cap = amz_attrs.size_capacity
    
    if not sup_cap or not amz_cap:
        return None
    
    # Extract numeric values
    sup_match = re.search(r'(\d+(?:\.\d+)?)', sup_cap)
    amz_match = re.search(r'(\d+(?:\.\d+)?)', amz_cap)
    
    if not sup_match or not amz_match:
        return None
    
    sup_val = float(sup_match.group(1))
    amz_val = float(amz_match.group(1))
    
    if sup_val == 0:
        return None
    
    # Calculate percentage difference
    delta = abs(sup_val - amz_val) / sup_val * 100
    return round(delta, 1)


def _get_required_action(bucket: str, checks: MatchChecks) -> Optional[str]:
    """Determine required next action for NEEDS_VERIFICATION items."""
    if bucket != Bucket.NEEDS_VERIFICATION.value:
        return None
    
    actions = []
    
    if not checks.brand_match:
        actions.append("Confirm brand on packaging")
    
    if not checks.is_exact_ean_strict and not checks.ean_strict_valid_amazon:
        actions.append("Check Amazon EAN")
    
    if checks.variant_match == "ambiguous":
        actions.append("Verify variant (size/color/scent)")
    
    if not checks.pack_match:
        actions.append("Confirm pack count")
    
    return "; ".join(actions) if actions else "Manual verification required"


def analyze_all_rows(
    df: pd.DataFrame, 
    config: Optional[Dict] = None,
    progress_callback=None
) -> List[RowDecisionRecord]:
    """
    Analyze all rows in a DataFrame.
    
    Args:
        df: Normalized DataFrame
        config: Optional calibration config
        progress_callback: Optional callback for progress updates
        
    Returns:
        List of RowDecisionRecord for all rows
    """
    records = []
    total = len(df)
    
    for idx, row in df.iterrows():
        record = analyze_row(row.to_dict(), config)
        records.append(record)
        
        if progress_callback and idx % 100 == 0:
            progress_callback(idx + 1, total)
    
    return records
