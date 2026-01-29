"""
FBA Product Analysis Script v4.0
Thorough Manual Analysis with Strict EAN Matching
"""

import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
import json
from pathlib import Path

# Input/Output paths
INPUT_PATH = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\part_30_dec.xlsx")
OUTPUT_DIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\Opus")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===== STAGE 1: Data Loading & Initial Cleaning =====
print("STAGE 1: Loading and cleaning data...")
df = pd.read_excel(INPUT_PATH)
print(f"Loaded {len(df)} rows")
print(f"Columns: {list(df.columns)}")

# Add RowID for traceability
df['RowID'] = df.index + 1

# Clean EAN columns
df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Handle sales column
if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
elif 'Sales' in df.columns:
    df['sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
else:
    df['sales'] = 0

# ===== STAGE 1B: EAN Normalization Safety Flags =====
print("STAGE 1B: EAN normalization...")

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    # If scientific notation appears, treat as corrupted
    if 'e+' in s.lower() or 'e-' in s.lower():
        # Try to convert back
        try:
            val = float(s)
            if val > 0:
                return str(int(val))
        except:
            pass
        return ''
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

# ===== STAGE 2: Title Similarity Calculation =====
print("STAGE 2: Calculating title similarity...")

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# ===== STAGE 3: Basic EAN Matching =====
print("STAGE 3: Basic EAN matching...")

def is_valid_ean(ean):
    if pd.isna(ean):
        return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-']

def is_exact_ean_match(row):
    ean_sup = str(row['EAN']).strip()
    ean_amz = str(row['EAN_OnPage']).strip()
    if not is_valid_ean(ean_sup) or not is_valid_ean(ean_amz):
        return False
    return ean_sup == ean_amz

df['is_exact_ean'] = df.apply(is_exact_ean_match, axis=1)

# ===== STAGE 3B: Strict Barcode Validity + Checksum + Left-Padding =====
print("STAGE 3B: Strict barcode validation...")

def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit():
        return False
    n = len(digits)
    if n not in (8, 12, 13, 14):
        return False
    
    body = digits[:-1]
    check = int(digits[-1])
    
    body_rev = list(map(int, body[::-1]))
    total = 0
    for i, d in enumerate(body_rev, start=1):
        total += d * (3 if i % 2 == 1 else 1)
    calc = (10 - (total % 10)) % 10
    return calc == check

def normalize_ean(digits: str) -> str:
    """Attempt left-padding to valid GTIN length if checksum passes"""
    if not isinstance(digits, str) or not digits:
        return digits if isinstance(digits, str) else ''
    if not digits.isdigit():
        return digits
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    for target_len in [12, 13, 14]:
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits

def is_strict_valid_barcode(digits: str) -> bool:
    if not isinstance(digits, str) or not digits:
        return False
    if not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    # Check for trailing zeros (corrupted barcodes)
    if re.search(r'0{6,}$', normalized):
        return False
    return gtin_checksum_ok(normalized)

df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)

df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)

df['is_exact_ean_strict'] = (
    df['EAN_strict_valid']
    & df['EAN_OnPage_strict_valid']
    & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
)

# ===== STAGE 4: Pack Size Extraction & Profit Recalculation =====
print("STAGE 4: Pack size extraction...")

# Dimension patterns to EXCLUDE from pack detection
DIMENSION_PATTERNS = [
    r'\d+\s*x\s*\d+\s*(x\s*\d+\s*)?(cm|mm|inch|in|m|"|\')',  # AxBxC cm
    r'\d+\s*cm\s*x\s*\d+\s*cm',  # A cm x B cm
    r'\d+\s*mm\s*x\s*\d+\s*mm',  # A mm x B mm
    r'\d+\s*inch\s*x\s*\d+\s*inch',  # A inch x B inch
    r'\d+x\d+mm',  # 280x115mm
    r'\d+\s*ml',  # XXml
    r'\d+\s*l\b',  # XXl
    r'\d+\s*oz',  # XXoz
    r'\d+\s*g\b',  # XXg
    r'\d+\s*kg',  # XXkg
    r'\d+\s*ft',  # XXft
    r'\d+\s*ltr',  # XXltr
]

def is_dimension_number(title, match_pos):
    """Check if a number at given position is part of dimensions"""
    if pd.isna(title):
        return False
    title_lower = str(title).lower()
    for pattern in DIMENSION_PATTERNS:
        for m in re.finditer(pattern, title_lower):
            if m.start() <= match_pos <= m.end():
                return True
    return False

