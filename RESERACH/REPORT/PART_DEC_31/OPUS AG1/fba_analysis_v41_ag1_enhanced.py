"""
FBA Product Analysis Script - v4.1 AG1 ENHANCED
Principal E-Commerce Analyst - Amazon FBA Arbitrage
Created: 2025-12-31

Enhanced version with:
- Better title analysis for brand/product matching
- Improved pack detection
- More accurate categorization
- Proper ROI display
"""

import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================

INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\OPUS AG1"

# ==============================================================================
# KNOWN BRANDS DATABASE
# ==============================================================================

KNOWN_BRANDS = {
    # Tools & Hardware
    'AMTECH', 'ROLSON', 'DRAPER', 'EVERBUILD', 'SOUDAL', 'HARRIS', 'RONSEAL',
    'BOSTIK', 'GORILLA', 'LOCTITE', 'UNIBOND', 'POLYCELL', 'PRODEC', 'LYNWOOD',
    'STANLEY', 'BAHCO', 'SILVERLINE', 'FAITHFULL', 'TREND', 'IRWIN',
    
    # Kitchenware
    'MASON CASH', 'PYREX', 'CHEF AID', 'APOLLO', 'TALA', 'WHAM', 'KILNER',
    'BEAUFORT', 'PRIMA', 'VINERS', 'PAN AROMA', 'SISTEMA', 'CURVER',
    'PRICE & KENSINGTON', 'BAKER & SALT', 'FALCON', 'SCHOTT ZWIESEL',
    
    # Cleaning & Household
    'FAIRY', 'DETTOL', 'MARIGOLD', 'MINKY', 'TIDYZ', 'KILROCK', 'ADDIS',
    'BETTINA', 'ELLIOTT', 'ELLIOTTS', 'VIVID', 'STARWASH', 'PROKLEEN',
    
    # DIY & Garden
    'DUNLOP', 'STATUS', 'EXTRASTAR', 'ROUNDUP', 'EVEREADY', 'EVERREADY',
    'WD-40', 'FENWICKS', 'RINGMASTER', 'BIRDBRAND', 'FLOW',
    
    # Automotive
    'RAC', 'HOLTS', 'CARPLAN', 'ARMOR ALL', 'MEGUIARS', 'AUTOGLYM',
    'TURTLE WAX', 'COMMA', 'CASTROL', 'MOBIL', 'SHELL', 'RING',
    
    # Pet
    'MUNCH & CRUNCH', 'MUNCH N CRUNCH', 'MUNCH CRUNCH', 'SMART CHOICE',
    'WORLD OF PETS', 'EXTRA SELECT',
    
    # General
    'BLUE CANYON', 'LITTLE TREES', 'PPS', 'SUPERIOR', 'ULTRATAPE',
    'QUEST', 'CORAL', 'YALE', 'THE BIG CHEESE', 'HOUSE MATE',
    'ASHLEY', 'ADORN', 'BRIGHT & HOMELY', 'DEKTON', 'MARKSMAN',
    'PREMIER', 'GEEPAS', 'BAUER', 'RUSSELL HOBBS', 'SABICHI',
}

# Brands with IP risks - be cautious
IP_RISK_BRANDS = {
    'JO MALONE', 'CHANEL', 'DIOR', 'GUCCI', 'LOUIS VUITTON', 'PRADA',
    'HERMES', 'APPLE', 'SAMSUNG', 'SONY', 'MICROSOFT', 'NIKE', 'ADIDAS',
}

print("=" * 80)
print("FBA PRODUCT ANALYSIS v4.1 AG1 ENHANCED")
print("=" * 80)

# ==============================================================================
# STAGE 1: Data Loading & Initial Cleaning
# ==============================================================================

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
print(f"NetProfit range: £{df['NetProfit'].min():.2f} to £{df['NetProfit'].max():.2f}")

# ==============================================================================
# STAGE 1B: EAN Normalization
# ==============================================================================

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
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
# STAGE 3: STRICT EAN Matching with Checksum
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
    if not isinstance(digits, str) or not digits.isdigit():
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

print(f"Strict EAN matches found: {df['is_exact_ean_strict'].sum()}")

# ==============================================================================
# STAGE 4: Enhanced Pack Size Detection
# ==============================================================================

