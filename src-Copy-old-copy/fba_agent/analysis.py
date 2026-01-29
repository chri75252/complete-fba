from __future__ import annotations

from dataclasses import replace
from typing import Any

import pandas as pd

from fba_agent.ean import normalize_and_validate
from fba_agent.pack import pack_ratio, parse_pack_quantity
from fba_agent.scoring import compute_confidence
from fba_agent.text import jaccard_similarity, tokenize
from fba_agent.types import MatchChecks, MergedConfig, RowDecisionRecord
from fba_agent.variant import capacity_delta_pct, capacity_gate, parse_variant


def _extract_brand(title: str, brand_position: str) -> str | None:
    # GARBAGE BRAND FILTER (Phase 3 Fix):
    # These words should NEVER be treated as brands.
    INVALID_BRAND_TOKENS = {
        "3", "4", "5", "6", "8", "10", "12", "16", "20", "24", "40", "48", "50", "100",  # Numbers
        "SET", "PACK", "BOX", "BAG", "BOTTLE", "JAR", "TIN", "CAN", "TUB", "CASE",     # Containers
        "LARGE", "SMALL", "MINI", "MEDIUM", "EXTRA", "BIG", "GIANT", "JUMBO",          # Sizes
        "WHITE", "BLACK", "RED", "BLUE", "GREEN", "GREY", "PINK", "YELLOW", "ORANGE",  # Colors
        "GOLD", "SILVER", "BRONZE", "CLEAR", "TRANSPARENT", "MULTI", "COLOUR",         # Colors/Finish
        "WATERPROOF", "STAINLESS", "PLASTIC", "WOODEN", "METAL", "GALVANISED",         # Materials
        "GLASS", "RUBBER", "SILICONE", "FABRIC", "LEATHER", "NYLON", "POLY",           # Materials
        "NEW", "PREMIUM", "BEST", "QUALITY", "PROFESSIONAL", "LUXURY", "DELUXE",       # Marketing
        "CHRISTMAS", "BIRTHDAY", "HAPPY", "MEMORIAL", "PARTY", "WEDDING",              # Occasion
        "CAT", "DOG", "PET", "FISH", "BIRD", "ANIMAL", "HORSE",                        # Animals (Generic)
        "HOME", "KITCHEN", "GARDEN", "OUTDOOR", "INDOOR", "HOUSE", "OFFICE",           # Locations
        "SUPER", "FAST", "QUICK", "STRONG", "HEAVY", "DUTY", "POWER", "TURBO",         # Adjectives
        "ROCKET", "SPACE", "MAGIC", "FUN", "PLAY", "TOY", "GAME",                      # Toys/Generic
        "SQUARE", "ROUND", "OVAL", "RECTANGLE", "SHAPE", "SHAPED",                     # Shapes
        "PC", "PCS", "PIECE", "PIECES", "PK", "X", "PLUS", "AND", "&",                 # Quantifiers
        "I", "LOVE", "YOU", "MY", "YOUR", "THE", "A", "AN", "OF", "FOR", "WITH",       # Stopwords
    }

    tokens = tokenize(title)
    if not tokens:
        return None
    
    # Try to find a valid brand token (skip garbage)
    for token in tokens[:3]:  # Only check first 3 tokens
        if token.upper() not in INVALID_BRAND_TOKENS:
            return token
    
    # If all first 3 tokens are garbage, return None (no brand detected)
    return None


def _product_tokens(title: str, brand: str | None) -> set[str]:
    tokens = tokenize(title)
    filtered: list[str] = []
    
    # SMART TOKEN CLEANING (Phase 2 Fix):
    # If a brand is provided (e.g. "CHEF AID"), we must remove ALL tokens
    # that appear in the brand string from the product tokens.
    # Otherwise "CHEF AID" vs "CHEF CHOICE" matches on "CHEF".
    brand_tokens = set()
    if brand:
        brand_tokens = set(tokenize(brand))

    for t in tokens:
        if t in brand_tokens:
            continue
        if any(ch.isdigit() for ch in t):
            continue
        if len(t) < 3:
            continue
        filtered.append(t)
    return set(filtered)


