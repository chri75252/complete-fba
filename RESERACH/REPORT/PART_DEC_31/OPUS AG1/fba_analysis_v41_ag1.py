"""
FBA Product Analysis Script - v4.1 AG1 (Antigravity Enhanced)
Principal E-Commerce Analyst - Amazon FBA Arbitrage
Created: 2025-12-31

This script implements the comprehensive multi-stage analysis protocol.
"""

import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# STAGE 1: Data Loading & Initial Cleaning
# ==============================================================================

INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\OPUS AG1"

print("=" * 80)
print("FBA PRODUCT ANALYSIS v4.1 AG1")
print("=" * 80)
print(f"\nLoading data from: {INPUT_PATH}")

df = pd.read_excel(INPUT_PATH)
print(f"Loaded {len(df)} rows with {len(df.columns)} columns")

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
else:
    df['sales'] = 0

# Convert numeric columns
df['NetProfit'] = pd.to_numeric(df['NetProfit'], errors='coerce').fillna(0)
df['ROI'] = pd.to_numeric(df['ROI'], errors='coerce').fillna(0)
df['SupplierPrice_incVAT'] = pd.to_numeric(df['SupplierPrice_incVAT'], errors='coerce').fillna(0)
df['SellingPrice_incVAT'] = pd.to_numeric(df['SellingPrice_incVAT'], errors='coerce').fillna(0)

print(f"Sales range: {df['sales'].min()} to {df['sales'].max()}")
print(f"NetProfit range: {df['NetProfit'].min():.2f} to {df['NetProfit'].max():.2f}")

# ==============================================================================
# STAGE 1B: EAN Normalization Safety Flags
# ==============================================================================

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    # If scientific notation appears, treat as corrupted
    if 'e+' in s.lower() or 'e-' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

# ==============================================================================
# STAGE 2: Title Similarity Calculation
# ==============================================================================

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)
print(f"\nTitle similarity computed. Mean: {df['title_match'].mean():.3f}")

# ==============================================================================
# STAGE 3: STRICT EAN Matching
# ==============================================================================

def is_valid_ean(ean):
    """Check if EAN is a valid barcode (not empty, nan, None, etc.)"""
    if pd.isna(ean):
        return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-']

def is_exact_ean_match(row):
    """Returns True ONLY if BOTH EANs are valid AND they match exactly"""
    ean_sup = str(row['EAN']).strip()
    ean_amz = str(row['EAN_OnPage']).strip()
    
    if not is_valid_ean(ean_sup) or not is_valid_ean(ean_amz):
        return False
    
    return ean_sup == ean_amz

df['is_exact_ean'] = df.apply(is_exact_ean_match, axis=1)

# ==============================================================================
# STAGE 3B: STRICT BARCODE VALIDITY + CHECKSUM + LEFT-PADDING
# ==============================================================================

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
    if not isinstance(digits, str) or not digits.isdigit():
        return digits if isinstance(digits, str) else ''
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    for target_len in [12, 13, 14]:
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits

def is_strict_valid_barcode(digits: str) -> bool:
    if not isinstance(digits, str):
        return False
    if not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
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

print(f"\nStrict EAN matches found: {df['is_exact_ean_strict'].sum()}")

# ==============================================================================
# STAGE 4: Pack Size Extraction & Profit Recalculation
# ==============================================================================

# Known dimension/measurement patterns to EXCLUDE from pack counting
DIMENSION_PATTERNS = [
    r'\d+\s*x\s*\d+\s*(cm|mm|m|inch|in|ft|")',  # e.g., "9 x 9 inch", "30 x 20 cm"
    r'\d+\s*(cm|mm|m|inch|in|ft|ml|l|ltr|g|gm|kg|oz)\b',  # e.g., "21CM", "500ML"
    r'\d+\s*x\s*\d+\s*x\s*\d+',  # 3D dimensions like "15 x 5.5 x 5.5"
]

def is_dimension_pattern(text):
    """Check if text contains dimension/measurement patterns"""
    if pd.isna(text):
        return False
    text_lower = str(text).lower()
    for pattern in DIMENSION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False