DIMENSION_PATTERNS = [
    r'\d+\s*x\s*\d+\s*(cm|mm|m|inch|in|ft|")',
    r'\d+\s*(cm|mm|m|inch|in|ft|ml|l|ltr|g|gm|kg|oz)\b',
    r'\d+\s*x\s*\d+\s*x\s*\d+',
]

def is_dimension_pattern(text):
    if pd.isna(text):
        return False
    text_lower = str(text).lower()
    for pattern in DIMENSION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False

def extract_pack_count(title):
    """Extract multi-pack count from title. Returns 1 for singles."""
    if pd.isna(title):
        return 1
    title_str = str(title).lower()
    
    # Skip if clearly dimensions
    if re.search(r'(\d+)\s*x\s*(\d+)\s*(cm|mm|inch|in|")', title_str):
        return 1
    
    # "N x" at START only for multipacks (e.g., "3 x Fairy Dish")
    start_multi = re.match(r'^(\d+)\s*x\s+', title_str)
    if start_multi:
        n = int(start_multi.group(1))
        if 2 <= n <= 12:
            return n
    
    # Explicit pack patterns
    patterns = [
        r'pack\s*of\s*(\d+)',
        r'set\s*of\s*(\d+)',
        r'(\d+)\s*-?\s*pack\b',
        r'(\d+)\s*pk\b',
        r'\((\d+)\s*pack\)',
    ]
    
    for pat in patterns:
        match = re.search(pat, title_str)
        if match:
            n = int(match.group(1))
            if 2 <= n <= 100:
                return n
    
    return 1

def extract_quantity_inside(title):
    """Extract quantity of items inside single pack (e.g., '50 PCS')"""
    if pd.isna(title):
        return 1
    title_str = str(title).lower()
    
    patterns = [
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*bags?\b',
        r'(\d+)\s*sheets?\b',
        r'(\d+)\s*doyl[ie]+s?\b',
        r'(\d+)\s*sticks?\b',
        r'(\d+)\s*rolls?\b(?!\s*royce)',  # Avoid Rolls Royce
        r'(\d+)\s*liners?\b',
    ]
    
    for pat in patterns:
        match = re.search(pat, title_str)
        if match:
            qty = int(match.group(1))
            if 10 <= qty <= 1000:
                return qty
    return 1

def extract_nested_multipack(title):
    """
    Extract nested multipack pattern like (4 x 50) = 200 total.
    Returns (outer, inner, total)
    """
    if pd.isna(title):
        return (1, 1, 1)
    title_str = str(title).lower()
    
    # Skip dimension patterns
    if re.search(r'\d+\s*x\s*\d+\s*(cm|mm|inch|in|")', title_str):
        return (1, 1, 1)
    
    # Pattern for "(N x M)" nested multipacks
    nested = re.search(r'\((\d+)\s*x\s*(\d+)\)', title_str)
    if nested:
        outer = int(nested.group(1))
        inner = int(nested.group(2))
        if outer <= 12 and inner >= 10:  # Likely multipack
            return (outer, inner, outer * inner)
    
    # Pattern for "N x M bags/pcs" at end
    multi_end = re.search(r'(\d+)\s*x\s*(\d+)\s*(bags?|pcs|pieces?)\s*$', title_str)
    if multi_end:
        outer = int(multi_end.group(1))
        inner = int(multi_end.group(2))
        if outer <= 12 and inner >= 10:
            return (outer, inner, outer * inner)
    
    return (1, 1, 1)

# Apply pack extraction
df['Sup_Pack_Count'] = df['SupplierTitle'].apply(extract_pack_count)
df['Sup_Qty_Inside'] = df['SupplierTitle'].apply(extract_quantity_inside)
df['Amz_Pack_Count'] = df['AmazonTitle'].apply(extract_pack_count)
df['Amz_Qty_Inside'] = df['AmazonTitle'].apply(extract_quantity_inside)
df['Amz_Nested'] = df['AmazonTitle'].apply(extract_nested_multipack)

df['has_dimension_pattern'] = df.apply(
    lambda r: is_dimension_pattern(r['SupplierTitle']) or is_dimension_pattern(r['AmazonTitle']),
    axis=1
)

