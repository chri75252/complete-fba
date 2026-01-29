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
    cap: int = 99,  # Changed from 50 to 99 (3 batches of 33)
    cap_percentage: float = 0.05,  # Changed from 2% to 5%
) -> list[int]:
    """
    Select row_ids for AI adjudication based on ambiguity triggers.
    
    Candidates are SORTED BY NET_PROFIT descending so highest-profit
    ambiguous rows are analyzed first.
    
    Args:
        ledger: Analysis ledger
        evidence: Evidence list from analysis
        config: Merged configuration
        cap: Absolute cap on candidates (default: 99, 3 batches of 33)
        cap_percentage: Percentage cap (default: 5%)
    
    Returns:
        List of row_ids to adjudicate, sorted by net_profit descending
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
    
    # 2. Rows with mid-range confidence (near decision boundaries: 45-70)
    if "confidence" in ledger.columns:
        confidence = pd.to_numeric(ledger["confidence"], errors="coerce").fillna(50)
        mid_confidence = ledger[(confidence >= 45) & (confidence <= 70)]
        candidates.update(mid_confidence["row_id"].tolist())
    
    # 3. NEEDS_VERIFICATION bucket (these are ambiguous by definition) - handle both naming variants
    needs_verif = ledger[ledger["bucket"].isin(["NEEDS_VERIFICATION", "NEEDS VERIFICATION"])]
    candidates.update(needs_verif["row_id"].tolist())
    
    # 4. HIGHLY_LIKELY with edge-case signals (potential false positives)
    if "bucket" in ledger.columns:
        hl_rows = ledger[ledger["bucket"] == "HIGHLY_LIKELY"]
        if "pack_verdict" in ledger.columns:
            # HL with any pack-related issues
            hl_pack_issues = hl_rows[
                hl_rows["pack_verdict"].str.lower().str.contains("pack|mismatch|ratio", na=False)
            ]
            candidates.update(hl_pack_issues["row_id"].tolist())
    
    # NOTE: Profit-based selection REMOVED per AI_LOGIC_PROPOSED_PLAN
    # "NET PROFIT/ROI WILL NEVER BE A DEFINING FILTER"
    
    # Sort candidates by net_profit descending so highest-value ambiguous rows are analyzed first
    candidate_rows = ledger[ledger["row_id"].isin(candidates)].copy()
    if "net_profit" in candidate_rows.columns:
        candidate_rows["_sort_profit"] = pd.to_numeric(candidate_rows["net_profit"], errors="coerce").fillna(0)
        candidate_rows = candidate_rows.sort_values("_sort_profit", ascending=False)
    
    # Apply cap on sorted list
    candidate_list = candidate_rows["row_id"].tolist()[:effective_cap]
    
    return candidate_list


def create_md_report_batches(
    md_report_content: str,
    batch_size: int = 70,
) -> list[dict]:
    """
    Extract batches of rows from MD report WITH category headers.
    
    Per AI_LOGIC_PROPOSED_PLAN:
    - Process ALL rows from MD report (~367 rows, not 2789 from Excel)
    - Batches of 70 rows
    - Each batch includes category headers
    - If batch continues from previous category, include "[CONTINUED]"
    
    Args:
        md_report_content: Full MD report content as string
        batch_size: Number of rows per batch (default: 70)
    
    Returns:
        List of batch dicts: [{batch_num, content, row_count, categories}]
    """
    import re
    
    # Parse MD report sections
    sections = []
    current_section = None
    current_header = None
    current_rows = []
    
    lines = md_report_content.split("\n")
    in_table = False
    table_header_lines = []
    
    for line in lines:
        # Detect section headers (## VERIFIED - RECOMMENDED, etc.)
        if line.startswith("## ") and any(cat in line.upper() for cat in 
            ["VERIFIED", "HIGHLY LIKELY", "HIGHLY_LIKELY", "NEEDS VERIFICATION", "NEEDS_VERIFICATION", "FILTERED"]):
            # Save previous section
            if current_section and current_rows:
                sections.append({
                    "header": current_header,
                    "category": current_section,
                    "table_header": "\n".join(table_header_lines),
                    "rows": current_rows,
                })
            current_header = line
            current_section = _extract_category_name(line)
            current_rows = []
            table_header_lines = []
            in_table = False
            continue
        
        # Detect table start (```text or | header | )
        if "```text" in line or (line.startswith("|") and "Verdict" in line):
            in_table = True
            if line.startswith("|"):
                table_header_lines.append(line)
            continue
        
        # Detect separator line
        if in_table and line.startswith("|-"):
            table_header_lines.append(line)
            continue
        
        # Detect table end
        if "```" in line and in_table and "```text" not in line:
            in_table = False
            continue
        
        # Collect table rows
        if in_table and line.startswith("|") and current_section:
            current_rows.append(line)
    
    # Don't forget last section
    if current_section and current_rows:
        sections.append({
            "header": current_header,
            "category": current_section,
            "table_header": "\n".join(table_header_lines),
            "rows": current_rows,
        })
    
    # Now create batches with headers
    batches = []
    all_rows_with_category = []
    
    for section in sections:
        for row in section["rows"]:
            all_rows_with_category.append({
                "category": section["category"],
                "header": section["header"],
                "table_header": section["table_header"],
                "row": row,
            })
    
    # Split into batches
    total_rows = len(all_rows_with_category)
    batch_num = 1
    
    for i in range(0, total_rows, batch_size):
        batch_rows = all_rows_with_category[i:i + batch_size]
        
        # Build batch content with category headers
        batch_content = []
        current_cat = None
        
        for idx, item in enumerate(batch_rows):
            if item["category"] != current_cat:
                # Add category header
                if idx == 0 and i > 0:
                    # This batch starts mid-category
                    batch_content.append(f"{item['header']} [CONTINUED]")
                else:
                    batch_content.append(item["header"])
                batch_content.append(item["table_header"])
                current_cat = item["category"]
            
            batch_content.append(item["row"])
        
        batches.append({
            "batch_num": batch_num,
            "content": "\n".join(batch_content),
            "row_count": len(batch_rows),
            "start_row": i + 1,
            "end_row": min(i + batch_size, total_rows),
            "categories": list(set(r["category"] for r in batch_rows)),
        })
        batch_num += 1
    
    return batches


def _extract_category_name(header_line: str) -> str:
    """Extract category name from MD header line."""
    header_line = header_line.replace("##", "").strip()
    # Remove count suffix like "(count=35)"
    import re
    header_line = re.sub(r"\s*\(count=\d+\)", "", header_line)
    return header_line.strip()


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
    batch_size: int = 33,  # Process 33 rows per API call (99 candidates = 3 batches)
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


def run_md_batch_adjudication(
    batch_content: str,
    provider: "BaseProvider",
) -> dict:
    """
    Run adjudication on a batch of MD report rows.
    
    Per AI_LOGIC_PROPOSED_PLAN:
    - Input: Batch of MD table rows with category headers
    - Analyzes bucket assignments
    - Returns findings: corrections, issues, recommendations
    
    Args:
        batch_content: MD report batch content (rows with category headers)
        provider: LLM provider instance
    
    Returns:
        Dict with analysis findings
    """
    system = """You are a **Principal E-Commerce Analyst** reviewing an FBA product analysis report.

