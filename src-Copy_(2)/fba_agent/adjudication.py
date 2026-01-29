"""AI Row Adjudication module.

This module handles AI-assisted adjudication of ambiguous rows.
IMPORTANT: AI adjudication provides SUGGESTIONS only — the deterministic
scoring formula remains authoritative.

Adjudication is triggered for:
- Pack verdict = "uncertain" or "ambiguous"
- Variant match = "ambiguous"
- EAN missing but title match > 70%
- High profit outlier with weak match
- Rows that flipped bucket vs previous iteration

Adjudication is CAPPED at min(200, 5% of total rows).
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import TYPE_CHECKING

import pandas as pd

from fba_agent.types import AdjudicationResult, MergedConfig

if TYPE_CHECKING:
    from fba_agent.providers import BaseProvider


# Adjudication JSON schema for strict output
ADJUDICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "row_id": {"type": "integer"},
        "extracted_signals": {
            "type": "object",
            "properties": {
                "supplier_brand": {"type": "string"},
                "amazon_brand": {"type": "string"},
                "brand_match": {"type": "boolean"},
                "supplier_pack": {"type": "integer"},
                "amazon_pack": {"type": "integer"},
                "pack_match": {"type": "boolean"},
                "product_type": {"type": "string"},
            },
        },
        "trap_detections": {"type": "array", "items": {"type": "string"}},
        "recommended_bucket": {"type": "string"},
        "confidence_suggestion": {"type": "integer"},
        "reasoning": {"type": "string"},
    },
    "required": ["row_id", "extracted_signals", "trap_detections", "recommended_bucket", "confidence_suggestion", "reasoning"],
}


def select_candidates(
    ledger: pd.DataFrame,
    evidence: list[dict],
    config: MergedConfig,
    cap: int = 50,  # REDUCED from 300 to save tokens
    cap_percentage: float = 0.02,  # REDUCED from 10% to 2%
) -> list[int]:
    """
    Select row_ids for AI adjudication based on ambiguity triggers.
    
    Args:
        ledger: Analysis ledger
        evidence: Evidence list from analysis
        config: Merged configuration
        cap: Absolute cap on candidates (default: 200)
        cap_percentage: Percentage cap (default: 5%)
    
    Returns:
        List of row_ids to adjudicate
    """
    total_rows = len(ledger)
    effective_cap = min(cap, int(total_rows * cap_percentage))
    
    candidates = set()
    
    # 1. Rows with ambiguous pack verdict
    if "pack_verdict" in ledger.columns:
        ambiguous_pack = ledger[
            ledger["pack_verdict"].str.lower().str.contains("ambiguous|uncertain|unknown", na=False)
        ]
        candidates.update(ambiguous_pack["row_id"].tolist())
    
    # 2. Rows with mid-range confidence (near decision boundaries)
    if "confidence" in ledger.columns:
        confidence = pd.to_numeric(ledger["confidence"], errors="coerce").fillna(50)
        mid_confidence = ledger[(confidence >= 45) & (confidence <= 60)]
        candidates.update(mid_confidence["row_id"].tolist())
    
    # 3. High profit with weak match
    if "adjusted_profit" in ledger.columns and "confidence" in ledger.columns:
        profit = pd.to_numeric(ledger["adjusted_profit"], errors="coerce").fillna(0)
        confidence = pd.to_numeric(ledger["confidence"], errors="coerce").fillna(50)
        high_profit_weak = ledger[(profit > 10) & (confidence < 65)]
        candidates.update(high_profit_weak["row_id"].tolist()[:20])
    
    # 4. NEEDS_VERIFICATION bucket (these are ambiguous by definition)
    needs_verif = ledger[ledger["bucket"] == "NEEDS_VERIFICATION"]
    candidates.update(needs_verif["row_id"].tolist()[:50])
    
    # 5. High original profit but FILTERED_OUT (likely pack detection errors)
    if "bucket" in ledger.columns and "net_profit" in ledger.columns and "adjusted_profit" in ledger.columns:
        high_profit_filtered = ledger[
            (ledger["bucket"] == "FILTERED_OUT") &
            (pd.to_numeric(ledger["net_profit"], errors="coerce").fillna(0) > 5) &
            (pd.to_numeric(ledger["adjusted_profit"], errors="coerce").fillna(0) <= 0)
        ]
        # Take top 100 by original profit
        if len(high_profit_filtered) > 0:
            sorted_filtered = high_profit_filtered.sort_values("net_profit", ascending=False)
            candidates.update(sorted_filtered["row_id"].tolist()[:100])
    
    # Apply cap
    candidate_list = list(candidates)[:effective_cap]
    
    return candidate_list


def build_adjudication_prompt(row_data: dict) -> tuple[str, str]:
    """
    Build system and user prompts for row adjudication.
    
    This prompt is based on the FBA Manual Analysis Methodology Guide
    and applies Appendix-C style reasoning for trap detection.
    
    Args:
        row_data: Row data dict with all relevant fields
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = """You are a **Principal E-Commerce Analyst** specializing in Amazon FBA arbitrage.

Your task is to analyze a single product row and determine the correct bucket assignment.
Apply THOROUGH MANUAL ANALYSIS following these strict rules:

## BUCKET DEFINITIONS

### VERIFIED (Confidence 90-100)
Requirements - ALL must be TRUE:
- ✓ Exact EAN match (both present, valid, identical after normalization)
- ✓ Pack ratio = 1 OR Adjusted Profit > 0 after pack calculation
- ✓ No variant mismatch (same size, color, scent)
- ✓ Adjusted Profit > 0

### HIGHLY_LIKELY (Confidence 70-89)
Requirements - ALL must be TRUE:
- ✓ Brand from known brands appears in BOTH titles (case-insensitive)
- ✓ Product type matches (same category of item)
- ✓ No pack mismatch OR Adjusted Profit > 0 after pack recalculation
- ✓ No variant mismatch
- ✓ Adjusted Profit > 0

### NEEDS_VERIFICATION (Confidence 50-69)
Requirements - ALL must be TRUE:
- ✓ Partial match evidence (brand in one title, OR strong product similarity)
- ✓ Only 1-2 specific details need confirmation
- ✓ Adjusted Profit > £0.50

### FILTERED_OUT (Confidence 0-49)
Assign here if ANY of these are TRUE:
- Pack mismatch makes Adjusted Profit ≤ 0
- Variant mismatch detected (same product family, different variant)
- Adjusted Profit ≤ 0
- Clear product mismatch (different product types)
- Category mismatch (cheap supplier item linked to expensive unrelated Amazon listing)

## CRITICAL TRAP DETECTION RULES

### DIMENSION SHIELD (NEVER treat as pack counts)
- Patterns: "X x Y cm", "X x Y mm", "X x Y inch", "X x Y in", "X x Y m"
- Examples: "9 x 9 inch", "30cm x 36cm", "280X115MM" = SIZE, NOT QUANTITY
- NEVER compute RSU by multiplying dimension numbers

### SPEC MULTIPLIER SHIELD (NEVER treat as pack counts)
- Patterns: "Nx magnification", "Nx zoom", "N LED", "N watt", "NW"
- Examples: "10x magnification", "9 LED", "60W" = SPECIFICATION, NOT QUANTITY

### CAPACITY MULTIPACK RULE
- Pattern: "N x 400ml" means RSU = N (the pack count), not N×400
- Pattern: "500ml x 6" means 6 bottles of 500ml each, RSU = 6

### QUANTITY-INSIDE RULE
- "STICKS 200" usually means ONE pack containing 200 sticks, NOT 200 packs
- Only treat as multipack if explicit multipack words (pack of, x, set of)

### VALID PACK INDICATORS
- "Pack of X", "X-pack", "X pack", "PK X", "PKX"
- "X pcs", "X pieces", "X ct", "X count"
- "Set of X", "X piece set"
- Leading "X x" at start (e.g., "3 x Product Name")

## BRAND MATCHING RULES
- Brand names may differ slightly ("ACME" vs "Acme Products")
- Check beginning of titles for brand position
- INVALID first words (NOT brands): MONEY, HAPPY, SALT, LED, BBQ, DOOR, PET, LARGE, SMALL, WOODEN, METAL, CHRISTMAS

## CAPACITY TOLERANCE (when same product confirmed)
- 0-10%: VERIFIED/HIGHLY_LIKELY with note
- 10-25%: NEEDS_VERIFICATION
- 25-50%: FILTERED_OUT (different SKU)
- >50%: FILTERED_OUT (completely different product)

## DECISION BIAS
For items with profit > £1 and reasonable brand/product match:
- Default to HIGHLY_LIKELY unless clear evidence of problem
- Missing Amazon EAN alone does NOT mean reject
- Only use FILTERED_OUT for clearly different products or negative profit

Respond with JSON only. Be precise about your reasoning."""

    user = f"""Analyze this product row:

## Row Data
- Row ID: {row_data.get('row_id')}
- Current Bucket: {row_data.get('bucket', '')}
- Current Confidence: {row_data.get('confidence', 50)}

## Titles
- Supplier Title: {row_data.get('supplier_title', '')}
- Amazon Title: {row_data.get('amazon_title', '')}

## EAN/Barcode
- Supplier EAN: {row_data.get('supplier_ean', '')}
- Amazon EAN: {row_data.get('amazon_ean', '')}
- ASIN: {row_data.get('asin', '')}

## Pack Analysis
- Pack Verdict: {row_data.get('pack_verdict', '')}
- Traps Detected: {row_data.get('traps', [])}

## Financial
- Adjusted Profit: £{row_data.get('adjusted_profit', 0):.2f}

## Your Task
1. Apply the trap detection rules to the titles
2. Determine if this is a valid match
3. Assign the correct bucket with confidence score
4. Provide clear reasoning

Return JSON with your analysis including:
- extracted_signals: brand, pack sizes, product type
- trap_detections: any traps you identified
- recommended_bucket: VERIFIED, HIGHLY_LIKELY, NEEDS_VERIFICATION, or FILTERED_OUT
- confidence_suggestion: 0-100
- reasoning: explanation of your decision"""

    return system, user


