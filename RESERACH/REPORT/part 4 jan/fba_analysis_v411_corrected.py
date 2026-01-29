"""
FBA Product Analysis Script v4.1.1 AG1 (CORRECTED)
Analyzes financial report for Amazon FBA arbitrage opportunities.
Applies proper dimension shielding and capacity multipack handling.
"""
import pandas as pd
import re
from datetime import datetime

# =============================================================================
# CONFIGURATION (Based on similar supplier calibration patterns)
# =============================================================================
INPUT_FILE = 'part 4 jan.xlsx'
OUTPUT_DIR = 'opus 1'

# Known valid brands for this supplier type (wholesale/hardware/household)
KNOWN_BRANDS = {
    'AMTECH', 'ROLSON', 'DRAPER', 'FAIRY', 'DETTOL', 'MARIGOLD', 'DUNLOP',
    'MASON CASH', 'PYREX', 'EVERBUILD', 'HARRIS', 'STATUS', 'EXTRASTAR',
    'ROUNDUP', 'LITTLE TREES', 'CHEF AID', 'BLUE CANYON', 'SOUDAL',
    'TIDYZ', 'KILROCK', 'PAN AROMA', 'APOLLO', 'SUPERIOR', 'JCB', 'YALE',
    'SCHOTT ZWIESEL', 'BEAUFORT', 'MASTERCLASS', 'MINKY', 'GIFTMAKER',
    'THERMOS', 'SISTEMA', 'WHAM', 'SWIRL', 'ELBOW GREASE', 'BACOFOIL',
    'RIZLA', 'QUEST', 'CHUPA CHUPS', 'MOKATE', 'KINGAVON', 'PUKKA',
    'PRODEC', 'ELLIOTT', 'TALA', 'VINERS', 'PASABAHCE', 'PLAYWRITE',
    'CLIPPER', 'CORAL', 'LAV', 'PRICE & KENSINGTON', 'PRICE AND KENSINGTON',
    'HOUSE MATE', 'TREAT AND EASE', 'FIRE UP', 'BIG CHEESE', 'AIRWICK',
    'AIR WICK', 'HIGHLAND COW', 'ROYLE HOME', 'SMART CHOICE', 'EXTRA SELECT',
    'VIVID', 'ASHLEY', 'HEM', 'SIMMER RING', 'GLASS WHISKEY', 'CARAFE',
    'MEMORIAL', 'CHRISTMAS', 'GEL LED', 'BAKER & SALT', 'BAKER AND SALT',
    'FIRST STEPS', 'KITCHEN PERFECTED', 'DEKTON', 'PENDEFORD', 'FALCON',
    'MARKSMAN', 'GROSVENOR', 'HOBBY', 'EVERYCHEF', 'PPS', 'VFM', 'PRIMA',
    'SUNNEX', 'SIL', 'ADORN', 'B&CO', 'BLOOME', 'FLOW', 'SWIFT', 'VRIYA',
    'BRIGHT & HOMELY', 'BRIGHT AND HOMELY', 'SHOP SMART', 'AUTO EXTREME',
    'CAR PRIDE', 'STEAM PUNK', 'DUVET', 'LUGGAGE', 'CORRUGATED', 'WOODEN',
    'WICKER', 'PADDED', 'SPECIAL OCCASIONS', 'PET STORE', 'WORLD OF PETS',
    'BABY PIPKIN', 'BUTTERFLY', 'SIGNATURE', 'FRAMED ART', 'ELF',
    'INCENSE', 'FLOWER SHOP', 'CHAMOIS', 'LONG PURSE', 'STAINLESS STEEL',
    'PRINT', 'HAPPY BIRTHDAY', 'MICROWAVE', 'SHOPPING BAG', 'HEAT HOLDERS',
    'ACRYLIC', 'NEMESIS NOW', 'ECO CHIC', 'SILK ROUTE', 'JUVALE', 'OXO',
    'PRESTIGE', 'JVL', 'DULUX', 'FAITHFULL', 'STAMFORD', 'KILNER',
}

# Supplier calibration (inferred from data patterns)
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pk", "pack", "pce", "pcs", "piece", "set", "each"],
    "allow_trailing_number_as_qty": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in", "ft", "m"],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ["magnification", "zoom", "power", "led", "watt", "w"],
    "table_pipe_sanitization": True
}

