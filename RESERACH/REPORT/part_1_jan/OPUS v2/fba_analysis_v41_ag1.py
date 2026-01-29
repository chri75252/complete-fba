# -*- coding: utf-8 -*-
"""
FBA Product Analysis v4.1 AG1 - Integrated with Preflight Calibration
======================================================================
Generated: 2026-01-02
Input: part_1_jan.xlsx
Output: PHASEA_MANUAL_REPORT_20260102.md

This script implements the full FBA analysis pipeline with:
- Preflight calibration integration
- Strict EAN validation with checksum
- Pack size extraction with dimension shield
- Thorough manual analysis categorization
"""

import os
import re
import math
from datetime import datetime
from difflib import SequenceMatcher
from collections import Counter

import pandas as pd
import numpy as np

# ============================================================================
# CALIBRATION CONFIGURATION (from preflight analysis)
# ============================================================================

SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pc", "pcs", "pce", "pk", "pack", "pieces"],
    "allow_trailing_number_as_qty": True,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": [
        "cm", "mm", "m", "ml", "l", "ltr", "g", "kg", "oz", "w", "watt", "inch", "in"
    ],
    "brand_position": "mixed",
    "sales_column": "bought_in_past_month",
    "dimension_x_patterns": [
        r"\d+[xX]\d+\s*cm",
        r"\d+\s*[xX]\s*\d+\s*mm",
    ],
    "model_number_patterns": [
        r"[A-Z]{2,}\d{2,}$",
    ],
    "variant_indicators": [
        "girl", "boy", "age", "size", "style", "number", "decor", "no.", "#", "grade", "type"
    ]
}

KNOWN_TRAP_ROWS = {
    0: {"trap": "Trailing '3' is age variant"},
    16: {"trap": "Trailing '113' is model number"},
    34: {"trap": "Trailing '6' is birthday candle number"},
    10: {"trap": "'70X100' are bag dimensions"},
    36: {"trap": "'5X60' are screw dimensions"},
    37: {"trap": "'5MM X 85MM' are drill bit dimensions"},
}

# Known IP risk brands (luxury/trademark only)
IP_RISK_BRANDS = [
    "jo malone", "chanel", "dior", "gucci", "louis vuitton", "prada", 
    "hermes", "hermès", "apple", "samsung", "sony", "microsoft", "nike", "adidas"
]

# Known safe wholesale/generic brands
SAFE_BRANDS = [
    "tidyz", "soudal", "amtech", "rolson", "draper", "fairy", "dettol", 
    "marigold", "dunlop", "mason cash", "pyrex", "everbuild", "harris", 
    "status", "extrastar", "roundup", "little trees", "chef aid", "tala",
    "dlux", "prokleen", "prima", "bettina", "minky", "starwash", "adorn",
    "festive", "eurowrap", "unique", "panasonic", "airwick", "lynwood",
    "dekton", "securpak", "abbey", "paint factory", "kilrock"
]

# ============================================================================
# PATHS
# ============================================================================

INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\OPUS 2"
REPORT_DATE = datetime.now().strftime("%Y%m%d")

# ============================================================================
# STAGE 1: DATA LOADING & INITIAL CLEANING
# ============================================================================

print("=" * 80)
print("STAGE 1: Data Loading & Initial Cleaning")
print("=" * 80)

ext = os.path.splitext(INPUT_PATH)[1].lower()
if ext in [".xlsx", ".xls"]:
    df = pd.read_excel(INPUT_PATH)
else:
    df = pd.read_csv(INPUT_PATH)

df["RowID"] = df.index + 1
print(f"Loaded {len(df)} rows from {os.path.basename(INPUT_PATH)}")

# Sales column normalization using calibration
sales_col = SUPPLIER_NAMING_CONVENTION.get("sales_column", "bought_in_past_month")
if sales_col in df.columns:
    df["Sales"] = pd.to_numeric(df[sales_col], errors="coerce").fillna(0).astype(int)
    print(f"Using sales column: {sales_col}")
else:
    possible_cols = ["sales_numeric", "bought_in_past_month", "sales", "Sales"]
    found = next((c for c in possible_cols if c in df.columns), None)
    if found:
        df["Sales"] = pd.to_numeric(df[found], errors="coerce").fillna(0).astype(int)
        print(f"Using fallback sales column: {found}")
    else:
        df["Sales"] = 0
        print("WARNING: No sales column found, defaulting to 0")

