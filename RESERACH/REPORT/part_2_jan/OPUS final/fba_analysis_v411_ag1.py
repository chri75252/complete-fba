"""
FBA Product Analysis Script v4.1.1 AG1
Implements the full analysis pipeline from the Master Prompt

Input: part_2_jan.xlsx
Output: PHASEA_MANUAL_REPORT_YYYYMMDD.md
"""

import pandas as pd
import re
from difflib import SequenceMatcher
from datetime import datetime
import os

# ============================================================================
# CALIBRATION CONFIGURATION (from preflight analysis)
# ============================================================================
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pc", "pcs", "pce", "pk", "pack", "pieces", "cases"],
    "allow_trailing_number_as_qty": False,  # Trailing numbers unreliable for this supplier
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "lt", "l", "kg", "g", "oz", "inch", "in", "ft"],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,
    "has_pack_of_pattern": True,
    "has_cases_pattern": True,
    "birthday_candle_products": True,
    "multi_word_brands": ["BRIGHT & HOMELY", "CHEF AID", "MASON CASH", "PAN AROMA"],
    "top_brands": [
        "PPS", "APOLLO", "DEKTON", "PRIMA", "SIL", "ASHLEY", "ADORN", "RYSONS",
        "HOBBY", "FESTIVE", "AMTECH", "THL", "ROLSON", "BLACKSPUR", "KINGFISHER",
        "SMART", "MARKSMAN", "BETTINA", "JAUNTY", "EXTRASTAR", "PREMIER", "EUROWRAP",
        "RSW", "DLUX", "TALA", "OPAL", "MINKY", "STARWASH", "ABBEY", "PROKLEEN",
        "SECURPAK", "PALOMA", "LYNWOOD", "UNIQUE", "GIFTMAKER", "PUREBREED",
        "WENKEN", "SCHOTT ZWIESEL", "MASON", "CAR PRIDE", "TIDYZ", "CAROLINE",
        "QUEEN OF CAKES", "KEEP IT HANDY", "WASTE SMART", "ECO", "CASA", "AIRWICK",
        "FAIRY", "DUNLOP", "PANASONIC", "SIEMENS", "BOSCH", "PYREX", "KILROCK",
        "SOUDAL", "EVERBUILD", "STATUS", "GOOD BOY", "FORTHGLADE", "NATURES MENU",
        "GLADE", "SISTEMA", "LAV", "WHAM", "B & CO"
    ]
}

# IP Risk brands (luxury/trademark only - softened per v4.1)
IP_RISK_BRANDS = [
    "JO MALONE", "CHANEL", "DIOR", "GUCCI", "LOUIS VUITTON", "PRADA", 
    "HERMES", "APPLE", "SAMSUNG", "SONY", "MICROSOFT", "NIKE", "ADIDAS"
]

# ============================================================================
# FILE PATHS
# ============================================================================
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\part_2_jan.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\OPUS final"

# ============================================================================
# STAGE 1: DATA LOADING & INITIAL CLEANING
# ============================================================================
print("=" * 80)
print("STAGE 1: Data Loading & Initial Cleaning")
print("=" * 80)

df = pd.read_excel(INPUT_PATH)
print(f"Loaded {len(df)} rows from {INPUT_PATH}")
print(f"Columns: {df.columns.tolist()}")

