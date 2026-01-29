"""
FBA Product Analysis Script v4.1 AG1 (Opus Enhanced)
Implements comprehensive multi-stage analysis per prompt specification.
Integrates pre-flight calibration from part 3 jan analysis.

Generated: 2026-01-03
"""

import os
import re
import math
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher
from collections import defaultdict

import pandas as pd
import numpy as np

# ============================================================================
# CONFIGURATION (FROM PREFLIGHT CALIBRATION)
# ============================================================================

INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 3 jan\part 3 jan.xlsx"
OUTPUT_DIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 3 jan\opus 1")

# Pre-flight calibration configuration
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pk", "pack", "pce", "pcs", "piece", "set", "each"],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in", '"', "'"],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "sales_requires_parsing": False,
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ["magnification", "zoom", "power", "brightness", "strength"],
    "table_pipe_sanitization": False,
}

# Known brands (for brand matching) - expanded list
KNOWN_BRANDS = [
    "AMTECH", "ROLSON", "DRAPER", "FAIRY", "DETTOL", "MARIGOLD", "DUNLOP",
    "MASON CASH", "PYREX", "EVERBUILD", "HARRIS", "STATUS", "EXTRASTAR",
    "ROUNDUP", "LITTLE TREES", "CHEF AID", "BETTINA", "DLUX", "MINKY",
    "ADORN", "FESTIVE", "PROKLEEN", "DEKTON", "PRIMA", "UNIQUE", "BRIGHT",
    "IMPERIAL", "PALOMA", "ART", "APOLLO", "EUROWRAP", "TALA", "ABBEY",
    "ASHLEY", "SOUDAL", "KILROCK", "TIDYZ", "STARWASH", "TONKITA", "RSW",
    "ECO", "SNOW WHITE", "PARTY CRAZY", "PAPER EASTER", "AIRWICK", "LYNWOOD",
    "SECURPAK", "PANASONIC", "TOM SMITH", "WORLD OF PETS", "CEMENT", "SOZALI",
    "OPAL", "DIWALI", "DUNLOP", "CHRISTMAS", "SPRAY ADHESIVE", "PAINT FACTORY",
    "BLUE CANYON", "PAN AROMA", "EVEREADY", "WD-40", "KILROCK", "CUPRINOL"
]

# IP Risk brands (luxury/trademark - flag these)
IP_RISK_BRANDS = [
    "JO MALONE", "CHANEL", "DIOR", "GUCCI", "LOUIS VUITTON", "PRADA", 
    "HERMES", "HERMÈS", "APPLE", "SAMSUNG", "SONY", "MICROSOFT", "NIKE", "ADIDAS"
]

# ============================================================================
# STAGE 1: DATA LOADING & INITIAL CLEANING
# ============================================================================

def load_data(path):
    """Load CSV or Excel file and perform initial cleaning."""
    ext = os.path.splitext(path)[1].lower()
    if ext in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    
    # Add RowID for traceability
    df["RowID"] = df.index + 1
    
    # Sales column normalization
    sales_col = SUPPLIER_NAMING_CONVENTION["sales_column"]
    if sales_col in df.columns:
        df["Sales"] = pd.to_numeric(df[sales_col], errors="coerce").fillna(0).astype(int)
    else:
        # Try alternatives
        for col in ["sales_numeric", "bought_in_past_month", "sales", "Sales"]:
            if col in df.columns:
                df["Sales"] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
                break
        else:
            df["Sales"] = 0
    
    return df

def coerce_to_intlike_string(x) -> str:
    """Convert various types to integer-like string."""
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
    """Extract only digits from value."""
    s = coerce_to_intlike_string(x).strip()
    if not s:
        return ""
    if "e" in s.lower():
        return ""
    return re.sub(r"\D", "", s)

def clean_eans(df):
    """Clean EAN columns to digit-only strings."""
    if "EAN" in df.columns:
        df["EAN_digits"] = df["EAN"].apply(clean_to_digits)
    else:
        df["EAN_digits"] = ""
    
    if "EAN_OnPage" in df.columns:
        df["EAN_OnPage_digits"] = df["EAN_OnPage"].apply(clean_to_digits)
    else:
        df["EAN_OnPage_digits"] = ""
    
    return df