# =============================================================================
# STAGE 1: Data Loading & Initial Cleaning
# =============================================================================
print("=" * 60)
print("STAGE 1: Loading and Cleaning Data")
print("=" * 60)

df = pd.read_excel(INPUT_FILE)
print(f"Loaded {len(df)} rows from {INPUT_FILE}")

# Clean EAN columns
df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Find ROI column
roi_col = None
for c in df.columns:
    if 'roi' in c.lower():
        roi_col = c
        break
print(f"ROI column found: {roi_col}")

# Handle sales column
if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
else:
    df['sales'] = 0

# Add RowID for traceability
df['RowID'] = df.index + 2  # +2 because Excel rows start at 1 and header is row 1

print(f"Sales column: using 'bought_in_past_month'")
print(f"Total rows: {len(df)}")

# =============================================================================
# STAGE 1B: EAN Normalization Safety Flags
# =============================================================================
print("\n" + "=" * 60)
print("STAGE 1B: EAN Normalization")
print("=" * 60)

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

print(f"EANs cleaned to digits")

# =============================================================================
# STAGE 2: Title Similarity Calculation
# =============================================================================
print("\n" + "=" * 60)
print("STAGE 2: Title Similarity Calculation")
print("=" * 60)

from difflib import SequenceMatcher

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)
print(f"Title similarity calculated")

# =============================================================================
# STAGE 3B: Strict Barcode Validity + Checksum + Left-Padding
# =============================================================================
print("\n" + "=" * 60)
print("STAGE 3B: Strict Barcode Validity")
print("=" * 60)

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

def is_valid_ean(ean):
    if pd.isna(ean):
        return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-']

df['is_exact_ean_strict'] = (
    df['EAN_strict_valid']
    & df['EAN_OnPage_strict_valid']
    & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
)

print(f"Strict valid Supplier EANs: {df['EAN_strict_valid'].sum()}")
print(f"Strict valid Amazon EANs: {df['EAN_OnPage_strict_valid'].sum()}")
print(f"Strict exact EAN matches: {df['is_exact_ean_strict'].sum()}")

# =============================================================================
# STAGE 4: IMPROVED Pack Size Extraction with DIMENSION SHIELD
# =============================================================================
print("\n" + "=" * 60)
print("STAGE 4: Pack Size Extraction (WITH DIMENSION SHIELD)")
print("=" * 60)

def is_dimension_context(title, pos, number):
    """
    Check if a number at position 'pos' is in a dimension context.
    Returns True if this number should NOT be treated as pack count.
    """
    title_lower = str(title).lower()
    
    # Check for unit immediately after the number
    after_pattern = rf'{number}\s*(?:cm|mm|ml|ltr|l|kg|g|oz|inch|in|ft|m)\b'
    if re.search(after_pattern, title_lower):
        return True
    
    # Check for "NxN" dimension patterns
    dim_patterns = [
        rf'\b{number}\s*x\s*\d+\s*(?:cm|mm|inch|in|ft|m)\b',  # NxM cm
        rf'\b\d+\s*x\s*{number}\s*(?:cm|mm|inch|in|ft|m)\b',  # MxN cm
        rf'\b{number}\s*x\s*\d+\s*x\s*\d+',  # NxMxP (3D dimensions)
    ]
    for pat in dim_patterns:
        if re.search(pat, title_lower):
            return True
    
    return False