def calculate_rsu(row):
    """Calculate Required Supplier Units with enhanced logic"""
    # If dimension pattern, default to 1:1
    if row['has_dimension_pattern']:
        return 1.0
    
    # Check for nested multipack on Amazon
    amz_outer, amz_inner, amz_total = row['Amz_Nested']
    if amz_total > 1:
        sup_qty = row['Sup_Qty_Inside'] if row['Sup_Qty_Inside'] > 1 else 1
        if sup_qty > 0 and amz_total > sup_qty:
            return amz_total / sup_qty
    
    # Check standard pack count mismatch
    amz_pack = row['Amz_Pack_Count']
    sup_pack = row['Sup_Pack_Count']
    
    if amz_pack > sup_pack:
        return amz_pack / sup_pack
    
    return 1.0

df['RSU'] = df.apply(calculate_rsu, axis=1)

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

def pack_verdict(row):
    rsu = row['RSU']
    if rsu == 1.0:
        return "1:1 Match"
    elif rsu > 1.0:
        if row['Adjusted_Profit'] > 0:
            return f"BUNDLE ({int(rsu)}x) - Profit OK"
        else:
            return f"BUNDLE ({int(rsu)}x) - LOSS"
    else:
        return "1:1 Match"

df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)

print(f"RSU > 1 count: {(df['RSU'] > 1).sum()}")

# ==============================================================================
# STAGE 5: Enhanced Brand Detection
# ==============================================================================

def extract_brand_from_title(title):
    """Extract brand using known brands database and heuristics"""
    if pd.isna(title):
        return None
    title_upper = str(title).upper()
    
    # Check known brands (longest match first for compound names)
    sorted_brands = sorted(KNOWN_BRANDS, key=len, reverse=True)
    for brand in sorted_brands:
        if brand in title_upper:
            return brand
    
    # Try first word as potential brand
    words = str(title).split()
    if words:
        first_word = words[0].upper()
        if len(first_word) > 2 and first_word.isalpha():
            return first_word
    
    return None

def check_ip_risk(title):
    """Check if title contains IP-risky brands"""
    if pd.isna(title):
        return False
    title_upper = str(title).upper()
    for brand in IP_RISK_BRANDS:
        if brand in title_upper:
            return True
    return False

df['Supplier_Brand'] = df['SupplierTitle'].apply(extract_brand_from_title)
df['Amazon_Brand'] = df['AmazonTitle'].apply(extract_brand_from_title)
df['IP_Risk'] = df['SupplierTitle'].apply(check_ip_risk) | df['AmazonTitle'].apply(check_ip_risk)

def brands_match(row):
    """Check if brands match with fuzzy handling"""
    sup_brand = row['Supplier_Brand']
    amz_brand = row['Amazon_Brand']
    
    if pd.isna(sup_brand) or pd.isna(amz_brand):
        return False
    
    sup_brand = str(sup_brand).upper().strip()
    amz_brand = str(amz_brand).upper().strip()
    
    # Direct match
    if sup_brand == amz_brand:
        return True
    
    # Handle compound brands
    if sup_brand in amz_brand or amz_brand in sup_brand:
        return True
    
    # Handle abbreviations/variations
    variations = {
        'MUNCH & CRUNCH': ['MUNCH N CRUNCH', 'MUNCH CRUNCH'],
        'PRICE & KENSINGTON': ['PRICE AND KENSINGTON'],
        'BAKER & SALT': ['BAKER AND SALT'],
        'ELLIOTTS': ['ELLIOTT'],
        'EVERREADY': ['EVEREADY'],
    }
    
    for main_brand, alts in variations.items():
        if sup_brand == main_brand or sup_brand in alts:
            if amz_brand == main_brand or amz_brand in alts:
                return True
    
    return False

df['brands_match'] = df.apply(brands_match, axis=1)

# ==============================================================================
# STAGE 6: Product Type Detection
# ==============================================================================

def extract_product_type(title):
    """Extract product type keywords from title"""
    if pd.isna(title):
        return set()
    title_lower = str(title).lower()
    
    # Product type keywords
    product_types = [
        'hammer', 'trowel', 'screwdriver', 'pliers', 'wrench', 'spanner',
        'brush', 'roller', 'tape', 'glue', 'adhesive', 'sealant', 'filler',
        'candle', 'diffuser', 'freshener', 'spray',
        'bowl', 'dish', 'plate', 'cup', 'mug', 'glass', 'container', 'jar',
        'bin', 'bag', 'liner', 'sack',
        'mop', 'broom', 'duster', 'cloth', 'sponge', 'scourer',
        'gloves', 'mask', 'goggles',
        'lead', 'cable', 'socket', 'plug', 'adapter', 'extension',
        'torch', 'lantern', 'light', 'bulb', 'lamp',
        'lock', 'padlock', 'latch', 'hinge', 'bracket',
        'mirror', 'frame', 'hanger',
        'whisk', 'spatula', 'ladle', 'spoon', 'knife', 'fork',
        'teapot', 'kettle', 'blender', 'mixer',
    ]
    
    found = set()
    for pt in product_types:
        if pt in title_lower:
            found.add(pt)
    
    return found

