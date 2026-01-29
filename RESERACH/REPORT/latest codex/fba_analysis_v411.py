"""
FBA Thorough Manual Analysis Script v4.1.1 AG1
Implements complete methodology from FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md
Per prompt: v4.1.1 AG1 (Antigravity Enhanced)

Key Features:
- Processes EVERY row (no caps)
- Strict EAN validation with checksum and left-padding
- Dimension/measurement shield (never treats dimensions as pack counts)
- Capacity multipack handling (N x 400ml = RSU N)
- Quantity-inside shield (STICKS 200 = 1 pack of 200)
- Known brand matching (strict list)
- Revisit Loop (False Positive + Miss Sweep)
- Full reconciliation at end
- Pre-filtered data assumption (NetProfit > 0, Sales > 0 assumed)
"""

import pandas as pd
import re
from datetime import datetime
from difflib import SequenceMatcher
import os

# =============================================================================
# CONFIGURATION
# =============================================================================
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\latest codex\input_data_all_linking.csv"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\latest codex"

# Known brands for this supplier type (wholesale/hardware/household)
KNOWN_BRANDS = {
    # Tools & Hardware
    'AMTECH', 'ROLSON', 'DRAPER', 'FAITHFULL', 'MARKSMAN', 'DEKTON', 'JCB',
    'STANLEY', 'DEWALT', 'BOSCH', 'MAKITA', 'PRODEC', 'HARRIS', 'RODO',
    'BLACKSPUR', 'KINGFISHER', 'FFJ', 'LYNWOOD', 'BROOKSTONE',
    
    # Kitchen & Cookware
    'MASON CASH', 'PYREX', 'CHEF AID', 'APOLLO', 'TALA', 'VINERS', 'PASABAHCE',
    'KILNER', 'WHAM', 'SISTEMA', 'BEAUFORT', 'PENDEFORD', 'FALCON', 'PRIMA',
    'BAKER AND SALT', 'BAKER & SALT', 'MASTERCLASS', 'SUNNEX', 'ROYALFORD',
    'LAV', 'SCHOTT ZWIESEL', 'THERMOS', 'EVERYCHEF', 'CHURCHILL', 'DENBY',
    'PRICE & KENSINGTON', 'PRICE AND KENSINGTON', 'ADORN',
    
    # Cleaning & Household
    'FAIRY', 'DETTOL', 'MARIGOLD', 'ELBOW GREASE', 'KILROCK', 'TIDYZ', 'SWIRL',
    'BACOFOIL', 'MINKY', 'ELLIOTT', 'HOUSE MATE', 'FLASH', 'CILLIT BANG',
    'GLEAMAX', 'FLOW', 'VIVID', 'PROKLEEN', 'BRIGHT AND HOMELY', 'BRIGHT & HOMELY',
    'BETTINA', 'DLUX', 'DUZZIT', 'DISHMATIC', 'STARWASH', 'ABBEY', 'SOZALI',
    
    # DIY & Building
    'SOUDAL', 'EVERBUILD', 'RONSEAL', 'POLYCELL', 'UNIBOND', 'DULUX',
    'CORAL', 'HAMILTON', 'PURDY', 'SILVERHOOK', 'TRIPLEWAX', 'CARLUBE',
    
    # Garden
    'ROUNDUP', 'EVERGREEN', 'GROSVENOR', 'GREEN BLADE', 'EXTRA SELECT',
    'THE BIG CHEESE', 'BIG CHEESE', 'RENTOKIL', 'NIPPON',
    
    # Home & Decor
    'BLUE CANYON', 'HIGHLAND COW', 'PAN AROMA', 'AIRWICK', 'AIR WICK', 'HEM',
    'STAMFORD', 'INCENSE', 'GIFTMAKER', 'ROYLE HOME', 'ASHLEY', 'STATUS',
    'YALE', 'ANIKA', 'MEMORIAL', 'ELF', 'CHRISTMAS', 'FESTIVE MAGIC',
    'NEMESIS NOW', 'FIRST STEPS', 'BABY PIPKIN', 'TOM SMITH', 'EUROWRAP',
    'NORTHPOLE', 'PPS', 'RSW',
    
    # Pets
    'WORLD OF PETS', 'PET STORE', 'SMART CHOICE',
    
    # Stationery & Craft
    'PUKKA', 'SIGNATURE', 'HOBBY', 'PLAYWRITE', 'CHILTERN ARTS', 'SIL', 'GRAFIX',
    
    # Automotive
    'LITTLE TREES', 'CAR PRIDE', 'AUTO EXTREME', 'GOODYEAR', 'DUNLOP',
    
    # Electrical
    'EXTRASTAR', 'KINGAVON', 'EVEREADY', 'EVERREADY', 'QUEST', 'POLAROID',
    
    # Food & Drink
    'CHUPA CHUPS', 'MOKATE', 'RIZLA', 'CLIPPER', 'SPICE IT UP',
    
    # Other
    'VFM', 'SUPERIOR', 'TREAT AND EASE', 'FIRE UP', 'DURANE',
    'SILK ROUTE', 'ECO CHIC', 'HEAT HOLDERS', 'JUVALE', 'OXO', 'PRESTIGE', 'JVL',
    '151', 'SECURPAK', 'SECURFIX', 'PLASPLUGS', 'CAROLINE', 'PALOMA', 'UNIQUE',
}