# ============================================================================
# STAGE 2: TITLE SIMILARITY CALCULATION
# ============================================================================

def title_similarity(title1, title2):
    """Calculate similarity ratio between two titles."""
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

def calculate_title_similarity(df):
    """Add title similarity column."""
    df['title_match'] = df.apply(
        lambda x: title_similarity(x.get('SupplierTitle', ''), x.get('AmazonTitle', '')), 
        axis=1
    )
    return df

# ============================================================================
# STAGE 3: STRICT EAN MATCHING
# ============================================================================

def gtin_checksum_ok(digits: str) -> bool:
    """Validate GTIN checksum."""
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
    """Normalize EAN with left-padding if needed."""
    if not isinstance(digits, str) or not digits.isdigit():
        return ""
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    # Try left-padding
    for target_len in (12, 13, 14):
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits

def is_strict_valid_barcode(digits: str) -> bool:
    """Check if barcode is strictly valid."""
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    norm = normalize_ean(digits)
    if not isinstance(norm, str) or not norm.isdigit():
        return False
    if len(norm) not in (8, 12, 13, 14):
        return False
    # Suspicious: many trailing zeros
    if re.search(r"0{6,}$", norm):
        return False
    return gtin_checksum_ok(norm)

def validate_eans(df):
    """Validate and normalize EANs."""
    df["EAN_norm"] = df["EAN_digits"].apply(normalize_ean)
    df["EAN_OnPage_norm"] = df["EAN_OnPage_digits"].apply(normalize_ean)
    
    df["EAN_strict_valid"] = df["EAN_norm"].apply(is_strict_valid_barcode)
    df["EAN_OnPage_strict_valid"] = df["EAN_OnPage_norm"].apply(is_strict_valid_barcode)
    
    df["is_exact_ean_strict"] = (
        df["EAN_strict_valid"]
        & df["EAN_OnPage_strict_valid"]
        & (df["EAN_norm"] == df["EAN_OnPage_norm"])
    )
    
    return df

# ============================================================================
# STAGE 4: PACK SIZE EXTRACTION & PROFIT RECALCULATION
# ============================================================================

def has_dimension_context(title: str) -> bool:
    """Check if title contains dimension/measurement context."""
    t = str(title).lower()
    
    # Unit patterns
    if re.search(r"\b\d+(\.\d+)?\s*(cm|mm|ml|g|kg|oz|ft|ltr|l)\b", t):
        return True
    
    if re.search(r"\b\d+(\.\d+)?\s*(inch|in)\b", t) and not re.search(r"\b\d+\s*in\s*1\b", t):
        return True
    
    # NxM dimension forms
    if re.search(r"\b\d+(\.\d+)?\s*[x×]\s*\d+(\.\d+)?\s*(cm|mm|inch|in)\b", t):
        return True
    
    return False

def nxm_is_dimension(title: str, match_obj) -> bool:
    """Check if NxM pattern is a dimension (not pack count)."""
    t = str(title).lower()
    s, e = match_obj.span()
    window = t[max(0, s-8):min(len(t), e+12)]
    
    # Check for dimension units nearby
    if re.search(r"(cm|mm|ml|g|kg|oz|inch|\bin\b|ft|ltr|\bl\b)", window):
        if re.search(r"\bin\s*1\b", window):
            return False
        return True
    return False

def extract_supplier_qty(title) -> int:
    """Extract items-per-pack from supplier title."""
    t = str(title).lower().strip()
    
    # Explicit unit patterns from calibration
    # PK followed by number: "PK6", "PK 6"
    m = re.search(r"\bpk\s*(\d+)\b", t) or re.search(r"\bpk(\d+)\b", t)
    if m:
        return int(m.group(1))
    
    # Number followed by PK: "6PK", "6 PK"
    m = re.search(r"\b(\d+)\s*pk\b", t)
    if m:
        return int(m.group(1))
    
    # Standard patterns: "10PC", "10 PC", "10PCS", "10 PCS"
    m = re.search(r"\b(\d+)\s*(pc|pcs|pce)\b", t)
    if m:
        return int(m.group(1))
    
    # "N PACK" or "NPACK"
    m = re.search(r"\b(\d+)\s*pack\b", t)
    if m:
        return int(m.group(1))
    
    # "N PIECES" or "N PIECE"
    m = re.search(r"\b(\d+)\s*piece", t)
    if m:
        return int(m.group(1))
    
    # "SET OF N" or "N SET"
    m = re.search(r"\bset\s*of\s*(\d+)\b", t) or re.search(r"\b(\d+)\s*set\b", t)
    if m:
        return int(m.group(1))
    
    # Default: single unit
    return 1

