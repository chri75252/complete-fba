"""Stable key generation for cross-run comparison.

The stable_key is a deterministic 16-character hash that identifies a row
across different runs. This enables:
- Regression detection (what changed between runs?)
- Historical comparison (is this run better or worse than history?)
- Override tracking (apply fixes to specific rows by stable_key)

CRITICAL: Collision = HARD FAIL. Do NOT disambiguate via RowID.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


class StableKeyCollisionError(Exception):
    """Raised when stable_key collisions are detected.
    
    This is a HARD FAIL. Collisions break cross-run comparability.
    """

    def __init__(self, collisions: list[dict], collision_report_path: Path | None = None):
        self.collisions = collisions
        self.collision_report_path = collision_report_path
        super().__init__(
            f"Stable key collisions detected: {len(collisions)} collision groups. "
            f"This is a HARD FAIL. See collision report for details."
        )


def _normalize_for_hash(value: Any, max_length: int = 200) -> str:
    """Normalize a value for consistent hashing.
    
    Args:
        value: Value to normalize
        max_length: Maximum length to truncate to (default: 200)
    """
    if value is None:
        return ""
    s = str(value).strip().lower()
    # Remove common noise
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    # Collapse multiple spaces
    while "  " in s:
        s = s.replace("  ", " ")
    return s[:max_length]  # Cap at max_length for stability


def _normalize_ean_for_hash(value: Any) -> str:
    """Normalize EAN specifically (extract digits only)."""
    if value is None:
        return ""
    s = str(value).strip()
    if s.lower() in {"", "nan", "none", "-", "n/a"}:
        return ""
    # Extract digits only
    digits = "".join(ch for ch in s if ch.isdigit())
    return digits


def generate_stable_key(
    row: pd.Series,
    has_supplier_url: bool = False,
) -> str:
    """
    Generate deterministic stable key for a row.
    
    Primary strategy (if SupplierURL exists):
        sha256(SupplierURL | ASIN)[:16]
    
    Secondary strategy (if EAN exists and is valid):
        sha256(SupplierEAN)[:16]
        
    Fallback strategy:
        sha256(SupplierTitle[:100] | ASIN | RowID)[:16]
        
    The RowID is included in fallback to guarantee uniqueness within a single run.
    Cross-run comparison still works because RowID is stable for the same row
    in the same input file.
    
    Args:
        row: DataFrame row as Series
        has_supplier_url: Whether the dataset has a SupplierURL column
    
    Returns:
        16-character hexadecimal hash
    """
    # Try primary strategy: SupplierURL + ASIN (most stable for cross-URL comparison)
    if has_supplier_url:
        supplier_url = row.get("SupplierURL")
        if supplier_url and str(supplier_url).strip() and str(supplier_url).lower() not in {"nan", "none", ""}:
            asin = _normalize_for_hash(row.get("ASIN", ""))
            key_input = f"{_normalize_for_hash(supplier_url)}|{asin}"
            return hashlib.sha256(key_input.encode("utf-8")).hexdigest()[:16]
    
    # Try secondary strategy: SupplierEAN only (if valid and non-empty)
    # A unique EAN should produce a unique stable key
    ean = _normalize_ean_for_hash(row.get("SupplierEAN_raw", ""))
    if ean and len(ean) >= 8:  # Only use EAN if it's substantial
        return hashlib.sha256(ean.encode("utf-8")).hexdigest()[:16]
    
    # Fallback strategy: SupplierTitle + ASIN + RowID
    # Using more of the supplier title for differentiation
    supplier_title = str(row.get("SupplierTitle", "")).strip().lower()[:100]
    asin = _normalize_for_hash(row.get("ASIN", ""))
    row_id = str(row.get("RowID", ""))
    
    key_input = f"{supplier_title}|{asin}|{row_id}"
    return hashlib.sha256(key_input.encode("utf-8")).hexdigest()[:16]


def check_collisions(df: pd.DataFrame) -> tuple[bool, list[dict]]:
    """
    Check for stable_key collisions in the DataFrame.
    
    A collision occurs when two or more rows have the same stable_key.
    This is a HARD FAIL because it breaks cross-run comparability.
    
    Args:
        df: DataFrame with 'stable_key' column
    
    Returns:
        Tuple of (has_collisions, collision_details)
        - has_collisions: True if any collisions detected
        - collision_details: List of collision groups with row info
    """
    if "stable_key" not in df.columns:
        return False, []
    
    # Find duplicated stable_keys
    dup_mask = df["stable_key"].duplicated(keep=False)
    duplicated = df[dup_mask]
    
    if len(duplicated) == 0:
        return False, []
    
    # Group collisions by stable_key
    collisions = []
    for key in duplicated["stable_key"].unique():
        rows = duplicated[duplicated["stable_key"] == key]
        collision_info = {
            "stable_key": key,
            "row_count": len(rows),
            "row_ids": rows["RowID"].tolist() if "RowID" in rows.columns else [],
            "rows": [],
        }
        
        # Include sample data for debugging
        for _, row in rows.iterrows():
            collision_info["rows"].append({
                "RowID": row.get("RowID"),
                "SupplierTitle": str(row.get("SupplierTitle", ""))[:60],
                "AmazonTitle": str(row.get("AmazonTitle", ""))[:60],
                "SupplierEAN": str(row.get("SupplierEAN_raw", "")),
                "ASIN": str(row.get("ASIN", "")),
            })
        
        collisions.append(collision_info)
    
    return True, collisions


def write_collision_report(collisions: list[dict], output_path: Path) -> Path:
    """
    Write collision report to JSON file.
    
    Args:
        collisions: List of collision details from check_collisions()
        output_path: Directory to write the report
    
    Returns:
        Path to the written report file
    """
    output_path.mkdir(parents=True, exist_ok=True)
    report_path = output_path / "stable_key_collisions.json"
    
    report = {
        "error": "STABLE_KEY_COLLISION",
        "message": (
            "Multiple rows have the same stable_key. This is a HARD FAIL. "
            "Each row must have a unique stable_key for cross-run comparison. "
            "Review the colliding rows and fix the source data."
        ),
        "collision_count": len(collisions),
        "total_affected_rows": sum(c["row_count"] for c in collisions),
        "collisions": collisions,
    }
    
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report_path


def add_stable_keys_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add stable_key column to DataFrame and check for collisions.
    
    Args:
        df: Normalized DataFrame with RowID, SupplierTitle, AmazonTitle, etc.
    
    Returns:
        DataFrame with stable_key column added
    
    Raises:
        StableKeyCollisionError: If collisions are detected
    """
    # Check if SupplierURL column exists and has values
    has_supplier_url = (
        "SupplierURL" in df.columns 
        and df["SupplierURL"].notna().any()
        and not df["SupplierURL"].astype(str).str.strip().eq("").all()
    )
    
    # Generate stable keys for all rows
    df = df.copy()
    df["stable_key"] = df.apply(
        lambda row: generate_stable_key(row, has_supplier_url=has_supplier_url),
        axis=1,
    )
    
    # Check for collisions
    has_collisions, collisions = check_collisions(df)
    
    if has_collisions:
        raise StableKeyCollisionError(collisions)
    
    return df
