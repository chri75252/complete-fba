"""
FBA Product Analysis V4.1 (AG1) - Main Analysis Script
Incorporates Preflight Calibration for PART_DEC_31.csv
Generated: 2026-01-01
"""

import os
import re
import math
import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from datetime import datetime

# --- CALIBRATION CONFIGURATION (From Preflight Analysis of PART_DEC_31.csv) ---
SUPPLIER_NAMING_CONVENTION = {
    # Explicit unit keywords to recognize as pack quantity indicators
    "explicit_units": ["pc", "pcs", "pce", "pk", "pack", "pieces", "scourer", "scourers", "cases"],
    
    # Shorthand patterns: matches like "2PC", "8PC", "PK6", "5PACK"
    "shorthand_patterns": [
        r"(\d+)\s*PC\b",      # 2PC, 8 PC
        r"(\d+)\s*PCS\b",     # 10PCS
        r"(\d+)\s*PCE\b",     # 6PCE
        r"PK\s*(\d+)",        # PK6, PK8
        r"(\d+)\s*PACK\b",    # 5PACK
        r"(\d+)\s*PIECES\b",  # 12 PIECES
        r"(\d+)\s*CASES\b",   # 100 CASES
    ],
    
    # WARNING: Trailing numbers in this dataset are UNRELIABLE
    "allow_trailing_number_as_qty": False,
    
    # No leading multipliers detected in this dataset
    "leading_multiplier_check": False,
    
    # Keywords that indicate dimensions/measurements, NOT pack quantities
    "dimension_shield_keywords": [
        "cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in", "ft"
    ],
    
    # Dimension regex patterns to exclude from pack quantity extraction
    "dimension_patterns": [
        r"\d+\s*CM\b",
        r"\d+\s*MM\b",
        r"\d+\s*ML\b",
        r"\d+\.?\d*\s*L\b",
        r"\d+\s*G\b",
        r"\d+\s*KG\b",
        r"\d+\s*OZ\b",
        r"\d+\s*INCH\b",
        r"\d+\s*X\s*\d+\s*(CM|MM|INCH|IN)\b",
    ],
    
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "sales_needs_parsing": False,
    "single_unit_keywords": ["each"],
}

# Known IP risk brands (luxury/trademark)
IP_RISK_BRANDS = {
    "jo malone", "chanel", "dior", "gucci", "louis vuitton", "prada", 
    "hermes", "hermès", "apple", "samsung", "sony", "microsoft", "nike", "adidas"
}

# Known SAFE wholesale/generic brands (NOT IP risk)
SAFE_BRANDS = {
    "tidyz", "soudal", "amtech", "rolson", "draper", "fairy", "dettol", 
    "marigold", "dunlop", "mason cash", "pyrex", "everbuild", "harris", 
    "status", "extrastar", "roundup", "little trees", "chef aid", "prima",
    "bettina", "dlux", "minky", "starwash", "tala", "dekton", "securpak",
    "lynwood", "abbey", "prokleen", "eurowrap", "airwick", "panasonic"
}

# ==================== STAGE 1: Data Loading ====================
print("=" * 60)
print("STAGE 1: Loading and Cleaning Data")
print("=" * 60)

INPUT_PATH = r"PART_DEC_31.csv"
ext = os.path.splitext(INPUT_PATH)[1].lower()

if ext in [".xlsx", ".xls"]:
    df = pd.read_excel(INPUT_PATH)
else:
    df = pd.read_csv(INPUT_PATH, encoding='utf-8-sig')

print(f"Loaded {len(df)} rows from {INPUT_PATH}")

# Add RowID for traceability
df["RowID"] = df.index + 1

# Sales column normalization (using calibration)
sales_col = SUPPLIER_NAMING_CONVENTION["sales_column"]
if sales_col in df.columns:
    df["Sales"] = pd.to_numeric(df[sales_col], errors="coerce").fillna(0).astype(int)
    print(f"Using '{sales_col}' as Sales column")
else:
    df["Sales"] = 0
    print("WARNING: No sales column found, defaulting to 0")

# EAN cleaning functions
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

if "EAN" in df.columns:
    df["EAN_digits"] = df["EAN"].apply(clean_to_digits)
else:
    df["EAN_digits"] = ""