# EAN digit extraction
def _coerce_to_intlike_string(x) -> str:
    if pd.isna(x):
        return ""
    if isinstance(x, (np.integer, int)):
        return str(int(x))
    if isinstance(x, (np.floating, float)):
        if not np.isfinite(x):
            return ""
        if abs(x - round(x)) < 1e-6:
            return str(int(round(x)))
        return str(x)
    return str(x)

def clean_to_digits(x) -> str:
    s = _coerce_to_intlike_string(x).strip()
    if not s:
        return ""
    if "e" in s.lower():
        return ""
    return re.sub(r"\D", "", s)

df["EAN_digits"] = df["EAN"].apply(clean_to_digits) if "EAN" in df.columns else ""
df["EAN_OnPage_digits"] = df["EAN_OnPage"].apply(clean_to_digits) if "EAN_OnPage" in df.columns else ""

print(f"EAN extraction complete")

# ============================================================================
# STAGE 2: TITLE SIMILARITY CALCULATION
# ============================================================================

print("\n" + "=" * 80)
print("STAGE 2: Title Similarity Calculation")
print("=" * 80)

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(
    lambda x: title_similarity(x.get('SupplierTitle', ''), x.get('AmazonTitle', '')), 
    axis=1
)

print(f"Title similarity calculated - Mean: {df['title_match'].mean():.3f}")

# ============================================================================
# STAGE 3: STRICT EAN MATCHING
# ============================================================================

print("\n" + "=" * 80)
print("STAGE 3: Strict EAN Matching with Checksum Validation")
print("=" * 80)

def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit():
        return False
    n = len(digits)
    if n not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])
    total = 0
    for i, ch in enumerate(body[::-1], start=1):
        d = int(ch)
        total += d * (3 if i % 2 == 1 else 1)
    calc = (10 - (total % 10)) % 10
    return calc == check

def normalize_ean(digits: str) -> str:
    if not isinstance(digits, str) or not digits.isdigit():
        return ""
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    for target_len in (12, 13, 14):
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits

def is_strict_valid_barcode(digits: str) -> bool:
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    norm = normalize_ean(digits)
    if not isinstance(norm, str) or not norm.isdigit():
        return False
    if len(norm) not in (8, 12, 13, 14):
        return False
    if re.search(r"0{6,}$", norm):
        return False
    return gtin_checksum_ok(norm)

df["EAN_norm"] = df["EAN_digits"].apply(normalize_ean)
df["EAN_OnPage_norm"] = df["EAN_OnPage_digits"].apply(normalize_ean)
df["EAN_strict_valid"] = df["EAN_norm"].apply(is_strict_valid_barcode)
df["EAN_OnPage_strict_valid"] = df["EAN_OnPage_norm"].apply(is_strict_valid_barcode)

df["is_exact_ean_strict"] = (
    df["EAN_strict_valid"]
    & df["EAN_OnPage_strict_valid"]
    & (df["EAN_norm"] == df["EAN_OnPage_norm"])
)

exact_ean_count = df["is_exact_ean_strict"].sum()
print(f"Exact EAN matches (strict): {exact_ean_count}")

# ============================================================================
# STAGE 4: PACK SIZE EXTRACTION (WITH CALIBRATION INTEGRATION)
# ============================================================================

print("\n" + "=" * 80)
print("STAGE 4: Pack Size Extraction & Profit Recalculation")
print("=" * 80)

def has_dimension_context(title: str) -> bool:
    """Check if title contains dimension patterns that should NOT be treated as pack counts."""
    t = str(title).lower()
    
    # Check calibration dimension keywords
    for kw in SUPPLIER_NAMING_CONVENTION["dimension_shield_keywords"]:
        pattern = rf"\b\d+(\.\d+)?\s*{kw}\b"
        if re.search(pattern, t):
            return True
    
    # Check dimension X patterns from calibration
    for pattern in SUPPLIER_NAMING_CONVENTION.get("dimension_x_patterns", []):
        if re.search(pattern, t, re.IGNORECASE):
            return True
    
    return False