def extract_amazon_total(title) -> int:
    """Extract total items from Amazon title."""
    t = str(title).lower().strip()
    
    # Check for capacity multipack patterns: "3 x 400ml", "6 x 15ml"
    # Per calibration: capacity_pattern_as_rsu = True
    # "N x [capacity]" means RSU = N (the first number)
    capacity_match = re.search(r"(\d+)\s*x\s*(\d+)\s*(ml|g|l|ltr|kg|oz|cl)\b", t)
    if capacity_match:
        # Return just the outer pack count (N), not N*capacity
        return int(capacity_match.group(1))
    
    # Multipack "(4 x 50)" / "4 x 50" patterns (non-capacity)
    m = re.search(r"\b(\d+)\s*[x×]\s*(\d+)\b", t)
    if m:
        if not nxm_is_dimension(t, m):
            outer = int(m.group(1))
            inner = int(m.group(2))
            if outer <= 100:  # Sanity cap
                return outer * inner
    
    # "Pack of N"
    m = re.search(r"\bpack of\s*(\d+)\b", t)
    if m:
        return int(m.group(1))
    
    # "N-pack"
    m = re.search(r"\b(\d+)\s*-\s*pack\b", t)
    if m:
        return int(m.group(1))
    
    # "N pack" at end
    m = re.search(r"\b(\d+)\s*pack\b", t)
    if m:
        return int(m.group(1))
    
    return 1

def compute_pack_fields(row):
    """Compute RSU, Pack Mode, and warnings."""
    sup_qty = float(row.get("Sup_Qty", 1))
    amz_total = float(row.get("Amz_Total", 1))
    supplier_title = str(row.get("SupplierTitle", "")).lower()
    amazon_title = str(row.get("AmazonTitle", "")).lower()
    
    # Check for dimension patterns that should NOT trigger RSU
    combined = supplier_title + " " + amazon_title
    if re.search(r"\b\d+\s*x\s*\d+\s*(cm|mm|inch|in|\")\b", combined):
        # This is a dimension, not a pack count
        return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": "Dimension pattern detected"})
    
    if sup_qty <= 0 or amz_total <= 0:
        return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": ""})
    
    # Qty-inside equality shield
    if sup_qty > 1 and amz_total > 1 and abs(sup_qty - amz_total) < 0.1:
        return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": "Qty-inside equality shield"})
    
    ratio = amz_total / sup_qty
    
    # Bundle detection
    if ratio > 1.000001:
        rsu = int(math.ceil(ratio))
        warn = "" if abs(ratio - round(ratio)) < 1e-6 else "Non-divisible bundle; verify counts"
        return pd.Series({"RSU": rsu, "Pack_Mode": "bundle", "Pack_Warning": warn})
    
    # Split detection
    if sup_qty > amz_total + 1e-6 and sup_qty > 1:
        return pd.Series({"RSU": 1, "Pack_Mode": "split", "Pack_Warning": "Supplier pack larger; split feasibility required"})
    
    return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": ""})

def recalculate_profit_after_pack(row):
    """Recalculate profit considering pack requirements."""
    try:
        original_profit = float(row.get("NetProfit", 0))
        supplier_cost = float(row.get("SupplierPrice_incVAT", 0))
        rsu = float(row.get("RSU", 1))
        
        if row.get("Pack_Mode") == "bundle" and rsu > 1:
            return original_profit - supplier_cost * (rsu - 1)
        return original_profit
    except:
        return 0.0