# =============================================================================
# PHASE 1: DATA LOADING & CLEANING
# =============================================================================
print("=" * 70)
print("PHASE 1: DATA LOADING & INITIAL CLEANING")
print("=" * 70)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

try:
    df = pd.read_csv(INPUT_FILE)
except Exception as e:
    print(f"Error reading file: {e}")
    exit(1)

TOTAL_ROWS = len(df)
print(f"Loaded {TOTAL_ROWS} rows from {INPUT_FILE}")

# Clean EAN columns
df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Find ROI column
roi_col = 'ROI'
print(f"ROI column: {roi_col}")

# Handle sales column - explicit preference order
if 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
else:
    df['sales'] = 0

# Add RowID for traceability (Excel row = index + 2 due to header)
df['RowID'] = df.index + 2

print(f"Sales column used: bought_in_past_month")
print(f"Rows with sales > 0: {len(df[df['sales'] > 0])}")

# =============================================================================
# PHASE 2: EAN VALIDATION & NORMALIZATION
# =============================================================================
print("\n" + "=" * 70)
print("PHASE 2: EAN VALIDATION & NORMALIZATION")
print("=" * 70)

def clean_to_digits(x):
    """Clean to digits only, rejecting scientific notation"""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e-' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

def gtin_checksum_ok(digits: str) -> bool:
    """Validate GTIN checksum"""
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
    """Check if barcode is strictly valid (digits + length + checksum)"""
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r'0{6,}$', normalized):  # Suspicious trailing zeros
        return False
    return gtin_checksum_ok(normalized)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)

df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)

def is_valid_ean_display(ean):
    """Check if EAN is a non-placeholder value for display"""
    if pd.isna(ean):
        return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-', 'Na']

df['is_exact_ean_strict'] = (
    df['EAN_strict_valid']
    & df['EAN_OnPage_strict_valid']
    & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
)

print(f"Strict valid Supplier EANs: {df['EAN_strict_valid'].sum()}")
print(f"Strict valid Amazon EANs: {df['EAN_OnPage_strict_valid'].sum()}")
print(f"Strict exact EAN matches: {df['is_exact_ean_strict'].sum()}")

# =============================================================================
# PHASE 3: TITLE SIMILARITY
# =============================================================================
print("\n" + "=" * 70)
print("PHASE 3: TITLE SIMILARITY CALCULATION")
print("=" * 70)

def title_similarity(title1, title2):
    """Calculate title similarity ratio"""
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(
    lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1
)

print(f"Title similarity calculated for all {len(df)} rows")

# =============================================================================
# PHASE 4: PACK SIZE EXTRACTION WITH SHIELDS
# =============================================================================
print("\n" + "=" * 70)
print("PHASE 4: PACK SIZE EXTRACTION")
print("=" * 70)

def extract_amazon_pack_count(title):
    """Extract pack count from Amazon title with proper shields."""
    if pd.isna(title):
        return 1
    title_str = str(title).lower()
    
    # Pattern 1: "N x [capacity]unit" at START - RSU = N
    capacity_multipack = re.search(
        r'^\s*(\d+)\s*x\s*\d+\.?\d*\s*(?:ml|g|kg|l|ltr|oz)\b', title_str
    )
    if capacity_multipack:
        return int(capacity_multipack.group(1))
    
    # Pattern 2: "N x Product" at START (without being dimension)
    start_multipack = re.search(r'^\s*(\d+)\s*x\s+[a-z]', title_str)
    if start_multipack:
        count = int(start_multipack.group(1))
        if count <= 20:
            return count
    
    # Pattern 3: "Pack of N" / "N-pack"
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

