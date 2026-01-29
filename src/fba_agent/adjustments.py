"""Bounded adjustment application module.

This module applies bounded adjustments proposed by AI critique.
IMPORTANT: Only safe, bounded changes are allowed — no schema drift.

Allowed adjustments:
- add_shield_token: Add keyword to dimension/spec shields
- add_pack_keyword: Add keyword to pack detection
- add_brand_alias: Add brand alias mapping
- adjust_threshold: Adjust threshold by small amount (±0.05 max)

Disallowed:
- Rewriting individual row decisions
- Schema changes
- Unbounded parameter changes
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Any

from fba_agent.types import MergedConfig, SupplierNamingConvention


# Maximum threshold adjustment allowed
MAX_THRESHOLD_DELTA = 0.05

# Allowed change types
ALLOWED_CHANGE_TYPES = {
    "add_shield_token",
    "add_pack_keyword",
    "add_brand_alias",
    "adjust_threshold",
}


def validate_proposal(proposal: dict) -> tuple[bool, str]:
    """
    Validate that a proposed change is within allowed bounds.
    
    Args:
        proposal: Dict with change_type, target, value, safe_to_apply
    
    Returns:
        Tuple of (is_valid, reason)
    """
    change_type = proposal.get("change_type", "")
    target = proposal.get("target", "")
    value = proposal.get("value", "")
    safe_to_apply = proposal.get("safe_to_apply", False)
    
    # Check change type is allowed
    if change_type not in ALLOWED_CHANGE_TYPES:
        return False, f"Change type '{change_type}' not allowed"
    
    # Must have safe_to_apply flag
    if not safe_to_apply:
        return False, "Proposal marked as not safe to auto-apply"
    
    # Must have target and value
    if not target or not value:
        return False, "Missing target or value"
    
    # Type-specific validation
    if change_type == "add_shield_token":
        if target not in {"dimension_shield_keywords", "spec_x_shield_keywords"}:
            return False, f"Invalid shield target: {target}"
        if len(value) < 1 or len(value) > 20:
            return False, f"Shield token must be 1-20 chars: '{value}'"
    
    elif change_type == "add_pack_keyword":
        if target != "explicit_units":
            return False, f"Invalid pack keyword target: {target}"
        if len(value) < 1 or len(value) > 20:
            return False, f"Pack keyword must be 1-20 chars: '{value}'"
    
    elif change_type == "add_brand_alias":
        if target != "brand_aliases":
            return False, f"Invalid brand alias target: {target}"
        # Value should be "from:to" format
        if ":" not in value:
            return False, f"Brand alias must be 'from:to' format: '{value}'"
    
    elif change_type == "adjust_threshold":
        try:
            delta = float(value)
            if abs(delta) > MAX_THRESHOLD_DELTA:
                return False, f"Threshold delta {delta} exceeds max {MAX_THRESHOLD_DELTA}"
        except ValueError:
            return False, f"Invalid threshold delta: '{value}'"
    
    return True, ""


def apply_adjustment(
    config: MergedConfig,
    proposal: dict,
    brand_aliases: dict[str, str] | None = None,
) -> tuple[MergedConfig, dict[str, str], dict]:
    """
    Apply a single adjustment to config.
    
    Args:
        config: Current MergedConfig
        proposal: Validated proposal dict
        brand_aliases: Current brand aliases dict
    
    Returns:
        Tuple of (updated_config, updated_brand_aliases, applied_log)
    """
    if brand_aliases is None:
        brand_aliases = {}
    
    change_type = proposal["change_type"]
    target = proposal["target"]
    value = proposal["value"]
    
    naming = config.naming
    applied_log = {
        "change_type": change_type,
        "target": target,
        "value": value,
        "applied": True,
    }
    
    if change_type == "add_shield_token":
        if target == "dimension_shield_keywords":
            new_keywords = list(set(naming.dimension_shield_keywords) | {value.lower()})
            naming = replace(naming, dimension_shield_keywords=new_keywords)
        elif target == "spec_x_shield_keywords":
            new_keywords = list(set(naming.spec_x_shield_keywords) | {value.lower()})
            naming = replace(naming, spec_x_shield_keywords=new_keywords)
    
    elif change_type == "add_pack_keyword":
        if target == "explicit_units":
            new_units = list(set(naming.explicit_units) | {value.lower()})
            naming = replace(naming, explicit_units=new_units)
    
    elif change_type == "add_brand_alias":
        if ":" in value:
            from_brand, to_brand = value.split(":", 1)
            brand_aliases = deepcopy(brand_aliases)
            brand_aliases[from_brand.strip().upper()] = to_brand.strip().upper()
    
    elif change_type == "adjust_threshold":
        try:
            delta = float(value)
            new_threshold = max(0.1, min(0.5, config.title_match_threshold + delta))
            config = replace(config, title_match_threshold=new_threshold)
            applied_log["new_value"] = new_threshold
        except ValueError:
            applied_log["applied"] = False
            applied_log["error"] = f"Invalid delta: {value}"
    
    # Update config with new naming
    config = replace(config, naming=naming)
    
    return config, brand_aliases, applied_log


def apply_adjustments(
    config: MergedConfig,
    proposals: list[dict],
    brand_aliases: dict[str, str] | None = None,
) -> tuple[MergedConfig, dict[str, str], list[dict]]:
    """
    Apply all valid adjustments to config.
    
    Only applies proposals that are marked as safe_to_apply=True
    and pass validation.
    
    Args:
        config: Current MergedConfig
        proposals: List of proposal dicts from critique
        brand_aliases: Current brand aliases dict
    
    Returns:
        Tuple of (updated_config, updated_brand_aliases, applied_logs)
    """
    if brand_aliases is None:
        brand_aliases = {}
    
    applied_logs = []
    
    for proposal in proposals:
        # Validate proposal
        is_valid, reason = validate_proposal(proposal)
        
        if not is_valid:
            applied_logs.append({
                "change_type": proposal.get("change_type", "unknown"),
                "target": proposal.get("target", "unknown"),
                "value": proposal.get("value", ""),
                "applied": False,
                "reason": reason,
            })
            continue
        
        # Apply adjustment
        config, brand_aliases, log = apply_adjustment(config, proposal, brand_aliases)
        applied_logs.append(log)
    
    return config, brand_aliases, applied_logs


def count_applied(logs: list[dict]) -> int:
    """Count how many adjustments were successfully applied."""
    return sum(1 for log in logs if log.get("applied", False))


def apply_adjudication_to_ledger(
    ledger: Any,  # pd.DataFrame
    adjudication_results: list,  # List of AdjudicationResult or dict
) -> tuple[Any, int]:
    """
    Apply adjudication AI recommendations to the ledger.
    
    For each result, if the AI recommends upgrading a row
    from NEEDS_VERIFICATION to HIGHLY_LIKELY, update the ledger.
    
    Only safe transitions are allowed:
    - NEEDS_VERIFICATION → HIGHLY_LIKELY
    - NEEDS_VERIFICATION → VERIFIED
    - FILTERED_OUT → NEEDS_VERIFICATION
    
    Args:
        ledger: DataFrame with all product rows
        adjudication_results: List of AI decisions (AdjudicationResult or dict)
        
    Returns:
        (updated_ledger, count_of_applied_changes)
    """
    import pandas as pd
    
    applied_count = 0
    
    for result in adjudication_results:
        # Handle both dict and dataclass
        if hasattr(result, 'row_id'):
            # It's a dataclass
            row_id = result.row_id
            recommended_bucket = result.recommended_bucket
            confidence = getattr(result, 'confidence_suggestion', None)
        else:
            # It's a dict
            row_id = result.get("row_id")
            recommended_bucket = result.get("recommended_bucket")
            confidence = result.get("confidence") or result.get("confidence_suggestion")
        
        if row_id is None or recommended_bucket is None:
            continue
        
        # Find row in ledger
        mask = ledger["row_id"] == row_id
        if not mask.any():
            continue  # Row not found
        
        current_bucket = ledger.loc[mask, "bucket"].iloc[0]
        
        # Only allow safe upgrades
        if (current_bucket in ["NEEDS_VERIFICATION", "NEEDS VERIFICATION"] and 
            recommended_bucket == "HIGHLY_LIKELY"):
            # Apply upgrade
            ledger.loc[mask, "bucket"] = "HIGHLY_LIKELY"
            ledger.loc[mask, "track"] = "HIGHLY_LIKELY"
            if confidence is not None:
                ledger.loc[mask, "confidence"] = confidence
            applied_count += 1
        
        elif (current_bucket in ["NEEDS_VERIFICATION", "NEEDS VERIFICATION"] and 
              recommended_bucket == "VERIFIED"):
            ledger.loc[mask, "bucket"] = "VERIFIED"
            ledger.loc[mask, "track"] = "VERIFIED"
            if confidence is not None:
                ledger.loc[mask, "confidence"] = confidence
            applied_count += 1
        
        elif (current_bucket == "FILTERED_OUT" and 
              recommended_bucket in ["NEEDS_VERIFICATION", "NEEDS VERIFICATION"]):
            ledger.loc[mask, "bucket"] = "NEEDS_VERIFICATION"
            ledger.loc[mask, "track"] = "NEEDS_VERIFICATION"
            ledger.loc[mask, "include_in_tables"] = True
            if confidence is not None:
                ledger.loc[mask, "confidence"] = confidence
            applied_count += 1
            
    return ledger, applied_count


def apply_batch_adjudication_to_ledger(
    ledger: Any,  # pd.DataFrame
    batch_results: list[dict],  # List of batch result dicts from MD report adjudication
) -> tuple[Any, int]:
    """
    Apply MD report batch adjudication results to the ledger.
    
    Per AI_LOGIC_PROPOSED_PLAN:
    - Each batch result contains bucket_corrections from LLM
    - Apply corrections to ledger
    
    Args:
        ledger: DataFrame with all product rows
        batch_results: List of batch result dicts with 'result' key
        
    Returns:
        (updated_ledger, count_of_applied_changes)
    """
    applied_count = 0
    
    for batch in batch_results:
        if "error" in batch:
            continue  # Skip failed batches
        
        result = batch.get("result", {})
        corrections = result.get("bucket_corrections", [])
        
        for correction in corrections:
            row_summary = correction.get("row_summary", "")
            current_bucket = correction.get("current_bucket", "")
            recommended_bucket = correction.get("recommended_bucket", "")
            reason = correction.get("reason", "")
            
            if not row_summary or not recommended_bucket:
                continue
            
            # Find matching row by partial title match
            # (since we don't have row_id in MD report tables)
            mask = None
            for col in ["supplier_title", "amazon_title"]:
                if col in ledger.columns:
                    # Partial match on first 30 chars of row_summary
                    search_term = row_summary[:30].lower()
                    col_lower = ledger[col].astype(str).str.lower()
                    matches = col_lower.str.contains(search_term, regex=False, na=False)
                    if matches.any():
                        mask = matches
                        break
            
            if mask is None or not mask.any():
                continue  # No match found
            
            # Only apply if single match found (avoid ambiguous corrections)
            if mask.sum() > 1:
                continue
            
            current_in_ledger = ledger.loc[mask, "bucket"].iloc[0]
            
            # Verify current_bucket matches
            if current_bucket and current_bucket != current_in_ledger:
                continue  # Bucket mismatch, skip to avoid errors
            
            # Apply safe transitions only
            safe_transitions = {
                ("NEEDS_VERIFICATION", "HIGHLY_LIKELY"),
                ("NEEDS_VERIFICATION", "VERIFIED"),
                ("NEEDS_VERIFICATION", "FILTERED_OUT"),
                ("HIGHLY_LIKELY", "VERIFIED"),
                ("HIGHLY_LIKELY", "NEEDS_VERIFICATION"),
                ("HIGHLY_LIKELY", "FILTERED_OUT"),
                ("VERIFIED", "FILTERED_OUT"),  # If complete mismatch detected
                ("FILTERED_OUT", "NEEDS_VERIFICATION"),
            }
            
            if (current_in_ledger, recommended_bucket) in safe_transitions:
                ledger.loc[mask, "bucket"] = recommended_bucket
                ledger.loc[mask, "track"] = recommended_bucket
                ledger.loc[mask, "filter_reason"] = f"AI Adj: {reason[:50]}" if reason else ""
                
                # Update include_in_tables based on new bucket
                if recommended_bucket == "FILTERED_OUT":
                    ledger.loc[mask, "include_in_tables"] = False
                elif recommended_bucket in ("VERIFIED", "HIGHLY_LIKELY", "NEEDS_VERIFICATION"):
                    ledger.loc[mask, "include_in_tables"] = True
                
                applied_count += 1
    
    return ledger, applied_count