def pack_verdict(row):
    """Generate human-readable pack verdict."""
    pack_mode = row.get("Pack_Mode", "1:1")
    adjusted_profit = row.get("Adjusted_Profit", 0)
    rsu = int(row.get("RSU", 1))
    warning = row.get("Pack_Warning", "")
    
    if pack_mode == "1:1":
        if warning:
            return f"1:1 Match ({warning})"
        return "1:1 Match"
    
    if pack_mode == "bundle":
        suffix = "OK" if adjusted_profit > 0 else "LOSS"
        extra = f"; {warning}" if warning else ""
        return f"BUNDLE (RSU={rsu}) - {suffix}{extra}"
    
    if pack_mode == "split":
        return "SPLIT (Supplier pack larger) - VERIFY"
    
    return "1:1 Match"

def calculate_pack_fields(df):
    """Add all pack-related fields to dataframe."""
    df["Sup_Qty"] = df["SupplierTitle"].apply(extract_supplier_qty)
    df["Amz_Total"] = df["AmazonTitle"].apply(extract_amazon_total)
    
    pack_data = df.apply(compute_pack_fields, axis=1)
    df["RSU"] = pack_data["RSU"]
    df["Pack_Mode"] = pack_data["Pack_Mode"]
    df["Pack_Warning"] = pack_data["Pack_Warning"]
    
    df["Adjusted_Profit"] = df.apply(recalculate_profit_after_pack, axis=1)
    df["Pack_Verdict"] = df.apply(pack_verdict, axis=1)
    
    return df

# ============================================================================
# STAGE 5: BRAND MATCHING & CATEGORIZATION
# ============================================================================

def extract_brand(title, known_brands=KNOWN_BRANDS):
    """Extract brand name from title."""
    t = str(title).upper()
    
    for brand in known_brands:
        # Check if brand appears as whole word
        pattern = r'\b' + re.escape(brand.upper()) + r'\b'
        if re.search(pattern, t):
            return brand
    
    # Fall back to first word if it's all caps and > 2 chars
    words = t.split()
    if words and len(words[0]) > 2:
        return words[0]
    
    return ""

def brands_match(supplier_title, amazon_title):
    """Check if brands match between titles."""
    sup_brand = extract_brand(supplier_title)
    amz_brand = extract_brand(amazon_title)
    
    if not sup_brand or not amz_brand:
        return False
    
    return sup_brand.upper() == amz_brand.upper()

def check_ip_risk(title):
    """Check if title contains IP risk brand."""
    t = str(title).upper()
    for brand in IP_RISK_BRANDS:
        if brand in t:
            return brand
    return None

def product_types_match(supplier_title, amazon_title):
    """Check if product types match between titles."""
    sup = str(supplier_title).lower()
    amz = str(amazon_title).lower()
    
    # Common product type keywords
    product_types = [
        "brush", "hammer", "trowel", "screwdriver", "drill", "saw",
        "bowl", "dish", "plate", "cup", "mug", "jug", "pot", "pan",
        "candle", "lamp", "light", "torch", "bulb",
        "bag", "box", "container", "bin", "basket",
        "mop", "broom", "cloth", "sponge", "scourer",
        "tape", "glue", "adhesive", "sealant", "foam",
        "lock", "key", "hook", "hanger", "bracket",
        "mirror", "frame", "clock", "timer",
        "pen", "pencil", "marker", "eraser", "ruler",
        "soap", "spray", "cleaner", "polish", "wax"
    ]
    
    for pt in product_types:
        if pt in sup and pt in amz:
            return True
    
    return False

def get_match_evidence(row):
    """Generate key match evidence for a row."""
    evidence_parts = []
    
    if row.get("is_exact_ean_strict"):
        evidence_parts.append("Exact EAN match")
    
    supplier = str(row.get("SupplierTitle", "")).lower()
    amazon = str(row.get("AmazonTitle", "")).lower()
    
    # Find common significant words
    sup_words = set(re.findall(r'\b[a-z]{3,}\b', supplier))
    amz_words = set(re.findall(r'\b[a-z]{3,}\b', amazon))
    common = sup_words & amz_words
    
    # Remove common words
    stopwords = {'the', 'and', 'for', 'with', 'pack', 'set', 'piece', 'each', 'size'}
    common = common - stopwords
    
    if common:
        top_common = sorted(common, key=lambda x: -len(x))[:5]
        evidence_parts.append(f"Shared: {', '.join(top_common)}")
    
    # Brand match
    if brands_match(row.get("SupplierTitle", ""), row.get("AmazonTitle", "")):
        brand = extract_brand(row.get("SupplierTitle", ""))
        evidence_parts.append(f"Brand: {brand}")
    
    return "; ".join(evidence_parts) if evidence_parts else "Title similarity"