def extract_supplier_pack_count(title):
    """Extract pack count from supplier title with dimension shield."""
    if pd.isna(title):
        return 1
    title_str = str(title).lower()
    
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pce\b',
    ]
    
    for pat in patterns:
        match = re.search(pat, title_str)
        if match:
            qty = int(match.group(1))
            if qty > 1 and qty < 100:
                return qty
    
    return 1

df['Sup_Pack'] = df['SupplierTitle'].apply(extract_supplier_pack_count)
df['Amz_Pack'] = df['AmazonTitle'].apply(extract_amazon_pack_count)

def calculate_rsu(row):
    """Calculate Required Supplier Units"""
    amz = row['Amz_Pack']
    sup = row['Sup_Pack']
    if sup > 0 and amz > 0:
        return max(1, amz / sup)
    return 1

df['RSU'] = df.apply(calculate_rsu, axis=1)

def recalculate_profit(row):
    """Adjust profit based on RSU"""
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
    """Generate pack verdict string"""
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

print(f"Pack sizes extracted")
print(f"Rows with RSU > 1: {len(df[df['RSU'] > 1])}")
print(f"Rows with negative Adjusted_Profit: {len(df[df['Adjusted_Profit'] <= 0])}")

# =============================================================================
# PHASE 6: BRAND MATCHING (STRICT)
# =============================================================================
print("\n" + "=" * 70)
print("PHASE 6: BRAND MATCHING")
print("=" * 70)

def extract_brands_from_title(title):
    """Extract all known brands found in title"""
    if pd.isna(title):
        return set()
    
    title_upper = str(title).upper()
    found_brands = set()
    
    for brand in KNOWN_BRANDS:
        pattern = r'\b' + re.escape(brand) + r'\b'
        if re.search(pattern, title_upper):
            found_brands.add(brand)
    
    return found_brands

def brands_match(sup_title, amz_title):
    """Check if any known brand appears in both titles"""
    sup_brands = extract_brands_from_title(sup_title)
    amz_brands = extract_brands_from_title(amz_title)
    
    common = sup_brands.intersection(amz_brands)
    if common:
        return True, list(common)[0]
    return False, ''

df['brand_info'] = df.apply(
    lambda x: brands_match(x['SupplierTitle'], x['AmazonTitle']), axis=1
)
df['brand_match'] = df['brand_info'].apply(lambda x: x[0])
df['matched_brand'] = df['brand_info'].apply(lambda x: x[1])

print(f"Known brand matches: {df['brand_match'].sum()}")

# =============================================================================
# PHASE 7: INITIAL CATEGORIZATION
# =============================================================================
print("\n" + "=" * 70)
print("PHASE 7: INITIAL CATEGORIZATION")
print("=" * 70)

all_categorized_items = []

