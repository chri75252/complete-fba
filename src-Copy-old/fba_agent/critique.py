"""AI Report Critique module.

This module handles AI-assisted critique of the overall report.
IMPORTANT: Critique provides BOUNDED suggestions only — no unbounded rewrites.

There are TWO DISTINCT comparison types in the agent workflow:

1. AI CRITIQUE (this module) - Compares CURRENT REPORT vs LAST SAVED REPORT
   - Purpose: Find discrepancies, identify regressions from previous reliable runs
   - Scope: All sections (VERIFIED, HIGHLY_LIKELY, NEEDS_VERIFICATION)
   - Data: Full ledger comparison (not just bucket counts)

2. ITERATION REGRESSION CHECK (regression.py) - Compares ITERATION 2 vs ITERATION 1
   - Purpose: Ensure config changes didn't make CURRENT RUN worse
   - Scope: Within-run comparison only
   - Data: Full ledger comparison

Critique reviews:
- Bucket distribution (are counts reasonable?)
- Validation results (any gate failures?)
- Contradictions (items with conflicting flags)
- EAN match integrity (matching EANs in wrong buckets?)
- Past report comparison (what changed from last saved report?)
- Sample rows (representative of each bucket - ALL rows, not just 5)

Critique outputs:
- high_severity_issues: Problems requiring attention
- proposed_changes: Bounded adjustments (add shield token, etc.)
- overall_assessment: Summary text
- recommended_action: "finalize", "apply_and_rerun", "block"
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from fba_agent.types import CritiqueResult

if TYPE_CHECKING:
    from fba_agent.providers import BaseProvider


# Critique JSON schema for strict output
CRITIQUE_SCHEMA = {
    "type": "object",
    "properties": {
        "high_severity_issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "issue_id": {"type": "string"},
                    "description": {"type": "string"},
                    "affected_rows_count": {"type": "integer"},
                    "suggested_resolution": {"type": "string"},
                },
            },
        },
        "proposed_changes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "change_type": {"type": "string"},
                    "target": {"type": "string"},
                    "value": {"type": "string"},
                    "safe_to_apply": {"type": "boolean"},
                },
            },
        },
        "overall_assessment": {"type": "string"},
        "recommended_action": {"type": "string", "enum": ["finalize", "apply_and_rerun", "block"]},
    },
    "required": ["high_severity_issues", "proposed_changes", "overall_assessment", "recommended_action"],
}


# Allowed change types (bounded adjustments only)
ALLOWED_CHANGE_TYPES = {
    "add_shield_token",      # Add to dimension_shield_keywords or spec_x_shield_keywords
    "add_pack_keyword",      # Add to explicit_units
    "add_brand_alias",       # Add brand alias mapping
    "adjust_threshold",      # Adjust title_match_threshold (+/- 0.05 max)
}


def _format_comprehensive_adj_for_prompt(findings: dict) -> dict:
    """
    Format comprehensive adjudication findings for the critique prompt.
    
    This creates a token-efficient summary that critique can review.
    """
    if not findings or "error" in findings:
        return {"status": "not_available", "reason": findings.get("error", "No findings available")}
    
    summary = {
        "errors_found_count": len(findings.get("errors_found", [])),
        "recategorizations_count": len(findings.get("recategorizations", [])),
        "should_run_critique": findings.get("should_run_critique", False),
        "overall_assessment": findings.get("overall_assessment", "")[:500],  # Truncate for tokens
    }
    
    # Include root causes if present (key insight for critique)
    root_causes = findings.get("root_causes", {})
    if root_causes:
        summary["root_causes_summary"] = {
            k: {"count": v.get("count", 0), "proposed_fix": v.get("proposed_fix", "")[:100]}
            for k, v in list(root_causes.items())[:5]  # Limit to 5 root causes
        }
    
    # Include sample errors (not all to save tokens)
    errors = findings.get("errors_found", [])
    if errors:
        summary["sample_errors"] = errors[:5]  # First 5 errors as sample
    
    # Include sample recategorizations
    recats = findings.get("recategorizations", [])
    if recats:
        summary["sample_recategorizations"] = recats[:5]  # First 5 recategorizations
    
    # Config recommendations (important for critique to review)
    config_recs = findings.get("config_recommendations", [])
    if config_recs:
        summary["config_recommendations"] = config_recs[:3]  # First 3 recommendations
    
    return summary


def detect_contradictions(ledger: pd.DataFrame) -> list[dict]:
    """
    Detect rows with contradictory flags that indicate logic errors.
    This runs on the FULL ledger, not just samples.
    
    CRITICAL: This function catches issues like the include_in_tables bug
    where items were correctly identified as VERIFIED but silently excluded.
    """
    issues = []
    
    # Issue 1: Items categorized as VERIFIED/HIGHLY_LIKELY but excluded from tables
    if "track" in ledger.columns and "include_in_tables" in ledger.columns:
        for track_value in ["VERIFIED", "HIGHLY_LIKELY", "NEEDS_VERIFICATION"]:
            excluded = ledger[
                (ledger["track"] == track_value) & 
                (ledger["include_in_tables"] == False)
            ]
            if len(excluded) > 0:
                sample_titles = excluded["supplier_title"].head(5).tolist() if "supplier_title" in excluded.columns else []
                issues.append({
                    "type": "EXCLUDED_FROM_REPORT",
                    "track": track_value,
                    "count": len(excluded),
                    "severity": "CRITICAL",
                    "sample_titles": sample_titles,
                    "description": f"{len(excluded)} {track_value} items have include_in_tables=False - SHOULD BE VISIBLE"
                })
    
    # Issue 2: Rows with matching EANs that are NOT in VERIFIED
    if "supplier_ean" in ledger.columns and "amazon_ean" in ledger.columns:
        # Find rows where EANs match
        matching_eans = ledger[
            (ledger["supplier_ean"].notna()) &
            (ledger["amazon_ean"].notna()) &
            (ledger["supplier_ean"].astype(str) != "") &
            (ledger["amazon_ean"].astype(str) != "") &
            (ledger["supplier_ean"].astype(str) == ledger["amazon_ean"].astype(str))
        ]
        
        for bucket in ["HIGHLY_LIKELY", "FILTERED_OUT", "NEEDS_VERIFICATION"]:
            wrong_bucket = matching_eans[matching_eans["bucket"] == bucket] if "bucket" in matching_eans.columns else pd.DataFrame()
            if len(wrong_bucket) > 0:
                sample_eans = wrong_bucket["supplier_ean"].head(5).tolist()
                issues.append({
                    "type": "EAN_MATCH_WRONG_BUCKET",
                    "bucket": bucket,
                    "count": len(wrong_bucket),
                    "severity": "HIGH" if bucket == "FILTERED_OUT" else "MEDIUM",
                    "sample_eans": sample_eans,
                    "description": f"{len(wrong_bucket)} rows have matching EANs but are in {bucket} instead of VERIFIED"
                })
    
    return issues


def compute_ean_statistics(ledger: pd.DataFrame) -> dict:
    """
    Compute statistics about EAN matches across buckets.
    This helps identify data quality issues.
    """
    stats = {
        "total_rows": len(ledger),
        "rows_with_supplier_ean": 0,
        "rows_with_amazon_ean": 0,
        "rows_with_both_eans": 0,
        "matching_ean_count": 0,
        "matching_eans_by_bucket": {},
    }
    
    if "supplier_ean" in ledger.columns:
        stats["rows_with_supplier_ean"] = len(ledger[ledger["supplier_ean"].notna() & (ledger["supplier_ean"].astype(str) != "")])
    
    if "amazon_ean" in ledger.columns:
        stats["rows_with_amazon_ean"] = len(ledger[ledger["amazon_ean"].notna() & (ledger["amazon_ean"].astype(str) != "")])
    
    if "supplier_ean" in ledger.columns and "amazon_ean" in ledger.columns:
        both_eans = ledger[
            (ledger["supplier_ean"].notna()) &
            (ledger["amazon_ean"].notna()) &
            (ledger["supplier_ean"].astype(str) != "") &
            (ledger["amazon_ean"].astype(str) != "")
        ]
        stats["rows_with_both_eans"] = len(both_eans)
        
        matching = both_eans[both_eans["supplier_ean"].astype(str) == both_eans["amazon_ean"].astype(str)]
        stats["matching_ean_count"] = len(matching)
        
        if "bucket" in matching.columns:
            stats["matching_eans_by_bucket"] = matching["bucket"].value_counts().to_dict()
    
    return stats


def compare_with_past_ledger(
    current: pd.DataFrame,
    past_path: Path | str | None,
) -> dict:
    """
    Load and compare current ledger against 1 past report.
    This is for AI critique to find discrepancies from previous reliable runs.
    
    NOTE: This is DIFFERENT from iteration regression check!
    - This compares against LAST SAVED REPORT (from memory)
    - Iteration regression compares ITER2 vs ITER1 within same run
    
    Args:
        current: Current run ledger
        past_path: Path to past coverage_ledger.csv
    
    Returns:
        Comparison dict with discrepancies
    """
    if past_path is None:
        return {"available": False, "reason": "No past ledger path provided"}
    
    past_path = Path(past_path)
    if not past_path.exists():
        return {"available": False, "reason": f"Past ledger not found: {past_path}"}
    
    try:
        past = pd.read_csv(past_path)
    except Exception as e:
        return {"available": False, "reason": f"Failed to load past ledger: {e}"}
    
    comparison = {
        "available": True,
        "past_path": str(past_path),
        "past_total_rows": len(past),
        "current_total_rows": len(current),
    }
    
    # Compare bucket counts
    if "bucket" in past.columns and "bucket" in current.columns:
        past_counts = past["bucket"].value_counts().to_dict()
        current_counts = current["bucket"].value_counts().to_dict()
        
        comparison["past_bucket_counts"] = past_counts
        comparison["current_bucket_counts"] = current_counts
        
        # Calculate differences
        all_buckets = set(past_counts.keys()) | set(current_counts.keys())
        bucket_differences = {}
        for bucket in all_buckets:
            past_count = past_counts.get(bucket, 0)
            current_count = current_counts.get(bucket, 0)
            diff = current_count - past_count
            if diff != 0:
                bucket_differences[bucket] = {
                    "past": past_count,
                    "current": current_count,
                    "difference": diff,
                    "change_pct": round((diff / max(past_count, 1)) * 100, 1),
                }
        
        comparison["bucket_differences"] = bucket_differences
    
    # Compare EAN matches
    if "supplier_ean" in past.columns and "supplier_ean" in current.columns:
        # Find EANs that were VERIFIED in past but not in current
        past_verified_eans = set()
        current_verified_eans = set()
        
        if "bucket" in past.columns:
            past_verified = past[past["bucket"] == "VERIFIED"]
            past_verified_eans = set(past_verified["supplier_ean"].dropna().astype(str))
        
        if "bucket" in current.columns:
            current_verified = current[current["bucket"] == "VERIFIED"]
            current_verified_eans = set(current_verified["supplier_ean"].dropna().astype(str))
        
        missing_from_verified = past_verified_eans - current_verified_eans
        new_in_verified = current_verified_eans - past_verified_eans
        
        comparison["verified_ean_comparison"] = {
            "past_verified_count": len(past_verified_eans),
            "current_verified_count": len(current_verified_eans),
            "missing_from_verified": list(missing_from_verified)[:20],
            "new_in_verified": list(new_in_verified)[:20],
        }
        
        # Same for HIGHLY_LIKELY
        past_hl_eans = set()
        current_hl_eans = set()
        
        if "bucket" in past.columns:
            past_hl = past[past["bucket"] == "HIGHLY_LIKELY"]
            past_hl_eans = set(past_hl["supplier_ean"].dropna().astype(str))
        
        if "bucket" in current.columns:
            current_hl = current[current["bucket"] == "HIGHLY_LIKELY"]
            current_hl_eans = set(current_hl["supplier_ean"].dropna().astype(str))
        
        missing_from_hl = past_hl_eans - current_hl_eans
        new_in_hl = current_hl_eans - past_hl_eans
        
        comparison["highly_likely_ean_comparison"] = {
            "past_hl_count": len(past_hl_eans),
            "current_hl_count": len(current_hl_eans),
            "missing_from_hl": list(missing_from_hl)[:20],
            "new_in_hl": list(new_in_hl)[:20],
        }
        
        # Flag discrepancies
        comparison["discrepancy_detected"] = len(missing_from_verified) > 0 or len(missing_from_hl) > 5
    
    return comparison


def build_critique_inputs(
    summary: dict,
    ledger: pd.DataFrame,
    evidence: list[dict],
    anomaly_summary: dict | None = None,
    regression_diff: dict | None = None,
    past_ledger_path: Path | str | None = None,
    comprehensive_adj_findings: dict | None = None,  # NEW: Comprehensive adjudication results
) -> dict:
    """
    Build inputs for report critique.
    
    CRITICAL CHANGE: No longer limited to 5 samples per bucket.
    For VERIFIED and HIGHLY_LIKELY, we include ALL rows.
    For FILTERED_OUT, we include a statistical summary.
    
    Args:
        summary: Run summary dict
        ledger: Analysis ledger
        evidence: Evidence list
        anomaly_summary: Anomaly detection results
        regression_diff: Regression comparison results
        past_ledger_path: Path to previous run's coverage_ledger.csv for comparison
    
    Returns:
        Dict of critique inputs
    """
    inputs = {
        "summary": {
            "input_file": summary.get("input_file", ""),
            "supplier": summary.get("supplier", ""),
            "total_rows": len(ledger),
            "validation_passed": summary.get("validation", {}).get("passed", False),
            "validation_errors": summary.get("validation", {}).get("errors", []),
        },
        "bucket_counts": {},
        "all_verified": [],
        "all_highly_likely": [],
        "sample_needs_verification": [],
        "filtered_summary": {},
        "contradictions": [],
        "ean_statistics": {},
        "past_comparison": {},
        "anomalies": anomaly_summary or {},
        "regression_diff": regression_diff or {},
        "comprehensive_adj_findings": comprehensive_adj_findings or {},  # NEW: Store comprehensive adj results
    }
    
    # Calculate bucket counts
    if "bucket" in ledger.columns:
        inputs["bucket_counts"] = ledger["bucket"].value_counts().to_dict()
    
    # CRITICAL: Include ALL VERIFIED rows (not just 5!)
    verified_rows = ledger[ledger["bucket"] == "VERIFIED"] if "bucket" in ledger.columns else pd.DataFrame()
    if len(verified_rows) > 0:
        inputs["all_verified"] = [
            {
                "row_id": int(row.get("row_id", 0)),
                "supplier_title": str(row.get("supplier_title", ""))[:80],
                "amazon_title": str(row.get("amazon_title", ""))[:80],
                "supplier_ean": str(row.get("supplier_ean", "")),
                "amazon_ean": str(row.get("amazon_ean", "")),
                "confidence": int(row.get("confidence", 0)),
                "adjusted_profit": float(row.get("adjusted_profit", 0)),
                "pack_verdict": str(row.get("pack_verdict", "")),
                "include_in_tables": bool(row.get("include_in_tables", True)),
            }
            for _, row in verified_rows.iterrows()
        ]
    
    # CRITICAL: Include ALL HIGHLY_LIKELY rows (not just 5!)
    hl_rows = ledger[ledger["bucket"] == "HIGHLY_LIKELY"] if "bucket" in ledger.columns else pd.DataFrame()
    if len(hl_rows) > 0:
        inputs["all_highly_likely"] = [
            {
                "row_id": int(row.get("row_id", 0)),
                "supplier_title": str(row.get("supplier_title", ""))[:80],
                "amazon_title": str(row.get("amazon_title", ""))[:80],
                "supplier_ean": str(row.get("supplier_ean", "")),
                "amazon_ean": str(row.get("amazon_ean", "")),
                "confidence": int(row.get("confidence", 0)),
                "adjusted_profit": float(row.get("adjusted_profit", 0)),
                "key_match_evidence": str(row.get("key_match_evidence", ""))[:100],
            }
            for _, row in hl_rows.iterrows()
        ]
    
    # Include sample of NEEDS_VERIFICATION (up to 20)
    nv_rows = ledger[ledger["bucket"] == "NEEDS_VERIFICATION"] if "bucket" in ledger.columns else pd.DataFrame()
    if len(nv_rows) > 0:
        inputs["sample_needs_verification"] = [
            {
                "row_id": int(row.get("row_id", 0)),
                "supplier_title": str(row.get("supplier_title", ""))[:60],
                "amazon_title": str(row.get("amazon_title", ""))[:60],
                "confidence": int(row.get("confidence", 0)),
                "filter_reason": str(row.get("filter_reason", "")),
            }
            for _, row in nv_rows.head(20).iterrows()
        ]
    
    # Filtered summary (statistical, not individual rows)
    filtered_rows = ledger[ledger["bucket"] == "FILTERED_OUT"] if "bucket" in ledger.columns else pd.DataFrame()
    if len(filtered_rows) > 0:
        matching_ean_filtered = 0
        if "supplier_ean" in filtered_rows.columns and "amazon_ean" in filtered_rows.columns:
            matching_ean_filtered = len(filtered_rows[
                (filtered_rows["supplier_ean"].notna()) &
                (filtered_rows["amazon_ean"].notna()) &
                (filtered_rows["supplier_ean"].astype(str) == filtered_rows["amazon_ean"].astype(str))
            ])
        
        inputs["filtered_summary"] = {
            "total_count": len(filtered_rows),
            "with_matching_eans": matching_ean_filtered,
            "average_confidence": round(filtered_rows["confidence"].mean(), 1) if "confidence" in filtered_rows.columns else 0,
            "common_filter_reasons": filtered_rows["filter_reason"].value_counts().head(5).to_dict() if "filter_reason" in filtered_rows.columns else {},
        }
    
    # Detect contradictions (CRITICAL for catching bugs like include_in_tables issue)
    inputs["contradictions"] = detect_contradictions(ledger)
    
    # EAN statistics
    inputs["ean_statistics"] = compute_ean_statistics(ledger)
    
    # Compare with past report (if available)
    if past_ledger_path:
        inputs["past_comparison"] = compare_with_past_ledger(ledger, past_ledger_path)
    
    # Add top profit rows
    if "adjusted_profit" in ledger.columns:
        top_profit = ledger.nlargest(5, "adjusted_profit")
        inputs["top_profit_rows"] = [
            {
                "row_id": int(row.get("row_id", 0)),
                "bucket": str(row.get("bucket", "")),
                "adjusted_profit": float(row.get("adjusted_profit", 0)),
                "confidence": int(row.get("confidence", 0)),
            }
            for _, row in top_profit.iterrows()
        ]
    
    return inputs


def build_critique_prompt(inputs: dict) -> tuple[str, str]:
    """
    Build system and user prompts for report critique.
    
    This prompt is based on the FBA Manual Analysis Methodology Guide
    and the Financial Report Prompt Analysis v1.2.
    
    Args:
        inputs: Critique inputs from build_critique_inputs()
    
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = """You are a **Principal E-Commerce Analyst** specializing in Amazon FBA arbitrage report validation.

Your task is to perform a THOROUGH MANUAL REVIEW of this FBA analysis report and:
1. Identify HIGH-SEVERITY ISSUES that indicate systematic problems
2. Detect CONTRADICTIONS in the data (items categorized but excluded, EAN matches in wrong buckets)
3. Compare against the previous report to identify REGRESSIONS
4. Propose BOUNDED config changes that could improve accuracy
5. Recommend whether to FINALIZE, APPLY CHANGES AND RE-RUN, or BLOCK the report

## CRITICAL VALIDATION CHECKS

You MUST check for these issues:

### 1. CONTRADICTION CHECK (HIGHEST PRIORITY)
- Any item with track=VERIFIED/HIGHLY_LIKELY but include_in_tables=False is a CRITICAL BUG
- Any item with matching EANs (supplier_ean == amazon_ean) that is NOT in VERIFIED is a HIGH severity issue
- If contradictions > 0, you MUST set recommended_action to "block"

### 2. EAN MATCH INTEGRITY
- All rows with exact EAN matches MUST be in VERIFIED section (or VERIFIED-FILTERED_OUT if unprofitable)
- Matching EANs in HIGHLY_LIKELY or FILTERED_OUT indicate bugs in the categorization logic

### 3. PAST REPORT COMPARISON (if available)
- If VERIFIED count dropped significantly, investigate WHY
- If items that were VERIFIED before are now missing, flag as regression
- Compare not just counts but WHICH items changed

### 4. PACK/PROFIT VALIDATION
- VERIFIED items should have positive adjusted profit
- Items with pack mismatches should have correct RSU calculation
- Dimension patterns (cm, mm, inch) should NOT be treated as pack sizes

## ALLOWED CHANGE TYPES (you may ONLY propose these)
- add_shield_token: Add a word to dimension/spec shields
- add_pack_keyword: Add a word to pack detection keywords
- add_brand_alias: Add a brand name mapping
- adjust_threshold: Adjust a threshold by small amount

## YOU CANNOT
- Rewrite individual row decisions
- Change bucket assignments directly
- Remove validation gates
- Make unbounded changes

## RESPONSE FORMAT
Respond with JSON only. Be conservative — only propose changes with high confidence.
If ANY contradictions are detected, you MUST set recommended_action to "block" and explain the issue."""

    # Build user prompt with all data
    contradictions_json = json.dumps(inputs.get("contradictions", []), indent=2)
    ean_stats_json = json.dumps(inputs.get("ean_statistics", {}), indent=2)
    past_comparison_json = json.dumps(inputs.get("past_comparison", {}), indent=2)
    
    # Truncate large arrays for prompt
    all_verified = inputs.get("all_verified", [])
    all_hl = inputs.get("all_highly_likely", [])
    
    # If more than 50 items, show first 25 and last 5 with count
    if len(all_verified) > 30:
        verified_sample = all_verified[:25] + [{"...": f"... and {len(all_verified) - 30} more ..."}] + all_verified[-5:]
    else:
        verified_sample = all_verified
    
    if len(all_hl) > 50:
        hl_sample = all_hl[:40] + [{"...": f"... and {len(all_hl) - 50} more ..."}] + all_hl[-10:]
    else:
        hl_sample = all_hl
    
    user = f"""Review this FBA analysis report:

## Summary
- Input File: {inputs['summary']['input_file']}
- Supplier: {inputs['summary']['supplier']}
- Total Rows: {inputs['summary']['total_rows']}
- Validation Passed: {inputs['summary']['validation_passed']}
- Validation Errors: {inputs['summary']['validation_errors']}

## Bucket Distribution
{json.dumps(inputs['bucket_counts'], indent=2)}

## ⚠️ CRITICAL: CONTRADICTION CHECK (REVIEW FIRST!)
{contradictions_json}

**IF ANY CONTRADICTIONS EXIST, YOU MUST BLOCK THE REPORT.**

## EAN Statistics
{ean_stats_json}

## Past Report Comparison
{past_comparison_json}

## ALL VERIFIED Items ({len(all_verified)} total)
{json.dumps(verified_sample, indent=2)}

## ALL HIGHLY LIKELY Items ({len(all_hl)} total)
{json.dumps(hl_sample, indent=2)}

## Filtered Summary
{json.dumps(inputs.get('filtered_summary', {}), indent=2)}

## Anomaly Summary
{json.dumps(inputs.get('anomalies', {}), indent=2)}

## Regression Diff (vs previous iteration)
{json.dumps(inputs.get('regression_diff', {}), indent=2)}

## Top Profit Rows
{json.dumps(inputs.get('top_profit_rows', []), indent=2)}

## 📊 Comprehensive Adjudication Findings (from previous AI step)
{json.dumps(_format_comprehensive_adj_for_prompt(inputs.get('comprehensive_adj_findings', {})), indent=2)}

---

Provide your critique as JSON. Remember:
1. If ANY contradictions exist, set recommended_action to "block"
2. If past report shows significant regressions, investigate and report
3. Review the Comprehensive Adjudication Findings - if it found errors, factor them into your decision
4. Be thorough but conservative with proposed changes"""

    return system, user