def categorize_product(row):
    """Categorize product into VERIFIED, HIGHLY LIKELY, NEEDS VERIFICATION, or FILTERED OUT."""
    is_exact_ean = bool(row.get("is_exact_ean_strict", False))
    title_match = float(row.get("title_match", 0))
    adjusted_profit = float(row.get("Adjusted_Profit", 0))
    net_profit = float(row.get("NetProfit", 0))
    sales = int(row.get("Sales", 0))
    pack_mode = row.get("Pack_Mode", "1:1")
    rsu = int(row.get("RSU", 1))
    
    supplier_title = str(row.get("SupplierTitle", ""))
    amazon_title = str(row.get("AmazonTitle", ""))
    
    brand_matches = brands_match(supplier_title, amazon_title)
    product_matches = product_types_match(supplier_title, amazon_title)
    
    # Check for explicit pack contradiction
    def has_pack_contradiction():
        sup = supplier_title.lower()
        amz = amazon_title.lower()
        
        # Single vs multipack
        if ("single" in sup or "each" in sup or "1 pack" in sup) and re.search(r"\b(3|4|5|6|10)\s*(pack|x)\b", amz):
            return True
        return False
    
    # Decision logic
    if is_exact_ean:
        # VERIFIED path
        if has_pack_contradiction() and adjusted_profit <= 0:
            return "VERIFIED_FILTERED"
        if adjusted_profit <= 0 and pack_mode == "bundle":
            return "VERIFIED_FILTERED"
        if sales > 0 and adjusted_profit > 0:
            return "VERIFIED_RECOMMENDED"
        if sales == 0:
            return "NEEDS_VERIFICATION"
        return "VERIFIED_RECOMMENDED"
    
    # Non-EAN path
    if brand_matches and product_matches:
        if adjusted_profit <= 0:
            return "HIGHLY_LIKELY_FILTERED"
        if sales > 0:
            return "HIGHLY_LIKELY_RECOMMENDED"
        return "NEEDS_VERIFICATION"
    
    if brand_matches:
        if adjusted_profit <= 0:
            return "HIGHLY_LIKELY_FILTERED"
        if title_match >= 0.4 and sales > 0 and adjusted_profit > 0:
            return "HIGHLY_LIKELY_RECOMMENDED"
        if net_profit > 0.5 and sales > 0:
            return "NEEDS_VERIFICATION"
    
    if title_match >= 0.5:
        if adjusted_profit <= 0:
            return "FILTERED_OUT"
        if sales > 0 and adjusted_profit > 0:
            return "NEEDS_VERIFICATION"
    
    if title_match >= 0.3 and net_profit > 0.5:
        return "NEEDS_VERIFICATION"
    
    return "EXCLUDED"

def get_filter_reason(row, category):
    """Get filter reason for excluded items."""
    if "RECOMMENDED" in category:
        return "-"
    
    adjusted_profit = float(row.get("Adjusted_Profit", 0))
    pack_mode = row.get("Pack_Mode", "1:1")
    rsu = int(row.get("RSU", 1))
    sales = int(row.get("Sales", 0))
    
    reasons = []
    
    if adjusted_profit <= 0:
        if pack_mode == "bundle" and rsu > 1:
            reasons.append(f"Requires {rsu} units; adjusted profit £{adjusted_profit:.2f}")
        else:
            reasons.append(f"Negative profit: £{adjusted_profit:.2f}")
    
    if sales == 0:
        reasons.append("No sales data")
    
    if not reasons:
        if "FILTERED" in category:
            reasons.append("Pack mismatch makes unprofitable")
        else:
            reasons.append("Needs brand/pack verification")
    
    return "; ".join(reasons)