def extract_amazon_multipack(title):
    """
    CORRECTED: Extract multipack count from Amazon title.
    Handles patterns like "3 x 400ml" correctly as RSU=3, not RSU=1200.
    Also handles "(4 x 50)" as RSU=4.
    """
    if pd.isna(title):
        return 1
    title_str = str(title).lower()
    
    # Pattern 1: "N x [capacity]ml/g/l" at START - this means N units (RSU=N)
    # E.g., "3 x 400ml" = 3 bottles of 400ml = RSU=3
    capacity_multipack = re.search(r'^\s*(\d+)\s*x\s*\d+\s*(?:ml|g|l|ltr|kg|oz)\b', title_str)
    if capacity_multipack:
        return int(capacity_multipack.group(1))
    
    # Pattern 2: "N x Product" at START without capacity - this means N units
    # E.g., "3 x Elbow Grease" = 3 units = RSU=3
    start_multipack = re.search(r'^\s*(\d+)\s*x\s+[a-z]', title_str)
    if start_multipack:
        count = int(start_multipack.group(1))
        if count <= 20:  # Reasonable multipack size
            return count
    
    # Pattern 3: "(N x M)" nested pack - check if M is capacity or quantity
    nested = re.search(r'\((\d+)\s*x\s*(\d+)\s*(?:ml|g|l|ltr|kg|oz)?\)', title_str)
    if nested:
        outer = int(nested.group(1))
        # If capacity unit present, RSU = outer count only
        if re.search(r'\((\d+)\s*x\s*(\d+)\s*(?:ml|g|l|ltr|kg|oz)\)', title_str):
            return outer
        # Otherwise might be quantity inside (like 4x50 bags)
        inner = int(nested.group(2))
        if outer <= 12 and inner >= 20:
            # This looks like outer packs of inner items (e.g., 4 packs of 50)
            return outer  # RSU = outer packs needed
    
    # Pattern 4: "Pack of N" / "N-pack" / "N pack"
    pack_patterns = [
        r'pack of (\d+)',
        r'(\d+)-pack\b',
        r'(\d+)\s*pack\b',
    ]
    for pat in pack_patterns:
        match = re.search(pat, title_str)
        if match:
            count = int(match.group(1))
            if count > 1 and count <= 100:
                return count
    
    return 1

def extract_supplier_quantity(title):
    """Extract pack size from supplier title. Defaults to 1."""
    if pd.isna(title):
        return 1
    title_str = str(title).lower()
    
    # Skip dimension patterns - these are NOT pack counts
    # E.g., "9X9IN" is size, not 81 packs
    
    patterns = [
        (r'pack of (\d+)', False),
        (r'set of (\d+)', False),
        (r'\b(\d+)\s*pack\b', False),
        (r'\b(\d+)\s*pk\b', False),
        (r'(\d+)\s*pce\b', True),  # Check dimension context
        (r'(\d+)\s*pcs\b', True),
        (r'(\d+)\s*pieces?\b', True),
    ]
    
    for pat, check_dim in patterns:
        match = re.search(pat, title_str)
        if match:
            qty = int(match.group(1))
            if qty > 1 and qty < 100:
                if check_dim:
                    # Check if this number is in dimension context
                    if is_dimension_context(title, match.start(), match.group(1)):
                        continue
                return qty
    
    return 1

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_supplier_quantity)
df['Amz_Multipack'] = df['AmazonTitle'].apply(extract_amazon_multipack)

# Calculate RSU (Required Supplier Units)
def calculate_rsu(row):
    amz = row['Amz_Multipack']
    sup = row['Sup_Qty']
    if sup > 0 and amz > 0:
        return max(1, amz / sup)
    return 1

df['RSU'] = df.apply(calculate_rsu, axis=1)

def recalculate_profit(row):
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        rsu = row['RSU']
        adjustment = supplier_cost * (rsu - 1)
        return original_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

def pack_verdict(row):
    rsu = row['RSU']
    if rsu == 1.0:
        return "1:1 Match"
    elif rsu > 1.0:
        if row['Adjusted_Profit'] > 0:
            return f"BUNDLE ({int(rsu)}x) - OK"
        else:
            return f"BUNDLE ({int(rsu)}x) - LOSS"
    return "1:1 Match"

df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)

print(f"Pack sizes extracted with dimension shield")
print(f"Rows with RSU > 1: {len(df[df['RSU'] > 1])}")
print(f"Rows with negative Adjusted_Profit: {len(df[df['Adjusted_Profit'] <= 0])}")

# =============================================================================
# STAGE 5B: STRICT BRAND MATCHING
# =============================================================================
print("\n" + "=" * 60)
print("STAGE 5B: Brand Matching (STRICT)")
print("=" * 60)

def extract_brand(title):
    """Extract brand from supplier title (usually first 1-2 words)"""
    if pd.isna(title):
        return ''
    
    title_upper = str(title).upper().strip()
    words = title_upper.split()
    
    if not words:
        return ''
    
    # Check for two-word brands first
    if len(words) >= 2:
        two_word = f"{words[0]} {words[1]}"
        for brand in KNOWN_BRANDS:
            if brand.upper() == two_word:
                return brand
    
    # Check single word
    for brand in KNOWN_BRANDS:
        if brand.upper() == words[0]:
            return brand
    
    return words[0]  # Return first word as potential brand