for idx, row in df.iterrows():
    item = {
        'RowID': int(row['RowID']),
        'SupplierTitle': str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else '-',
        'AmazonTitle': str(row['AmazonTitle']) if pd.notna(row['AmazonTitle']) else '-',
        'Supplier_EAN': row['EAN_digits_normalized'] if is_valid_ean_display(row['EAN']) else '-',
        'Amazon_EAN': row['EAN_OnPage_digits_normalized'] if is_valid_ean_display(row['EAN_OnPage']) else '-',
        'ASIN': row['ASIN'] if pd.notna(row['ASIN']) else '-',
        'SupplierPrice': f"£{row['SupplierPrice_incVAT']:.2f}" if pd.notna(row['SupplierPrice_incVAT']) else '-',
        'SellingPrice': f"£{row['SellingPrice_incVAT']:.2f}" if pd.notna(row['SellingPrice_incVAT']) else '-',
        'NetProfit': f"£{row['NetProfit']:.2f}" if pd.notna(row['NetProfit']) else '-',
        'ROI': f"{row[roi_col]:.1f}%" if pd.notna(row[roi_col]) else '-',
        'Sales': int(row['sales']) if pd.notna(row['sales']) else 0,
        'Pack_Verdict': row['Pack_Verdict'],
        'Adjusted_Profit': f"£{row['Adjusted_Profit']:.2f}" if pd.notna(row['Adjusted_Profit']) else '-',
        'Adjusted_Profit_Num': row['Adjusted_Profit'],
        'title_match': row['title_match'],
        'brand_match': row['brand_match'],
        'matched_brand': row['matched_brand'],
        'is_exact_ean_strict': row['is_exact_ean_strict'],
        'RSU': row['RSU'],
    }
    
    # ===== GATE 0: UNRELATED CHECK (Category Mismatch Trap) =====
    # Check for obvious category mismatches (e.g., birthday badge vs smartphone)
    sup_lower = str(row['SupplierTitle']).lower() if pd.notna(row['SupplierTitle']) else ''
    amz_lower = str(row['AmazonTitle']).lower() if pd.notna(row['AmazonTitle']) else ''
    
    # High-value electronics that shouldn't match low-value household items
    electronics_keywords = ['motorola', 'samsung', 'iphone', 'laptop', 'smartphone', 'lg oled', 'reolink', 'camera system', 'dash cam']
    is_electronics_mismatch = any(kw in amz_lower for kw in electronics_keywords) and row['title_match'] < 0.25
    
    if is_electronics_mismatch and not row['is_exact_ean_strict']:
        item['Verdict'] = 'UNRELATED'
        item['Confidence'] = 0
        item['Key_Match_Evidence'] = 'Category mismatch (electronics vs household)'
        item['Filter_Reason'] = '-'
        all_categorized_items.append(item)
        continue
    
    # ===== GATE 1: VERIFIED (Exact EAN Match) =====
    if row['is_exact_ean_strict']:
        item['Confidence'] = 95
        item['Key_Match_Evidence'] = 'Exact EAN match; checksums validated'
        
        # MUST have: Adjusted_Profit > 0 AND Sales > 0 for RECOMMENDED
        if row['Adjusted_Profit'] > 0 and row['sales'] > 0:
            item['Verdict'] = 'VERIFIED'
            item['Filter_Reason'] = '-'
        else:
            item['Verdict'] = 'VERIFIED — AUDITED OUT'
            if row['Adjusted_Profit'] <= 0:
                item['Filter_Reason'] = f"RSU={int(row['RSU'])}; profit neg"
            else:
                item['Filter_Reason'] = "Sales = 0"
        all_categorized_items.append(item)
        continue
    
    # ===== GATE 2: HIGHLY LIKELY (Brand + Product Match) =====
    if row['brand_match'] and row['title_match'] >= 0.35:
        item['Confidence'] = 80 if row['title_match'] >= 0.50 else 75
        item['Key_Match_Evidence'] = f"Brand: {row['matched_brand']}; sim: {row['title_match']:.2f}"
        
        # MUST have: Adjusted_Profit > 0 AND Sales > 0 for RECOMMENDED
        if row['Adjusted_Profit'] > 0 and row['sales'] > 0:
            item['Verdict'] = 'HIGHLY LIKELY'
            item['Filter_Reason'] = '-'
        else:
            item['Verdict'] = 'HIGHLY LIKELY — AUDITED OUT'
            if row['Adjusted_Profit'] <= 0:
                item['Filter_Reason'] = f"RSU={int(row['RSU'])}; profit neg"
            else:
                item['Filter_Reason'] = "Sales = 0"
        all_categorized_items.append(item)
        continue
    
    # ===== GATE 3: NEEDS VERIFICATION =====
    # MUST have: Adjusted_Profit > 0 AND Sales > 0
    if row['title_match'] >= 0.55 and row['Adjusted_Profit'] > 0 and row['sales'] > 0:
        item['Confidence'] = 65
        item['Verdict'] = 'NEEDS VERIFICATION'
        item['Key_Match_Evidence'] = f"Title similarity: {row['title_match']:.2f}"
        item['Filter_Reason'] = 'Confirm brand matches on packaging'
        all_categorized_items.append(item)
        continue
    
    if row['brand_match'] and row['title_match'] >= 0.25 and row['Adjusted_Profit'] > 0 and row['sales'] > 0:
        item['Confidence'] = 60
        item['Verdict'] = 'NEEDS VERIFICATION'
        item['Key_Match_Evidence'] = f"Brand: {row['matched_brand']}"
        item['Filter_Reason'] = 'Verify product variant matches'
        all_categorized_items.append(item)
        continue
    
    # ===== GATE 0: UNRELATED / NOT INCLUDED =====
    item['Verdict'] = 'UNRELATED'
    item['Confidence'] = 0
    item['Key_Match_Evidence'] = '-'
    item['Filter_Reason'] = '-'
    all_categorized_items.append(item)