def extract_quantity(title):
    """Extract pack size from product title. Defaults to 1."""
    if pd.isna(title):
        return 1.0
    title_str = str(title).lower()
    
    # Skip if it's clearly a dimension pattern
    dimension_check = re.search(r'(\d+)\s*x\s*(\d+)\s*(cm|mm|m|inch|in|ft|")', title_str)
    if dimension_check:
        # This is dimensions, not pack count
        pass
    
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*-?\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)',
        r'\b(\d+)\s*rolls?\b',
        r'\bx\s*(\d+)\s*(?:pack|pk)\b',  # "x 10 pack"
    ]
    
    for pat in patterns:
        match = re.search(pat, title_str)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:
                return qty
    return 1.0

def extract_multipack_total(title):
    """
    Extract total items from multipack patterns like '(4 x 50)' or '3 x Product Name'.
    Returns (outer_count, inner_count, total) or (1, qty, qty) if no multipack.
    """
    if pd.isna(title):
        return (1, 1, 1)
    title_str = str(title).lower()
    
    # Check for dimension patterns first - DO NOT treat as multipacks
    if re.search(r'\d+\s*x\s*\d+\s*(cm|mm|m|inch|in|ft|")', title_str):
        # It's dimensions, not multipack
        qty = extract_quantity(title)
        return (1, int(qty), int(qty))
    
    # Pattern for "N x M" multipacks (e.g., "(4 x 50)", "3 x 500ml")
    multipack_pattern = r'\(?\s*(\d+)\s*x\s*(\d+)\s*(?:ml|g|pcs|pieces|pack|bags?)?\s*\)?'
    match = re.search(multipack_pattern, title_str)
    if match:
        outer = int(match.group(1))
        inner = int(match.group(2))
        # Avoid dimension patterns (small numbers with units nearby)
        # Check if this looks like a real multipack: outer is small (1-12), inner is larger
        if outer <= 12 and inner > outer:
            return (outer, inner, outer * inner)
    
    # Pattern for "N x Product" at start of title (e.g., "3 x Fairy Dish Brush")
    start_multipack = r'^(\d+)\s*x\s+'
    match = re.search(start_multipack, title_str)
    if match:
        outer = int(match.group(1))
        if 2 <= outer <= 12:
            return (outer, 1, outer)
    
    # Fallback to simple quantity extraction
    qty = extract_quantity(title_str)
    return (1, int(qty), int(qty))

def extract_quantity_inside(title):
    """Extract quantity-inside-pack (e.g., '50 PCS', '200 sticks') but NOT packs"""
    if pd.isna(title):
        return 1
    title_str = str(title).lower()
    
    # Quantity-inside patterns
    patterns = [
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*sticks?\b',
        r'(\d+)\s*bags?\b',
        r'(\d+)\s*sheets?\b',
        r'(\d+)\s*wipes?\b',
        r'(\d+)\s*doyl[ie]+s?\b',
    ]
    
    for pat in patterns:
        match = re.search(pat, title_str)
        if match:
            qty = int(match.group(1))
            if 10 <= qty <= 1000:  # Reasonable quantity-inside range
                return qty
    return 1

# Apply pack extraction
df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Sup_Qty_Inside'] = df['SupplierTitle'].apply(extract_quantity_inside)
df['Amz_Multipack'] = df['AmazonTitle'].apply(extract_multipack_total)
df['Amz_Qty_Inside'] = df['AmazonTitle'].apply(extract_quantity_inside)
df['Amz_Total'] = df['Amz_Multipack'].apply(lambda x: x[2])

# Determine if titles have dimension patterns
df['has_dimension_pattern'] = df.apply(
    lambda r: is_dimension_pattern(r['SupplierTitle']) or is_dimension_pattern(r['AmazonTitle']),
    axis=1
)