def analyze_row(row: pd.Series, config: MergedConfig, brand_aliases: dict[str, str] | None = None) -> RowDecisionRecord:
    row_id = int(row["RowID"])

    supplier_title = str(row["SupplierTitle"] or "")
    amazon_title = str(row["AmazonTitle"] or "")
    asin = str(row["ASIN"] or "")

    supplier_ean_info = normalize_and_validate(row.get("SupplierEAN_raw"))
    amazon_ean_info = normalize_and_validate(row.get("AmazonEAN_raw"))

    supplier_ean = supplier_ean_info.normalized or "-"
    amazon_ean = amazon_ean_info.normalized or "-"
    amazon_ean_missing = row.get("AmazonEAN_raw") is None or str(row.get("AmazonEAN_raw")).strip() in {"", "nan", "NaN"}

    # STRICT: Both checksums must validate
    strict_exact_ean = bool(
        supplier_ean_info.is_valid
        and amazon_ean_info.is_valid
        and supplier_ean_info.normalized == amazon_ean_info.normalized
    )
    
    # SOFT: Digit strings match even if one/both checksums fail (catches data entry errors)
    # Use digits field which has the raw extracted digits before validation
    soft_exact_ean = bool(
        supplier_ean_info.digits
        and amazon_ean_info.digits
        and len(supplier_ean_info.digits) >= 8  # At least UPC-8 length
        and len(amazon_ean_info.digits) >= 8
        and supplier_ean_info.digits == amazon_ean_info.digits
    )
    
    # Combined: Use either match type for VERIFIED categorization
    exact_ean_match = strict_exact_ean or soft_exact_ean

    supplier_pack = parse_pack_quantity(supplier_title, config.naming)
    amazon_pack = parse_pack_quantity(amazon_title, config.naming)
    ratio = pack_ratio(amazon_pack.quantity, supplier_pack.quantity)

    traps = sorted(set(supplier_pack.traps + amazon_pack.traps))

    supplier_var = parse_variant(supplier_title)
    amazon_var = parse_variant(amazon_title)
    delta = capacity_delta_pct(supplier_var.capacity_base, amazon_var.capacity_base)
    cap_gate = capacity_gate(delta)

    brand_s = _extract_brand(supplier_title, config.naming.brand_position)
    brand_a = _extract_brand(amazon_title, config.naming.brand_position)
    
    # Track if brands are VALIDATED (found in known brands list)
    # This prevents random first words from triggering exclusion
    brand_s_validated = False
    brand_a_validated = False
    
    if brand_aliases:
        if brand_s and brand_s in brand_aliases:
            brand_s = brand_aliases[brand_s]
            brand_s_validated = True
        if brand_a and brand_a in brand_aliases:
            brand_a = brand_aliases[brand_a]
            brand_a_validated = True

    brand_match = bool(brand_s and brand_a and brand_s == brand_a)

    product_s = _product_tokens(supplier_title, brand_s)
    product_a = _product_tokens(amazon_title, brand_a)
    similarity = jaccard_similarity(product_s, product_a)
    product_type_match = similarity >= config.title_match_threshold and len(product_s & product_a) >= 1

    variant_ok = cap_gate in {"unknown", "ok_0_10"}
    if cap_gate == "nv_10_25":
        variant_ok = False
    if cap_gate in {"fo_25_50", "fo_gt_50"}:
        variant_ok = False

    supplier_price = row.get("SupplierPrice")
    selling_price = row.get("SellingPrice")
    net_profit = row.get("NetProfit")
    roi = row.get("ROI")
    sales = row.get("Sales")

    adjusted_profit: float | None
    if net_profit is None or (isinstance(net_profit, float) and pd.isna(net_profit)):
        adjusted_profit = None
    else:
        adjusted_profit = float(net_profit)

    pack_verdict = "UNKNOWN"
    if ratio is None:
        pack_ambiguous = True
    else:
        # If both sides are implicitly single-unit and ratio is 1, treat as non-ambiguous (common case).
        if ratio == 1 and supplier_pack.quantity == 1 and amazon_pack.quantity == 1:
            pack_ambiguous = False
        else:
            pack_ambiguous = supplier_pack.ambiguous or amazon_pack.ambiguous

    filter_reason = "-"
    key_match_evidence = "-"

    # EXPANDED BOOLEAN LOGIC: Calculate additional match conditions
    partial_brand_match = (brand_s and not brand_a) or (brand_a and not brand_s)
    
    # MUCH MORE INCLUSIVE product matching
    strong_product_match = (
        similarity >= 0.30  # Tightened from 0.20 - reduce over-inclusiveness
        and len(product_s & product_a) >= 2  # At least 2 shared tokens
    )
    
    # DIFFERENT_BRANDS: Fail-Closed Logic (Phase 2 Fix)
    # If Brand_S is Known AND Brand_S != Brand_A -> Mismatch (regardless of if A is known)
    # If Brand_S is Unknown AND Brand_A is Known -> Mismatch (Generic vs Brand)
    # Also if text similarity of brands is 0.0 -> Mismatch
    
    brand_s_known = brand_s_validated
    brand_a_known = brand_a_validated
    
    is_brand_mismatch = False
    
    if brand_s and brand_a:
         # 1. Known Brand Mismatch
         if brand_s_known and brand_s != brand_a:
             is_brand_mismatch = True
         # 2. Unknown vs Known (Generic vs Brand)
         # PHASE 3: Removed. This rule creates too many false positives when
         # brand extraction returns garbage. Let similarity/EAN decide instead.
         # elif not brand_s_known and brand_a_known:
         #     is_brand_mismatch = True
         # 3. Complete Text Mismatch (Jaccard 0)
         else:
             b_s_tok = set(tokenize(brand_s))
             b_a_tok = set(tokenize(brand_a))
             if not (b_s_tok & b_a_tok): 
                 is_brand_mismatch = True

    different_brands_validated = is_brand_mismatch
    
    # Keep original check for reporting (but don't use for exclusion)
    different_brands = bool(brand_s and brand_a and brand_s != brand_a)

    # EXCLUSION RULE FIRST (only if BOTH are validated known brands)
    # PHASE 5: BALANCED MODE - Restore Fail-Closed Gate + Smarter Thresholds
    
    # 1. EAN Match OVERRIDES Brand Mismatch (Keep this Phase 3 Fix)
    if different_brands_validated and not exact_ean_match:
        include_in_tables = False
        bucket = "FILTERED_OUT"
        track = "UNKNOWN"
        filter_reason = f"Different known brands detected ({brand_s} vs {brand_a}); products not compatible"
        confirmed_match = False
    elif different_brands_validated and exact_ean_match:
        # EAN Override: Brand mismatch warning, but still process as EAN match
        confirmed_match = True
        filter_reason = f"Brand mismatch ({brand_s} vs {brand_a}) - EAN override"
    else:
        # MATCHING LOGIC - Context-Aware Thresholds
        
        # Scenario A: Brands Match (Strong Signal)
        if brand_match:
            # Very inclusive on text if brands agree
            confirmed_match = (
                exact_ean_match 
                or product_type_match 
                or (len(product_s & product_a) >= 1) # Just 1 matching token needed if brand is confirmed
            )
            
        # Scenario B: Partial Brand Match (One side has brand, other doesn't/is unknown)
        elif partial_brand_match:
            # Need moderate text evidence
            confirmed_match = (
                exact_ean_match
                or strong_product_match 
                or (similarity >= 0.25 and len(product_s & product_a) >= 2)
            )

        # Scenario C: No Brand / Unknown Brand Logic
        else:
            # High Risk Zone - Require Stronger Evidence
            confirmed_match = (
                exact_ean_match
                or (strong_product_match and len(product_s & product_a) >= 3) # 3+ tokens matching
                or (similarity >= 0.40) # Higher threshold for generic matches
            )


    if exact_ean_match:
        if strict_exact_ean:
            key_match_evidence = "Exact EAN match; checksums validate"
        else:
            key_match_evidence = "Exact EAN match (digits match, checksum not validated)"
    else:
        shared = sorted(list(product_s & product_a))[:6]
        if brand_match:
            key_match_evidence = f"Brand match: {brand_s}; anchors: {', '.join(shared) or '-'}"
        elif partial_brand_match and shared:
            key_match_evidence = f"Partial brand ({brand_s or brand_a}); anchors: {', '.join(shared)}"
        elif shared:
            key_match_evidence = f"Shared anchors: {', '.join(shared)}"

    if ratio is not None:
        if ratio == 1:
            pack_verdict = "1:1 Match"
        elif ratio > 1:
            pack_verdict = f"BUNDLE ({ratio:.2f}x) - requires multiple supplier units"
        else:
            pack_verdict = f"SPLIT CANDIDATE ({ratio:.2f}x) - supplier has more"

    if ratio is not None and ratio > 1 and adjusted_profit is not None and supplier_price is not None:
        adjusted_profit = float(adjusted_profit) - float(supplier_price) * (float(ratio) - 1.0)

    # Bucket policy with UNRELATED represented as FILTERED_OUT + include_in_tables=False.
    # Only set include_in_tables if  we haven't already excluded (different brands)
    if not different_brands_validated:
        include_in_tables = confirmed_match
    track = "UNKNOWN"
    bucket = "FILTERED_OUT"

    # Use combined EAN match (strict OR soft) for VERIFIED categorization
    if exact_ean_match:
        # STRICT VERIFIED: Only if checksums pass (Phase 2 Fix)
        if strict_exact_ean:
            track = "VERIFIED"
            bucket = "VERIFIED"
        else:
             # Soft match (invalid checksum) goes to HIGHLY LIKELY
             track = "HIGHLY_LIKELY"
             bucket = "HIGHLY_LIKELY"
             filter_reason = "Exact EAN match but invalid checksum (Soft Match)"

        include_in_tables = True
        if cap_gate in {"fo_25_50", "fo_gt_50"}:
            bucket = "FILTERED_OUT"
            filter_reason = f"Capacity mismatch ({cap_gate})"
        elif adjusted_profit is not None and adjusted_profit <= 0:
            bucket = "FILTERED_OUT"
            filter_reason = "Adjusted profit <= 0 after pack adjustment"
        elif ratio is not None and ratio < 1:
            bucket = "NEEDS_VERIFICATION"
            filter_reason = "Split candidate (supplier pack > Amazon pack)"
        # Note: bucket/track already set above based on strict vs soft
    elif confirmed_match and not different_brands_validated:
        track = "HIGHLY_LIKELY"
        if cap_gate == "nv_10_25":
            bucket = "NEEDS_VERIFICATION"
            filter_reason = "Capacity difference 10–25% (needs verification)"
        elif cap_gate in {"fo_25_50", "fo_gt_50"}:
            bucket = "FILTERED_OUT"
            filter_reason = f"Capacity mismatch ({cap_gate})"
        elif adjusted_profit is not None and adjusted_profit <= 0:
            bucket = "FILTERED_OUT"
            filter_reason = "Adjusted profit <= 0 after pack adjustment"
            # CRITICAL: Keep in tables for AUDITED OUT section
            include_in_tables = True
        # REMOVED pack_ambiguous check - strong matches should stay HIGHLY_LIKELY
        else:
            bucket = "HIGHLY_LIKELY"
            filter_reason = "-"
    # NEW PATH: NEEDS_VERIFICATION for partial matches (from ULTIMATE_FIX_PLAN)
    # Per gate mode logic: partial evidence that needs manual verification
    elif not different_brands_validated and (
        partial_brand_match  # Brand in ONE title only
        or (similarity >= 0.20 and len(product_s & product_a) >= 2)  # PHASE 3: Return to 0.20 (safe with clean tokens)
    ):
        # Check if profit is sufficient for NEEDS_VERIFICATION (> £0.50)
        if adjusted_profit is not None and adjusted_profit > 0.50:
            track = "NEEDS_VERIFICATION"
            bucket = "NEEDS_VERIFICATION"
            include_in_tables = True
            if partial_brand_match:
                filter_reason = f"Partial brand match ({brand_s or brand_a}) - requires verification"
            else:
                shared = sorted(list(product_s & product_a))[:4]
                filter_reason = f"Moderate product similarity ({', '.join(shared)}) - requires verification"
        else:
            # Profit too low for verification
            include_in_tables = False
            bucket = "FILTERED_OUT"
            track = "UNKNOWN"
            filter_reason = "Partial match but profit too low for verification"
    else:
        # No match or different brands: exclude from tables
        include_in_tables = False
        bucket = "FILTERED_OUT"
        track = "UNKNOWN"
        if different_brands:
            filter_reason = "Different brands detected; products not compatible"
        else:
            filter_reason = "Unrelated / not included"

    checks = MatchChecks(
        strict_exact_ean=strict_exact_ean,
        supplier_ean_valid=supplier_ean_info.is_valid,
        amazon_ean_valid=amazon_ean_info.is_valid,
        amazon_ean_missing=amazon_ean_missing,
        brand_match=brand_match,
        product_type_match=product_type_match,
        variant_within_tolerance=cap_gate in {"unknown", "ok_0_10"},
        capacity_delta_pct=delta,
        capacity_gate=cap_gate,  # type: ignore[arg-type]
    )

    provisional = RowDecisionRecord(
        row_id=row_id,
        bucket=bucket,  # type: ignore[arg-type]
        confidence=0,
        track=track,  # type: ignore[arg-type]
        include_in_tables=include_in_tables,
        supplier_title=supplier_title,
        amazon_title=amazon_title,
        supplier_ean=supplier_ean,
        amazon_ean=amazon_ean,
        asin=asin,
        supplier_price=None if supplier_price is None or pd.isna(supplier_price) else float(supplier_price),
        selling_price=None if selling_price is None or pd.isna(selling_price) else float(selling_price),
        net_profit=None if net_profit is None or pd.isna(net_profit) else float(net_profit),
        roi=None if roi is None or pd.isna(roi) else float(roi),
        sales=None if sales is None or pd.isna(sales) else float(sales),
        supplier_pack_qty=supplier_pack.quantity,
        amazon_pack_qty=amazon_pack.quantity,
        pack_ratio=ratio,
        pack_verdict=pack_verdict,
        adjusted_profit=adjusted_profit,
        key_match_evidence=key_match_evidence,
        filter_reason=filter_reason,
        traps=traps,
        checks=checks,
    )

    confidence = compute_confidence(provisional)
    return replace(provisional, confidence=confidence)


