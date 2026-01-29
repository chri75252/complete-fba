from __future__ import annotations

import pandas as pd

from fba_agent.types import ValidationResult


def validate_coverage(ledger: pd.DataFrame, original_df: pd.DataFrame) -> ValidationResult:
    """
    Validate that every RowID from original data appears exactly once in ledger.
    
    This is a HARD gate — failure blocks finalization.
    """
    expected = set(original_df["RowID"].tolist())
    got = ledger["row_id"].tolist()
    got_set = set(got)

    missing = sorted(expected - got_set)
    duplicated = sorted(ledger[ledger["row_id"].duplicated()]["row_id"].tolist())

    errors: list[str] = []
    if missing:
        errors.append(f"Missing RowIDs: {missing[:50]}{'...' if len(missing) > 50 else ''}")
    if duplicated:
        errors.append(f"Duplicate RowIDs: {duplicated[:50]}{'...' if len(duplicated) > 50 else ''}")

    return ValidationResult(passed=not errors, errors=errors)


def validate_stable_key_coverage(ledger: pd.DataFrame, original_df: pd.DataFrame) -> ValidationResult:
    """
    Validate that every stable_key from original data appears exactly once in ledger.
    
    This is a HARD gate — failure blocks finalization.
    Stable key coverage is critical for regression detection.
    """
    # Check if stable_key column exists
    if "stable_key" not in original_df.columns:
        return ValidationResult(
            passed=True,
            warnings=["stable_key column not found in original data (skipping coverage check)"],
        )
    
    if "stable_key" not in ledger.columns:
        return ValidationResult(
            passed=False,
            errors=["stable_key column missing from ledger — cannot validate coverage"],
        )
    
    expected = set(original_df["stable_key"].tolist())
    got = ledger["stable_key"].tolist()
    got_set = set(got)

    missing = sorted(expected - got_set)
    duplicated = sorted(ledger[ledger["stable_key"].duplicated()]["stable_key"].tolist())

    errors: list[str] = []
    if missing:
        errors.append(
            f"Missing stable_keys: {len(missing)} keys not in ledger "
            f"(first 10: {missing[:10]}{'...' if len(missing) > 10 else ''})"
        )
    if duplicated:
        errors.append(
            f"Duplicate stable_keys in ledger: {len(duplicated)} duplicates "
            f"(first 10: {duplicated[:10]}{'...' if len(duplicated) > 10 else ''})"
        )

    return ValidationResult(passed=not errors, errors=errors)


def validate_profit(ledger: pd.DataFrame) -> ValidationResult:
    """
    Validate that no row in positive buckets has adjusted_profit <= 0.
    
    This is a HARD gate — failure blocks finalization.
    
    Positive buckets: VERIFIED, HIGHLY_LIKELY, NEEDS_VERIFICATION
    Rows with profit <= 0 should be in FILTERED_OUT instead.
    """
    positive = {"VERIFIED", "HIGHLY_LIKELY", "NEEDS_VERIFICATION"}
    df = ledger.copy()
    df["adjusted_profit"] = pd.to_numeric(df["adjusted_profit"], errors="coerce")
    violations = df[(df["bucket"].isin(positive)) & (df["adjusted_profit"] <= 0)]
    if len(violations) == 0:
        return ValidationResult(passed=True)
    row_ids = violations["row_id"].tolist()
    return ValidationResult(
        passed=False,
        errors=[f"Profit gate failed: {len(row_ids)} rows in positive buckets with adjusted_profit <= 0"],
    )


def validate_all_gates(
    ledger: pd.DataFrame,
    original_df: pd.DataFrame,
) -> tuple[bool, list[str], list[str]]:
    """
    Run all validation gates and return combined result.
    
    Returns:
        Tuple of (all_passed, errors, warnings)
    """
    gates = [
        ("coverage", validate_coverage(ledger, original_df)),
        ("stable_key_coverage", validate_stable_key_coverage(ledger, original_df)),
        ("profit", validate_profit(ledger)),
    ]
    
    all_passed = True
    all_errors: list[str] = []
    all_warnings: list[str] = []
    
    for name, result in gates:
        if not result.passed:
            all_passed = False
            all_errors.extend([f"[{name}] {e}" for e in result.errors])
        all_warnings.extend([f"[{name}] {w}" for w in result.warnings])
    
    return all_passed, all_errors, all_warnings