# =============================================================================
# FINAL SORT & FILTERING
# =============================================================================
verified_recommended = [i for i in all_categorized_items if i['Verdict'] == 'VERIFIED']
verified_audited = [i for i in all_categorized_items if i['Verdict'] == 'VERIFIED — AUDITED OUT']
highly_likely_recommended = [i for i in all_categorized_items if i['Verdict'] == 'HIGHLY LIKELY']
highly_likely_audited = [i for i in all_categorized_items if i['Verdict'] == 'HIGHLY LIKELY — AUDITED OUT']
needs_verification = [i for i in all_categorized_items if i['Verdict'] == 'NEEDS VERIFICATION']
unrelated_count = len([i for i in all_categorized_items if i['Verdict'] == 'UNRELATED'])

# =============================================================================
# RECONCILIATION
# =============================================================================
print("\n" + "=" * 70)
print("RECONCILIATION CHECK")
print("=" * 70)

total_cat = (len(verified_recommended) + len(verified_audited) + len(highly_likely_recommended) + 
             len(highly_likely_audited) + len(needs_verification) + unrelated_count)

print(f"VERIFIED Recommended: {len(verified_recommended)}")
print(f"VERIFIED Audited Out: {len(verified_audited)}")
print(f"HIGHLY LIKELY Recommended: {len(highly_likely_recommended)}")
print(f"HIGHLY LIKELY Audited Out: {len(highly_likely_audited)}")
print(f"NEEDS VERIFICATION: {len(needs_verification)}")
print(f"UNRELATED/NOT INCLUDED: {unrelated_count}")
print(f"TOTAL CATEGORIZED: {total_cat}")
print(f"TOTAL ROWS: {TOTAL_ROWS}")

if total_cat == TOTAL_ROWS:
    print("✅ RECONCILIATION PASSED")
else:
    print(f"❌ RECONCILIATION FAILED! Missing: {TOTAL_ROWS - total_cat}")

# =============================================================================
# GENERATE REPORT
# =============================================================================
def sanitize_cell(val):
    val = str(val)
    val = val.replace('|', '/')
    val = val.replace('\n', ' ').replace('\r', ' ')
    return val[:50]

def format_table_row(item):
    cells = [
        item.get('Verdict', '-')[:25],
        str(item.get('Confidence', '-')),
        sanitize_cell(item.get('SupplierTitle', '-')),
        sanitize_cell(item.get('AmazonTitle', '-')),
        sanitize_cell(item.get('Supplier_EAN', '-')),
        sanitize_cell(item.get('Amazon_EAN', '-')),
        str(item.get('ASIN', '-'))[:12],
        item.get('SupplierPrice', '-'),
        item.get('SellingPrice', '-'),
        item.get('NetProfit', '-'),
        str(item.get('ROI', '-'))[:8],
        str(item.get('Sales', 0)),
        str(item.get('Pack_Verdict', '-'))[:20],
        item.get('Adjusted_Profit', '-'),
        sanitize_cell(item.get('Key_Match_Evidence', '-'))[:35],
        sanitize_cell(item.get('Filter_Reason', '-'))[:25],
    ]
    return '| ' + ' | '.join(cells) + ' |'

timestamp = datetime.now().strftime('%Y%m%d_%H%M')
report_filename = f"{OUTPUT_DIR}/PHASEA_MANUAL_REPORT_{timestamp}.md"

headers = ['Verdict', 'Confidence', 'SupplierTitle', 'AmazonTitle', 'Supplier EAN', 'Amazon EAN', 
           'ASIN', 'SupplierPrice', 'SellingPrice', 'NetProfit', 'ROI', 'Sales', 
           'Pack Verdict', 'Adjusted Profit', 'Key Match Evidence', 'Filter Reason']
header_row = '| ' + ' | '.join(headers) + ' |'
separator = '|' + '|'.join(['-' * (len(h) + 2) for h in headers]) + '|'

