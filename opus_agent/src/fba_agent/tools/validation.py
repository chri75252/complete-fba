"""
Validation Tools for FBA Agent.

Implements validation gates to ensure output quality and coverage.
"""

import pandas as pd
from typing import List, Set
from ..models.schemas import RowDecisionRecord, ValidationResult, Bucket


def validate_ledger(
    records: List[RowDecisionRecord], 
    original_df: pd.DataFrame
) -> List[ValidationResult]:
    """
    Run all validation gates on the coverage ledger.
    
    Args:
        records: List of decision records
        original_df: Original input DataFrame
        
    Returns:
        List of ValidationResult for each gate
    """
    results = []
    
    # Gate 1: Coverage
    results.append(validate_coverage(records, original_df))
    
    # Gate 2: Profit
    results.append(validate_profit(records))
    
    # Gate 3: Trap checks
    results.append(validate_trap_consistency(records))
    
    # Gate 4: Distribution sanity
    results.append(validate_distribution(records))
    
    return results


def validate_coverage(
    records: List[RowDecisionRecord], 
    original_df: pd.DataFrame
) -> ValidationResult:
    """
    Validate that every RowID from original data appears exactly once.
    
    This is a HARD FAIL gate - no report generated if this fails.
    
    Args:
        records: List of decision records
        original_df: Original input DataFrame
        
    Returns:
        ValidationResult
    """
    expected_rows: Set[int] = set(original_df['RowID'].astype(int).tolist())
    ledger_rows: Set[int] = set(r.row_id for r in records)
    
    missing = expected_rows - ledger_rows
    extra = ledger_rows - expected_rows
    
    # Check for duplicates
    row_ids = [r.row_id for r in records]
    duplicates = [rid for rid in row_ids if row_ids.count(rid) > 1]
    duplicates = list(set(duplicates))
    
    if missing or duplicates:
        error_parts = []
        if missing:
            error_parts.append(f"Missing RowIDs: {sorted(list(missing))[:10]}...")
        if duplicates:
            error_parts.append(f"Duplicate RowIDs: {duplicates[:10]}")
        
        return ValidationResult(
            passed=False,
            gate_name="coverage",
            error="; ".join(error_parts),
            violation_rows=list(missing)[:20] + duplicates[:20]
        )
    
    return ValidationResult(
        passed=True,
        gate_name="coverage",
        error="",
        warnings=[f"Extra rows in ledger: {list(extra)[:5]}"] if extra else []
    )


def validate_profit(records: List[RowDecisionRecord]) -> ValidationResult:
    """
    Validate that no positive bucket contains items with non-positive profit.
    
    This is a HARD FAIL gate.
    
    Args:
        records: List of decision records
        
    Returns:
        ValidationResult
    """
    positive_buckets = {Bucket.VERIFIED.value, Bucket.HIGHLY_LIKELY.value, Bucket.NEEDS_VERIFICATION.value}
    
    violations = [
        r.row_id for r in records 
        if r.bucket in positive_buckets and r.adjusted_profit <= 0
    ]
    
    if violations:
        return ValidationResult(
            passed=False,
            gate_name="profit",
            error=f"{len(violations)} rows in positive buckets with non-positive profit",
            violation_rows=violations[:20]
        )
    
    return ValidationResult(
        passed=True,
        gate_name="profit",
        error=""
    )


def validate_trap_consistency(records: List[RowDecisionRecord]) -> ValidationResult:
    """
    Validate that traps were applied consistently.
    
    This is a SOFT FAIL gate - generates warnings but doesn't block report.
    
    Args:
        records: List of decision records
        
    Returns:
        ValidationResult
    """
    warnings = []
    
    # Check for dimension patterns that may have caused incorrect RSU
    for r in records:
        if r.rsu > 10:  # Suspicious RSU
            # Check if dimension trap should have applied
            has_dim_trap = any(t.trap_type == "dimension_trap" for t in r.trap_detections)
            if not has_dim_trap:
                warnings.append(f"RowID {r.row_id}: RSU={r.rsu} without dimension trap detection")
    
    return ValidationResult(
        passed=True,  # Soft fail
        gate_name="trap_consistency",
        error="",
        warnings=warnings[:10]
    )


def validate_distribution(records: List[RowDecisionRecord]) -> ValidationResult:
    """
    Validate that bucket distribution is sane.
    
    This is a SOFT FAIL gate - generates warnings.
    
    Args:
        records: List of decision records
        
    Returns:
        ValidationResult
    """
    from collections import Counter
    
    warnings = []
    bucket_counts = Counter(r.bucket for r in records)
    total = len(records)
    
    # Check for suspicious distributions
    verified_pct = bucket_counts.get(Bucket.VERIFIED.value, 0) / total * 100 if total > 0 else 0
    needs_ver_pct = bucket_counts.get(Bucket.NEEDS_VERIFICATION.value, 0) / total * 100 if total > 0 else 0
    
    if verified_pct > 50:
        warnings.append(f"Unusually high VERIFIED rate: {verified_pct:.1f}%")
    
    if needs_ver_pct > 40:
        warnings.append(f"High NEEDS_VERIFICATION rate: {needs_ver_pct:.1f}% - may indicate weak filtering")
    
    return ValidationResult(
        passed=True,
        gate_name="distribution",
        error="",
        warnings=warnings
    )


def check_all_gates(results: List[ValidationResult]) -> bool:
    """
    Check if all validation gates passed.
    
    Args:
        results: List of validation results
        
    Returns:
        True if all gates passed
    """
    return all(r.passed for r in results)


def get_gate_summary(results: List[ValidationResult]) -> str:
    """
    Get a summary string of all gate results.
    
    Args:
        results: List of validation results
        
    Returns:
        Summary string
    """
    lines = []
    for r in results:
        status = "✅ PASSED" if r.passed else "❌ FAILED"
        lines.append(f"  {r.gate_name}: {status}")
        if r.error:
            lines.append(f"    Error: {r.error}")
        for w in r.warnings[:3]:
            lines.append(f"    Warning: {w}")
    
    return "\n".join(lines)