def calculate_rsu(row):
    """Calculate Required Supplier Units with dimension shield"""
    # If dimension pattern detected, default to 1:1
    if row['has_dimension_pattern']:
        # Check if both have same quantity-inside
        if row['Sup_Qty_Inside'] == row['Amz_Qty_Inside'] and row['Sup_Qty_Inside'] > 1:
            return 1.0  # Same quantity-inside = 1:1 match
        elif row['Amz_Total'] > 1 and row['Sup_Qty'] > 0:
            return max(1, row['Amz_Total'] / row['Sup_Qty'])
        return 1.0
    
    # Normal RSU calculation
    if row['Sup_Qty'] > 0:
        # If Amazon shows multipack
        if row['Amz_Total'] > row['Sup_Qty']:
            return row['Amz_Total'] / row['Sup_Qty']
        return 1.0
    return 1.0

df['RSU'] = df.apply(calculate_rsu, axis=1)
df['Qty_Ratio'] = df['RSU']

def recalculate_profit(row):
    """Adjust profit based on Required Supplier Units."""
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        rsu = row['RSU']
        if rsu > 1:
            adjustment = supplier_cost * (rsu - 1)
            return original_profit - adjustment
        return original_profit
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

print(f"RSU > 1 count: {(df['RSU'] > 1).sum()}")
print(f"Dimension pattern count: {df['has_dimension_pattern'].sum()}")

# ==============================================================================
# STAGE 5: Product Categorization (Base)
# ==============================================================================

def pack_verdict(row):
    rsu = row['RSU']
    if rsu == 1.0:
        return "1:1 Match"
    elif rsu > 1.0:
        if row['Adjusted_Profit'] > 0:
            return f"BUNDLE ({int(rsu)}x) - OK"
        else:
            return f"BUNDLE ({int(rsu)}x) - LOSS"
    else:
        if row['Adjusted_Profit'] > 0:
            return f"SPLIT (1/{int(1/rsu)}) - OK"
        else:
            return "SPLIT - LOSS"

df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)

# ==============================================================================
# STAGE 5B: Brand Detection & HIGHLY LIKELY Upgrade
# ==============================================================================

# Known brands for matching
KNOWN_BRANDS = [
    'AMTECH', 'ROLSON', 'DRAPER', 'EVERBUILD', 'SOUDAL', 'HARRIS', 'RONSEAL',
    'FAIRY', 'DETTOL', 'MARIGOLD', 'DUNLOP', 'MASON CASH', 'PYREX', 'CHEF AID',
    'STATUS', 'EXTRASTAR', 'ROUNDUP', 'LITTLE TREES', 'PAN AROMA', 'KILROCK',
    'TIDYZ', 'EASYO', 'BLUE CANYON', 'APOLLO', 'SUPERIOR', 'PPS', 'BOSTIK',
    'RAC', 'HOLTS', 'CARPLAN', 'ARMOR ALL', 'WD-40', 'GORILLA', 'LOCTITE',
    'UNIBOND', 'POLYCELL', 'FENWICKS', 'MEGUIARS', 'AUTOGLYM', 'TURTLE WAX',
    'STA-BIL', 'COMMA', 'CASTROL', 'MOBIL', 'SHELL', 'TOTAL', 'VALVOLINE',
    'EVEREADY', 'DURACELL', 'ENERGIZER', 'VARTA', 'PANASONIC', 'PHILIPS',
    'OSRAM', 'GE', 'RING', 'BOSCH', 'LUCAS', 'CHAMPION', 'NGK', 'DENSO',
]

def extract_brand(title):
    """Extract brand from title if known"""
    if pd.isna(title):
        return None
    title_upper = str(title).upper()
    for brand in KNOWN_BRANDS:
        if brand in title_upper:
            return brand
    # Try first word as brand
    first_word = str(title).split()[0].upper() if title else ''
    if len(first_word) > 2 and first_word.isalpha():
        return first_word
    return None

df['Supplier_Brand'] = df['SupplierTitle'].apply(extract_brand)
df['Amazon_Brand'] = df['AmazonTitle'].apply(extract_brand)

def brands_match(row):
    """Check if brands match between supplier and Amazon"""
    sup_brand = row['Supplier_Brand']
    amz_brand = row['Amazon_Brand']
    if pd.isna(sup_brand) or pd.isna(amz_brand):
        return False
    return sup_brand.upper() == amz_brand.upper()