def run_adjudication_single(
    row_data: dict,
    provider: "BaseProvider",
) -> AdjudicationResult:
    """
    Run adjudication for a single row.
    
    Args:
        row_data: Row data dict
        provider: LLM provider instance
    
    Returns:
        AdjudicationResult
    """
    system, user = build_adjudication_prompt(row_data)
    
    try:
        response = provider.chat_json(system, user, schema=ADJUDICATION_SCHEMA)
        
        return AdjudicationResult(
            row_id=row_data.get("row_id", 0),
            stable_key=row_data.get("stable_key", ""),
            extracted_signals=response.get("extracted_signals", {}),
            trap_detections=response.get("trap_detections", []),
            recommended_bucket=response.get("recommended_bucket", "NEEDS_VERIFICATION"),
            confidence_suggestion=response.get("confidence_suggestion", 50),
            reasoning=response.get("reasoning", ""),
        )
    except Exception as e:
        # On failure, return neutral result
        return AdjudicationResult(
            row_id=row_data.get("row_id", 0),
            stable_key=row_data.get("stable_key", ""),
            extracted_signals={},
            trap_detections=[],
            recommended_bucket="NEEDS_VERIFICATION",
            confidence_suggestion=50,
            reasoning=f"Adjudication failed: {type(e).__name__}",
        )