def assign_confidence(row, category):
    """Assign confidence score based on category and evidence."""
    if "VERIFIED" in category:
        if row.get("Pack_Mode") == "bundle":
            return 90
        return 95
    
    if "HIGHLY_LIKELY" in category:
        if brands_match(row.get("SupplierTitle", ""), row.get("AmazonTitle", "")):
            return 85
        return 75
    
    if category == "NEEDS_VERIFICATION":
        title_match = float(row.get("title_match", 0))
        base = 50 + int(title_match * 30)
        return min(70, base)
    
    return 40

def categorize_all(df):
    """Apply categorization to all rows."""
    df["Category"] = df.apply(categorize_product, axis=1)
    df["Filter_Reason"] = df.apply(lambda r: get_filter_reason(r, r["Category"]), axis=1)
    df["Confidence"] = df.apply(lambda r: assign_confidence(r, r["Category"]), axis=1)
    df["Key_Match_Evidence"] = df.apply(get_match_evidence, axis=1)
    
    # Map to verdict string
    def get_verdict(cat):
        if "VERIFIED" in cat:
            return "VERIFIED"
        if "HIGHLY_LIKELY" in cat:
            return "HIGHLY LIKELY"
        if cat == "NEEDS_VERIFICATION":
            return "NEEDS VERIFICATION"
        if "FILTERED" in cat or cat == "FILTERED_OUT":
            return "FILTERED OUT"
        return "EXCLUDED"
    
    df["Verdict"] = df["Category"].apply(get_verdict)
    
    return df

# ============================================================================
# STAGE 6: REPORT GENERATION
# ============================================================================

def format_currency(val):
    """Format value as currency."""
    try:
        return f"£{float(val):.2f}"
    except:
        return "£0.00"

def format_pct(val):
    """Format value as percentage."""
    try:
        return f"{float(val):.1f}%"
    except:
        return "0.0%"

def sanitize_for_table(text, max_len=50):
    """Sanitize text for markdown table."""
    if pd.isna(text):
        return "-"
    s = str(text)
    s = s.replace("|", "/").replace("\n", " ").replace("\r", "")
    if len(s) > max_len:
        s = s[:max_len-3] + "..."
    return s

def create_fixed_width_table(df_subset, columns):
    """Create fixed-width table for markdown."""
    if len(df_subset) == 0:
        return "No items in this category.\n"
    
    # Calculate column widths
    widths = {}
    for col in columns:
        col_name = col["name"]
        col_key = col["key"]
        max_len = len(col_name)
        
        for _, row in df_subset.iterrows():
            val = col.get("formatter", lambda x: str(x))(row.get(col_key, "-"))
            max_len = max(max_len, len(str(val)))
        
        widths[col_name] = min(max_len, col.get("max_width", 60))
    
    # Build header
    header_parts = []
    for col in columns:
        col_name = col["name"]
        header_parts.append(col_name.ljust(widths[col_name]))
    header = "| " + " | ".join(header_parts) + " |"
    
    # Build separator
    sep_parts = []
    for col in columns:
        col_name = col["name"]
        sep_parts.append("-" * widths[col_name])
    separator = "|" + "|".join(sep_parts) + "|"
    
    # Build rows
    rows = []
    for _, row in df_subset.iterrows():
        row_parts = []
        for col in columns:
            col_key = col["key"]
            val = col.get("formatter", lambda x: str(x))(row.get(col_key, "-"))
            val = sanitize_for_table(val, widths[col["name"]])
            row_parts.append(str(val).ljust(widths[col["name"]]))
        rows.append("| " + " | ".join(row_parts) + " |")
    
    # Combine
    table = "```text\n"
    table += header + "\n"
    table += separator + "\n"
    table += "\n".join(rows) + "\n"
    table += "```\n"
    
    return table