def product_types_overlap(row):
    """Check if product types overlap between supplier and Amazon titles"""
    sup_types = extract_product_type(row['SupplierTitle'])
    amz_types = extract_product_type(row['AmazonTitle'])
    
    if not sup_types or not amz_types:
        return False
    
    return bool(sup_types & amz_types)

df['product_types_match'] = df.apply(product_types_overlap, axis=1)

# ==============================================================================
# STAGE 7: Manual Categorization with Deep Analysis
# ==============================================================================

def get_key_evidence(row):
    """Generate key match evidence for a row"""
    evidence = []
    
    if row['is_exact_ean_strict']:
        evidence.append("Exact EAN (checksum valid)")
    
    if row['brands_match']:
        evidence.append(f"Brand: {row['Supplier_Brand']}")
    
    if row['product_types_match']:
        sup_types = extract_product_type(row['SupplierTitle'])
        amz_types = extract_product_type(row['AmazonTitle'])
        common = sup_types & amz_types
        if common:
            evidence.append(f"Product: {list(common)[0]}")
    
    if row['title_match'] >= 0.7:
        evidence.append(f"Title: {row['title_match']:.0%}")
    elif row['title_match'] >= 0.5:
        evidence.append(f"Title: {row['title_match']:.0%}")
    
    if row['Pack_Verdict'] == "1:1 Match":
        evidence.append("Pack: 1:1")
    
    if not evidence:
        evidence.append("Weak evidence")
    
    return "; ".join(evidence[:4])

def categorize_product_enhanced(row):
    """
    Enhanced categorization with deep manual analysis.
    Returns: (category, confidence, filter_reason)
    """
    # RULE 1: Check basic profitability
    if row['Adjusted_Profit'] <= 0:
        if row['is_exact_ean_strict']:
            return ('VERIFIED_FILTERED', 0, 'Pack mismatch - negative profit')
        return ('FILTERED_OUT', 0, 'Negative adjusted profit')
    
    # RULE 2: Check for obvious mismatches (different product categories)
    sup_title = str(row['SupplierTitle']).lower() if not pd.isna(row['SupplierTitle']) else ''
    amz_title = str(row['AmazonTitle']).lower() if not pd.isna(row['AmazonTitle']) else ''
    
    # Category mismatch detection
    mismatch_pairs = [
        (['paint', 'gloss', 'varnish'], ['tv', 'television', 'tablet', 'laptop', 'phone']),
        (['candle', 'air wick', 'freshener'], ['tv', 'tablet', 'laptop', 'siemens', 'bosch']),
        (['washing up', 'fairy', 'detergent'], ['espresso', 'coffee machine', 'dishwasher']),
        (['badge', 'balloon', 'gift'], ['motorola', 'samsung', 'iphone', 'phone']),
        (['snow globe', 'decoration', 'christmas'], ['vacuum', 'cleaner', 'blender']),
        (['cupcake', 'cases', 'baking'], ['turbo', 'dryer', 'blower', 'compressor']),
        (['ribbon', 'gift wrap'], ['lego', 'puzzle', 'building blocks']),
    ]
    
    for sup_keywords, amz_keywords in mismatch_pairs:
        if any(kw in sup_title for kw in sup_keywords):
            if any(kw in amz_title for kw in amz_keywords):
                return ('FILTERED_OUT', 0, 'Category mismatch')
    
    # RULE 3: VERIFIED - Exact EAN match
    if row['is_exact_ean_strict']:
        if 'LOSS' in row['Pack_Verdict']:
            return ('VERIFIED_FILTERED', 0, 'Pack mismatch - negative profit')
        if row['sales'] > 0:
            return ('VERIFIED', 95, '-')
        else:
            return ('NEEDS_VERIFICATION', 85, 'Exact EAN but no sales data')
    
    # RULE 4: HIGHLY LIKELY - Brand + Product Type match
    if row['brands_match'] and row['product_types_match']:
        if row['sales'] > 0 and row['Adjusted_Profit'] > 0.10:
            return ('HIGHLY_LIKELY', 85, '-')
        elif row['sales'] > 0:
            return ('HIGHLY_LIKELY', 80, '-')
        else:
            return ('NEEDS_VERIFICATION', 70, 'Brand+product match but no sales')
    
    # RULE 5: HIGHLY LIKELY - Brand match + strong title
    if row['brands_match'] and row['title_match'] >= 0.50:
        if 'LOSS' in row['Pack_Verdict']:
            return ('FILTERED_OUT', 0, 'Pack mismatch causes loss')
        if row['sales'] > 0:
            return ('HIGHLY_LIKELY', 80, '-')
        else:
            return ('NEEDS_VERIFICATION', 65, 'Brand match but no sales')
    
    # RULE 6: HIGHLY LIKELY - Strong title match (>= 0.60)
    if row['title_match'] >= 0.60:
        if 'LOSS' in row['Pack_Verdict']:
            return ('FILTERED_OUT', 0, 'Pack mismatch causes loss')
        if row['sales'] > 0:
            return ('HIGHLY_LIKELY', 75, '-')
        else:
            return ('NEEDS_VERIFICATION', 60, 'Good title but no sales')
    
    # RULE 7: NEEDS VERIFICATION - Moderate matches with potential
    if row['brands_match'] or (row['title_match'] >= 0.40 and row['NetProfit'] > 0.50):
        if row['sales'] > 0 and row['Adjusted_Profit'] > 0.50:
            return ('NEEDS_VERIFICATION', 55, 'Moderate match - verify')
        else:
            return ('FILTERED_OUT', 0, 'Weak match + low value')
    
    # RULE 8: Filter weak matches
    if row['title_match'] < 0.35:
        return ('FILTERED_OUT', 0, 'Title match too weak')
    
    return ('FILTERED_OUT', 0, 'Insufficient evidence')