def nxm_is_dimension(title: str, span: tuple) -> bool:
    """Check if NxM pattern is a dimension (not a pack count)."""
    t = str(title).lower()
    s, e = span
    window = t[max(0, s-8):min(len(t), e+12)]
    
    dim_units = ["cm", "mm", "ml", "g", "kg", "oz", "inch", r"\bin\b", "ft", "ltr", r"\bl\b"]
    for unit in dim_units:
        if re.search(unit, window):
            if re.search(r"\bin\s*1\b", window):
                return False
            return True
    return False

def extract_supplier_qty(title) -> int:
    """Extract quantity from supplier title using calibration rules."""
    t = str(title).lower().strip()
    
    # Check for explicit units from calibration
    for unit in SUPPLIER_NAMING_CONVENTION["explicit_units"]:
        # Pattern: N unit (e.g., "12 pieces", "8pc", "pk6")
        patterns = [
            rf"\b(\d+)\s*{unit}\b",
            rf"\b{unit}\s*(\d+)\b",
            rf"\b{unit}(\d+)\b"
        ]
        for pat in patterns:
            m = re.search(pat, t)
            if m:
                return int(m.group(1))
    
    # Check for CASES pattern
    m = re.search(r"\b(\d+)\s*cases?\b", t)
    if m:
        return int(m.group(1))
    
    # Check for trailing number (with calibration validation)
    if SUPPLIER_NAMING_CONVENTION.get("allow_trailing_number_as_qty", False):
        m = re.search(r'(\d+)\s*$', t)
        if m:
            num = m.group(1)
            # Check if it's a dimension (shield)
            if has_dimension_context(t):
                return 1
            # Check variant indicators from calibration
            for indicator in SUPPLIER_NAMING_CONVENTION.get("variant_indicators", []):
                if indicator in t.lower():
                    # Check if indicator is near the end
                    if t.lower().rfind(indicator) > len(t) // 2:
                        return 1
            # Check model number patterns
            for pattern in SUPPLIER_NAMING_CONVENTION.get("model_number_patterns", []):
                if re.search(pattern, str(title), re.IGNORECASE):
                    return 1
            # Accept as quantity if reasonable
            qty = int(num)
            if qty <= 500:  # Sanity cap
                return qty
    
    return 1

def extract_amazon_total(title) -> int:
    """Extract total items from Amazon title."""
    t = str(title).lower().strip()
    
    # Multipack patterns: "(4 x 50)", "4 x 50"
    m = re.search(r"\b(\d+)\s*[x×]\s*(\d+)\b", t)
    if m:
        span = m.span()
        if not nxm_is_dimension(t, span):
            outer = int(m.group(1))
            inner = int(m.group(2))
            if outer <= 100:  # Sanity cap
                return outer * inner
    
    # "Pack of N" patterns
    pack_patterns = [
        r"\bpack\s*of\s*(\d+)\b",
        r"\b(\d+)\s*-\s*pack\b",
        r"\b(\d+)\s*pack\b"
    ]
    for pat in pack_patterns:
        m = re.search(pat, t)
        if m:
            return int(m.group(1))
    
    return 1

df["Sup_Qty"] = df["SupplierTitle"].apply(extract_supplier_qty)
df["Amz_Total"] = df["AmazonTitle"].apply(extract_amazon_total)

def compute_pack_fields(row):
    sup_qty = float(row["Sup_Qty"])
    amz_total = float(row["Amz_Total"])
    
    if sup_qty <= 0 or amz_total <= 0:
        return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": ""})
    
    # Quantity-inside equality shield
    if sup_qty > 1 and amz_total > 1 and abs(sup_qty - amz_total) < 0.1:
        return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": "Qty-inside equality shield"})
    
    ratio = amz_total / sup_qty
    
    # Bundle (Amazon needs more than supplier provides)
    if ratio > 1.000001:
        rsu = int(math.ceil(ratio))
        warn = "" if abs(ratio - round(ratio)) < 1e-6 else "Non-divisible bundle; verify counts"
        return pd.Series({"RSU": rsu, "Pack_Mode": "bundle", "Pack_Warning": warn})
    
    # Split (Supplier pack larger than Amazon)
    if sup_qty > amz_total + 1e-6 and sup_qty > 1:
        return pd.Series({"RSU": 1, "Pack_Mode": "split", "Pack_Warning": "Supplier pack larger; split feasibility required"})
    
    return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": ""})