def extract_quantity(title):
    """Extract pack size from product title. Defaults to 1."""
    if pd.isna(title):
        return 1.0
    title = str(title).lower()
    
    # Pack patterns - order matters (more specific first)
    patterns = [
        (r'pack\s*of\s*(\d+)', 1),
        (r'set\s*of\s*(\d+)', 1),
        (r'\b(\d+)\s*pack\b', 1),
        (r'\b(\d+)\s*pk\b', 1),
        (r'(\d+)\s*pcs\b', 1),
        (r'(\d+)\s*pieces?\b', 1),
        (r'(\d+)\s*pairs?\b', 1),
        (r'\bx\s*(\d+)\b', 1),
        (r'\((\d+)\s*pack\)', 1),
        (r'\(pack\s*of\s*(\d+)\)', 1),
        (r'\b(\d+)\s*rolls?\b', 1),
        (r'\b(\d+)\s*bags?\b', 1),
        (r'\b(\d+)\s*containers?\b', 1),
    ]
    
    for pat, grp in patterns:
        for match in re.finditer(pat, title):
            qty = float(match.group(grp))
            # Skip if this looks like dimensions
            if is_dimension_number(title, match.start()):
                continue
            if qty > 1 and qty < 500:
                return qty
    return 1.0

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']

def recalculate_profit(row):
    """Adjust profit based on quantity ratio."""
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        adjustment = supplier_cost * (ratio - 1)
        return original_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# ===== STAGE 5: Initial Categorization =====
print("STAGE 5: Initial categorization...")

def pack_verdict(row):
    if row['Qty_Ratio'] == 1.0:
        return "1:1 Match"
    elif row['Qty_Ratio'] > 1.0:
        if row['Adjusted_Profit'] > 0:
            return f"BUNDLE ({int(row['Qty_Ratio'])}x) - OK"
        else:
            return f"BUNDLE ({int(row['Qty_Ratio'])}x) - LOSS"
    else:
        if row['Adjusted_Profit'] > 0:
            return f"SPLIT (1/{int(1/row['Qty_Ratio'])}) - OK"
        else:
            return "SPLIT - LOSS"

df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)

# ===== Output Summary Stats =====
print("\n===== SUMMARY STATISTICS =====")
print(f"Total rows: {len(df)}")
print(f"Exact EAN matches (strict): {df['is_exact_ean_strict'].sum()}")
print(f"Rows with Sales > 0: {(df['sales'] > 0).sum()}")
print(f"Rows with NetProfit > 0: {(df['NetProfit'] > 0).sum()}")
print(f"Rows with Adjusted_Profit > 0: {(df['Adjusted_Profit'] > 0).sum()}")

# Save intermediate analysis
df.to_csv(OUTPUT_DIR / 'intermediate_analysis.csv', index=False)
print(f"\nIntermediate analysis saved to: {OUTPUT_DIR / 'intermediate_analysis.csv'}")

# ===== Create summary for each category =====
exact_ean_verified = df[df['is_exact_ean_strict'] & (df['sales'] > 0) & (df['Adjusted_Profit'] > 0)]
exact_ean_filtered = df[df['is_exact_ean_strict'] & ~((df['sales'] > 0) & (df['Adjusted_Profit'] > 0))]

print(f"\nEXACT EAN VERIFIED (sales>0, profit>0): {len(exact_ean_verified)}")
print(f"EXACT EAN FILTERED OUT: {len(exact_ean_filtered)}")

# High title match candidates (for HIGHLY LIKELY)
high_title_match = df[~df['is_exact_ean_strict'] & (df['title_match'] >= 0.5)]
print(f"High title match (>=0.5, non-EAN): {len(high_title_match)}")

# Save a detailed JSON with key stats
stats = {
    "total_rows": len(df),
    "exact_ean_strict": int(df['is_exact_ean_strict'].sum()),
    "sales_positive": int((df['sales'] > 0).sum()),
    "profit_positive": int((df['NetProfit'] > 0).sum()),
    "adjusted_profit_positive": int((df['Adjusted_Profit'] > 0).sum()),
    "exact_ean_verified": len(exact_ean_verified),
    "exact_ean_filtered": len(exact_ean_filtered),
    "high_title_match": len(high_title_match),
}

with open(OUTPUT_DIR / 'analysis_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print("\n===== COLUMNS IN DATASET =====")
print(list(df.columns))

# Show sample of exact EAN matches
print("\n===== SAMPLE EXACT EAN MATCHES =====")
if len(exact_ean_verified) > 0:
    sample_cols = ['RowID', 'EAN_digits_normalized', 'EAN_OnPage_digits_normalized', 'SupplierTitle', 'AmazonTitle', 'NetProfit', 'Adjusted_Profit', 'sales']
    print(exact_ean_verified[sample_cols].head(10).to_string())