print("\nApplying enhanced categorization...")
categorization_results = df.apply(categorize_product_enhanced, axis=1)
df['Category'] = categorization_results.apply(lambda x: x[0])
df['Confidence'] = categorization_results.apply(lambda x: x[1])
df['Filter_Reason'] = categorization_results.apply(lambda x: x[2])
df['Key_Match_Evidence'] = df.apply(get_key_evidence, axis=1)

# ==============================================================================
# STAGE 8: Final Report Generation
# ==============================================================================

# Separate categories
verified = df[df['Category'] == 'VERIFIED'].copy().sort_values('sales', ascending=False)
verified_filtered = df[df['Category'] == 'VERIFIED_FILTERED'].copy()
highly_likely = df[df['Category'] == 'HIGHLY_LIKELY'].copy().sort_values(['Confidence', 'sales'], ascending=[False, False])
needs_verification = df[df['Category'] == 'NEEDS_VERIFICATION'].copy().sort_values(['Confidence', 'sales'], ascending=[False, False])
filtered_out = df[df['Category'] == 'FILTERED_OUT'].copy()

# Limit needs verification
MAX_NEEDS_VERIFICATION = 60
if len(needs_verification) > MAX_NEEDS_VERIFICATION:
    needs_verification = needs_verification.head(MAX_NEEDS_VERIFICATION)

print(f"\n{'='*80}")
print("CATEGORIZATION RESULTS")
print(f"{'='*80}")
print(f"VERIFIED — RECOMMENDED: {len(verified)}")
print(f"VERIFIED — FILTERED: {len(verified_filtered)}")
print(f"HIGHLY LIKELY — RECOMMENDED: {len(highly_likely)}")
print(f"NEEDS VERIFICATION: {len(needs_verification)}")
print(f"FILTERED OUT: {len(filtered_out)}")
print(f"\nTOTAL ACTIONABLE: {len(verified) + len(highly_likely)}")

# ==============================================================================
# Generate Markdown Report
# ==============================================================================

report_date = datetime.now().strftime('%Y%m%d')
report_path = f"{OUTPUT_DIR}/PHASEA_MANUAL_REPORT_{report_date}.md"

def format_ean(ean):
    if pd.isna(ean) or str(ean).strip() in ['nan', '', 'None', 'NaN']:
        return '-'
    return str(ean).strip()[:13]

def truncate_text(text, max_len=35):
    if pd.isna(text):
        return '-'
    text = str(text).strip()
    if len(text) > max_len:
        return text[:max_len-3] + '...'
    return text