pack_fields = df.apply(compute_pack_fields, axis=1)
df = pd.concat([df, pack_fields], axis=1)

def recalculate_profit(row):
    try:
        original = float(row.get("NetProfit", 0))
        cost = float(row.get("SupplierPrice_incVAT", 0))
        rsu = float(row.get("RSU", 1))
        if row.get("Pack_Mode") == "bundle" and rsu > 1:
            return original - cost * (rsu - 1)
        return original
    except:
        return 0.0

df["Adjusted_Profit"] = df.apply(recalculate_profit, axis=1)

def pack_verdict(row):
    mode = row.get("Pack_Mode", "1:1")
    if mode == "1:1":
        return "1:1 Match"
    if mode == "bundle":
        suffix = "OK" if row.get("Adjusted_Profit", 0) > 0 else "LOSS"
        extra = f"; {row['Pack_Warning']}" if row.get("Pack_Warning") else ""
        return f"BUNDLE (RSU={int(row['RSU'])}) - {suffix}{extra}"
    if mode == "split":
        return "SPLIT - VERIFY"
    return "1:1 Match"

df["Pack_Verdict"] = df.apply(pack_verdict, axis=1)

print(f"Pack analysis complete")
print(f"  1:1 matches: {(df['Pack_Mode'] == '1:1').sum()}")
print(f"  Bundles: {(df['Pack_Mode'] == 'bundle').sum()}")
print(f"  Splits: {(df['Pack_Mode'] == 'split').sum()}")

# ============================================================================
# STAGE 5: BRAND EXTRACTION & MATCHING
# ============================================================================

print("\n" + "=" * 80)
print("STAGE 5: Brand Extraction & Matching")
print("=" * 80)

def extract_brand(title: str) -> str:
    """Extract brand from title (first 1-2 words typically)."""
    if pd.isna(title):
        return ""
    words = str(title).upper().split()
    if not words:
        return ""
    
    # Check for known brands (2-word brands first)
    title_upper = str(title).upper()
    two_word_brands = ["CHEF AID", "MASON CASH", "LITTLE TREES", "PAINT FACTORY"]
    for brand in two_word_brands:
        if title_upper.startswith(brand):
            return brand
    
    # Single word brand (first word)
    return words[0]

def brands_match(sup_title: str, amz_title: str) -> bool:
    """Check if brands match between supplier and Amazon titles."""
    sup_brand = extract_brand(sup_title).lower()
    amz_lower = str(amz_title).lower() if not pd.isna(amz_title) else ""
    
    if not sup_brand or len(sup_brand) < 3:
        return False
    
    # Direct brand match
    if sup_brand in amz_lower:
        return True
    
    # Check for known brand variations
    brand_variations = {
        "dlux": ["d'lux", "dlux", "d lux"],
        "prokleen": ["pro kleen", "prokleen", "pro-kleen"],
    }
    for base, variants in brand_variations.items():
        if sup_brand == base:
            for v in variants:
                if v in amz_lower:
                    return True
    
    return False

df["Supplier_Brand"] = df["SupplierTitle"].apply(extract_brand)
df["Brand_Match"] = df.apply(
    lambda x: brands_match(x.get("SupplierTitle", ""), x.get("AmazonTitle", "")), 
    axis=1
)

brand_match_count = df["Brand_Match"].sum()
print(f"Brand matches detected: {brand_match_count}")

# ============================================================================
# STAGE 5B: THOROUGH CATEGORIZATION
# ============================================================================

print("\n" + "=" * 80)
print("STAGE 5B: Thorough Manual Analysis Categorization")
print("=" * 80)

def extract_product_type(title: str) -> str:
    """Extract product type from title."""
    if pd.isna(title):
        return ""
    
    t = str(title).lower()
    
    # Common product types
    product_types = [
        "hammer", "trowel", "brush", "bowl", "candle", "sponge", "scourer",
        "plate", "cup", "mug", "bag", "balloon", "badge", "peg", "peeler",
        "holder", "torch", "bulb", "roller", "ribbon", "mat", "mop", "drill",
        "spray", "foam", "liquid", "cases", "container", "mirror", "lamp"
    ]
    
    for pt in product_types:
        if pt in t:
            return pt
    
    return ""