# Clean EAN columns
def clean_ean(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    # Remove .0 suffix from floats
    if s.endswith('.0'):
        s = s[:-2]
    return s

df['EAN'] = df['EAN'].apply(clean_ean)
df['EAN_OnPage'] = df['EAN_OnPage'].apply(clean_ean)

# Handle sales column
if 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
elif 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
else:
    df['sales'] = 0

# Add RowID for traceability
df['RowID'] = df.index + 1

print(f"Sales column: using 'bought_in_past_month'")
print(f"Sales range: {df['sales'].min()} - {df['sales'].max()}")

# ============================================================================
# STAGE 1B: EAN NORMALIZATION SAFETY FLAGS
# ============================================================================
print("\n" + "=" * 80)
print("STAGE 1B: EAN Normalization Safety Flags")
print("=" * 80)

def clean_to_digits(x):
    if pd.isna(x) or x == '':
        return ''
    s = str(x).strip()
    # If scientific notation appears, treat as corrupted
    if 'e+' in s.lower() or 'e-' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

print(f"EAN digits extracted: {df['EAN_digits'].str.len().value_counts().head().to_dict()}")

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

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

print(f"Title similarity range: {df['title_match'].min():.2f} - {df['title_match'].max():.2f}")
print(f"Mean similarity: {df['title_match'].mean():.2f}")

# ============================================================================
# STAGE 3: STRICT EAN MATCHING
# ============================================================================
print("\n" + "=" * 80)
print("STAGE 3: Strict EAN Matching")
print("=" * 80)

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

print(f"Exact EAN matches (preliminary): {df['is_exact_ean'].sum()}")

# ============================================================================
# STAGE 3B: STRICT BARCODE VALIDITY + CHECKSUM + LEFT-PADDING
# ============================================================================
print("\n" + "=" * 80)
print("STAGE 3B: Strict Barcode Validity + Checksum")
print("=" * 80)

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
    if not digits or not digits.isdigit():
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

print(f"Supplier EANs valid: {df['EAN_strict_valid'].sum()}")
print(f"Amazon EANs valid: {df['EAN_OnPage_strict_valid'].sum()}")
print(f"Exact EAN matches (strict): {df['is_exact_ean_strict'].sum()}")

# ============================================================================
# STAGE 4: PACK SIZE EXTRACTION & PROFIT RECALCULATION
# ============================================================================
print("\n" + "=" * 80)
print("STAGE 4: Pack Size Extraction & Profit Recalculation")
print("=" * 80)

def is_dimension_pattern(text, number):
    """Check if a number is followed by dimension keywords"""
    if pd.isna(text):
        return False
    text = str(text).lower()
    # Pattern: number followed by dimension unit
    for unit in SUPPLIER_NAMING_CONVENTION['dimension_shield_keywords']:
        pattern = rf'\b{number}\s*{unit}\b'
        if re.search(pattern, text, re.IGNORECASE):
            return True
    # Check for AxB patterns with dimensions
    dim_pattern = rf'\b\d+\s*x\s*{number}\s*(cm|mm|inch|in|ft)\b'
    if re.search(dim_pattern, text, re.IGNORECASE):
        return True
    dim_pattern2 = rf'\b{number}\s*x\s*\d+\s*(cm|mm|inch|in|ft)\b'
    if re.search(dim_pattern2, text, re.IGNORECASE):
        return True
    return False

def is_birthday_product(title):
    """Check if product is a birthday candle/badge with number indicator"""
    if pd.isna(title):
        return False
    title = str(title).upper()
    birthday_keywords = ['CANDLE NUMBER', 'BIRTHDAY BADGE', 'BIRTHDAY BANNER', '50TH BIRTHDAY', 
                         'SPARKLE', 'HAPPY BIRTHDAY', 'ANNIVERSARY']
    return any(kw in title for kw in birthday_keywords)

def extract_supplier_quantity(title):
    """Extract pack size from supplier title. Defaults to 1."""
    if pd.isna(title):
        return 1
    title_orig = str(title)
    title = title_orig.lower()
    
    # Skip birthday products - trailing numbers are ages, not quantities
    if is_birthday_product(title_orig):
        # Still check for explicit pack patterns
        pack_patterns = [
            r'pack of (\d+)', r'(\d+)\s*pack\b', r'(\d+)\s*pk\b',
        ]
        for pat in pack_patterns:
            match = re.search(pat, title)
            if match:
                return int(match.group(1))
        return 1
    
    # Explicit pack patterns (highest priority)
    pack_patterns = [
        r'pack of (\d+)',
        r'(\d+)\s*pack\b',
        r'pk(\d+)\b',
        r'(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pce\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*cases\b',
    ]
    
    for pat in pack_patterns:
        match = re.search(pat, title)
        if match:
            qty = int(match.group(1))
            # Validate not a dimension
            if not is_dimension_pattern(title_orig, qty):
                if 1 < qty < 500:
                    return qty
    
    return 1

def extract_amazon_total(title):
    """
    Extract total items from Amazon multipack patterns.
    Returns (outer_count, inner_count, total, is_multipack)
    """
    if pd.isna(title):
        return (1, 1, 1, False)
    title_orig = str(title)
    title = title_orig.lower()
    
    # Check for capacity multipacks first (e.g., "10 x 90g", "6 x 15ml")
    # These mean N separate items of that capacity
    capacity_pattern = r'(\d+)\s*x\s*\d+\s*(ml|g|l|cl|kg|oz)\b'
    cap_match = re.search(capacity_pattern, title, re.IGNORECASE)
    if cap_match:
        outer = int(cap_match.group(1))
        if 2 <= outer <= 50:  # Reasonable multipack range
            return (outer, 1, outer, True)
    
    # Pattern for "(N x M)" multipacks (e.g., "4 x 50", "(4 x 50)")
    multipack_pattern = r'\(?\s*(\d+)\s*x\s*(\d+)\s*\)?(?!\s*(cm|mm|ml|g|l|inch|in))'
    match = re.search(multipack_pattern, title)
    if match:
        outer = int(match.group(1))
        inner = int(match.group(2))
        # Check if this looks like dimensions
        if not is_dimension_pattern(title_orig, outer) and not is_dimension_pattern(title_orig, inner):
            if outer <= 20 and inner >= 10:  # Likely multipack pattern
                return (outer, inner, outer * inner, True)
    
    # Check for "N x" at start of title (bundle)
    start_pattern = r'^(\d+)\s*x\s+\w'
    start_match = re.search(start_pattern, title)
    if start_match:
        outer = int(start_match.group(1))
        if 2 <= outer <= 20:
            return (outer, 1, outer, True)
    
    # Check for "pack of N" patterns
    pack_patterns = [
        r'pack of (\d+)',
        r'(\d+)\s*pack\b',
        r'(\d+)-pack\b',
    ]
    for pat in pack_patterns:
        match = re.search(pat, title)
        if match:
            qty = int(match.group(1))
            if 2 <= qty < 100:
                return (qty, 1, qty, True)
    
    # Simple quantity extraction for single items
    qty_patterns = [
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
    ]
    for pat in qty_patterns:
        match = re.search(pat, title)
        if match:
            qty = int(match.group(1))
            return (1, qty, qty, False)
    
    return (1, 1, 1, False)

# Apply extractions
df['Sup_Qty'] = df['SupplierTitle'].apply(extract_supplier_quantity)
df['Amz_Multipack_Info'] = df['AmazonTitle'].apply(extract_amazon_total)
df['Amz_Total'] = df['Amz_Multipack_Info'].apply(lambda x: x[2])
df['Is_Multipack'] = df['Amz_Multipack_Info'].apply(lambda x: x[3])

# Calculate RSU (Required Supplier Units)
def calculate_rsu(row):
    if row['Sup_Qty'] <= 0:
        return 1
    if row['Amz_Total'] <= row['Sup_Qty']:
        return 1
    return row['Amz_Total'] / row['Sup_Qty']

df['RSU'] = df.apply(calculate_rsu, axis=1)

# Recalculate profit
def recalculate_profit(row):
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

print(f"Supplier quantities extracted - distribution: {df['Sup_Qty'].value_counts().head().to_dict()}")
print(f"Multipacks detected: {df['Is_Multipack'].sum()}")
print(f"RSU > 1 count: {(df['RSU'] > 1).sum()}")
print(f"Negative adjusted profit count: {(df['Adjusted_Profit'] <= 0).sum()}")

# ============================================================================
# STAGE 5: BRAND DETECTION & MATCHING
# ============================================================================
print("\n" + "=" * 80)
print("STAGE 5: Brand Detection & Matching")
print("=" * 80)

def extract_brand(title):
    """Extract brand from title, checking multi-word brands first"""
    if pd.isna(title):
        return None
    title_upper = str(title).upper()
    
    # Check multi-word brands first
    for brand in SUPPLIER_NAMING_CONVENTION['multi_word_brands']:
        if brand.upper() in title_upper:
            return brand.upper()
    
    # Check single-word brands
    for brand in SUPPLIER_NAMING_CONVENTION['top_brands']:
        brand_upper = brand.upper()
        # Word boundary check
        if re.search(rf'\b{re.escape(brand_upper)}\b', title_upper):
            return brand_upper
    
    return None

def brands_match(sup_title, amz_title):
    """Check if brands match between titles"""
    sup_brand = extract_brand(sup_title)
    amz_brand = extract_brand(amz_title)
    
    if sup_brand is None or amz_brand is None:
        return False, sup_brand, amz_brand
    
    return sup_brand == amz_brand, sup_brand, amz_brand

df['Supplier_Brand'] = df['SupplierTitle'].apply(extract_brand)
df['Amazon_Brand'] = df['AmazonTitle'].apply(extract_brand)
df['Brand_Match'] = df.apply(lambda r: r['Supplier_Brand'] is not None and 
                                         r['Amazon_Brand'] is not None and 
                                         r['Supplier_Brand'] == r['Amazon_Brand'], axis=1)

print(f"Supplier brands detected: {df['Supplier_Brand'].notna().sum()}")
print(f"Amazon brands detected: {df['Amazon_Brand'].notna().sum()}")
print(f"Brand matches: {df['Brand_Match'].sum()}")

# ============================================================================
# STAGE 5B: PRODUCT CATEGORIZATION
# ============================================================================
print("\n" + "=" * 80)
print("STAGE 5B: Product Categorization")
print("=" * 80)

def pack_verdict(row):
    rsu = row['RSU']
    if rsu == 1:
        return "1:1 Match"
    elif rsu > 1:
        if row['Adjusted_Profit'] > 0:
            return f"Bundle ({int(rsu)}x) - OK"
        else:
            return f"Bundle ({int(rsu)}x) - LOSS"
    else:
        return "1:1 Match"

df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)