def brands_match(sup_title, amz_title):
    """
    STRICT brand matching - only match if brand is in KNOWN_BRANDS
    or both titles contain the same distinctive brand term.
    """
    if pd.isna(sup_title) or pd.isna(amz_title):
        return False, ''
    
    sup_upper = str(sup_title).upper()
    amz_upper = str(amz_title).upper()
    
    # Check against known brands
    for brand in KNOWN_BRANDS:
        brand_upper = brand.upper()
        if brand_upper in sup_upper and brand_upper in amz_upper:
            return True, brand
    
    return False, ''

df['brand_info'] = df.apply(lambda x: brands_match(x['SupplierTitle'], x['AmazonTitle']), axis=1)
df['brand_match'] = df['brand_info'].apply(lambda x: x[0])
df['matched_brand'] = df['brand_info'].apply(lambda x: x[1])

print(f"Known brand matches: {df['brand_match'].sum()}")

# =============================================================================
# FINAL CATEGORIZATION
# =============================================================================
print("\n" + "=" * 60)
print("FINAL CATEGORIZATION")
print("=" * 60)

verified_recommended = []
verified_filtered = []
highly_likely_recommended = []
highly_likely_filtered = []
needs_verification = []

for idx, row in df.iterrows():
    # Prepare base data
    item = {
        'RowID': row['RowID'],
        'SupplierTitle': str(row['SupplierTitle'])[:80] if pd.notna(row['SupplierTitle']) else '-',
        'AmazonTitle': str(row['AmazonTitle'])[:80] if pd.notna(row['AmazonTitle']) else '-',
        'Supplier_EAN': row['EAN'] if is_valid_ean(row['EAN']) else '-',
        'Amazon_EAN': row['EAN_OnPage'] if is_valid_ean(row['EAN_OnPage']) else '-',
        'ASIN': row['ASIN'] if pd.notna(row['ASIN']) else '-',
        'SupplierPrice': f"£{row['SupplierPrice_incVAT']:.2f}" if pd.notna(row['SupplierPrice_incVAT']) else '-',
        'SellingPrice': f"£{row['SellingPrice_incVAT']:.2f}" if pd.notna(row['SellingPrice_incVAT']) else '-',
        'NetProfit': f"£{row['NetProfit']:.2f}" if pd.notna(row['NetProfit']) else '-',
        'ROI': f"{row[roi_col]:.1f}%" if pd.notna(row[roi_col]) else '-',
        'Sales': int(row['sales']) if pd.notna(row['sales']) else 0,
        'Pack_Verdict': row['Pack_Verdict'],
        'Adjusted_Profit': f"£{row['Adjusted_Profit']:.2f}" if pd.notna(row['Adjusted_Profit']) else '-',
        'title_match': row['title_match'],
        'brand_match': row['brand_match'],
        'matched_brand': row['matched_brand'],
        'is_exact_ean_strict': row['is_exact_ean_strict'],
        'RSU': row['RSU'],
    }
    
    # ===== CATEGORY 1: VERIFIED (Exact EAN Match) =====
    if row['is_exact_ean_strict']:
        item['Confidence'] = 95
        item['Key_Match_Evidence'] = 'Exact EAN match; barcodes validated'
        
        if row['Adjusted_Profit'] > 0:
            item['Verdict'] = 'VERIFIED'
            item['Filter_Reason'] = '-'
            verified_recommended.append(item)
        else:
            item['Verdict'] = 'FILTERED OUT'
            item['Filter_Reason'] = f"RSU={int(row['RSU'])}; adjusted profit negative"
            verified_filtered.append(item)
    
    # ===== CATEGORY 2: HIGHLY LIKELY (Brand + Product Match) =====
    elif row['brand_match'] and row['title_match'] >= 0.35:
        item['Confidence'] = 80
        item['Key_Match_Evidence'] = f"Brand: {row['matched_brand']}; title sim: {row['title_match']:.2f}"
        
        if row['Adjusted_Profit'] > 0:
            item['Verdict'] = 'HIGHLY LIKELY'
            item['Filter_Reason'] = '-'
            highly_likely_recommended.append(item)
        else:
            item['Verdict'] = 'FILTERED OUT'
            item['Filter_Reason'] = f"RSU={int(row['RSU'])}; adjusted profit negative"
            highly_likely_filtered.append(item)
    
    # ===== CATEGORY 3: NEEDS VERIFICATION =====
    elif row['title_match'] >= 0.50 and row['Adjusted_Profit'] > 0:
        # High title similarity but brand not confirmed
        item['Confidence'] = 65
        item['Verdict'] = 'NEEDS VERIFICATION'
        item['Key_Match_Evidence'] = f"Title similarity: {row['title_match']:.2f}"
        item['Filter_Reason'] = 'Confirm brand matches on packaging'
        needs_verification.append(item)
    
    elif row['brand_match'] and row['Adjusted_Profit'] > 0 and row['title_match'] >= 0.25:
        # Brand matches but low title similarity (may be variant)
        item['Confidence'] = 60
        item['Verdict'] = 'NEEDS VERIFICATION'
        item['Key_Match_Evidence'] = f"Brand: {row['matched_brand']}"
        item['Filter_Reason'] = 'Verify product variant matches'
        needs_verification.append(item)