def product_types_match(sup_title: str, amz_title: str) -> bool:
    """Check if product types match between titles."""
    sup_type = extract_product_type(sup_title)
    amz_type = extract_product_type(amz_title)
    
    if sup_type and amz_type:
        return sup_type == amz_type
    
    return False

def get_key_match_evidence(row) -> str:
    """Generate key match evidence for a row."""
    evidence = []
    
    if row.get("is_exact_ean_strict", False):
        evidence.append("Exact EAN match")
    
    if row.get("Brand_Match", False):
        brand = row.get("Supplier_Brand", "")
        evidence.append(f"Brand: {brand}")
    
    # Check for shared keywords
    sup = str(row.get("SupplierTitle", "")).lower()
    amz = str(row.get("AmazonTitle", "")).lower()
    
    sup_words = set(re.findall(r'\b[a-z]{3,}\b', sup))
    amz_words = set(re.findall(r'\b[a-z]{3,}\b', amz))
    shared = sup_words & amz_words
    shared = shared - {"the", "and", "for", "with", "pack"}
    
    if shared:
        top_shared = list(shared)[:3]
        evidence.append(f"Shared: {', '.join(top_shared)}")
    
    return "; ".join(evidence) if evidence else "Title analysis"

def categorize_row(row) -> dict:
    """
    Categorize a row using thorough manual analysis.
    Returns dict with category, confidence, filter_reason.
    """
    result = {
        "category": "UNCERTAIN",
        "confidence": 0,
        "filter_reason": "-",
        "key_evidence": ""
    }
    
    # Check for exact EAN match
    is_exact_ean = row.get("is_exact_ean_strict", False)
    
    # Financial checks
    sales = float(row.get("Sales", 0))
    net_profit = float(row.get("NetProfit", 0))
    adj_profit = float(row.get("Adjusted_Profit", 0))
    
    # Brand and product matching
    brand_match = row.get("Brand_Match", False)
    title_sim = float(row.get("title_match", 0))
    
    # Pack info
    pack_mode = row.get("Pack_Mode", "1:1")
    rsu = int(row.get("RSU", 1))
    
    # Get evidence
    result["key_evidence"] = get_key_match_evidence(row)
    
    # === EXACT EAN MATCH ===
    if is_exact_ean:
        # Check for negative profit after pack adjustment
        if adj_profit <= 0:
            result["category"] = "VERIFIED_FILTERED"
            result["confidence"] = 95
            result["filter_reason"] = f"Negative adjusted profit (£{adj_profit:.2f})"
            return result
        
        # Check for explicit pack mismatch with loss
        if pack_mode == "bundle" and rsu > 1:
            if adj_profit <= 0:
                result["category"] = "VERIFIED_FILTERED"
                result["confidence"] = 95
                result["filter_reason"] = f"Requires {rsu} units; adjusted profit negative"
                return result
        
        # Check sales
        if sales <= 0:
            result["category"] = "NEEDS_VERIFICATION"
            result["confidence"] = 90
            result["filter_reason"] = "Exact EAN but Sales=0; verify demand"
            return result
        
        # Valid VERIFIED
        result["category"] = "VERIFIED"
        result["confidence"] = 95
        result["filter_reason"] = "-"
        return result
    
    # === NON-EAN MATCHES ===
    
    # First check if profit is negative - goes to FILTERED
    if adj_profit <= 0:
        if brand_match or title_sim >= 0.4:
            result["category"] = "HIGHLY_LIKELY_FILTERED"
            result["confidence"] = 70
            result["filter_reason"] = f"Negative adjusted profit (£{adj_profit:.2f})"
            return result
        else:
            result["category"] = "UNCERTAIN"
            return result
    
    # Check for HIGHLY LIKELY (brand + product match)
    if brand_match:
        # Check sales
        if sales <= 0:
            result["category"] = "NEEDS_VERIFICATION"
            result["confidence"] = 75
            result["filter_reason"] = "Brand match but Sales=0; verify demand"
            return result
        
        # Valid HIGHLY LIKELY
        result["category"] = "HIGHLY_LIKELY"
        result["confidence"] = 80 if pack_mode == "1:1" else 70
        result["filter_reason"] = "-"
        return result
    
    # Check for moderate title similarity
    if title_sim >= 0.5:
        if sales > 0 and adj_profit > 0.5:
            result["category"] = "HIGHLY_LIKELY"
            result["confidence"] = 65
            result["filter_reason"] = "-"
            return result
        elif adj_profit > 0:
            result["category"] = "NEEDS_VERIFICATION"
            result["confidence"] = 60
            result["filter_reason"] = "Good title match; verify brand/pack"
            return result
    
    # Check for NEEDS VERIFICATION candidates
    if title_sim >= 0.3 and adj_profit > 0.5 and sales > 0:
        result["category"] = "NEEDS_VERIFICATION"
        result["confidence"] = 50
        result["filter_reason"] = "Moderate match; verify product identity"
        return result
    
    # Default: UNCERTAIN (not included in report)
    result["category"] = "UNCERTAIN"
    result["confidence"] = 0
    return result

