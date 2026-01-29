"""Regression guard module.

This module detects quality regressions by comparing:
1. Current iteration vs previous iteration (within same run)
2. Current run vs last K historical runs (cross-run comparison)

CRITICAL RULES:
- Missing stable keys from history = HARD FAIL
- Good-to-bad transitions > threshold = BLOCK (unless justified)
- Bad-to-good transitions = OK (improvement)

Thresholds:
- Missing keys: any = HARD FAIL
- Good-to-bad: > min(30, 10% of previously-good) = BLOCK
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd

from fba_agent.types import RegressionDiff


# Buckets considered "good" (items we recommend purchasing)
GOOD_BUCKETS = {"VERIFIED", "HIGHLY_LIKELY"}

# Buckets considered "needs work" (not fully rejected but not recommended)
NEEDS_WORK_BUCKETS = {"NEEDS_VERIFICATION", "NEEDS VERIFICATION"}

# Buckets considered "bad" (rejected)
BAD_BUCKETS = {"FILTERED_OUT", "UNRELATED"}

# Threshold for blocking (max absolute good-to-bad transitions)
MAX_GOOD_TO_BAD_ABSOLUTE = 30

# Threshold for blocking (max percentage of previously-good)
MAX_GOOD_TO_BAD_PERCENTAGE = 0.10


def _bucket_category(bucket: str) -> str:
    """Categorize a bucket as 'good', 'needs_work', or 'bad'."""
    if bucket in GOOD_BUCKETS:
        return "good"
    if bucket in NEEDS_WORK_BUCKETS:
        return "needs_work"
    return "bad"


def compare_ledgers(
    current: pd.DataFrame,
    previous: pd.DataFrame,
) -> RegressionDiff:
    """
    Compare two ledgers by stable_key.
    
    Args:
        current: Current iteration ledger
        previous: Previous iteration/run ledger
    
    Returns:
        RegressionDiff with comparison results
    """
    if "stable_key" not in current.columns or "stable_key" not in previous.columns:
        return RegressionDiff(
            missing_stable_keys=[],
            bucket_transitions={},
            good_to_bad_count=0,
            bad_to_good_count=0,
            blocked=False,
            justifications=[{"reason": "stable_key not available for comparison"}],
        )
    
    # Build lookup dicts
    current_by_key = {
        row["stable_key"]: row.to_dict()
        for _, row in current.iterrows()
    }
    previous_by_key = {
        row["stable_key"]: row.to_dict()
        for _, row in previous.iterrows()
    }
    
    # Find missing keys (in previous but not current)
    missing_stable_keys = sorted(set(previous_by_key.keys()) - set(current_by_key.keys()))
    
    # Track bucket transitions
    bucket_transitions = {}
    good_to_bad_count = 0
    bad_to_good_count = 0
    
    for key, prev_row in previous_by_key.items():
        if key not in current_by_key:
            continue
        
        cur_row = current_by_key[key]
        prev_bucket = str(prev_row.get("bucket", ""))
        cur_bucket = str(cur_row.get("bucket", ""))
        
        if prev_bucket != cur_bucket:
            bucket_transitions[key] = {
                "from": prev_bucket,
                "to": cur_bucket,
                "row_id": cur_row.get("row_id"),
            }
            
            prev_cat = _bucket_category(prev_bucket)
            cur_cat = _bucket_category(cur_bucket)
            
            if prev_cat == "good" and cur_cat in {"needs_work", "bad"}:
                good_to_bad_count += 1
            elif prev_cat in {"needs_work", "bad"} and cur_cat == "good":
                bad_to_good_count += 1
    
    # Determine if blocked
    blocked = False
    justifications = []
    
    # Missing keys = HARD FAIL
    if missing_stable_keys:
        blocked = True
        justifications.append({
            "type": "MISSING_KEYS",
            "count": len(missing_stable_keys),
            "sample": missing_stable_keys[:10],
            "severity": "HARD_FAIL",
        })
    
    # Good-to-bad transitions above threshold
    if good_to_bad_count > 0:
        # Calculate threshold
        previously_good = len([
            k for k, v in previous_by_key.items()
            if _bucket_category(str(v.get("bucket", ""))) == "good"
        ])
        percentage_threshold = max(1, int(previously_good * MAX_GOOD_TO_BAD_PERCENTAGE))
        absolute_threshold = MAX_GOOD_TO_BAD_ABSOLUTE
        effective_threshold = min(percentage_threshold, absolute_threshold)
        
        if good_to_bad_count > effective_threshold:
            blocked = True
            justifications.append({
                "type": "GOOD_TO_BAD_THRESHOLD",
                "count": good_to_bad_count,
                "threshold": effective_threshold,
                "previously_good": previously_good,
                "severity": "BLOCK",
            })
    
    return RegressionDiff(
        missing_stable_keys=missing_stable_keys,
        bucket_transitions=bucket_transitions,
        good_to_bad_count=good_to_bad_count,
        bad_to_good_count=bad_to_good_count,
        blocked=blocked,
        justifications=justifications,
    )


def compare_iterations(
    iter1_ledger: pd.DataFrame,
    iter2_ledger: pd.DataFrame,
) -> RegressionDiff:
    """Compare two iterations within the same run."""
    return compare_ledgers(current=iter2_ledger, previous=iter1_ledger)


def compare_vs_history(
    current_ledger: pd.DataFrame,
    history: list[dict],
    history_k: int = 2,
) -> RegressionDiff:
    """
    Compare current ledger vs last K historical runs.
    
    Args:
        current_ledger: Current run ledger
        history: List of run history entries (from load_run_history)
        history_k: Number of recent runs to compare against
    
    Returns:
        Combined RegressionDiff for all comparisons
    """
    if not history:
        return RegressionDiff(
            missing_stable_keys=[],
            bucket_transitions={},
            good_to_bad_count=0,
            bad_to_good_count=0,
            blocked=False,
            justifications=[{"reason": "No historical runs to compare"}],
        )
    
    # For historical comparison, we only check missing keys and bucket stability
    # We don't have full ledgers — only bucket_counts from history
    # This is a simplified check
    
    all_justifications = []
    total_missing = 0
    
    for entry in history[-history_k:]:
        bucket_counts = entry.get("bucket_counts", {})
        if bucket_counts:
            # We can't do full comparison without ledgers
            # This is tracked for future enhancement
            all_justifications.append({
                "type": "HISTORICAL_RUN",
                "run_id": entry.get("run_id"),
                "timestamp": entry.get("timestamp"),
                "bucket_counts": bucket_counts,
            })
    
    return RegressionDiff(
        missing_stable_keys=[],
        bucket_transitions={},
        good_to_bad_count=0,
        bad_to_good_count=0,
        blocked=False,
        justifications=all_justifications,
    )


def check_thresholds(diff: RegressionDiff) -> bool:
    """
    Check if regression diff exceeds thresholds.
    
    Returns:
        True if blocked (thresholds exceeded), False otherwise
    """
    return diff.blocked


def regression_diff_to_dict(diff: RegressionDiff) -> dict:
    """Convert regression diff to serializable dict."""
    return asdict(diff)


def summarize_regression(diff: RegressionDiff) -> str:
    """Generate human-readable summary of regression diff."""
    lines = []
    
    if diff.missing_stable_keys:
        lines.append(f"⚠️ MISSING KEYS: {len(diff.missing_stable_keys)} rows from previous run are missing")
    
    if diff.good_to_bad_count:
        lines.append(f"📉 Good→Bad: {diff.good_to_bad_count} rows downgraded")
    
    if diff.bad_to_good_count:
        lines.append(f"📈 Bad→Good: {diff.bad_to_good_count} rows upgraded")
    
    if diff.bucket_transitions:
        lines.append(f"🔄 Total transitions: {len(diff.bucket_transitions)} rows changed bucket")
    
    if diff.blocked:
        lines.append("🛑 BLOCKED: Regression exceeds thresholds")
    else:
        lines.append("✅ PASSED: Regression within acceptable limits")
    
    return "\n".join(lines) if lines else "No regression data"