print(f"VERIFIED Recommended: {len(verified_recommended)}")
print(f"VERIFIED Filtered: {len(verified_filtered)}")
print(f"HIGHLY LIKELY Recommended: {len(highly_likely_recommended)}")
print(f"HIGHLY LIKELY Filtered: {len(highly_likely_filtered)}")
print(f"NEEDS VERIFICATION: {len(needs_verification)}")

# =============================================================================
# GENERATE REPORT
# =============================================================================
print("\n" + "=" * 60)
print("GENERATING REPORT")
print("=" * 60)

def sanitize_cell(val):
    """Sanitize cell value for markdown table"""
    val = str(val)
    val = val.replace('|', '/')
    val = val.replace('\n', ' ').replace('\r', ' ')
    return val

def format_table_row(item):
    """Format a single table row"""
    cells = [
        item.get('Verdict', '-'),
        str(item.get('Confidence', '-')),
        sanitize_cell(item.get('SupplierTitle', '-'))[:50],
        sanitize_cell(item.get('AmazonTitle', '-'))[:50],
        sanitize_cell(item.get('Supplier_EAN', '-')),
        sanitize_cell(item.get('Amazon_EAN', '-')),
        item.get('ASIN', '-'),
        item.get('SupplierPrice', '-'),
        item.get('SellingPrice', '-'),
        item.get('NetProfit', '-'),
        item.get('ROI', '-'),
        str(item.get('Sales', 0)),
        item.get('Pack_Verdict', '-'),
        item.get('Adjusted_Profit', '-'),
        sanitize_cell(item.get('Key_Match_Evidence', '-'))[:40],
        sanitize_cell(item.get('Filter_Reason', '-'))[:30],
    ]
    
    return '| ' + ' | '.join(cells) + ' |'

# Generate timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
report_filename = f"{OUTPUT_DIR}/PHASEA_MANUAL_REPORT_{timestamp}.md"

# Table headers
headers = ['Verdict', 'Confidence', 'SupplierTitle', 'AmazonTitle', 'Supplier EAN', 'Amazon EAN', 
           'ASIN', 'SupplierPrice', 'SellingPrice', 'NetProfit', 'ROI', 'Sales', 
           'Pack Verdict', 'Adjusted Profit', 'Key Match Evidence', 'Filter Reason']
header_row = '| ' + ' | '.join(headers) + ' |'
separator = '|' + '|'.join(['-' * (len(h) + 2) for h in headers]) + '|'