def run_critique(
    inputs: dict,
    provider: "BaseProvider",
) -> CritiqueResult:
    """
    Run AI critique on report inputs.
    
    Args:
        inputs: Critique inputs from build_critique_inputs()
        provider: LLM provider instance
    
    Returns:
        CritiqueResult
    """
    system, user = build_critique_prompt(inputs)
    
    try:
        response = provider.chat_json(system, user, schema=CRITIQUE_SCHEMA)
        
        # Validate proposed changes (filter out disallowed types)
        valid_changes = []
        for change in response.get("proposed_changes", []):
            if change.get("change_type") in ALLOWED_CHANGE_TYPES:
                valid_changes.append(change)
        
        # CRITICAL: If contradictions were detected, force block
        contradictions = inputs.get("contradictions", [])
        if contradictions:
            critical_contradictions = [c for c in contradictions if c.get("severity") == "CRITICAL"]
            if critical_contradictions:
                # Force block if there are critical issues
                response["recommended_action"] = "block"
                if not any(i.get("issue_id") == "CONTRADICTION_DETECTED" for i in response.get("high_severity_issues", [])):
                    response["high_severity_issues"] = response.get("high_severity_issues", []) + [{
                        "issue_id": "CONTRADICTION_DETECTED",
                        "description": f"Found {len(critical_contradictions)} CRITICAL contradictions in the ledger",
                        "affected_rows_count": sum(c.get("count", 0) for c in critical_contradictions),
                        "suggested_resolution": "Fix the include_in_tables logic or EAN categorization",
                    }]
        
        return CritiqueResult(
            high_severity_issues=response.get("high_severity_issues", []),
            proposed_changes=valid_changes,
            overall_assessment=response.get("overall_assessment", ""),
            recommended_action=response.get("recommended_action", "finalize"),
        )
    except Exception as e:
        # On failure, return conservative result
        return CritiqueResult(
            high_severity_issues=[{
                "issue_id": "CRITIQUE_FAILED",
                "description": f"Critique failed: {type(e).__name__}",
                "affected_rows_count": 0,
                "suggested_resolution": "Manual review required",
            }],
            proposed_changes=[],
            overall_assessment="Critique could not be completed",
            recommended_action="block",
        )


def critique_result_to_dict(result: CritiqueResult) -> dict:
    """Convert critique result to serializable dict."""
    return asdict(result)