def analyze_all_rows(
    df: pd.DataFrame, config: MergedConfig, brand_aliases: dict[str, str] | None = None
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        rec = analyze_row(row, config, brand_aliases=brand_aliases)
        records.append(
            {
                "row_id": rec.row_id,
                "bucket": rec.bucket,
                "confidence": rec.confidence,
                "track": rec.track,
                "include_in_tables": rec.include_in_tables,
                "supplier_title": rec.supplier_title,
                "amazon_title": rec.amazon_title,
                "supplier_ean": rec.supplier_ean,
                "amazon_ean": rec.amazon_ean,
                "asin": rec.asin,
                "supplier_price": rec.supplier_price,
                "selling_price": rec.selling_price,
                "net_profit": rec.net_profit,
                "roi": rec.roi,
                "sales": rec.sales,
                "supplier_pack_qty": rec.supplier_pack_qty,
                "amazon_pack_qty": rec.amazon_pack_qty,
                "pack_ratio": rec.pack_ratio,
                "pack_verdict": rec.pack_verdict,
                "adjusted_profit": rec.adjusted_profit,
                "key_match_evidence": rec.key_match_evidence,
                "filter_reason": rec.filter_reason,
                "traps": ",".join(rec.traps),
            }
        )
        evidence.append(
            {
                "row_id": rec.row_id,
                "bucket": rec.bucket,
                "confidence": rec.confidence,
                "include_in_tables": rec.include_in_tables,
                "ean": {
                    "supplier": rec.supplier_ean,
                    "amazon": rec.amazon_ean,
                    "strict_exact": rec.checks.strict_exact_ean,
                },
                "pack": {
                    "supplier_qty": rec.supplier_pack_qty,
                    "amazon_qty": rec.amazon_pack_qty,
                    "ratio": rec.pack_ratio,
                    "verdict": rec.pack_verdict,
                },
                "variant": {
                    "capacity_delta_pct": rec.checks.capacity_delta_pct,
                    "capacity_gate": rec.checks.capacity_gate,
                },
                "checks": {
                    "brand_match": rec.checks.brand_match,
                    "product_type_match": rec.checks.product_type_match,
                    "variant_within_tolerance": rec.checks.variant_within_tolerance,
                },
                "titles": {"supplier": rec.supplier_title, "amazon": rec.amazon_title},
                "key_match_evidence": rec.key_match_evidence,
                "filter_reason": rec.filter_reason,
                "traps": rec.traps,
            }
        )

    ledger = pd.DataFrame.from_records(records)
    return ledger, evidence
