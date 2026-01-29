"""
Data Loading Tools for FBA Agent.

Handles loading and normalizing input files (CSV/XLSX).
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
import re

from ..models.schemas import SchemaInfo


def load_report(input_path: str) -> Tuple[pd.DataFrame, SchemaInfo]:
    """
    Load a financial report from CSV or XLSX file.
    
    Args:
        input_path: Path to the input file
        
    Returns:
        Tuple of (DataFrame, SchemaInfo)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported
    """
    path = Path(input_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    suffix = path.suffix.lower()
    
    if suffix == ".csv":
        df = pd.read_csv(input_path)
        file_format = "csv"
    elif suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(input_path)
        file_format = "xlsx"
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .csv or .xlsx")
    
    # Detect schema
    schema_info = _detect_schema(df, file_format)
    
    return df, schema_info


def _detect_schema(df: pd.DataFrame, file_format: str) -> SchemaInfo:
    """Detect the schema of the loaded DataFrame."""
    columns = df.columns.tolist()
    
    # Detect EAN column
    ean_column = _find_column(columns, ["EAN", "ean", "Ean", "SupplierEAN", "Supplier_EAN"])
    
    # Detect Amazon EAN column
    ean_onpage_column = _find_column(columns, [
        "EAN_OnPage", "EAN_onPage", "ean_onpage", "AmazonEAN", "Amazon_EAN", "EANOnPage"
    ])
    
    # Detect sales column
    sales_column = _find_column(columns, [
        "sales_numeric", "Sales", "sales", "bought_in_past_month", "MonthlySales"
    ])
    
    # Check for RowID
    has_rowid = "RowID" in columns or "rowid" in columns or "row_id" in columns
    
    return SchemaInfo(
        detected_columns=columns,
        ean_column=ean_column or "EAN",
        ean_onpage_column=ean_onpage_column or "EAN_OnPage",
        sales_column=sales_column,
        has_rowid=has_rowid,
        row_count=len(df),
        file_format=file_format
    )


def _find_column(columns: List[str], candidates: List[str]) -> Optional[str]:
    """Find the first matching column name from candidates."""
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def normalize_columns(df: pd.DataFrame, schema_info: SchemaInfo) -> pd.DataFrame:
    """
    Normalize DataFrame columns for consistent processing.
    
    - Creates RowID if not present
    - Cleans EAN columns (strips whitespace, removes .0, handles NaN)
    - Normalizes sales column
    
    Args:
        df: Input DataFrame
        schema_info: Detected schema information
        
    Returns:
        Normalized DataFrame
    """
    df = df.copy()
    
    # Create RowID if not present
    if not schema_info.has_rowid:
        df['RowID'] = df.index + 1
    else:
        # Normalize existing RowID column name
        for col in ['rowid', 'row_id', 'RowID']:
            if col in df.columns and col != 'RowID':
                df['RowID'] = df[col]
                break
    
    # Clean EAN columns
    ean_col = schema_info.ean_column
    ean_onpage_col = schema_info.ean_onpage_column
    
    if ean_col in df.columns:
        df['EAN_clean'] = df[ean_col].apply(_clean_ean_value)
        df['EAN_digits'] = df['EAN_clean'].apply(_extract_digits)
    else:
        df['EAN_clean'] = ""
        df['EAN_digits'] = ""
    
    if ean_onpage_col in df.columns:
        df['EAN_OnPage_clean'] = df[ean_onpage_col].apply(_clean_ean_value)
        df['EAN_OnPage_digits'] = df['EAN_OnPage_clean'].apply(_extract_digits)
    else:
        df['EAN_OnPage_clean'] = ""
        df['EAN_OnPage_digits'] = ""
    
    # Normalize sales column
    if schema_info.sales_column and schema_info.sales_column in df.columns:
        df['sales'] = pd.to_numeric(df[schema_info.sales_column], errors='coerce').fillna(0)
    else:
        df['sales'] = 0
    
    # Ensure title columns exist
    for col in ['SupplierTitle', 'AmazonTitle']:
        if col not in df.columns:
            df[col] = ""
        else:
            df[col] = df[col].fillna("").astype(str)
    
    # Ensure price columns exist and are numeric
    for col in ['SupplierPrice_incVAT', 'SellingPrice_incVAT', 'NetProfit', 'ROI']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0.0
    
    return df


def _clean_ean_value(value) -> str:
    """Clean an EAN value to a normalized string."""
    if pd.isna(value):
        return ""
    
    s = str(value).strip()
    
    # Handle Excel float conversion (remove .0)
    if s.endswith('.0'):
        s = s[:-2]
    
    # Handle scientific notation (treat as corrupted)
    if 'e+' in s.lower() or 'e-' in s.lower():
        return ""
    
    return s


def _extract_digits(value: str) -> str:
    """Extract only digits from a string."""
    if not value:
        return ""
    return re.sub(r'\D', '', value)


def sample_rows(df: pd.DataFrame, n: int = 50) -> List[Dict[str, Any]]:
    """
    Sample rows for preflight calibration.
    
    Args:
        df: Normalized DataFrame
        n: Number of rows to sample
        
    Returns:
        List of row dictionaries
    """
    sample_size = min(n, len(df))
    
    if len(df) <= n:
        sample_df = df
    else:
        # Take a stratified sample: first 20, last 10, random 20,
        # to capture patterns across the file
        first_rows = df.head(20)
        last_rows = df.tail(10)
        middle_rows = df.iloc[20:-10].sample(min(20, len(df) - 30)) if len(df) > 30 else pd.DataFrame()
        sample_df = pd.concat([first_rows, middle_rows, last_rows]).drop_duplicates()
    
    return sample_df.to_dict('records')
