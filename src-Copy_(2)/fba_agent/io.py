from __future__ import annotations

from pathlib import Path

import pandas as pd

from fba_agent.stable_key import add_stable_keys_to_dataframe, StableKeyCollisionError
from fba_agent.text import sanitize_cell
from fba_agent.types import SchemaInfo


def load_report(input_path: Path) -> tuple[pd.DataFrame, SchemaInfo]:
    if not input_path.exists():
        raise FileNotFoundError(str(input_path))

    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(input_path)
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(input_path)
    else:
        raise ValueError(f"Unsupported input format: {input_path.suffix}")

    columns = [str(c) for c in df.columns]
    schema = SchemaInfo(
        input_path=str(input_path),
        rows=int(len(df)),
        detected_sales_column=None,
        detected_columns=columns,
        warnings=[],
    )
    return df, schema


def normalize_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    original_columns = list(df.columns)

    def find_col(candidates: list[str]) -> str | None:
        lower_to_actual = {str(c).strip().lower(): c for c in df.columns}
        for cand in candidates:
            if cand.lower() in lower_to_actual:
                return str(lower_to_actual[cand.lower()])
        return None

    row_id_col = find_col(["RowID", "row_id", "rowid"])
    supplier_title_col = find_col(["SupplierTitle", "supplier_title", "Supplier Title"])
    amazon_title_col = find_col(["AmazonTitle", "amazon_title", "Amazon Title"])
    supplier_ean_col = find_col(["EAN", "Supplier EAN", "supplier_ean"])
    amazon_ean_col = find_col(["EAN_OnPage", "Amazon EAN", "amazon_ean", "EAN OnPage"])
    asin_col = find_col(["ASIN", "asin"])
    supplier_price_col = find_col(["SupplierPrice_incVAT", "SupplierPrice", "supplier_price_incvat"])
    selling_price_col = find_col(["SellingPrice_incVAT", "SellingPrice", "selling_price_incvat"])
    net_profit_col = find_col(["NetProfit", "net_profit"])
    roi_col = find_col(["ROI", "roi"])

    sales_col = (
        find_col(["sales_numeric"])
        or find_col(["bought_in_past_month"])
        or find_col(["Sales"])
        or find_col(["sales"])
    )

    normalized = df.copy()

    if row_id_col is None:
        normalized.insert(0, "RowID", list(range(1, len(normalized) + 1)))
        row_id_col = "RowID"

    def safe_text(value: object) -> str:
        return sanitize_cell("" if value is None else str(value))

    normalized["RowID"] = pd.to_numeric(normalized[row_id_col], errors="coerce").fillna(0).astype(int)
    if (normalized["RowID"] <= 0).any():
        normalized["RowID"] = list(range(1, len(normalized) + 1))

    normalized["SupplierTitle"] = (
        normalized[supplier_title_col].map(safe_text) if supplier_title_col else ""
    )
    normalized["AmazonTitle"] = normalized[amazon_title_col].map(safe_text) if amazon_title_col else ""
    normalized["SupplierEAN_raw"] = normalized[supplier_ean_col] if supplier_ean_col else None
    normalized["AmazonEAN_raw"] = normalized[amazon_ean_col] if amazon_ean_col else None
    normalized["ASIN"] = normalized[asin_col].map(safe_text) if asin_col else ""
    
    # Preserve SupplierURL if present (for stable key generation)
    supplier_url_col = find_col(["SupplierURL", "supplier_url", "Supplier URL"])
    if supplier_url_col:
        normalized["SupplierURL"] = normalized[supplier_url_col].map(safe_text)
    else:
        normalized["SupplierURL"] = None

    def to_float(col: str | None) -> pd.Series:
        if not col:
            return pd.Series([None] * len(normalized))
        s = normalized[col].astype(str).str.replace("£", "", regex=False).str.replace(",", "", regex=False)
        return pd.to_numeric(s, errors="coerce")

    normalized["SupplierPrice"] = to_float(supplier_price_col)
    normalized["SellingPrice"] = to_float(selling_price_col)
    normalized["NetProfit"] = to_float(net_profit_col)
    normalized["ROI"] = to_float(roi_col)
    normalized["Sales"] = to_float(sales_col) if sales_col else pd.Series([None] * len(normalized))

    report = {
        "original_columns": [str(c) for c in original_columns],
        "detected": {
            "row_id": row_id_col,
            "supplier_title": supplier_title_col,
            "amazon_title": amazon_title_col,
            "supplier_ean": supplier_ean_col,
            "amazon_ean": amazon_ean_col,
            "asin": asin_col,
            "supplier_price": supplier_price_col,
            "selling_price": selling_price_col,
            "net_profit": net_profit_col,
            "roi": roi_col,
            "sales": sales_col,
        },
    }

    # Select columns to keep (stable_key will be added later)
    output_columns = [
        "RowID",
        "SupplierTitle",
        "AmazonTitle",
        "SupplierEAN_raw",
        "AmazonEAN_raw",
        "ASIN",
        "SupplierURL",
        "SupplierPrice",
        "SellingPrice",
        "NetProfit",
        "ROI",
        "Sales",
    ]
    
    # Only include columns that exist
    output_columns = [c for c in output_columns if c in normalized.columns]
    normalized = normalized[output_columns]
    
    # Track SupplierURL detection in report
    report["detected"]["supplier_url"] = supplier_url_col

    return normalized, report


def normalize_columns_with_stable_keys(
    df: pd.DataFrame,
    collision_report_dir: Path | None = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Normalize columns AND add stable_key column.
    
    This is the preferred entry point for vNext pipeline.
    Raises StableKeyCollisionError if collisions detected.
    
    Args:
        df: Raw DataFrame from load_report()
        collision_report_dir: Directory to write collision report (optional)
    
    Returns:
        Tuple of (normalized DataFrame with stable_key, normalization report)
    
    Raises:
        StableKeyCollisionError: If stable_key collisions are detected
    """
    normalized, report = normalize_columns(df)
    
    try:
        normalized = add_stable_keys_to_dataframe(normalized)
        report["stable_key_generated"] = True
        report["stable_key_collision"] = False
    except StableKeyCollisionError as e:
        # Write collision report if directory provided
        if collision_report_dir:
            from fba_agent.stable_key import write_collision_report
            report_path = write_collision_report(e.collisions, collision_report_dir)
            e.collision_report_path = report_path
        report["stable_key_generated"] = False
        report["stable_key_collision"] = True
        report["collision_count"] = len(e.collisions)
        raise
    
    return normalized, report