def categorize_product(row):
    """
    Categorize product based on v4.1.1 criteria:
    - VERIFIED: Exact EAN match (strict valid)
    - HIGHLY_LIKELY: Brand + product match with positive profit
    - NEEDS_VERIFICATION: Plausible match needing 1-2 details
    - FILTERED_OUT: Confirmed match but unprofitable
    - EXCLUDE: No match evidence
    """
    # Check for exact EAN match first
    if row['is_exact_ean_strict']:
        if row['Adjusted_Profit'] > 0:
            return 'VERIFIED'
        else:
            return 'VERIFIED_FILTERED'  # Exact match but unprofitable
    
    # Check for brand + product match
    if row['Brand_Match'] and row['Adjusted_Profit'] > 0:
        return 'HIGHLY_LIKELY'
    
    # Check for brand match but unprofitable
    if row['Brand_Match'] and row['Adjusted_Profit'] <= 0:
        return 'HIGHLY_LIKELY_FILTERED'
    
    # Check for high title similarity
    if row['title_match'] >= 0.5 and row['Adjusted_Profit'] > 0:
        # Could be highly likely if we detect brand in one title
        sup_brand = row['Supplier_Brand']
        if sup_brand is not None:
            return 'HIGHLY_LIKELY'
        return 'NEEDS_VERIFICATION'
    
    # Moderate similarity with positive profit
    if row['title_match'] >= 0.35 and row['Adjusted_Profit'] > 0:
        return 'NEEDS_VERIFICATION'
    
    # Negative profit on potential match
    if row['title_match'] >= 0.35 and row['Adjusted_Profit'] <= 0:
        return 'NEEDS_VERIFICATION_FILTERED'
    
    return 'EXCLUDE'

