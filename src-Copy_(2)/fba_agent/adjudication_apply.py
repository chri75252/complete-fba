"""Adjudication Application Module.

Apply comprehensive adjudication recommendations to the ledger DataFrame.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def apply_adjudication_recategorizations(
    ledger: "pd.DataFrame",
    recategorizations: list[dict],
) -> tuple["pd.DataFrame", int]:
    """
    Apply comprehensive adjudication recommendations to ledger.
    
    This function updates the DataFrame based on AI's comprehensive
    review of the full MD report.
    
    Args:
        ledger: Current DataFrame
        recategorizations: List of dicts with:
            - row_id: int
            - from_bucket: str (current bucket)
            - to_bucket: str (target bucket)
            - reason: str
            - confidence: int (optional)
    
    Returns:
        (updated_ledger, count_applied)
    """
    applied = 0
    
    for recat in recategorizations:
        row_id = recat.get("row_id")
        new_bucket = recat.get("to_bucket")
        reason = recat.get("reason", "Comprehensive adjudication recommendation")
        
        if row_id is None or new_bucket is None:
            continue
        
        # Find row in ledger
        mask = ledger["row_id"] == row_id
        if not mask.any():
            print(f"Warning: Row {row_id} not found in ledger (may have been pre-filtered)")
            continue
        
        # Extract track from bucket if format is "CATEGORY - STATUS"
        # e.g., "VERIFIED - RECOMMENDED" → track="VERIFIED"
        if " - " in new_bucket:
            track = new_bucket.split(" - ")[0]
        else:
            track = new_bucket
        
        # Update bucket and track
        ledger.loc[mask, "bucket"] = new_bucket
        ledger.loc[mask, "track"] = track
        
        # Update filter reason
        ledger.loc[mask, "filter_reason"] = reason
        
        # Update confidence if provided
        if "confidence" in recat:
            ledger.loc[mask, "confidence"] = recat["confidence"]
        
        # Ensure included in tables if promoted to good bucket
        if track in ["VERIFIED", "HIGHLY_LIKELY", "NEEDS_VERIFICATION"]:
            ledger.loc[mask, "include_in_tables"] = True
        elif track == "FILTERED_OUT":
            ledger.loc[mask, "include_in_tables"] = False
        
        applied += 1
    
    return ledger, applied


def log_adjudication_summary(adjudication_result: dict) -> None:
    """
    Print a summary of comprehensive adjudication results.
    
    Args:
        adjudication_result: Dict from run_comprehensive_adjudication
    """
    print("\n" + "="*70)
    print("COMPREHENSIVE ADJUDICATION SUMMARY")
    print("="*70)
    
    # Reconciliation
    recon = adjudication_result.get("reconciliation", {})
    print(f"\nEntries Reviewed:")
    print(f"  VERIFIED:      {recon.get('verified_reviewed', 0)}")
    print(f"  HIGHLY_LIKELY: {recon.get('highly_likely_reviewed', 0)}")
    print(f"  NEEDS_VER:     {recon.get('needs_ver_reviewed', 0)}")
    print(f"  AUDITED_OUT:   {recon.get('audited_out_reviewed', 0)}")
    
    # Errors found
    errors = adjudication_result.get("errors_found", [])
    print(f"\nErrors Detected: {len(errors)}")
    
    # Group by severity
    high = [e for e in errors if e.get("severity") == "high"]
    medium = [e for e in errors if e.get("severity") == "medium"]
    low = [e for e in errors if e.get("severity") == "low"]
    
    if high:
        print(f"  - High severity:   {len(high)}")
    if medium:
        print(f"  - Medium severity: {len(medium)}")
    if low:
        print(f"  - Low severity:    {len(low)}")
    
    # Recategorizations
    recats = adjudication_result.get("recategorizations", [])
    print(f"\nRecategorizations Recommended: {len(recats)}")
    
    # Root causes
    root_causes = adjudication_result.get("root_causes", {})
    if root_causes:
        print(f"\nRoot Cause Analysis:")
        for cause_type, details in root_causes.items():
            count = details.get("count", 0)
            print(f"  - {cause_type}: {count} occurrences")
    
    # Critique recommendation
    should_critique = adjudication_result.get("should_run_critique", False)
    critique_reason = adjudication_result.get("critique_reasoning", "")
    print(f"\nCritique Recommendation: {'YES' if should_critique else 'NO'}")
    if critique_reason:
        print(f"  Reason: {critique_reason}")
    
    # Overall assessment
    assessment = adjudication_result.get("overall_assessment", "")
    if assessment:
        print(f"\nOverall Assessment:")
        # Wrap long text
        for line in assessment.split("\n"):
            if len(line) > 68:
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= 68:
                        current_line += (" " if current_line else "") + word
                    else:
                        print(f"  {current_line}")
                        current_line = word
                if current_line:
                    print(f"  {current_line}")
            else:
                print(f"  {line}")
    
    print("="*70 + "\n")