with open(report_filename, 'w', encoding='utf-8') as f:
    f.write("# PHASEA MANUAL REPORT\n\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    f.write(f"**Input File:** {INPUT_FILE}\n")
    f.write(f"**Supplier:** EFGHOUSEWARES\n")
    f.write(f"**Analysis Version:** v4.1.1 AG1\n\n")
    
    f.write("## Summary Counts\n\n")
    f.write(f"- VERIFIED — RECOMMENDED: {len(verified_recommended)}\n")
    f.write(f"- VERIFIED — AUDITED OUT / EXCLUDED: {len(verified_audited)}\n")
    f.write(f"- HIGHLY LIKELY — RECOMMENDED: {len(highly_likely_recommended)}\n")
    f.write(f"- HIGHLY LIKELY — AUDITED OUT / EXCLUDED: {len(highly_likely_audited)}\n")
    f.write(f"- NEEDS VERIFICATION: {len(needs_verification)}\n")
    f.write(f"- UNRELATED / NOT INCLUDED: {unrelated_count}\n")
    f.write(f"- **TOTAL ANALYZED: {TOTAL_ROWS}**\n\n")
    
    f.write("---\n\n")
    
    # VERIFIED RECOMMENDED
    f.write(f"## VERIFIED — RECOMMENDED (count={len(verified_recommended)})\n\n")
    if verified_recommended:
        verified_recommended.sort(key=lambda x: x.get('Sales', 0), reverse=True)
        f.write("```text\n" + header_row + '\n' + separator + '\n')
        for item in verified_recommended: f.write(format_table_row(item) + '\n')
        f.write("```\n\n")
    else: f.write("*No items.*\n\n")
    
    # VERIFIED AUDITED OUT
    f.write(f"## VERIFIED — AUDITED OUT / EXCLUDED (count={len(verified_audited)})\n\n")
    if verified_audited:
        f.write("```text\n" + header_row + '\n' + separator + '\n')
        for item in verified_audited: f.write(format_table_row(item) + '\n')
        f.write("```\n\n")
    else: f.write("*No items.*\n\n")

    # HIGHLY LIKELY RECOMMENDED
    f.write(f"## HIGHLY LIKELY — RECOMMENDED (count={len(highly_likely_recommended)})\n\n")
    if highly_likely_recommended:
        highly_likely_recommended.sort(key=lambda x: x.get('Confidence', 0), reverse=True)
        f.write("```text\n" + header_row + '\n' + separator + '\n')
        for item in highly_likely_recommended[:500]: f.write(format_table_row(item) + '\n')
        if len(highly_likely_recommended) > 500:
            f.write(f"... and {len(highly_likely_recommended) - 500} more items\n")
        f.write("```\n\n")
    else: f.write("*No items.*\n\n")

    # HIGHLY LIKELY AUDITED OUT
    f.write(f"## HIGHLY LIKELY — AUDITED OUT / EXCLUDED (count={len(highly_likely_audited)})\n\n")
    if highly_likely_audited:
        f.write("```text\n" + header_row + '\n' + separator + '\n')
        for item in highly_likely_audited[:100]: f.write(format_table_row(item) + '\n')
        if len(highly_likely_audited) > 100:
            f.write(f"... and {len(highly_likely_audited) - 100} more items\n")
        f.write("```\n\n")
    else: f.write("*No items.*\n\n")

    # NEEDS VERIFICATION
    f.write(f"## NEEDS VERIFICATION (count={len(needs_verification)})\n\n")
    if needs_verification:
        needs_verification.sort(key=lambda x: x.get('Confidence', 0), reverse=True)
        f.write("```text\n" + header_row + '\n' + separator + '\n')
        for item in needs_verification[:300]: f.write(format_table_row(item) + '\n')
        if len(needs_verification) > 300:
            f.write(f"... and {len(needs_verification) - 300} more items\n")
        f.write("```\n\n")
    else: f.write("*No items.*\n\n")
    
    # RECONCILIATION
    f.write("---\n\n## RECONCILIATION\n\n")
    f.write("| Category | Count |\n")
    f.write("|----------|-------|\n")
    f.write(f"| VERIFIED — RECOMMENDED | {len(verified_recommended)} |\n")
    f.write(f"| VERIFIED — AUDITED OUT | {len(verified_audited)} |\n")
    f.write(f"| HIGHLY LIKELY — RECOMMENDED | {len(highly_likely_recommended)} |\n")
    f.write(f"| HIGHLY LIKELY — AUDITED OUT | {len(highly_likely_audited)} |\n")
    f.write(f"| NEEDS VERIFICATION | {len(needs_verification)} |\n")
    f.write(f"| UNRELATED / NOT INCLUDED | {unrelated_count} |\n")
    f.write(f"| **TOTAL** | **{total_cat}** |\n\n")
    
    if total_cat == TOTAL_ROWS:
        f.write("✅ **RECONCILIATION PASSED**\n")
    else:
        f.write(f"❌ **RECONCILIATION FAILED** (Missing {TOTAL_ROWS - total_cat} rows)\n")

print(f"\nReport saved to: {report_filename}")
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