def run_adjudication(
    candidates: list[dict],
    provider: "BaseProvider",
    batch_size: int = 10,  # Process 10 rows per API call to save tokens
) -> list[AdjudicationResult]:
    """
    Run BATCH adjudication for candidates.
    
    TOKEN OPTIMIZATION: Instead of 1 API call per row (280 calls = ~420K tokens),
    we batch multiple rows per call. With batch_size=10:
    - 28 calls instead of 280
    - System prompt repeated 28 times instead of 280
    - Saves ~280K tokens per run (~70% reduction)
    
    Args:
        candidates: List of row data dicts
        provider: LLM provider instance
        batch_size: Number of rows per API call (default 10)
    
    Returns:
        List of AdjudicationResults
    """
    if not candidates:
        return []
    
    results = []
    
    # Process in batches
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i + batch_size]
        batch_results = run_adjudication_batch(batch, provider)
        results.extend(batch_results)
    
    return results


def run_adjudication_batch(
    batch: list[dict],
    provider: "BaseProvider",
) -> list[AdjudicationResult]:
    """
    Run adjudication for a batch of rows in a SINGLE API call.
    
    Args:
        batch: List of row data dicts (typically 10 rows)
        provider: LLM provider instance
    
    Returns:
        List of AdjudicationResults
    """
    # Build batch prompt using the same system prompt but multiple rows in user
    system, _ = build_adjudication_prompt(batch[0])  # Get system prompt
    
    # Build batch user prompt
    rows_text = []
    for idx, row_data in enumerate(batch):
        row_text = f"""### ROW {idx + 1} (Row ID: {row_data.get('row_id')})
- Current Bucket: {row_data.get('bucket', '')}
- Current Confidence: {row_data.get('confidence', 50)}
- Supplier Title: {row_data.get('supplier_title', '')}
- Amazon Title: {row_data.get('amazon_title', '')}
- Supplier EAN: {row_data.get('supplier_ean', '')}
- Amazon EAN: {row_data.get('amazon_ean', '')}
- Pack Verdict: {row_data.get('pack_verdict', '')}
- Adjusted Profit: £{row_data.get('adjusted_profit', 0):.2f}
"""
        rows_text.append(row_text)
    
    user = f"""Analyze these {len(batch)} product rows and return a JSON array with one result per row:

{chr(10).join(rows_text)}

Return JSON array with {len(batch)} objects, each containing:
- row_id, extracted_signals, trap_detections, recommended_bucket, confidence_suggestion, reasoning

Format: {{"results": [{{...}}, {{...}}, ...]}}"""
    
    try:
        response = provider.chat_json(system, user)
        
        # Parse batch response
        results_data = response.get("results", [])
        if not isinstance(results_data, list):
            results_data = [response]  # Fallback if single object returned
        
        results = []
        for idx, row_data in enumerate(batch):
            if idx < len(results_data):
                r = results_data[idx]
                results.append(AdjudicationResult(
                    row_id=row_data.get("row_id", 0),
                    stable_key=row_data.get("stable_key", ""),
                    extracted_signals=r.get("extracted_signals", {}),
                    trap_detections=r.get("trap_detections", []),
                    recommended_bucket=r.get("recommended_bucket", "NEEDS_VERIFICATION"),
                    confidence_suggestion=r.get("confidence_suggestion", 50),
                    reasoning=r.get("reasoning", ""),
                ))
            else:
                # Missing result for this row
                results.append(AdjudicationResult(
                    row_id=row_data.get("row_id", 0),
                    stable_key=row_data.get("stable_key", ""),
                    extracted_signals={},
                    trap_detections=[],
                    recommended_bucket="NEEDS_VERIFICATION",
                    confidence_suggestion=50,
                    reasoning="Batch response missing this row",
                ))
        
        return results
        
    except Exception as e:
        # On failure, return neutral results for all rows in batch
        return [
            AdjudicationResult(
                row_id=row_data.get("row_id", 0),
                stable_key=row_data.get("stable_key", ""),
                extracted_signals={},
                trap_detections=[],
                recommended_bucket="NEEDS_VERIFICATION",
                confidence_suggestion=50,
                reasoning=f"Batch adjudication failed: {type(e).__name__}",
            )
            for row_data in batch
        ]


def adjudication_results_to_dict(results: list[AdjudicationResult]) -> list[dict]:
    """Convert adjudication results to serializable dicts."""
    return [asdict(r) for r in results]