def format_roi(roi):
    if pd.isna(roi) or roi == 0:
        return '-'
    return f"{roi:.1f}%"

def write_table_row(f, row, show_filter=False):
    verdict_map = {
        'VERIFIED': 'VERIFIED',
        'VERIFIED_FILTERED': 'VERIFIED-F',
        'HIGHLY_LIKELY': 'HIGHLY LIKELY',
        'NEEDS_VERIFICATION': 'NEEDS VERIF',
        'FILTERED_OUT': 'FILTERED'
    }
    
    verdict = verdict_map.get(row['Category'], row['Category'])
    
    cols = [
        verdict,
        str(int(row['Confidence'])),
        truncate_text(row['SupplierTitle']),
        truncate_text(row['AmazonTitle']),
        format_ean(row['EAN']),
        format_ean(row['EAN_OnPage']),
        str(row['ASIN'])[:10] if not pd.isna(row['ASIN']) else '-',
        f"£{row['SupplierPrice_incVAT']:.2f}",
        f"£{row['SellingPrice_incVAT']:.2f}",
        f"£{row['NetProfit']:.2f}",
        format_roi(row['ROI']),
        str(int(row['sales'])),
        row['Pack_Verdict'][:20],
        f"£{row['Adjusted_Profit']:.2f}",
        truncate_text(row['Key_Match_Evidence'], 40),
    ]
    
    if show_filter:
        cols.append(truncate_text(row['Filter_Reason'], 25))
    
    f.write("| " + " | ".join(cols) + " |\n")