with open(report_filename, 'w', encoding='utf-8') as f:
    f.write("# PHASEA MANUAL REPORT\n\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**Input File:** {INPUT_FILE}\n")
    f.write(f"**Supplier:** Unknown (pre-filtered data)\n\n")
    
    f.write("## Summary Counts\n\n")
    f.write(f"- VERIFIED — RECOMMENDED: {len(verified_recommended)}\n")
    f.write(f"- VERIFIED — FILTERED OUT / EXCLUDED: {len(verified_filtered)}\n")
    f.write(f"- HIGHLY LIKELY — RECOMMENDED: {len(highly_likely_recommended)}\n")
    f.write(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {len(highly_likely_filtered)}\n")
    f.write(f"- NEEDS VERIFICATION: {len(needs_verification)}\n")
    total_categorized = len(verified_recommended) + len(verified_filtered) + len(highly_likely_recommended) + len(highly_likely_filtered) + len(needs_verification)
    f.write(f"- UNRELATED / NOT INCLUDED: {len(df) - total_categorized}\n")
    f.write(f"- TOTAL ANALYZED: {len(df)}\n\n")
    
    f.write("This report applies v4.1.1 Thorough Manual Analysis with CORRECTED dimension shielding:\n")
    f.write("- Dimension patterns (e.g., 9x9in, 500ML) are NOT treated as pack counts.\n")
    f.write("- Capacity multipacks (e.g., '3 x 400ml') correctly interpreted as RSU=3.\n")
    f.write("- Only KNOWN BRANDS trigger HIGHLY LIKELY classification.\n")
    f.write("- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit).\n\n")
    
    # VERIFIED RECOMMENDED
    f.write(f"## VERIFIED — RECOMMENDED (count={len(verified_recommended)})\n\n")
    if verified_recommended:
        verified_recommended.sort(key=lambda x: x.get('Sales', 0), reverse=True)
        f.write("```text\n")
        f.write(header_row + '\n')
        f.write(separator + '\n')
        for item in verified_recommended:
            f.write(format_table_row(item) + '\n')
        f.write("```\n\n")
    else:
        f.write("*No exact EAN matches found with positive adjusted profit.*\n\n")
    
    # VERIFIED FILTERED
    f.write(f"## VERIFIED — FILTERED OUT / EXCLUDED (count={len(verified_filtered)})\n\n")
    if verified_filtered:
        f.write("```text\n")
        f.write(header_row + '\n')
        f.write(separator + '\n')
        for item in verified_filtered:
            f.write(format_table_row(item) + '\n')
        f.write("```\n\n")
    else:
        f.write("*No exact EAN matches filtered out due to pack/profit issues.*\n\n")
    
    # HIGHLY LIKELY RECOMMENDED
    f.write(f"## HIGHLY LIKELY — RECOMMENDED (count={len(highly_likely_recommended)})\n\n")
    if highly_likely_recommended:
        highly_likely_recommended.sort(key=lambda x: (x.get('Confidence', 0), x.get('Sales', 0)), reverse=True)
        f.write("```text\n")
        f.write(header_row + '\n')
        f.write(separator + '\n')
        for item in highly_likely_recommended:
            f.write(format_table_row(item) + '\n')
        f.write("```\n\n")
    else:
        f.write("*No strong brand+product matches found with positive profit.*\n\n")
    
    # HIGHLY LIKELY FILTERED
    f.write(f"## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={len(highly_likely_filtered)})\n\n")
    if highly_likely_filtered:
        f.write("```text\n")
        f.write(header_row + '\n')
        f.write(separator + '\n')
        for item in highly_likely_filtered:
            f.write(format_table_row(item) + '\n')
        f.write("```\n\n")
    else:
        f.write("*No brand+product matches filtered out.*\n\n")
    
    # NEEDS VERIFICATION
    f.write(f"## NEEDS VERIFICATION (count={len(needs_verification)})\n\n")
    if needs_verification:
        needs_verification.sort(key=lambda x: (x.get('Confidence', 0), x.get('Sales', 0)), reverse=True)
        f.write("```text\n")
        f.write(header_row + '\n')
        f.write(separator + '\n')
        for item in needs_verification[:100]:
            f.write(format_table_row(item) + '\n')
        if len(needs_verification) > 100:
            f.write(f"... and {len(needs_verification) - 100} more items\n")
        f.write("```\n\n")
    else:
        f.write("*No items requiring verification.*\n\n")
    
    # Reconciliation
    f.write("## RECONCILIATION\n\n")
    f.write(f"| Category | Count |\n")
    f.write(f"|----------|-------|\n")
    f.write(f"| VERIFIED — RECOMMENDED | {len(verified_recommended)} |\n")
    f.write(f"| VERIFIED — FILTERED OUT | {len(verified_filtered)} |\n")
    f.write(f"| HIGHLY LIKELY — RECOMMENDED | {len(highly_likely_recommended)} |\n")
    f.write(f"| HIGHLY LIKELY — FILTERED OUT | {len(highly_likely_filtered)} |\n")
    f.write(f"| NEEDS VERIFICATION | {len(needs_verification)} |\n")
    f.write(f"| UNRELATED / NOT INCLUDED | {len(df) - total_categorized} |\n")
    f.write(f"| **TOTAL ANALYZED** | **{len(df)}** |\n\n")
    
    f.write("---\n")
    f.write("*Report generated by FBA Analysis Script v4.1.1 AG1 (CORRECTED)*\n")

print(f"\nReport saved to: {report_filename}")
print("=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