if "EAN_OnPage" in df.columns:
    df["EAN_OnPage_digits"] = df["EAN_OnPage"].apply(clean_to_digits)
else:
    df["EAN_OnPage_digits"] = ""

print(f"EAN columns cleaned")

# ==================== STAGE 2: Title Similarity ====================
print("\n" + "=" * 60)
print("STAGE 2: Calculating Title Similarity")
print("=" * 60)

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x.get('SupplierTitle', ''), x.get('AmazonTitle', '')), axis=1)
print(f"Title similarity calculated. Mean: {df['title_match'].mean():.3f}")

# ==================== STAGE 3: Strict EAN Matching ====================
print("\n" + "=" * 60)
print("STAGE 3: Strict EAN Validation & Matching")
print("=" * 60)

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

# ==================== STAGE 4: Pack Size Extraction ====================
print("\n" + "=" * 60)
print("STAGE 4: Pack Size Extraction & Profit Recalculation")
print("=" * 60)

def _has_dimension_context(title: str) -> bool:
    """Check if title contains dimension/measurement patterns"""
    t = str(title).lower()
    
    # Check for calibrated dimension patterns
    for pattern in SUPPLIER_NAMING_CONVENTION["dimension_patterns"]:
        if re.search(pattern, t, re.IGNORECASE):
            return True
    
    # Additional dimension checks
    if re.search(r"\b\d+(\.\d+)?\s*(cm|mm|ml|g|kg|oz|ft|ltr|l)\b", t):
        return True
    if re.search(r"\b\d+(\.\d+)?\s*(inch|in)\b", t) and not re.search(r"\b\d+\s*in\s*1\b", t):
        return True
    if re.search(r"\b\d+(\.\d+)?\s*[x×]\s*\d+(\.\d+)?\s*(cm|mm|inch|in)\b", t):
        return True
    return False

def _nxm_is_dimension(title: str, span: tuple) -> bool:
    """Check if NxM pattern in title is a dimension (not pack count)"""
    t = str(title).lower()
    s, e = span
    window = t[max(0, s-8):min(len(t), e+12)]
    
    dim_keys = SUPPLIER_NAMING_CONVENTION["dimension_shield_keywords"]
    for key in dim_keys:
        if key in window:
            if key == "in" and re.search(r"\bin\s*1\b", window):
                return False
            return True
    return False

def extract_supplier_qty(title) -> int:
    """Extract items per supplier pack using calibrated patterns"""
    t = str(title).upper().strip()
    
    # Check for "EACH" keyword (single unit)
    for kw in SUPPLIER_NAMING_CONVENTION["single_unit_keywords"]:
        if kw.upper() in t:
            return 1
    
    # Check calibrated shorthand patterns
    for pattern in SUPPLIER_NAMING_CONVENTION["shorthand_patterns"]:
        m = re.search(pattern, t, re.IGNORECASE)
        if m:
            # Get the captured group (digit)
            for g in m.groups():
                if g and g.isdigit():
                    qty = int(g)
                    if 1 < qty <= 500:  # Reasonable range
                        return qty
    
    # Trailing number check (DISABLED per calibration)
    if SUPPLIER_NAMING_CONVENTION["allow_trailing_number_as_qty"]:
        m = re.search(r"\s+(\d+)$", t)
        if m:
            qty = int(m.group(1))
            if 2 <= qty <= 500:
                return qty
    
    return 1

def extract_amazon_total(title) -> int:
    """Extract Amazon total items (handling multipacks)"""
    t = str(title).lower().strip()
    
    # Multipack "(4 x 50)" / "4 x 50" patterns
    m = re.search(r"\b(\d+)\s*[x×]\s*(\d+)\b", t)
    if m:
        span = m.span()
        if not _nxm_is_dimension(t, span):
            outer = int(m.group(1))
            inner = int(m.group(2))
            if outer <= 100 and inner <= 1000:  # Sanity cap
                return outer * inner
    
    # "Pack of 10", "10-pack", "10 pack"
    m = re.search(r"\bpack\s*of\s*(\d+)\b", t)
    if m:
        return int(m.group(1))
    
    m = re.search(r"\b(\d+)\s*-\s*pack\b", t)
    if m:
        return int(m.group(1))
    
    m = re.search(r"\b(\d+)\s*pack\b", t)
    if m:
        val = int(m.group(1))
        if val <= 100:
            return val
    
    return 1