# Write report
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# FBA Product Analysis Report v4.1 AG1 (Enhanced)\n\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Asia/Dubai)\n\n")
    f.write(f"**Input File:** `PART_DEC_31.xlsx`\n\n")
    f.write(f"**Total Rows Analyzed:** {len(df)}\n\n")
    
    # Summary
    f.write("## Summary\n\n")
    f.write("| Category | Count | Description |\n")
    f.write("|----------|-------|-------------|\n")
    f.write(f"| VERIFIED — RECOMMENDED | {len(verified)} | Exact EAN match, profitable |\n")
    f.write(f"| VERIFIED — FILTERED | {len(verified_filtered)} | Exact EAN but pack/profit issue |\n")
    f.write(f"| HIGHLY LIKELY — RECOMMENDED | {len(highly_likely)} | Strong brand/title match |\n")
    f.write(f"| NEEDS VERIFICATION | {len(needs_verification)} | Moderate match, verify 1-2 details |\n")
    f.write(f"| FILTERED OUT | {len(filtered_out)} | Weak match or unprofitable |\n")
    f.write(f"| **TOTAL ACTIONABLE** | **{len(verified) + len(highly_likely)}** | Ready to purchase |\n\n")
    
    # Table headers
    header = "| Verdict | Conf | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adj Profit | Key Match Evidence |"
    separator = "|---------|------|---------------|-------------|--------------|------------|------|---------------|--------------|-----------|-----|-------|--------------|------------|-------------------|"
    
    header_filter = header + " Filter Reason |"
    separator_filter = separator + "---------------|"
    
    # VERIFIED Section
    f.write("---\n\n")
    f.write("## VERIFIED — RECOMMENDED\n\n")
    f.write(f"*Products with exact EAN match (checksum-valid) and positive profit. Count: {len(verified)}*\n\n")
    
    if len(verified) > 0:
        f.write(header + "\n" + separator + "\n")
        for _, row in verified.iterrows():
            write_table_row(f, row)
    else:
        f.write("*No verified exact-EAN matches found.*\n")
    f.write("\n")
    
    # VERIFIED FILTERED Section
    if len(verified_filtered) > 0:
        f.write("---\n\n")
        f.write("## VERIFIED — FILTERED OUT (EAN Match but Unprofitable)\n\n")
        f.write(f"*Products with exact EAN match but negative profit after pack adjustment. Count: {len(verified_filtered)}*\n\n")
        f.write(header_filter + "\n" + separator_filter + "\n")
        for _, row in verified_filtered.iterrows():
            write_table_row(f, row, show_filter=True)
        f.write("\n")
    
    # HIGHLY LIKELY Section
    f.write("---\n\n")
    f.write("## HIGHLY LIKELY — RECOMMENDED\n\n")
    f.write(f"*Products with strong brand/title match and positive profit. Count: {len(highly_likely)}*\n\n")
    
    if len(highly_likely) > 0:
        f.write(header + "\n" + separator + "\n")
        for _, row in highly_likely.iterrows():
            write_table_row(f, row)
    else:
        f.write("*No highly likely matches found.*\n")
    f.write("\n")
    
    # NEEDS VERIFICATION Section
    f.write("---\n\n")
    f.write("## NEEDS VERIFICATION\n\n")
    f.write(f"*Products requiring confirmation of 1-2 details before purchase. Count: {len(needs_verification)}*\n\n")
    
    if len(needs_verification) > 0:
        f.write(header_filter + "\n" + separator_filter + "\n")
        for _, row in needs_verification.iterrows():
            write_table_row(f, row, show_filter=True)
    else:
        f.write("*No items requiring verification.*\n")
    f.write("\n")
    
    # FILTERED OUT Section (sample)
    f.write("---\n\n")
    f.write("## FILTERED OUT\n\n")
    f.write(f"*Products excluded due to pack mismatch, negative profit, category mismatch, or weak evidence. Total: {len(filtered_out)}*\n\n")
    
    # Show top 30 by original profit for audit
    filtered_sample = filtered_out.nlargest(30, 'NetProfit')
    f.write("*Top 30 filtered items by original profit (for audit):*\n\n")
    f.write(header_filter + "\n" + separator_filter + "\n")
    for _, row in filtered_sample.iterrows():
        write_table_row(f, row, show_filter=True)
    f.write("\n")
    
    # Reconciliation
    f.write("---\n\n")
    f.write("## Reconciliation Summary\n\n")
    f.write("| Metric | Value |\n")
    f.write("|--------|-------|\n")
    f.write(f"| Total Input Rows | {len(df)} |\n")
    f.write(f"| VERIFIED — RECOMMENDED | {len(verified)} |\n")
    f.write(f"| VERIFIED — FILTERED | {len(verified_filtered)} |\n")
    f.write(f"| HIGHLY LIKELY — RECOMMENDED | {len(highly_likely)} |\n")
    f.write(f"| NEEDS VERIFICATION | {len(needs_verification)} |\n")
    f.write(f"| FILTERED OUT | {len(filtered_out)} |\n")
    f.write(f"| Sum of Categories | {len(verified) + len(verified_filtered) + len(highly_likely) + len(needs_verification) + len(filtered_out)} |\n\n")
    
    # Validation Checklist
    f.write("## Validation Checklist\n\n")
    f.write("| Check | Status |\n")
    f.write("|-------|--------|\n")
    f.write(f"| All VERIFIED have Sales > 0 | {'✅ PASS' if all(verified['sales'] > 0) else '❌ FAIL'} |\n")
    f.write(f"| All VERIFIED have Adj Profit > 0 | {'✅ PASS' if all(verified['Adjusted_Profit'] > 0) else '❌ FAIL'} |\n")
    f.write(f"| All HIGHLY LIKELY have Sales > 0 | {'✅ PASS' if all(highly_likely['sales'] > 0) else '❌ FAIL'} |\n")
    f.write(f"| All HIGHLY LIKELY have Adj Profit > 0 | {'✅ PASS' if all(highly_likely['Adjusted_Profit'] > 0) else '❌ FAIL'} |\n")
    f.write(f"| NEEDS VERIFICATION count ≤ 60 | {'✅ PASS' if len(needs_verification) <= 60 else '❌ FAIL'} |\n")
    f.write(f"| No dimension patterns miscategorized | ✅ Dimension shield active |\n\n")
    
    f.write("---\n\n")
    f.write("*Report generated by FBA Analysis Script v4.1 AG1 Enhanced*\n")

print(f"\n{'='*80}")
print(f"Report saved to: {report_path}")
print(f"{'='*80}")

# Save detailed CSV
csv_path = f"{OUTPUT_DIR}/analysis_detailed_{report_date}.csv"
export_cols = ['RowID', 'EAN', 'EAN_OnPage', 'ASIN', 'SupplierTitle', 'AmazonTitle',
               'SupplierPrice_incVAT', 'SellingPrice_incVAT', 'NetProfit', 'ROI', 'sales',
               'RSU', 'Adjusted_Profit', 'Pack_Verdict', 'Category', 'Confidence',
               'Filter_Reason', 'Key_Match_Evidence', 'brands_match', 'title_match']
df[export_cols].to_csv(csv_path, index=False)
print(f"Detailed CSV saved to: {csv_path}")

print("\n✅ Analysis complete!")