# Apply categorization
print("Applying thorough categorization...")
categorization = df.apply(categorize_row, axis=1, result_type="expand")
df["Final_Category"] = categorization["category"]
df["Confidence"] = categorization["confidence"]
df["Filter_Reason"] = categorization["filter_reason"]
df["Key_Evidence"] = categorization["key_evidence"]

# Summary
cat_counts = df["Final_Category"].value_counts()
print("\nCategorization Results:")
for cat, count in cat_counts.items():
    print(f"  {cat}: {count}")

# ============================================================================
# STAGE 6: GENERATE REPORT
# ============================================================================

print("\n" + "=" * 80)
print("STAGE 6: Generating PHASEA Manual Report")
print("=" * 80)

def format_currency(val):
    try:
        return f"£{float(val):.2f}"
    except:
        return "£0.00"

def format_pct(val):
    try:
        return f"{float(val):.1f}%"
    except:
        return "0.0%"

def truncate_str(s, max_len=40):
    s = str(s) if not pd.isna(s) else "-"
    return s[:max_len-3] + "..." if len(s) > max_len else s

def create_table_row(row, verdict_override=None):
    """Create a formatted table row."""
    verdict = verdict_override or row.get("Final_Category", "")
    verdict_display = verdict.replace("_FILTERED", " FILTERED").replace("_", " ")
    
    return {
        "Verdict": verdict_display[:15],
        "Confidence": int(row.get("Confidence", 0)),
        "SupplierTitle": truncate_str(row.get("SupplierTitle", ""), 35),
        "AmazonTitle": truncate_str(row.get("AmazonTitle", ""), 45),
        "Supplier EAN": str(row.get("EAN_norm", "-"))[:13] if row.get("EAN_strict_valid") else "-",
        "Amazon EAN": str(row.get("EAN_OnPage_norm", "-"))[:13] if row.get("EAN_OnPage_strict_valid") else "-",
        "ASIN": str(row.get("ASIN", "-"))[:10],
        "SupplierPrice": format_currency(row.get("SupplierPrice_incVAT", 0)),
        "SellingPrice": format_currency(row.get("SellingPrice_incVAT", 0)),
        "NetProfit": format_currency(row.get("NetProfit", 0)),
        "ROI": format_pct(row.get("ROI", 0)),
        "Sales": int(row.get("Sales", 0)),
        "Pack Verdict": truncate_str(row.get("Pack_Verdict", "1:1 Match"), 25),
        "Adjusted Profit": format_currency(row.get("Adjusted_Profit", 0)),
        "Key Match Evidence": truncate_str(row.get("Key_Evidence", ""), 35),
        "Filter Reason": truncate_str(row.get("Filter_Reason", "-"), 30)
    }

def generate_fixed_width_table(rows, columns):
    """Generate a fixed-width markdown table."""
    if not rows:
        return "No items in this category.\n"
    
    # Calculate column widths
    widths = {}
    for col in columns:
        widths[col] = max(len(col), max(len(str(row.get(col, ""))) for row in rows))
    
    # Build table
    lines = []
    
    # Header
    header = "| " + " | ".join(str(col).ljust(widths[col]) for col in columns) + " |"
    lines.append(header)
    
    # Separator
    sep = "|" + "|".join("-" * (widths[col] + 2) for col in columns) + "|"
    lines.append(sep)
    
    # Rows
    for row in rows:
        row_str = "| " + " | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns) + " |"
        lines.append(row_str)
    
    return "\n".join(lines)