df["Sup_Qty"] = df["SupplierTitle"].apply(extract_supplier_qty)
df["Amz_Total"] = df["AmazonTitle"].apply(extract_amazon_total)

def compute_pack_fields(row):
    sup_qty = float(row["Sup_Qty"])
    amz_total = float(row["Amz_Total"])
    
    if sup_qty <= 0 or amz_total <= 0:
        return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": ""})
    
    # Numeric Equality Shield: if both show same quantity-inside, treat as 1:1
    if sup_qty > 1 and amz_total > 1 and abs(sup_qty - amz_total) < 0.1:
        return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": "Qty-inside equality shield"})
    
    ratio = amz_total / sup_qty
    
    # Bundle (Amazon needs more items than supplier provides)
    if ratio > 1.000001:
        rsu = int(math.ceil(ratio))
        warn = "" if abs(ratio - round(ratio)) < 1e-6 else "Non-divisible bundle; verify counts"
        return pd.Series({"RSU": rsu, "Pack_Mode": "bundle", "Pack_Warning": warn})
    
    # Split (Supplier pack is larger than Amazon total)
    if sup_qty > amz_total + 1e-6 and sup_qty > 1:
        return pd.Series({"RSU": 1, "Pack_Mode": "split", "Pack_Warning": "Supplier pack larger; split feasibility required"})
    
    return pd.Series({"RSU": 1, "Pack_Mode": "1:1", "Pack_Warning": ""})

df[["RSU", "Pack_Mode", "Pack_Warning"]] = df.apply(compute_pack_fields, axis=1)

def recalculate_profit_after_pack(row):
    try:
        original_profit = float(row.get("NetProfit", 0))
        supplier_cost = float(row.get("SupplierPrice_incVAT", 0))
        rsu = float(row.get("RSU", 1))
        
        if row.get("Pack_Mode") == "bundle" and rsu > 1:
            return original_profit - supplier_cost * (rsu - 1)
        return original_profit
    except:
        return 0.0

df["Adjusted_Profit"] = df.apply(recalculate_profit_after_pack, axis=1)

def pack_verdict(row):
    if row["Pack_Mode"] == "1:1":
        return "1:1 Match"
    if row["Pack_Mode"] == "bundle":
        suffix = "OK" if row["Adjusted_Profit"] > 0 else "LOSS"
        extra = f"; {row['Pack_Warning']}" if row["Pack_Warning"] else ""
        return f"BUNDLE (RSU={int(row['RSU'])}) - {suffix}{extra}"
    if row["Pack_Mode"] == "split":
        return "SPLIT - VERIFY"
    return "1:1 Match"

df["Pack_Verdict"] = df.apply(pack_verdict, axis=1)

print(f"Pack analysis complete. Bundle cases: {(df['Pack_Mode'] == 'bundle').sum()}")

# ==================== STAGE 5: Brand Detection & Categorization ====================
print("\n" + "=" * 60)
print("STAGE 5: Brand Detection & Initial Categorization")
print("=" * 60)

def extract_brand(title, position="start"):
    """Extract brand from title based on calibrated position"""
    if pd.isna(title):
        return ""
    
    t = str(title).strip()
    words = t.split()
    
    if not words:
        return ""
    
    if position == "start":
        # First word(s) that are uppercase
        brand_parts = []
        for word in words:
            if word.isupper() and len(word) > 1 and word.isalpha():
                brand_parts.append(word)
            else:
                break
        return " ".join(brand_parts) if brand_parts else words[0].upper()
    
    return words[0].upper()

def brands_match(sup_title, amz_title) -> tuple:
    """Check if brands match between supplier and Amazon titles"""
    sup_brand = extract_brand(sup_title, SUPPLIER_NAMING_CONVENTION["brand_position"])
    
    # For Amazon, check if brand appears anywhere
    amz_lower = str(amz_title).lower() if not pd.isna(amz_title) else ""
    sup_brand_lower = sup_brand.lower()
    
    if len(sup_brand_lower) >= 3 and sup_brand_lower in amz_lower:
        return (True, sup_brand)
    
    # Check for multi-word brands
    multi_word_brands = ["mason cash", "chef aid", "little trees", "blue canyon"]
    for brand in multi_word_brands:
        if brand in str(sup_title).lower() and brand in amz_lower:
            return (True, brand.upper())
    
    return (False, sup_brand)