df['brands_match'] = df.apply(brands_match, axis=1)

# ==============================================================================
# STAGE 6: Manual Analysis Categorization
# ==============================================================================

def get_match_evidence(row):
    """Generate key match evidence for a row"""
    evidence_parts = []
    
    if row['is_exact_ean_strict']:
        evidence_parts.append("Exact EAN match (checksum valid)")
    
    if row['brands_match']:
        evidence_parts.append(f"Brand: {row['Supplier_Brand']}")
    
    if row['title_match'] >= 0.7:
        evidence_parts.append(f"Strong title match ({row['title_match']:.0%})")
    elif row['title_match'] >= 0.5:
        evidence_parts.append(f"Good title match ({row['title_match']:.0%})")
    
    if row['Pack_Verdict'] == "1:1 Match":
        evidence_parts.append("Pack: 1:1")
    
    if not evidence_parts:
        evidence_parts.append("Titles similar")
    
    return "; ".join(evidence_parts[:3])  # Limit to 3 pieces of evidence

def categorize_product(row):
    """
    Apply thorough manual analysis to categorize products.
    Returns: (category, confidence, filter_reason)
    """
    # Check basic profitability first
    if row['Adjusted_Profit'] <= 0:
        return ('FILTERED_OUT', 0, 'Negative adjusted profit')
    
    # VERIFIED: Exact EAN match with no contradictions
    if row['is_exact_ean_strict']:
        if 'LOSS' in row['Pack_Verdict']:
            return ('FILTERED_OUT', 0, 'Pack mismatch causes loss')
        if row['sales'] > 0:
            return ('VERIFIED', 95, '-')
        else:
            return ('NEEDS_VERIFICATION', 85, 'No sales data (exact EAN)')
    
    # HIGHLY LIKELY: Brand + Product match
    if row['brands_match'] and row['title_match'] >= 0.4:
        if 'LOSS' in row['Pack_Verdict']:
            return ('FILTERED_OUT', 0, 'Pack mismatch causes loss')
        if row['sales'] > 0:
            return ('HIGHLY_LIKELY', 80, '-')
        else:
            return ('NEEDS_VERIFICATION', 70, 'No sales data (brand match)')
    
    # Strong title match without brand
    if row['title_match'] >= 0.6:
        if 'LOSS' in row['Pack_Verdict']:
            return ('FILTERED_OUT', 0, 'Pack mismatch causes loss')
        if row['sales'] > 0:
            return ('HIGHLY_LIKELY', 75, '-')
        else:
            return ('NEEDS_VERIFICATION', 65, 'No sales data')
    
    # Moderate title match - needs verification
    if row['title_match'] >= 0.4:
        if row['NetProfit'] > 0.5 and row['ROI'] > 15:
            return ('NEEDS_VERIFICATION', 55, 'Moderate match')
        else:
            return ('FILTERED_OUT', 0, 'Weak match + low profit')
    
    # Weak matches
    if row['title_match'] >= 0.3:
        if row['brands_match']:
            return ('NEEDS_VERIFICATION', 50, 'Weak title but brand match')
        return ('FILTERED_OUT', 0, 'Title match too weak')
    
    return ('FILTERED_OUT', 0, 'No match evidence')

# Apply categorization
print("\nApplying manual categorization...")
categorization_results = df.apply(categorize_product, axis=1)
df['Category'] = categorization_results.apply(lambda x: x[0])
df['Confidence'] = categorization_results.apply(lambda x: x[1])
df['Filter_Reason'] = categorization_results.apply(lambda x: x[2])
df['Key_Match_Evidence'] = df.apply(get_match_evidence, axis=1)

# ==============================================================================
# STAGE 7: Final Filtering & Report Generation
# ==============================================================================

# Separate by category
verified = df[df['Category'] == 'VERIFIED'].copy()
highly_likely = df[df['Category'] == 'HIGHLY_LIKELY'].copy()
needs_verification = df[df['Category'] == 'NEEDS_VERIFICATION'].copy()
filtered_out = df[df['Category'] == 'FILTERED_OUT'].copy()

