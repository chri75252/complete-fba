import pandas as pd
import re
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Responsible for loading financial reports (CSV/XLSX),
    normalizing column names, generating RowIDs, and cleaning basic data.
    """

    REQUIRED_COLUMNS = [
        "SupplierTitle", "AmazonTitle", 
        "SupplierPrice_incVAT", "SellingPrice_incVAT", 
        "NetProfit"
    ]
    
    # Mapping of normalized internal names to possible inputs
    # We will try to find these columns in the input
    COLUMN_MAPPING = {
        "SupplierEAN": ["Supplier EAN", "EAN", "ean", "SupplierEan"],
        "AmazonEAN": ["Amazon EAN", "EAN_OnPage", "AmazonEan", "ean_onpage"],
        "ASIN": ["ASIN", "asin", "Asin"],
        "SupplierTitle": ["SupplierTitle", "Supplier Title", "title_supplier"],
        "AmazonTitle": ["AmazonTitle", "Amazon Title", "title_amazon"],
        "SupplierPrice": ["SupplierPrice_incVAT", "Supplier Price", "Cost"],
        "SellingPrice": ["SellingPrice_incVAT", "Selling Price", "Price"],
        "NetProfit": ["NetProfit", "Profit", "Net Profit"],
        "Sales": ["sales_numeric", "bought_in_past_month", "Sales", "Estimated Sales"],
        "ROI": ["ROI", "roi", "Return on Investment"]
    }

    def load_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Loads a file and returns the normalized DataFrame + Metadata.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        # 1. Read File
        try:
            if path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
                # Fallback for encoding if utf-8 fails could be added here
            elif path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        except Exception as e:
            raise ValueError(f"Failed to read file: {e}")

        if df.empty:
            raise ValueError("Input file is empty")

        # 2. Generate RowID
        # If RowID exists, use it. Else create one 1-based index
        if "RowID" not in df.columns:
            df.insert(0, "RowID", range(1, len(df) + 1))
        
        # 3. Normalize Columns
        normalized_df = self._normalize_columns(df)
        
        # 4. Basic Data Cleaning
        normalized_df = self._clean_data(normalized_df)

        metadata = {
            "source_file": str(path),
            "total_rows": len(normalized_df),
            "columns": list(normalized_df.columns)
        }
        
        return normalized_df, metadata

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Renames columns to internal standard names based on COLUMN_MAPPING.
        Keeps extra columns but standardizes the critical ones.
        """
        rename_map = {}
        found_cols = set(df.columns)
        
        for internal_name, aliases in self.COLUMN_MAPPING.items():
            for alias in aliases:
                if alias in found_cols:
                    rename_map[alias] = internal_name
                    break # Found the best match for this internal column
        
        return df.rename(columns=rename_map)

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans EANs and Sales columns.
        """
        # Clean EAN columns to string, remove scientific notation '.0', strip spaces
        for col in ["SupplierEAN", "AmazonEAN"]:
            if col in df.columns:
                df[col] = df[col].astype(str).apply(self._clean_ean)
            else:
                # Ensure column exists even if missing, fill with nan strings
                df[col] = ""

        # Ensure Sales is numeric
        if "Sales" in df.columns:
            df["Sales"] = df["Sales"].apply(self._parse_sales)
        else:
            df["Sales"] = 0

        # Ensure Numeric for Financials
        for col in ["SupplierPrice", "SellingPrice", "NetProfit", "ROI"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # Fill NaNs in Titles with empty string to avoid AttributeError later
        for col in ["SupplierTitle", "AmazonTitle"]:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str)
                
        return df

    def _clean_ean(self, val: Any) -> str:
        if pd.isna(val):
            return ""
        s = str(val).strip()
        # Remove .0 for floats
        if s.endswith(".0"):
            s = s[:-2]
        # Remove scientific notation e+
        if "e+" in s.lower():
            return ""
        # Keep digits only? Or keep original? 
        # PRD says: "remove .0 artifacts, strip spaces"
        # We will keep just digits to be safe for matching, 
        # but validation tool might want to know if it was corrupted.
        # For loader, let's just strip whitespace and .0.
        return s

    def _parse_sales(self, val: Any) -> int:
        """
        Parses sales like "100+", "1K+", "50" into integers.
        """
        if pd.isna(val):
            return 0
        s = str(val).lower().strip()
        s = s.replace("+", "").replace(",", "")
        
        try:
            if "k" in s:
                return int(float(s.replace("k", "")) * 1000)
            return int(float(s))
        except:
            return 0