def get_product_type(title) -> str:
    """Extract core product type from title"""
    if pd.isna(title):
        return ""
    
    t = str(title).lower()
    
    # Common product types
    product_types = [
        "hammer", "trowel", "brush", "bowl", "plate", "candle", "torch", "lamp",
        "peeler", "screwdriver", "pliers", "scissors", "knife", "spoon", "fork",
        "cup", "mug", "glass", "container", "bag", "bags", "bin", "bucket",
        "mop", "broom", "sponge", "scourer", "cloth", "duster", "wipes",
        "tape", "glue", "adhesive", "foam", "sealant", "filler",
        "cable", "wire", "plug", "socket", "bulb", "battery",
        "lock", "key", "hinge", "screw", "nail", "bolt", "bracket"
    ]
    
    for ptype in product_types:
        if ptype in t:
            return ptype
    
    return ""

def check_ip_risk(title) -> bool:
    """Check if title contains IP-risk luxury brands"""
    t = str(title).lower() if not pd.isna(title) else ""
    
    for brand in IP_RISK_BRANDS:
        if brand in t:
            return True
    return False

df["Sup_Brand"] = df["SupplierTitle"].apply(lambda x: extract_brand(x, "start"))
df["Brand_Match"], df["Matched_Brand"] = zip(*df.apply(lambda r: brands_match(r["SupplierTitle"], r["AmazonTitle"]), axis=1))
df["IP_Risk"] = df.apply(lambda r: check_ip_risk(r["SupplierTitle"]) or check_ip_risk(r["AmazonTitle"]), axis=1)

print(f"Brand matches detected: {df['Brand_Match'].sum()}")
print(f"IP Risk flags: {df['IP_Risk'].sum()}")

# ==================== STAGE 5B: Thorough Manual Categorization ====================
print("\n" + "=" * 60)
print("STAGE 5B: Thorough Manual Categorization")
print("=" * 60)

def get_key_match_evidence(row) -> str:
    """Generate evidence string based on row data"""
    evidence_parts = []
    
    if row.get("is_exact_ean_strict"):
        evidence_parts.append("Exact EAN match")
    
    if row.get("Brand_Match"):
        evidence_parts.append(f"Brand: {row.get('Matched_Brand', '')}")
    
    # Find common keywords
    sup = str(row.get("SupplierTitle", "")).lower()
    amz = str(row.get("AmazonTitle", "")).lower()
    
    sup_words = set(re.findall(r'\b[a-z]{3,}\b', sup))
    amz_words = set(re.findall(r'\b[a-z]{3,}\b', amz))
    common = sup_words & amz_words
    
    # Filter out common stopwords
    stopwords = {"the", "and", "for", "with", "from", "that", "this", "pack", "set"}
    common = common - stopwords
    
    if common:
        evidence_parts.append(f"Keywords: {', '.join(list(common)[:5])}")
    
    if row.get("title_match", 0) >= 0.5:
        evidence_parts.append(f"Title sim: {row['title_match']:.0%}")
    
    return "; ".join(evidence_parts) if evidence_parts else "-"