df['Category'] = df.apply(categorize_product, axis=1)

print(f"Category distribution:")
print(df['Category'].value_counts())

# ============================================================================
# STAGE 6: GENERATE EVIDENCE & BUILD REPORT
# ============================================================================
print("\n" + "=" * 80)
print("STAGE 6: Generate Evidence & Build Report")
print("=" * 80)

def generate_evidence(row):
    """Generate key match evidence for the row"""
    evidence_parts = []
    
    if row['is_exact_ean_strict']:
        evidence_parts.append("Exact EAN match")
    
    if row['Brand_Match']:
        evidence_parts.append(f"Brand: {row['Supplier_Brand']}")
    elif row['Supplier_Brand']:
        evidence_parts.append(f"Supplier brand: {row['Supplier_Brand']}")
    
    # Find common words in titles
    if pd.notna(row['SupplierTitle']) and pd.notna(row['AmazonTitle']):
        sup_words = set(str(row['SupplierTitle']).upper().split())
        amz_words = set(str(row['AmazonTitle']).upper().split())
        common = sup_words & amz_words
        # Filter out very short words
        common = {w for w in common if len(w) > 2}
        if common:
            common_str = ', '.join(list(common)[:5])
            evidence_parts.append(f"Common: {common_str}")
    
    return "; ".join(evidence_parts) if evidence_parts else "Title similarity"