Your task is to analyze these product rows from the generated MD report and identify:
1. **Incorrect Bucket Assignments** - Products in wrong categories
2. **Pack Size Issues** - Obvious pack detection errors
3. **Brand Matching Issues** - Incorrect brand associations
4. **Missing Products** - Products that should be in a different bucket

## BUCKET DEFINITIONS

### VERIFIED (Confidence 90-100)
- ✓ Exact EAN match (both present, valid, identical)
- ✓ Pack ratio = 1 OR Adjusted Profit > 0 after pack calculation
- ✓ No variant mismatch
- ✓ Adjusted Profit > 0

### HIGHLY_LIKELY (Confidence 70-89)
- ✓ Brand appears in BOTH titles
- ✓ Product type matches
- ✓ No pack/variant mismatch OR profit still positive
- ✓ Adjusted Profit > 0

### NEEDS_VERIFICATION (Confidence 50-69)
- ✓ Partial match evidence
- ✓ 1-2 specific details need confirmation
- ✓ Adjusted Profit > £0.50

### FILTERED_OUT (Confidence 0-49)
- Pack mismatch makes profit ≤ 0
- Variant mismatch detected
- Clear product mismatch
- Category mismatch

## OUTPUT FORMAT

Return JSON:
{
    "bucket_corrections": [
        {
            "row_summary": "ELBOW GREASE...",
            "current_bucket": "VERIFIED",
            "recommended_bucket": "FILTERED_OUT",
            "reason": "Pack 12 detected but profit calculation wrong"
        }
    ],
    "pack_issues": [
        {
            "row_summary": "...",
            "issue": "Dimension 30x20cm read as pack 30"
        }
    ],
    "overall_assessment": "Batch contains X correctly categorized, Y need correction"
}
"""

    user = f"""Analyze these product rows from the MD report batch:

{batch_content}

Identify any incorrect bucket assignments, pack detection issues, or other problems.
Return your analysis as JSON."""

    try:
        response = provider.chat_json(system, user)
        return response
    except Exception as e:
        return {
            "error": str(e),
            "bucket_corrections": [],
            "pack_issues": [],
            "overall_assessment": f"Batch analysis failed: {type(e).__name__}"
        }


# Alias for backward compatibility with new iteration.py
run_adjudication_batch_from_md = run_md_batch_adjudication


def adjudication_results_to_dict(results: list[AdjudicationResult]) -> list[dict]:
    """Convert adjudication results to serializable dicts."""
    return [asdict(r) for r in results]