def categorize_thorough(row) -> dict:
    """Apply thorough manual analysis to categorize each row"""
    result = {
        "verdict": "EXCLUDE",
        "confidence": 0,
        "filter_reason": "-",
        "key_evidence": ""
    }
    
    is_exact_ean = bool(row.get("is_exact_ean_strict", False))
    brand_match = bool(row.get("Brand_Match", False))
    title_sim = float(row.get("title_match", 0.0))
    sales = int(row.get("Sales", 0))
    adjusted_profit = float(row.get("Adjusted_Profit", 0))
    net_profit = float(row.get("NetProfit", 0))
    rsu = int(row.get("RSU", 1))
    pack_mode = row.get("Pack_Mode", "1:1")
    ip_risk = bool(row.get("IP_Risk", False))
    
    result["key_evidence"] = get_key_match_evidence(row)
    
    # === EXACT EAN MATCH PATH ===
    if is_exact_ean:
        # Check for pack contradictions
        if pack_mode == "bundle" and adjusted_profit <= 0:
            result["verdict"] = "VERIFIED_EXCLUDED"
            result["confidence"] = 95
            result["filter_reason"] = f"Pack mismatch (RSU={rsu}); Adj Profit: £{adjusted_profit:.2f}"
            return result
        
        # Check profitability
        if adjusted_profit <= 0:
            result["verdict"] = "VERIFIED_EXCLUDED"
            result["confidence"] = 95
            result["filter_reason"] = f"Negative profit: £{adjusted_profit:.2f}"
            return result
        
        # Check sales (if zero, might still be valid but needs verification)
        if sales <= 0:
            result["verdict"] = "NEEDS_VERIFICATION"
            result["confidence"] = 85
            result["filter_reason"] = "Exact EAN but Sales=0; verify listing is active"
            return result
        
        # Valid VERIFIED
        result["verdict"] = "VERIFIED"
        result["confidence"] = 95
        result["filter_reason"] = "-"
        return result
    
    # === NON-EAN MATCH PATH ===
    
    # Check for IP risk
    if ip_risk:
        result["verdict"] = "EXCLUDE"
        result["confidence"] = 0
        result["filter_reason"] = "Potential IP risk (luxury brand)"
        return result
    
    # Check profitability first
    if adjusted_profit <= 0:
        if brand_match or title_sim >= 0.4:
            result["verdict"] = "HL_EXCLUDED"
            result["confidence"] = 70
            result["filter_reason"] = f"Match likely but unprofitable (Adj: £{adjusted_profit:.2f})"
            return result
        return result  # Just exclude silently
    
    # HIGHLY LIKELY: Brand + reasonable title match + profitable
    if brand_match and adjusted_profit > 0 and title_sim >= 0.25:
        if sales > 0:
            result["verdict"] = "HIGHLY_LIKELY"
            result["confidence"] = 85
            result["filter_reason"] = "-"
        else:
            result["verdict"] = "NEEDS_VERIFICATION"
            result["confidence"] = 75
            result["filter_reason"] = "Brand match but Sales=0"
        return result
    
    # HIGHLY LIKELY: Strong title match without brand
    if title_sim >= 0.55 and adjusted_profit > 0:
        if sales > 0:
            result["verdict"] = "HIGHLY_LIKELY"
            result["confidence"] = 80
            result["filter_reason"] = "-"
        else:
            result["verdict"] = "NEEDS_VERIFICATION"
            result["confidence"] = 70
            result["filter_reason"] = "Strong title match but Sales=0"
        return result
    
    # NEEDS VERIFICATION: Moderate confidence
    if title_sim >= 0.35 and adjusted_profit > 0.50 and net_profit > 0.50:
        if sales > 0:
            result["verdict"] = "NEEDS_VERIFICATION"
            result["confidence"] = 65
            result["filter_reason"] = "Moderate title match; verify brand/model"
        else:
            result["verdict"] = "NEEDS_VERIFICATION"
            result["confidence"] = 55
            result["filter_reason"] = "Moderate match but Sales=0"
        return result
    
    # Weak evidence - exclude
    return result

# Apply categorization
categorization_results = df.apply(categorize_thorough, axis=1, result_type='expand')
df["Verdict"] = categorization_results["verdict"]
df["Confidence"] = categorization_results["confidence"]
df["Filter_Reason"] = categorization_results["filter_reason"]
df["Key_Match_Evidence"] = categorization_results["key_evidence"]

# Count categories
print("\nCategorization Results:")
for verdict in df["Verdict"].unique():
    count = (df["Verdict"] == verdict).sum()
    print(f"  {verdict}: {count}")

# ==================== STAGE 6: Generate Report ====================
print("\n" + "=" * 60)
print("STAGE 6: Generating Report")
print("=" * 60)

# Prepare columns for output
def format_currency(val):
    try:
        return f"£{float(val):.2f}"
    except:
        return "£0.00"

def format_pct(val):
    try:
        return f"{float(val)*100:.1f}%"
    except:
        return "0.0%"

def format_ean(val):
    if pd.isna(val) or val == "" or val == "0":
        return "-"
    return str(val)

# Split into categories
verified_rec = df[df["Verdict"] == "VERIFIED"].copy()
verified_exc = df[df["Verdict"] == "VERIFIED_EXCLUDED"].copy()
hl_rec = df[df["Verdict"] == "HIGHLY_LIKELY"].copy()
hl_exc = df[df["Verdict"] == "HL_EXCLUDED"].copy()
needs_ver = df[df["Verdict"] == "NEEDS_VERIFICATION"].copy()