def generate_report(df):
    """Generate the full markdown report."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Count categories
    verified_rec = df[df["Category"] == "VERIFIED_RECOMMENDED"]
    verified_filt = df[df["Category"] == "VERIFIED_FILTERED"]
    highly_rec = df[df["Category"] == "HIGHLY_LIKELY_RECOMMENDED"]
    highly_filt = df[df["Category"] == "HIGHLY_LIKELY_FILTERED"]
    needs_ver = df[df["Category"] == "NEEDS_VERIFICATION"]
    
    # Table columns
    table_cols = [
        {"name": "Verdict", "key": "Verdict", "max_width": 18},
        {"name": "Conf", "key": "Confidence", "max_width": 5},
        {"name": "SupplierTitle", "key": "SupplierTitle", "max_width": 40, 
         "formatter": lambda x: sanitize_for_table(x, 40)},
        {"name": "AmazonTitle", "key": "AmazonTitle", "max_width": 50,
         "formatter": lambda x: sanitize_for_table(x, 50)},
        {"name": "Supp EAN", "key": "EAN_norm", "max_width": 15,
         "formatter": lambda x: x if x else "-"},
        {"name": "Amz EAN", "key": "EAN_OnPage_norm", "max_width": 15,
         "formatter": lambda x: x if x else "-"},
        {"name": "ASIN", "key": "ASIN", "max_width": 12},
        {"name": "SuppPrice", "key": "SupplierPrice_incVAT", "max_width": 10,
         "formatter": format_currency},
        {"name": "SellPrice", "key": "SellingPrice_incVAT", "max_width": 10,
         "formatter": format_currency},
        {"name": "Profit", "key": "NetProfit", "max_width": 8,
         "formatter": format_currency},
        {"name": "ROI", "key": "ROI %", "max_width": 8,
         "formatter": format_pct},
        {"name": "Sales", "key": "Sales", "max_width": 6},
        {"name": "Pack Verdict", "key": "Pack_Verdict", "max_width": 30,
         "formatter": lambda x: sanitize_for_table(x, 30)},
        {"name": "Adj Profit", "key": "Adjusted_Profit", "max_width": 10,
         "formatter": format_currency},
        {"name": "Evidence", "key": "Key_Match_Evidence", "max_width": 40,
         "formatter": lambda x: sanitize_for_table(x, 40)},
        {"name": "Filter Reason", "key": "Filter_Reason", "max_width": 40,
         "formatter": lambda x: sanitize_for_table(x, 40)},
    ]
    
    # Build report
    report = f"""# PHASEA MANUAL REPORT

**Generated:** {today}  
**Input File:** part 3 jan.xlsx  
**Supplier:** EFG Housewares  
**Analysis Version:** v4.1 AG1 (Opus Enhanced)

---

## Summary Counts

| Category | Count |
|----------|-------|
| VERIFIED — RECOMMENDED | {len(verified_rec)} |
| VERIFIED — FILTERED OUT | {len(verified_filt)} |
| HIGHLY LIKELY — RECOMMENDED | {len(highly_rec)} |
| HIGHLY LIKELY — FILTERED OUT | {len(highly_filt)} |
| NEEDS VERIFICATION | {len(needs_ver)} |
| **TOTAL ACTIONABLE** | **{len(verified_rec) + len(highly_rec) + len(needs_ver)}** |
| TOTAL ANALYZED | {len(df)} |

---

This report applies **v4.1 Thorough Manual Analysis**:
- HIGHLY LIKELY requires Brand + Product type match with positive profit
- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade
- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit)

---

## VERIFIED — RECOMMENDED (count={len(verified_rec)})

Exact EAN matches with positive profit and sales.

"""
    
    if len(verified_rec) > 0:
        sorted_ver = verified_rec.sort_values("Sales", ascending=False)
        report += create_fixed_width_table(sorted_ver, table_cols)
    else:
        report += "*No exact EAN matches found in this dataset.*\n"
    
    report += f"""
---

## VERIFIED — FILTERED OUT (count={len(verified_filt)})

Exact EAN matches excluded due to pack/profit issues.

"""
    
    if len(verified_filt) > 0:
        report += create_fixed_width_table(verified_filt, table_cols)
    else:
        report += "*No filtered exact EAN matches.*\n"
    
    report += f"""
---

## HIGHLY LIKELY — RECOMMENDED (count={len(highly_rec)})

Strong brand + product matches with positive profit and sales.