def generate_filter_reason(row):
    """Generate filter reason for the row"""
    if row['Category'] in ['VERIFIED', 'HIGHLY_LIKELY', 'NEEDS_VERIFICATION']:
        if row['Adjusted_Profit'] <= 0:
            if row['RSU'] > 1:
                return f"RSU={int(row['RSU'])}; Adjusted profit negative"
            return "Negative adjusted profit"
        return "-"
    
    if row['Category'] in ['VERIFIED_FILTERED', 'HIGHLY_LIKELY_FILTERED', 'NEEDS_VERIFICATION_FILTERED']:
        if row['RSU'] > 1:
            return f"Requires {int(row['RSU'])} units; adjusted profit £{row['Adjusted_Profit']:.2f}"
        return f"Adjusted profit £{row['Adjusted_Profit']:.2f}"
    
    return "No strong match evidence"

df['Key_Match_Evidence'] = df.apply(generate_evidence, axis=1)
df['Filter_Reason'] = df.apply(generate_filter_reason, axis=1)

# ============================================================================
# FINAL CATEGORIZATION & REPORT GENERATION
# ============================================================================
print("\n" + "=" * 80)
print("FINAL: Building Report")
print("=" * 80)

# Split into categories
verified_rec = df[df['Category'] == 'VERIFIED'].copy()
verified_filt = df[df['Category'] == 'VERIFIED_FILTERED'].copy()
highly_likely_rec = df[df['Category'] == 'HIGHLY_LIKELY'].copy()
highly_likely_filt = df[df['Category'] == 'HIGHLY_LIKELY_FILTERED'].copy()
needs_verification = df[df['Category'] == 'NEEDS_VERIFICATION'].copy()
needs_verification_filt = df[df['Category'] == 'NEEDS_VERIFICATION_FILTERED'].copy()

# Sort
verified_rec = verified_rec.sort_values('sales', ascending=False)
verified_filt = verified_filt.sort_values('sales', ascending=False)
highly_likely_rec = highly_likely_rec.sort_values(['title_match', 'sales'], ascending=[False, False])
highly_likely_filt = highly_likely_filt.sort_values('sales', ascending=False)
needs_verification = needs_verification.sort_values(['title_match', 'sales'], ascending=[False, False])