# Sort appropriately
verified_rec = verified_rec.sort_values("Sales", ascending=False)
verified_exc = verified_exc.sort_values("Adjusted_Profit", ascending=False)
hl_rec = hl_rec.sort_values(["Confidence", "Sales"], ascending=[False, False])
hl_exc = hl_exc.sort_values("Adjusted_Profit", ascending=False)
needs_ver = needs_ver.sort_values(["Confidence", "Sales"], ascending=[False, False])

def create_table_row(row):
    """Create a formatted table row"""
    return {
        "Verdict": row.get("Verdict", "-"),
        "Confidence": int(row.get("Confidence", 0)),
        "SupplierTitle": str(row.get("SupplierTitle", ""))[:50],
        "AmazonTitle": str(row.get("AmazonTitle", ""))[:60],
        "Supplier_EAN": format_ean(row.get("EAN_norm", "")),
        "Amazon_EAN": format_ean(row.get("EAN_OnPage_norm", "")),
        "ASIN": str(row.get("ASIN", "-")),
        "SupplierPrice": format_currency(row.get("SupplierPrice_incVAT", 0)),
        "SellingPrice": format_currency(row.get("SellingPrice_incVAT", 0)),
        "NetProfit": format_currency(row.get("NetProfit", 0)),
        "ROI": format_pct(row.get("ROI", 0)),
        "Sales": int(row.get("Sales", 0)),
        "Pack_Verdict": str(row.get("Pack_Verdict", "1:1 Match"))[:30],
        "Adjusted_Profit": format_currency(row.get("Adjusted_Profit", 0)),
        "Key_Match_Evidence": str(row.get("Key_Match_Evidence", "-"))[:50],
        "Filter_Reason": str(row.get("Filter_Reason", "-"))[:40]
    }

# Generate report
report_date = datetime.now().strftime("%Y-%m-%d")
report_content = f"""# PHASEA MANUAL REPORT

**Generated:** {report_date}  
**Input File:** {INPUT_PATH}  
**Supplier:** Wholesale Supplier (Calibrated)  
**Analysis Version:** V4.1 AG1 (Preflight Calibrated)

---

## Summary Counts

| Category | Count |
|----------|-------|
| VERIFIED — RECOMMENDED | {len(verified_rec)} |
| VERIFIED — FILTERED OUT / EXCLUDED | {len(verified_exc)} |
| HIGHLY LIKELY — RECOMMENDED | {len(hl_rec)} |
| HIGHLY LIKELY — FILTERED OUT / EXCLUDED | {len(hl_exc)} |
| NEEDS VERIFICATION | {len(needs_ver)} |
| **TOTAL ANALYZED** | {len(df)} |

---

This report applies v4.1 Thorough Manual Analysis with Preflight Calibration:
- **Calibrated Pack Detection:** Using identified patterns (PC, PK, PIECES, CASES)
- **Dimension Shield Active:** Protecting CM, MM, ML, G patterns from pack misinterpretation
- **Trailing Number Shield:** Disabled (unreliable for this supplier)
- **Brand Position:** START (96% pattern detected)

---

## VERIFIED — RECOMMENDED (count={len(verified_rec)})

Exact EAN matches with positive profit and sales.

"""

# Add VERIFIED table
if len(verified_rec) > 0:
    report_content += "```text\n"
    report_content += "| Verdict  | Conf | SupplierTitle                                      | AmazonTitle                                                | Supplier EAN  | Amazon EAN    | ASIN       | Sup.Price | Sell.Price | NetProfit | ROI    | Sales | Pack Verdict                  | Adj Profit | Key Match Evidence                          | Filter Reason |\n"
    report_content += "|----------|------|----------------------------------------------------|------------------------------------------------------------|---------------|---------------|------------|-----------|------------|-----------|--------|-------|-------------------------------|------------|---------------------------------------------|---------------|\n"
    
    for _, row in verified_rec.iterrows():
        r = create_table_row(row)
        report_content += f"| VERIFIED | {r['Confidence']:4} | {r['SupplierTitle']:<50} | {r['AmazonTitle']:<58} | {r['Supplier_EAN']:<13} | {r['Amazon_EAN']:<13} | {r['ASIN']:<10} | {r['SupplierPrice']:>9} | {r['SellingPrice']:>10} | {r['NetProfit']:>9} | {r['ROI']:>6} | {r['Sales']:>5} | {r['Pack_Verdict']:<29} | {r['Adjusted_Profit']:>10} | {r['Key_Match_Evidence']:<43} | {r['Filter_Reason']:<13} |\n"
    
    report_content += "```\n\n"