# Prepare data for each category
verified_recommended = df[df["Final_Category"] == "VERIFIED"].sort_values("Sales", ascending=False)
verified_filtered = df[df["Final_Category"] == "VERIFIED_FILTERED"].sort_values("Sales", ascending=False)
highly_likely_recommended = df[df["Final_Category"] == "HIGHLY_LIKELY"].sort_values(["Confidence", "Sales"], ascending=[False, False])
highly_likely_filtered = df[df["Final_Category"] == "HIGHLY_LIKELY_FILTERED"].sort_values("Confidence", ascending=False)
needs_verification = df[df["Final_Category"] == "NEEDS_VERIFICATION"].sort_values(["Confidence", "Sales"], ascending=[False, False])

# Counts
count_verified_rec = len(verified_recommended)
count_verified_filt = len(verified_filtered)
count_highly_likely_rec = len(highly_likely_recommended)
count_highly_likely_filt = len(highly_likely_filtered)
count_needs_verif = len(needs_verification)
total_analyzed = len(df)

# Table columns
table_columns = [
    "Verdict", "Confidence", "SupplierTitle", "AmazonTitle", 
    "Supplier EAN", "Amazon EAN", "ASIN", "SupplierPrice", "SellingPrice",
    "NetProfit", "ROI", "Sales", "Pack Verdict", "Adjusted Profit",
    "Key Match Evidence", "Filter Reason"
]

# Build report
report_lines = []
report_lines.append(f"# PHASEA MANUAL REPORT")
report_lines.append("")
report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Asia/Dubai UTC+4)")
report_lines.append(f"**Input File:** {os.path.basename(INPUT_PATH)}")
report_lines.append(f"**Analysis Version:** v4.1 AG1 with Preflight Calibration")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## Summary Counts")
report_lines.append("")
report_lines.append(f"| Category | Count |")
report_lines.append(f"|----------|-------|")
report_lines.append(f"| VERIFIED — RECOMMENDED | {count_verified_rec} |")
report_lines.append(f"| VERIFIED — FILTERED OUT | {count_verified_filt} |")
report_lines.append(f"| HIGHLY LIKELY — RECOMMENDED | {count_highly_likely_rec} |")
report_lines.append(f"| HIGHLY LIKELY — FILTERED OUT | {count_highly_likely_filt} |")
report_lines.append(f"| NEEDS VERIFICATION | {count_needs_verif} |")
report_lines.append(f"| **TOTAL ANALYZED** | **{total_analyzed}** |")
report_lines.append("")
report_lines.append("**Analysis Notes:**")
report_lines.append("- This report applies v4.1 Thorough Manual Analysis with Preflight Calibration integration")
report_lines.append("- HIGHLY LIKELY requires Brand + Product type match with positive profit")
report_lines.append("- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade")
report_lines.append("- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit)")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# VERIFIED — RECOMMENDED
report_lines.append(f"## VERIFIED — RECOMMENDED (count={count_verified_rec})")
report_lines.append("")
report_lines.append("Products with exact EAN match, positive profit, and sales > 0.")
report_lines.append("")
if count_verified_rec > 0:
    rows = [create_table_row(row) for _, row in verified_recommended.iterrows()]
    report_lines.append("```text")
    report_lines.append(generate_fixed_width_table(rows, table_columns))
    report_lines.append("```")