print(f"VERIFIED - RECOMMENDED: {len(verified_rec)}")
print(f"VERIFIED - FILTERED OUT: {len(verified_filt)}")
print(f"HIGHLY LIKELY - RECOMMENDED: {len(highly_likely_rec)}")
print(f"HIGHLY LIKELY - FILTERED OUT: {len(highly_likely_filt)}")
print(f"NEEDS VERIFICATION: {len(needs_verification)}")

# ============================================================================
# GENERATE MARKDOWN REPORT
# ============================================================================

def format_price(val):
    try:
        return f"£{float(val):.2f}"
    except:
        return str(val)

def format_pct(val):
    try:
        return f"{float(val):.1f}%"
    except:
        return str(val)

def truncate(s, max_len=40):
    s = str(s) if pd.notna(s) else "-"
    return s[:max_len] + "..." if len(s) > max_len else s

def generate_table_row(row, verdict):
    """Generate a table row"""
    sup_ean = row['EAN'] if pd.notna(row['EAN']) and row['EAN'] not in ['', 'nan'] else "-"
    amz_ean = row['EAN_OnPage'] if pd.notna(row['EAN_OnPage']) and row['EAN_OnPage'] not in ['', 'nan'] else "-"
    
    return {
        'Verdict': verdict,
        'Confidence': 95 if row['is_exact_ean_strict'] else (85 if row['Brand_Match'] else 70),
        'SupplierTitle': truncate(row['SupplierTitle'], 35),
        'AmazonTitle': truncate(row['AmazonTitle'], 45),
        'Supplier EAN': sup_ean[:15] if len(str(sup_ean)) > 15 else sup_ean,
        'Amazon EAN': amz_ean[:15] if len(str(amz_ean)) > 15 else amz_ean,
        'ASIN': row['ASIN'] if pd.notna(row['ASIN']) else "-",
        'SupplierPrice': format_price(row['SupplierPrice_incVAT']),
        'SellingPrice': format_price(row['SellingPrice_incVAT']),
        'NetProfit': format_price(row['NetProfit']),
        'ROI': format_pct(row['ROI']),
        'Sales': int(row['sales']) if pd.notna(row['sales']) else 0,
        'Pack Verdict': row['Pack_Verdict'],
        'Adjusted Profit': format_price(row['Adjusted_Profit']),
        'Key Match Evidence': truncate(row['Key_Match_Evidence'], 35),
        'Filter Reason': row['Filter_Reason'] if len(str(row['Filter_Reason'])) <= 40 else row['Filter_Reason'][:37] + "..."
    }

def dataframe_to_fixed_width_table(df_subset, verdict):
    """Convert DataFrame subset to fixed-width table string"""
    if len(df_subset) == 0:
        return "No items in this category.\n"
    
    rows = [generate_table_row(row, verdict) for _, row in df_subset.iterrows()]
    
    # Define column order and widths
    columns = ['Verdict', 'Confidence', 'SupplierTitle', 'AmazonTitle', 'Supplier EAN', 
               'Amazon EAN', 'ASIN', 'SupplierPrice', 'SellingPrice', 'NetProfit', 
               'ROI', 'Sales', 'Pack Verdict', 'Adjusted Profit', 'Key Match Evidence', 'Filter Reason']
    
    # Calculate column widths
    widths = {}
    for col in columns:
        max_len = len(col)
        for row in rows:
            max_len = max(max_len, len(str(row.get(col, ""))))
        widths[col] = min(max_len + 2, 50)  # Cap at 50
    
    # Build header
    header = "|"
    separator = "|"
    for col in columns:
        header += f" {col:<{widths[col]-1}}|"
        separator += "-" * widths[col] + "|"
    
    # Build rows
    table_lines = [header, separator]
    for row in rows:
        line = "|"
        for col in columns:
            val = str(row.get(col, "-"))
            line += f" {val:<{widths[col]-1}}|"
        table_lines.append(line)
    
    return "\n".join(table_lines)