else:
    report_content += "*No exact EAN matches found that meet all criteria.*\n\n"

# Add VERIFIED EXCLUDED
report_content += f"""---

## VERIFIED — FILTERED OUT / EXCLUDED (count={len(verified_exc)})

Exact EAN matches confirmed as same product but excluded due to pack/variant/profit issues.

"""

if len(verified_exc) > 0:
    report_content += "```text\n"
    report_content += "| Verdict  | Conf | SupplierTitle                                      | AmazonTitle                                                | Supplier EAN  | Amazon EAN    | ASIN       | Sup.Price | Sell.Price | NetProfit | ROI    | Sales | Pack Verdict                  | Adj Profit | Key Match Evidence                          | Filter Reason                      |\n"
    report_content += "|----------|------|----------------------------------------------------|------------------------------------------------------------|---------------|---------------|------------|-----------|------------|-----------|--------|-------|-------------------------------|------------|---------------------------------------------|------------------------------------|\n"
    
    for _, row in verified_exc.head(20).iterrows():
        r = create_table_row(row)
        report_content += f"| FILTERED | {r['Confidence']:4} | {r['SupplierTitle']:<50} | {r['AmazonTitle']:<58} | {r['Supplier_EAN']:<13} | {r['Amazon_EAN']:<13} | {r['ASIN']:<10} | {r['SupplierPrice']:>9} | {r['SellingPrice']:>10} | {r['NetProfit']:>9} | {r['ROI']:>6} | {r['Sales']:>5} | {r['Pack_Verdict']:<29} | {r['Adjusted_Profit']:>10} | {r['Key_Match_Evidence']:<43} | {r['Filter_Reason']:<34} |\n"
    
    report_content += "```\n\n"
else:
    report_content += "*No exact EAN matches were excluded.*\n\n"

# Add HIGHLY LIKELY
report_content += f"""---

## HIGHLY LIKELY — RECOMMENDED (count={len(hl_rec)})

Strong brand + product matches with positive profit and sales.

"""

if len(hl_rec) > 0:
    report_content += "```text\n"
    report_content += "| Verdict       | Conf | SupplierTitle                                      | AmazonTitle                                                | Supplier EAN  | Amazon EAN    | ASIN       | Sup.Price | Sell.Price | NetProfit | ROI    | Sales | Pack Verdict                  | Adj Profit | Key Match Evidence                          | Filter Reason |\n"
    report_content += "|---------------|------|----------------------------------------------------|------------------------------------------------------------|---------------|---------------|------------|-----------|------------|-----------|--------|-------|-------------------------------|------------|---------------------------------------------|---------------|\n"
    
    for _, row in hl_rec.head(60).iterrows():
        r = create_table_row(row)
        report_content += f"| HIGHLY LIKELY | {r['Confidence']:4} | {r['SupplierTitle']:<50} | {r['AmazonTitle']:<58} | {r['Supplier_EAN']:<13} | {r['Amazon_EAN']:<13} | {r['ASIN']:<10} | {r['SupplierPrice']:>9} | {r['SellingPrice']:>10} | {r['NetProfit']:>9} | {r['ROI']:>6} | {r['Sales']:>5} | {r['Pack_Verdict']:<29} | {r['Adjusted_Profit']:>10} | {r['Key_Match_Evidence']:<43} | {r['Filter_Reason']:<13} |\n"
    
    report_content += "```\n\n"
else:
    report_content += "*No highly likely matches found.*\n\n"

# Add HIGHLY LIKELY EXCLUDED
report_content += f"""---

## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={len(hl_exc)})

Strong brand/product matches confirmed but excluded due to negative adjusted profit.

"""