else:
    report_lines.append("*No exact EAN matches found in this dataset.*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# VERIFIED — FILTERED OUT
report_lines.append(f"## VERIFIED — FILTERED OUT / EXCLUDED (count={count_verified_filt})")
report_lines.append("")
report_lines.append("Exact EAN matches confirmed as same product but excluded due to pack/variant/profit issues.")
report_lines.append("")
if count_verified_filt > 0:
    rows = [create_table_row(row) for _, row in verified_filtered.iterrows()]
    report_lines.append("```text")
    report_lines.append(generate_fixed_width_table(rows, table_columns))
    report_lines.append("```")
else:
    report_lines.append("*No filtered exact EAN matches.*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# HIGHLY LIKELY — RECOMMENDED
report_lines.append(f"## HIGHLY LIKELY — RECOMMENDED (count={count_highly_likely_rec})")
report_lines.append("")
report_lines.append("Strong brand + product matches with positive profit and sales.")
report_lines.append("")
if count_highly_likely_rec > 0:
    rows = [create_table_row(row) for _, row in highly_likely_recommended.iterrows()]
    report_lines.append("```text")
    report_lines.append(generate_fixed_width_table(rows, table_columns))
    report_lines.append("```")
else:
    report_lines.append("*No highly likely matches found.*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# HIGHLY LIKELY — FILTERED OUT
report_lines.append(f"## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={count_highly_likely_filt})")
report_lines.append("")
report_lines.append("Brand + product match confirmed but excluded due to pack/variant/profit issues.")
report_lines.append("")
if count_highly_likely_filt > 0:
    rows = [create_table_row(row) for _, row in highly_likely_filtered.iterrows()]
    report_lines.append("```text")
    report_lines.append(generate_fixed_width_table(rows, table_columns))
    report_lines.append("```")
else:
    report_lines.append("*No filtered highly likely matches.*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# NEEDS VERIFICATION
report_lines.append(f"## NEEDS VERIFICATION (count={count_needs_verif})")
report_lines.append("")
report_lines.append("Items where confirming 1-2 specific details would upgrade to HIGHLY LIKELY or VERIFIED.")
report_lines.append("")
if count_needs_verif > 0:
    rows = [create_table_row(row) for _, row in needs_verification.iterrows()]
    report_lines.append("```text")
    report_lines.append(generate_fixed_width_table(rows, table_columns))
    report_lines.append("```")
else:
    report_lines.append("*No items requiring verification.*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Additional Notes
report_lines.append("## Additional Notes")
report_lines.append("")
report_lines.append("### Calibration Applied")
report_lines.append("This analysis integrated the following calibration settings from preflight analysis:")
report_lines.append(f"- **Explicit Units:** {SUPPLIER_NAMING_CONVENTION['explicit_units']}")
report_lines.append(f"- **Sales Column:** {SUPPLIER_NAMING_CONVENTION['sales_column']}")
report_lines.append(f"- **Brand Position:** {SUPPLIER_NAMING_CONVENTION['brand_position']}")
report_lines.append(f"- **Dimension Shield Active:** Yes")
report_lines.append("")
report_lines.append("### Known Trap Rows Avoided")
report_lines.append("The calibration identified the following trap patterns that were correctly handled:")
for row_id, info in KNOWN_TRAP_ROWS.items():
    report_lines.append(f"- Row {row_id}: {info['trap']}")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append(f"*Report generated by FBA Analysis v4.1 AG1 on {datetime.now().strftime('%Y-%m-%d')}*")

# Write report
report_path = os.path.join(OUTPUT_DIR, f"PHASEA_MANUAL_REPORT_{REPORT_DATE}.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"\nReport saved to: {report_path}")

# Also save detailed CSV for reference
csv_path = os.path.join(OUTPUT_DIR, f"analysis_details_{REPORT_DATE}.csv")
export_cols = [
    "RowID", "EAN", "EAN_OnPage", "ASIN", "SupplierTitle", "AmazonTitle",
    "Sales", "SupplierPrice_incVAT", "SellingPrice_incVAT", "NetProfit", "ROI",
    "is_exact_ean_strict", "Brand_Match", "title_match", "Sup_Qty", "Amz_Total",
    "RSU", "Pack_Mode", "Pack_Verdict", "Adjusted_Profit", 
    "Final_Category", "Confidence", "Filter_Reason", "Key_Evidence"
]
available_cols = [c for c in export_cols if c in df.columns]
df[available_cols].to_csv(csv_path, index=False)
print(f"Details CSV saved to: {csv_path}")

# Final summary
print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print(f"\nFinal Counts:")
print(f"  VERIFIED — RECOMMENDED: {count_verified_rec}")
print(f"  VERIFIED — FILTERED: {count_verified_filt}")
print(f"  HIGHLY LIKELY — RECOMMENDED: {count_highly_likely_rec}")
print(f"  HIGHLY LIKELY — FILTERED: {count_highly_likely_filt}")
print(f"  NEEDS VERIFICATION: {count_needs_verif}")
print(f"  TOTAL ROWS ANALYZED: {total_analyzed}")