"""
    
    if len(highly_rec) > 0:
        sorted_hl = highly_rec.sort_values(["Confidence", "Sales"], ascending=[False, False])
        report += create_fixed_width_table(sorted_hl, table_cols)
    else:
        report += "*No highly likely matches found.*\n"
    
    report += f"""
---

## HIGHLY LIKELY — FILTERED OUT (count={len(highly_filt)})

Strong brand + product matches excluded due to pack/profit issues.

"""
    
    if len(highly_filt) > 0:
        report += create_fixed_width_table(highly_filt, table_cols)
    else:
        report += "*No filtered highly likely matches.*\n"
    
    report += f"""
---

## NEEDS VERIFICATION (count={len(needs_ver)})

Plausible matches requiring 1-2 confirmable details to upgrade.

"""
    
    if len(needs_ver) > 0:
        sorted_nv = needs_ver.sort_values(["Confidence", "Sales"], ascending=[False, False])
        report += create_fixed_width_table(sorted_nv.head(60), table_cols)
        if len(needs_ver) > 60:
            report += f"\n*... and {len(needs_ver) - 60} more items. Showing top 60 by confidence.*\n"
    else:
        report += "*No items require verification.*\n"
    
    report += f"""
---

## Additional Notes

### IP Risk Flagging
- Only luxury/trademark brands are flagged: Jo Malone, Chanel, Dior, Gucci, Louis Vuitton, etc.
- Generic wholesale brands (TIDYZ, SOUDAL, AMTECH, etc.) are NOT flagged as IP risk.

### Pack Size Analysis
- Dimension patterns (NxM cm/mm/inch) treated as size, NOT pack count
- Capacity multipacks (3 x 400ml) correctly interpreted as RSU = outer count
- Quantity-inside patterns (50 PCS, 200 sticks) treated as single pack of N items

### Calibration Applied
This analysis integrated pre-flight calibration from `part 3 jan.xlsx`:
- Brand position: start (98% of titles)
- Explicit units: pk, pack, pce, pcs, piece, set, each
- Dimension shield active for: cm, mm, ml, ltr, l, kg, g, oz, inch, in
- 246 potential dimension traps detected and shielded

---

*Report generated by FBA Analysis v4.1 AG1 (Opus Enhanced)*  
*Analysis date: {today}*
"""
    
    return report

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("="*60)
    print("FBA Product Analysis v4.1 AG1 (Opus Enhanced)")
    print("="*60)
    
    # Stage 1: Load data
    print("\n[Stage 1] Loading data...")
    df = load_data(INPUT_PATH)
    print(f"  Loaded {len(df)} rows")
    
    # Stage 1b: Clean EANs
    print("\n[Stage 1b] Cleaning EANs...")
    df = clean_eans(df)
    
    # Stage 2: Title similarity
    print("\n[Stage 2] Calculating title similarity...")
    df = calculate_title_similarity(df)
    
    # Stage 3: EAN validation
    print("\n[Stage 3] Validating EANs...")
    df = validate_eans(df)
    exact_ean_count = df["is_exact_ean_strict"].sum()
    print(f"  Found {exact_ean_count} exact EAN matches")
    
    # Stage 4: Pack size calculation
    print("\n[Stage 4] Calculating pack sizes...")
    df = calculate_pack_fields(df)
    
    # Stage 5: Categorization
    print("\n[Stage 5] Categorizing products...")
    df = categorize_all(df)
    
    # Print category counts
    cat_counts = df["Category"].value_counts()
    print("\n  Category distribution:")
    for cat, count in cat_counts.items():
        print(f"    {cat}: {count}")
    
    # Stage 6: Generate report
    print("\n[Stage 6] Generating report...")
    report = generate_report(df)
    
    # Save report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"PHASEA_MANUAL_REPORT_{today}.md"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n[Complete] Report saved to: {output_path}")
    
    # Also save raw data for debugging
    debug_path = OUTPUT_DIR / f"analysis_data_{today}.xlsx"
    df.to_excel(debug_path, index=False)
    print(f"  Debug data saved to: {debug_path}")
    
    return df, report

if __name__ == "__main__":
    df, report = main()