# Sort appropriately
verified = verified.sort_values('sales', ascending=False)
highly_likely = highly_likely.sort_values(['Confidence', 'sales'], ascending=[False, False])
needs_verification = needs_verification.sort_values(['Confidence', 'sales'], ascending=[False, False])

# Limit needs verification to reasonable count
max_needs_verification = 60
if len(needs_verification) > max_needs_verification:
    needs_verification = needs_verification.head(max_needs_verification)

print(f"\n{'='*80}")
print("CATEGORIZATION RESULTS")
print(f"{'='*80}")
print(f"VERIFIED: {len(verified)}")
print(f"HIGHLY LIKELY: {len(highly_likely)}")
print(f"NEEDS VERIFICATION: {len(needs_verification)}")
print(f"FILTERED OUT: {len(filtered_out)}")

# ==============================================================================
# Generate Markdown Report
# ==============================================================================

report_date = datetime.now().strftime('%Y%m%d')
report_path = f"{OUTPUT_DIR}/PHASEA_MANUAL_REPORT_{report_date}.md"

def format_ean(ean):
    """Format EAN for display"""
    if pd.isna(ean) or str(ean).strip() in ['nan', '', 'None', 'NaN']:
        return '-'
    return str(ean).strip()

def truncate_text(text, max_len=40):
    """Truncate text to max length"""
    if pd.isna(text):
        return '-'
    text = str(text).strip()
    if len(text) > max_len:
        return text[:max_len-3] + '...'
    return text

def generate_table_row(row, show_filter_reason=False):
    """Generate a formatted table row"""
    verdict = "VERIFIED" if row['Category'] == 'VERIFIED' else \
              "HIGHLY LIKELY" if row['Category'] == 'HIGHLY_LIKELY' else \
              "NEEDS VERIFICATION" if row['Category'] == 'NEEDS_VERIFICATION' else "FILTERED OUT"
    
    cols = [
        verdict,
        str(int(row['Confidence'])),
        truncate_text(row['SupplierTitle'], 35),
        truncate_text(row['AmazonTitle'], 35),
        format_ean(row['EAN']),
        format_ean(row['EAN_OnPage']),
        str(row['ASIN']) if not pd.isna(row['ASIN']) else '-',
        f"£{row['SupplierPrice_incVAT']:.2f}" if not pd.isna(row['SupplierPrice_incVAT']) else '-',
        f"£{row['SellingPrice_incVAT']:.2f}" if not pd.isna(row['SellingPrice_incVAT']) else '-',
        f"£{row['NetProfit']:.2f}" if not pd.isna(row['NetProfit']) else '-',
        f"{row['ROI']:.1f}%" if not pd.isna(row['ROI']) else '-',
        str(int(row['sales'])),
        row['Pack_Verdict'],
        f"£{row['Adjusted_Profit']:.2f}" if not pd.isna(row['Adjusted_Profit']) else '-',
        truncate_text(row['Key_Match_Evidence'], 40),
    ]
    
    if show_filter_reason:
        cols.append(truncate_text(row['Filter_Reason'], 30))
    
    return cols