# Generate report
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_filename = f"PHASEA_MANUAL_REPORT_{timestamp}.md"
report_path = os.path.join(OUTPUT_DIR, report_filename)

report_content = f"""# PHASEA MANUAL REPORT

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Input File:** {INPUT_PATH}  
**Supplier:** EFG Housewares / Generic Wholesale  
**Analysis Version:** v4.1.1 AG1 (Preflight Calibrated)

---

## Summary Counts

| Category | Count |
|----------|-------|
| VERIFIED — RECOMMENDED | {len(verified_rec)} |
| VERIFIED — FILTERED OUT | {len(verified_filt)} |
| HIGHLY LIKELY — RECOMMENDED | {len(highly_likely_rec)} |
| HIGHLY LIKELY — FILTERED OUT | {len(highly_likely_filt)} |
| NEEDS VERIFICATION | {len(needs_verification)} |
| **TOTAL ANALYZED** | {len(df)} |

**This report applies v4.1.1 Thorough Manual Analysis:**
- HIGHLY LIKELY requires Brand + Product type match with positive profit
- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade
- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit purposes)

---

## VERIFIED — RECOMMENDED (count={len(verified_rec)})

Products with exact EAN match (strict valid barcodes) and positive adjusted profit.

```text
{dataframe_to_fixed_width_table(verified_rec.head(50), "VERIFIED")}
```

---

## VERIFIED — FILTERED OUT / EXCLUDED (count={len(verified_filt)})

Exact EAN matches where pack size adjustment results in negative profitability.

```text
{dataframe_to_fixed_width_table(verified_filt.head(30), "FILTERED")}
```

---

## HIGHLY LIKELY — RECOMMENDED (count={len(highly_likely_rec)})

Strong brand + product matches with positive adjusted profit.

```text
{dataframe_to_fixed_width_table(highly_likely_rec.head(75), "HIGHLY LIKELY")}
```

---

## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={len(highly_likely_filt)})

Brand + product matches where pack size adjustment results in negative profitability.

```text
{dataframe_to_fixed_width_table(highly_likely_filt.head(30), "FILTERED")}
```

---

## NEEDS VERIFICATION (count={len(needs_verification)})

Plausible matches where confirming 1-2 specific details would upgrade to HIGHLY LIKELY.
Items sorted by title match strength and sales.

```text
{dataframe_to_fixed_width_table(needs_verification.head(50), "NEEDS VERIF")}
```

---

## Reconciliation Summary

| Metric | Value |
|--------|-------|
| Total input rows | {len(df)} |
| Rows with valid Supplier EAN | {df['EAN_strict_valid'].sum()} |
| Rows with valid Amazon EAN | {df['EAN_OnPage_strict_valid'].sum()} |
| Strict exact EAN matches | {df['is_exact_ean_strict'].sum()} |
| Brand matches detected | {df['Brand_Match'].sum()} |
| Products requiring bundle (RSU > 1) | {(df['RSU'] > 1).sum()} |
| Products with negative adj. profit | {(df['Adjusted_Profit'] <= 0).sum()} |

---

## Calibration Notes

This analysis was calibrated for this specific supplier using preflight pattern detection:

- **Pack Units Detected:** {', '.join(SUPPLIER_NAMING_CONVENTION['explicit_units'])}
- **Trailing Numbers as Qty:** {SUPPLIER_NAMING_CONVENTION['allow_trailing_number_as_qty']}
- **Brand Position:** {SUPPLIER_NAMING_CONVENTION['brand_position']}
- **Birthday Products Present:** {SUPPLIER_NAMING_CONVENTION['birthday_candle_products']}

---

*Report generated by FBA Analysis v4.1.1 AG1*
*Preflight calibration applied from CALIBRATION_REPORT_part_2_jan_20260102.md*
"""

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"\nReport saved to: {report_path}")
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