if len(hl_exc) > 0:
    report_content += "```text\n"
    report_content += "| Verdict  | Conf | SupplierTitle                                      | AmazonTitle                                                | Supplier EAN  | Amazon EAN    | ASIN       | Sup.Price | Sell.Price | NetProfit | ROI    | Sales | Pack Verdict                  | Adj Profit | Key Match Evidence                          | Filter Reason                      |\n"
    report_content += "|----------|------|----------------------------------------------------|------------------------------------------------------------|---------------|---------------|------------|-----------|------------|-----------|--------|-------|-------------------------------|------------|---------------------------------------------|------------------------------------|\n"
    
    for _, row in hl_exc.head(35).iterrows():
        r = create_table_row(row)
        report_content += f"| FILTERED | {r['Confidence']:4} | {r['SupplierTitle']:<50} | {r['AmazonTitle']:<58} | {r['Supplier_EAN']:<13} | {r['Amazon_EAN']:<13} | {r['ASIN']:<10} | {r['SupplierPrice']:>9} | {r['SellingPrice']:>10} | {r['NetProfit']:>9} | {r['ROI']:>6} | {r['Sales']:>5} | {r['Pack_Verdict']:<29} | {r['Adjusted_Profit']:>10} | {r['Key_Match_Evidence']:<43} | {r['Filter_Reason']:<34} |\n"
    
    report_content += "```\n\n"
else:
    report_content += "*No highly likely matches were excluded.*\n\n"

# Add NEEDS VERIFICATION
report_content += f"""---

## NEEDS VERIFICATION (count={len(needs_ver)})

Items where confirming 1-2 specific details would upgrade to HIGHLY LIKELY or VERIFIED.

"""

if len(needs_ver) > 0:
    report_content += "```text\n"
    report_content += "| Verdict    | Conf | SupplierTitle                                      | AmazonTitle                                                | Supplier EAN  | Amazon EAN    | ASIN       | Sup.Price | Sell.Price | NetProfit | ROI    | Sales | Pack Verdict                  | Adj Profit | Key Match Evidence                          | Filter Reason                      |\n"
    report_content += "|------------|------|----------------------------------------------------|------------------------------------------------------------|---------------|---------------|------------|-----------|------------|-----------|--------|-------|-------------------------------|------------|---------------------------------------------|------------------------------------|\n"
    
    for _, row in needs_ver.head(60).iterrows():
        r = create_table_row(row)
        report_content += f"| NEEDS VER. | {r['Confidence']:4} | {r['SupplierTitle']:<50} | {r['AmazonTitle']:<58} | {r['Supplier_EAN']:<13} | {r['Amazon_EAN']:<13} | {r['ASIN']:<10} | {r['SupplierPrice']:>9} | {r['SellingPrice']:>10} | {r['NetProfit']:>9} | {r['ROI']:>6} | {r['Sales']:>5} | {r['Pack_Verdict']:<29} | {r['Adjusted_Profit']:>10} | {r['Key_Match_Evidence']:<43} | {r['Filter_Reason']:<34} |\n"
    
    report_content += "```\n\n"
else:
    report_content += "*No items require verification.*\n\n"

# Add reconciliation
report_content += f"""---

## Reconciliation Summary

| Metric | Value |
|--------|-------|
| Total Rows Processed | {len(df)} |
| Actionable (VERIFIED + HIGHLY LIKELY rec) | {len(verified_rec) + len(hl_rec)} |
| Review Needed (NEEDS VERIFICATION) | {len(needs_ver)} |
| Excluded (All FILTERED OUT) | {len(verified_exc) + len(hl_exc)} |
| Silently Dropped (Weak evidence) | {len(df) - len(verified_rec) - len(verified_exc) - len(hl_rec) - len(hl_exc) - len(needs_ver)} |

---

## Calibration Applied

```python
{SUPPLIER_NAMING_CONVENTION}
```

---

*Report generated by FBA Analysis V4.1 AG1 with Preflight Calibration*
*{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (Asia/Dubai)*
"""

# Write report
output_path = f"PHASEA_MANUAL_REPORT_{datetime.now().strftime('%Y%m%d')}.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"\nReport saved to: {output_path}")
print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
print(f"""
Final Summary:
- VERIFIED (Recommended): {len(verified_rec)}
- VERIFIED (Excluded): {len(verified_exc)}
- HIGHLY LIKELY (Recommended): {len(hl_rec)}
- HIGHLY LIKELY (Excluded): {len(hl_exc)}
- NEEDS VERIFICATION: {len(needs_ver)}
- TOTAL PROCESSED: {len(df)}
""")