# Write report
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(f"# FBA Product Analysis Report v4.1 AG1\n\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Asia/Dubai)\n\n")
    f.write(f"**Input File:** `PART_DEC_31.xlsx`\n\n")
    f.write(f"**Total Rows Analyzed:** {len(df)}\n\n")
    
    # Summary
    f.write("## Summary\n\n")
    f.write(f"| Category | Count |\n")
    f.write(f"|----------|-------|\n")
    f.write(f"| VERIFIED | {len(verified)} |\n")
    f.write(f"| HIGHLY LIKELY | {len(highly_likely)} |\n")
    f.write(f"| NEEDS VERIFICATION | {len(needs_verification)} |\n")
    f.write(f"| FILTERED OUT | {len(filtered_out)} |\n")
    f.write(f"| **TOTAL ACTIONABLE** | **{len(verified) + len(highly_likely)}** |\n\n")
    
    # Table header
    header = "| Verdict | Conf | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adj Profit | Key Match Evidence |"
    separator = "|---------|------|---------------|-------------|--------------|------------|------|---------------|--------------|-----------|-----|-------|--------------|------------|-------------------|"
    
    header_with_filter = header + " Filter Reason |"
    separator_with_filter = separator + "--------------|"
    
    # VERIFIED section
    f.write("## VERIFIED — RECOMMENDED\n\n")
    f.write(f"*Products with exact EAN match (checksum-valid) and positive profit. Count: {len(verified)}*\n\n")
    if len(verified) > 0:
        f.write(header + "\n")
        f.write(separator + "\n")
        for _, row in verified.iterrows():
            cols = generate_table_row(row)
            f.write("| " + " | ".join(cols) + " |\n")
    else:
        f.write("*No verified exact-EAN matches found.*\n")
    f.write("\n")
    
    # HIGHLY LIKELY section
    f.write("## HIGHLY LIKELY — RECOMMENDED\n\n")
    f.write(f"*Products with strong brand/title match and positive profit. Count: {len(highly_likely)}*\n\n")
    if len(highly_likely) > 0:
        f.write(header + "\n")
        f.write(separator + "\n")
        for _, row in highly_likely.iterrows():
            cols = generate_table_row(row)
            f.write("| " + " | ".join(cols) + " |\n")
    else:
        f.write("*No highly likely matches found.*\n")
    f.write("\n")
    
    # NEEDS VERIFICATION section
    f.write("## NEEDS VERIFICATION\n\n")
    f.write(f"*Products requiring confirmation of 1-2 details. Count: {len(needs_verification)} (capped at {max_needs_verification})*\n\n")
    if len(needs_verification) > 0:
        f.write(header_with_filter + "\n")
        f.write(separator_with_filter + "\n")
        for _, row in needs_verification.iterrows():
            cols = generate_table_row(row, show_filter_reason=True)
            f.write("| " + " | ".join(cols) + " |\n")
    else:
        f.write("*No items requiring verification.*\n")
    f.write("\n")
    
    # FILTERED OUT section (sample)
    f.write("## FILTERED OUT\n\n")
    f.write(f"*Products excluded due to pack mismatch, negative profit, or weak evidence. Total: {len(filtered_out)}*\n\n")
    f.write("*Showing top 50 filtered items by original profit:*\n\n")
    
    filtered_sample = filtered_out.nlargest(50, 'NetProfit')
    if len(filtered_sample) > 0:
        f.write(header_with_filter + "\n")
        f.write(separator_with_filter + "\n")
        for _, row in filtered_sample.iterrows():
            cols = generate_table_row(row, show_filter_reason=True)
            f.write("| " + " | ".join(cols) + " |\n")
    f.write("\n")
    
    # Reconciliation
    f.write("## Reconciliation\n\n")
    f.write(f"| Metric | Value |\n")
    f.write(f"|--------|-------|\n")
    f.write(f"| Total Input Rows | {len(df)} |\n")
    f.write(f"| VERIFIED | {len(verified)} |\n")
    f.write(f"| HIGHLY LIKELY | {len(highly_likely)} |\n")
    f.write(f"| NEEDS VERIFICATION | {len(needs_verification)} |\n")
    f.write(f"| FILTERED OUT | {len(filtered_out)} |\n")
    f.write(f"| Sum of Categories | {len(verified) + len(highly_likely) + len(needs_verification) + len(filtered_out)} |\n\n")
    
    f.write("---\n")
    f.write(f"*Report generated by FBA Analysis Script v4.1 AG1*\n")

print(f"\n{'='*80}")
print(f"Report saved to: {report_path}")
print(f"{'='*80}")

# Save detailed CSV for analysis
csv_path = f"{OUTPUT_DIR}/analysis_detailed_{report_date}.csv"
df.to_csv(csv_path, index=False)
print(f"Detailed CSV saved to: {csv_path}")

print("\nAnalysis complete!")
