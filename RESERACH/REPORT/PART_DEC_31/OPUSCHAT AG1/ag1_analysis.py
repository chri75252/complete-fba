"""
FBA Manual Analysis Script - AG1 Methodology
Analyzes PART_DEC_31.xlsx using v4.1 AG1 prompt methodology
"""

import pandas as pd
import re
from difflib import SequenceMatcher
from datetime import datetime

# Configuration
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\OPUSCHAT AG1"

print("="*80)
print("FBA MANUAL ANALYSIS - AG1 METHODOLOGY")
print("="*80)

# Load data
print("\n[STAGE 1] Loading and cleaning data...")
df = pd.read_excel(INPUT_FILE)
print(f"Loaded {len(df)} rows")

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

# Add RowID
df['RowID'] = df.index + 1

# Stage 1B: EAN Normalization
print("[STAGE 1B] EAN normalization...")

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

# Stage 2: Title Similarity
print("[STAGE 2] Calculating title similarity...")

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x.get('SupplierTitle', ''), x.get('AmazonTitle', '')), axis=1)

# Stage 3: Strict EAN Matching
print("[STAGE 3] Strict EAN matching...")

def gtin_checksum_ok(digits):
    if not digits.isdigit():
        return False
    n = len(digits)
    if n not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])
    body_rev = list(map(int, body[::-1]))
    total = sum(d * (3 if i % 2 == 1 else 1) for i, d in enumerate(body_rev, start=1))
    calc = (10 - (total % 10)) % 10
    return calc == check

def normalize_ean(digits):
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

def is_strict_valid_barcode(digits):
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r'0{6,}$', normalized):
        return False
    return gtin_checksum_ok(normalized)

df['EAN_normalized'] = df['EAN_digits'].apply(normalize_ean)
df['EAN_OnPage_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)
df['EAN_strict_valid'] = df['EAN_normalized'].apply(is_strict_valid_barcode)
df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_normalized'].apply(is_strict_valid_barcode)
df['is_exact_ean_strict'] = (
    df['EAN_strict_valid'] & 
    df['EAN_OnPage_strict_valid'] & 
    (df['EAN_normalized'] == df['EAN_OnPage_normalized'])
)

print(f"  Exact EAN matches found: {df['is_exact_ean_strict'].sum()}")

# Stage 4: Pack Size Extraction (AG1 Enhanced)
print("[STAGE 4] Pack size extraction (AG1 methodology)...")

# Dimension patterns to exclude from pack detection
DIMENSION_PATTERNS = [
    r'\d+\s*x\s*\d+\s*(?:x\s*\d+\s*)?(?:cm|mm|inch|in|m)\b',  # AxBxC cm/mm/inch
    r'\d+(?:cm|mm|ml|ltr?|g|gm|kg|oz|ft|inch|in)\b',  # Single dimension with unit
    r'\d+\s*x\s*\d+\s*(?:cm|mm|inch|in)',  # AxB cm
]

def is_dimension_pattern(text, number):
    """Check if a number is part of a dimension pattern"""
    if pd.isna(text):
        return False
    text_lower = str(text).lower()
    # Check if number is followed by dimension unit
    patterns = [
        rf'\b{number}\s*(?:cm|mm|ml|ltr?|g|gm|kg|oz|ft|inch|in)\b',
        rf'\b{number}\s*x\s*\d+\s*(?:cm|mm|inch|in)',
        rf'\d+\s*x\s*{number}\s*(?:cm|mm|inch|in)',
    ]
    for pat in patterns:
        if re.search(pat, text_lower):
            return True
    return False

def extract_pack_count(title):
    """Extract pack count, distinguishing from dimensions and quantity-inside"""
    if pd.isna(title):
        return 1
    title_lower = str(title).lower()
    
    # Explicit pack patterns (highest priority)
    pack_patterns = [
        (r'pack\s*of\s*(\d+)', 1),
        (r'set\s*of\s*(\d+)', 1),
        (r'\b(\d+)\s*pack\b', 1),
        (r'\b(\d+)\s*pk\b', 1),
        (r'\(pack\s*of\s*(\d+)\)', 1),
        (r'\((\d+)\s*pack\)', 1),
    ]
    
    for pattern, group in pack_patterns:
        match = re.search(pattern, title_lower)
        if match:
            qty = int(match.group(group))
            if 1 < qty < 500 and not is_dimension_pattern(title, qty):
                return qty
    
    return 1

def extract_multipack_total(title):
    """Extract total from multipack patterns like (4 x 50) = 200 or '42 pcs'"""
    if pd.isna(title):
        return (1, 1, 1)
    title_lower = str(title).lower()
    
    # Pattern for "N x M" at start or in parentheses (multipack indicator)
    multipack_patterns = [
        r'\((\d+)\s*x\s*(\d+)\)',  # (4 x 50)
        r'^(\d+)\s*x\s+',  # "3 x Product Name" at start
    ]
    
    for pat in multipack_patterns:
        match = re.search(pat, title_lower)
        if match:
            if len(match.groups()) == 2:
                outer = int(match.group(1))
                inner = int(match.group(2))
                if 2 <= outer <= 20 and inner > outer:
                    return (outer, inner, outer * inner)
            elif len(match.groups()) == 1:
                outer = int(match.group(1))
                if 2 <= outer <= 20:
                    return (outer, 1, outer)
    
    # Check for "200 x Product" pattern (total count)
    total_pattern = r'\b(\d+)\s*x\s+(?![\d])'
    match = re.search(total_pattern, title_lower)
    if match:
        total = int(match.group(1))
        if total > 20:
            return (1, total, total)
    
    # NEW: Check for explicit quantity patterns like "42 pcs", "20 pce", "pack of 10"
    qty_patterns = [
        r'^(\d+)\s*pcs\b',          # "42 pcs x 15mm..." at start
        r'^(\d+)\s*pce\b',          # "42 pce..." at start
        r'pack\s*of\s*(\d+)',       # "pack of 20"
        r'set\s*of\s*(\d+)',        # "set of 3"
        r'\b(\d+)\s*-?pack\b',      # "3-pack" or "3 pack"
        r'\b(\d+)\s*pk\b',          # "3pk"
    ]
    
    for pattern in qty_patterns:
        match = re.search(pattern, title_lower)
        if match:
            qty = int(match.group(1))
            if qty > 1:
                return (1, qty, qty)
    
    # Default: single pack
    pack = extract_pack_count(title)
    return (1, pack, pack)

df['Sup_Pack'] = df['SupplierTitle'].apply(extract_pack_count)
df['Amz_Multipack'] = df['AmazonTitle'].apply(extract_multipack_total)
df['Amz_Total'] = df['Amz_Multipack'].apply(lambda x: x[2])

# Stage 5: Brand Detection (MOVED BEFORE RSU CALCULATION)
print("[STAGE 5] Brand detection...")

KNOWN_BRANDS = [
    'AMTECH', 'ROLSON', 'DRAPER', 'EVERBUILD', 'PYREX', 'MASON CASH', 'KILNER',
    'FAIRY', 'DETTOL', 'TIDYZ', 'SOUDAL', 'ROUNDUP', 'CHEF AID', 'HARRIS',
    'BLUE CANYON', 'BEAUFORT', 'APOLLO', 'WHAM', 'TALA', 'FALCON', 'KILROCK',
    'QUEST', 'PRIMA', 'BAKER & SALT', 'BAKER AND SALT', 'ULTRATAPE', 'SMART CHOICE',
    'LITTLE TREES', 'STATUS', 'EXTRASTAR', 'PAN AROMA', 'AIRWICK', 'AIR WICK',
    'EVEREADY', 'EVERREADY', 'GIFTMAKER', 'HIGHLAND COW', 'HOUSE MATE',
    'MEMORIAL', 'THE BIG CHEESE', 'FIRE UP', 'PENDEFORD', 'SUPERIOR', 'PPS',
    'ELLIOTT', 'ELLIOTTS', 'SPONTEX', 'RUSSELL HOBBS', 'SCHOTT ZWIESEL',
    'PRODEC', 'WORLD OF PETS', 'EXTRA SELECT', 'MARIGOLD', 'DUNLOP', 'BACOFOIL',
    'CURVER', 'MINKY', 'VINERS', 'KINGAVON', 'GROSVENOR', 'DEKTON', 'SUNNEX',
    'CORAL', 'BETTINA', 'ADORN', 'CAR PRIDE', 'SECURPAK', 'SECURPLUMB'
]

def detect_brand_match(sup_title, amz_title):
    if pd.isna(sup_title) or pd.isna(amz_title):
        return None
    sup_lower = str(sup_title).lower()
    amz_lower = str(amz_title).lower()
    
    for brand in KNOWN_BRANDS:
        brand_lower = brand.lower()
        if brand_lower in sup_lower and brand_lower in amz_lower:
            return brand
    return None

df['Brand_Match'] = df.apply(lambda x: detect_brand_match(x.get('SupplierTitle', ''), x.get('AmazonTitle', '')), axis=1)

# Calculate RSU (Required Supplier Units)
# CRITICAL FIX: For exact EAN OR brand matches, default to RSU=1 unless explicit pack mismatch
print("[STAGE 6] Pack size verification (conservative for EAN/brand matches)...")

def has_explicit_pack_mismatch(sup_title, amz_title):
    """Check for EXPLICIT pack keyword mismatch like 'single' vs '10-pack'"""
    if pd.isna(sup_title) or pd.isna(amz_title):
        return False
    sup_lower = str(sup_title).lower()
    amz_lower = str(amz_title).lower()
    
    # Extract quantity from SUPPLIER title (including patterns like 20PCE, 50 PCS)
    sup_qty_patterns = [
        r'(\d+)\s*pce\b',       # "20PCE"
        r'(\d+)\s*pcs\b',       # "50 PCS"
        r'(\d+)\s*pieces?\b',   # "20 pieces"
        r'pack\s*of\s*(\d+)',   # "pack of 20"
        r'(\d+)\s*-?pack\b',    # "20-pack"
        r'(\d+)\s*pk\b',        # "20pk"
        r'set\s*of\s*(\d+)',    # "set of 3"
    ]
    
    sup_qty = None
    for pattern in sup_qty_patterns:
        match = re.search(pattern, sup_lower)
        if match:
            sup_qty = int(match.group(1))
            break
    
    # Extract quantity from AMAZON title
    amz_qty_patterns = [
        r'pack\s*of\s*(\d+)',   # "pack of 20"
        r'set\s*of\s*(\d+)',    # "set of 3"
        r'(\d+)\s*-?pack\b',    # "3-pack"
        r'(\d+)\s*pk\b',        # "3pk"
        r'\b(\d+)\s*x\s*pack',  # "3 x pack"
        r'(\d+)\s*pce\b',       # "20PCE"
        r'(\d+)\s*pcs\b',       # "50 PCS"
    ]
    
    amz_qty = None
    for pattern in amz_qty_patterns:
        match = re.search(pattern, amz_lower)
        if match:
            amz_qty = int(match.group(1))
            break
    
    # If BOTH have quantities and they MATCH = NO mismatch (1:1)
    if sup_qty is not None and amz_qty is not None:
        if sup_qty == amz_qty:
            return False  # Same quantity = 1:1 match
        elif amz_qty > sup_qty:
            return True  # Amazon has MORE = mismatch
    
    # If only Amazon has explicit pack count > 1 and supplier doesn't
    if amz_qty is not None and amz_qty > 1 and sup_qty is None:
        # Check if supplier says "single", "sold each", etc.
        if 'single' not in sup_lower and 'sold each' not in sup_lower:
            return True  # Potential mismatch
    
    return False

def calculate_rsu(row):
    # CRITICAL: For exact EAN OR brand matches, default to RSU=1
    # Only apply pack adjustment if there's EXPLICIT pack keyword mismatch
    is_exact_ean = row['is_exact_ean_strict']
    brand_match = row['Brand_Match']
    
    sup_title = row.get('SupplierTitle', '')
    amz_title = row.get('AmazonTitle', '')
    
    # For exact EAN matches: very conservative, only explicit pack keywords
    if is_exact_ean:
        if has_explicit_pack_mismatch(sup_title, amz_title):
            sup_pack = row['Sup_Pack']
            amz_total = row['Amz_Total']
            if sup_pack > 0 and amz_total > sup_pack:
                return amz_total / sup_pack
        return 1  # Default: exact EAN = same product = RSU 1
    
    # For brand matches: also conservative, only explicit pack keywords  
    if brand_match:
        if has_explicit_pack_mismatch(sup_title, amz_title):
            sup_pack = row['Sup_Pack']
            amz_total = row['Amz_Total']
            if sup_pack > 0 and amz_total > sup_pack:
                return amz_total / sup_pack
        return 1  # Default: brand match = likely same product = RSU 1
    
    # For non-EAN, non-brand matches: use calculated values but be careful
    sup_pack = row['Sup_Pack']
    amz_total = row['Amz_Total']
    if sup_pack <= 0:
        sup_pack = 1
    if amz_total <= sup_pack:
        return 1
    
    # Only apply RSU if there's explicit pack language
    if has_explicit_pack_mismatch(sup_title, amz_title):
        return amz_total / sup_pack
    
    return 1  # Default conservative

df['RSU'] = df.apply(calculate_rsu, axis=1)

# Recalculate profit
def recalculate_profit(row):
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row.get('SupplierPrice_incVAT', row.get('SupplierPrice', 0)))
        rsu = row['RSU']
        if rsu > 1:
            adjustment = supplier_cost * (rsu - 1)
            return original_profit - adjustment
        return original_profit
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# Pack verdict
def get_pack_verdict(row):
    rsu = row['RSU']
    adj_profit = row['Adjusted_Profit']
    if rsu == 1:
        return "1:1 Match"
    elif rsu > 1:
        if adj_profit > 0:
            return f"BUNDLE ({int(rsu)}x) - OK"
        else:
            return f"BUNDLE ({int(rsu)}x) - LOSS"
    return "1:1 Match"

df['Pack_Verdict'] = df.apply(get_pack_verdict, axis=1)

# Stage 7: Categorization (AG1 Rules)
print("[STAGE 7] Categorizing products (AG1 rules)...")

def categorize_product(row):
    is_exact_ean = row['is_exact_ean_strict']
    adj_profit = row['Adjusted_Profit']
    sales = row['sales']
    brand_match = row['Brand_Match']
    title_sim = row['title_match']
    rsu = row['RSU']
    
    # Rule 1: Negative profit → FILTERED OUT
    if adj_profit <= 0:
        if is_exact_ean:
            return ('VERIFIED', 'FILTERED_OUT', 'Negative adjusted profit')
        elif brand_match:
            return ('HIGHLY_LIKELY', 'FILTERED_OUT', 'Negative adjusted profit')
        else:
            return ('FILTERED_OUT', 'EXCLUDED', 'Negative adjusted profit')
    
    # Rule 2: Exact EAN match with positive profit → VERIFIED
    if is_exact_ean:
        if sales > 0:
            return ('VERIFIED', 'RECOMMENDED', '-')
        else:
            return ('NEEDS_VERIFICATION', 'CHECK', 'Exact EAN but Sales=0')
    
    # Rule 3: Brand match + positive profit → HIGHLY LIKELY
    if brand_match and adj_profit > 0:
        if sales > 0:
            return ('HIGHLY_LIKELY', 'RECOMMENDED', '-')
        else:
            return ('NEEDS_VERIFICATION', 'CHECK', f'{brand_match} match but Sales=0')
    
    # Rule 4: High title similarity + positive profit → Check for upgrade
    if title_sim >= 0.55 and adj_profit > 0:
        if sales > 0:
            return ('HIGHLY_LIKELY', 'RECOMMENDED', 'Strong title match')
        else:
            return ('NEEDS_VERIFICATION', 'CHECK', 'Title match but Sales=0')
    
    # Rule 5: Moderate confidence
    if title_sim >= 0.40 and adj_profit > 0.50:
        return ('NEEDS_VERIFICATION', 'CHECK', 'Moderate title match - verify brand')
    
    # Default: Not included
    return ('EXCLUDED', 'WEAK', 'Weak evidence')

df['Category_Result'] = df.apply(categorize_product, axis=1)
df['Category'] = df['Category_Result'].apply(lambda x: x[0])
df['SubCategory'] = df['Category_Result'].apply(lambda x: x[1])
df['Filter_Reason'] = df['Category_Result'].apply(lambda x: x[2])

# Generate summary
print("\n" + "="*80)
print("ANALYSIS SUMMARY")
print("="*80)

verified_rec = df[(df['Category'] == 'VERIFIED') & (df['SubCategory'] == 'RECOMMENDED')]
verified_fo = df[(df['Category'] == 'VERIFIED') & (df['SubCategory'] == 'FILTERED_OUT')]
highly_likely_rec = df[(df['Category'] == 'HIGHLY_LIKELY') & (df['SubCategory'] == 'RECOMMENDED')]
highly_likely_fo = df[(df['Category'] == 'HIGHLY_LIKELY') & (df['SubCategory'] == 'FILTERED_OUT')]
needs_verif = df[df['Category'] == 'NEEDS_VERIFICATION']
filtered_out = df[df['Category'] == 'FILTERED_OUT']

print(f"\nVERIFIED — RECOMMENDED: {len(verified_rec)}")
print(f"VERIFIED — FILTERED OUT: {len(verified_fo)}")
print(f"HIGHLY LIKELY — RECOMMENDED: {len(highly_likely_rec)}")
print(f"HIGHLY LIKELY — FILTERED OUT: {len(highly_likely_fo)}")
print(f"NEEDS VERIFICATION: {len(needs_verif)}")
print(f"FILTERED OUT (other): {len(filtered_out)}")
print(f"\nTOTAL ACTIONABLE: {len(verified_rec) + len(highly_likely_rec) + len(needs_verif)}")

# Save detailed CSV
csv_path = f"{OUTPUT_DIR}\\analysis_details_{datetime.now().strftime('%Y%m%d')}.csv"
output_cols = ['RowID', 'SupplierTitle', 'AmazonTitle', 'EAN', 'EAN_OnPage', 'ASIN',
               'NetProfit', 'Adjusted_Profit', 'ROI', 'sales', 'title_match',
               'is_exact_ean_strict', 'Brand_Match', 'RSU', 'Pack_Verdict',
               'Category', 'SubCategory', 'Filter_Reason']
existing_cols = [c for c in output_cols if c in df.columns]
df[existing_cols].to_csv(csv_path, index=False)
print(f"\nSaved detailed CSV: {csv_path}")

# Generate Markdown report
print("\nGenerating Markdown report...")

report_lines = []
report_lines.append("# PHASEA MANUAL REPORT")
report_lines.append("")
report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
report_lines.append(f"**Input File:** PART_DEC_31.xlsx")
report_lines.append(f"**Methodology:** AG1 v4.1")
report_lines.append(f"**Total Rows Analyzed:** {len(df)}")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## Summary Counts")
report_lines.append("")
report_lines.append(f"- **VERIFIED — RECOMMENDED:** {len(verified_rec)}")
report_lines.append(f"- **VERIFIED — FILTERED OUT:** {len(verified_fo)}")
report_lines.append(f"- **HIGHLY LIKELY — RECOMMENDED:** {len(highly_likely_rec)}")
report_lines.append(f"- **HIGHLY LIKELY — FILTERED OUT:** {len(highly_likely_fo)}")
report_lines.append(f"- **NEEDS VERIFICATION:** {len(needs_verif)}")
report_lines.append(f"- **TOTAL ACTIONABLE:** {len(verified_rec) + len(highly_likely_rec) + len(needs_verif)}")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Helper to format table rows
def format_table_row(row, include_filter=False):
    sup_title = str(row.get('SupplierTitle', ''))[:40]
    amz_title = str(row.get('AmazonTitle', ''))[:45]
    ean = str(row.get('EAN', '-'))[:13]
    ean_amz = str(row.get('EAN_OnPage', '-'))[:13]
    asin = str(row.get('ASIN', '-'))[:10]
    profit = f"£{row.get('NetProfit', 0):.2f}"
    adj_profit = f"£{row.get('Adjusted_Profit', 0):.2f}"
    roi = f"{row.get('ROI', 0):.1f}%" if pd.notna(row.get('ROI')) else '-'
    sales = int(row.get('sales', 0))
    pack = str(row.get('Pack_Verdict', '-'))[:20]
    brand = str(row.get('Brand_Match', '-'))[:15] if row.get('Brand_Match') else '-'
    evidence = brand if brand != '-' else f"{row.get('title_match', 0)*100:.0f}% title"
    filter_reason = str(row.get('Filter_Reason', '-'))[:25]
    
    if include_filter:
        return f"| {row['RowID']:>5} | {sup_title:<40} | {amz_title:<45} | {profit:>8} | {adj_profit:>10} | {sales:>5} | {pack:<20} | {filter_reason:<25} |"
    else:
        return f"| {row['RowID']:>5} | {sup_title:<40} | {amz_title:<45} | {profit:>8} | {adj_profit:>10} | {sales:>5} | {pack:<20} | {evidence:<18} |"

# VERIFIED — RECOMMENDED
report_lines.append(f"## VERIFIED — RECOMMENDED (count={len(verified_rec)})")
report_lines.append("")
if len(verified_rec) > 0:
    report_lines.append("```text")
    report_lines.append(f"| {'Row':>5} | {'SupplierTitle':<40} | {'AmazonTitle':<45} | {'Profit':>8} | {'AdjProfit':>10} | {'Sales':>5} | {'Pack Verdict':<20} | {'Evidence':<18} |")
    report_lines.append(f"|{'-'*7}|{'-'*42}|{'-'*47}|{'-'*10}|{'-'*12}|{'-'*7}|{'-'*22}|{'-'*20}|")
    for _, row in verified_rec.sort_values('Adjusted_Profit', ascending=False).head(50).iterrows():
        report_lines.append(format_table_row(row))
    report_lines.append("```")
else:
    report_lines.append("*No products in this category*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# VERIFIED — FILTERED OUT
report_lines.append(f"## VERIFIED — FILTERED OUT (count={len(verified_fo)})")
report_lines.append("")
if len(verified_fo) > 0:
    report_lines.append("```text")
    report_lines.append(f"| {'Row':>5} | {'SupplierTitle':<40} | {'AmazonTitle':<45} | {'Profit':>8} | {'AdjProfit':>10} | {'Sales':>5} | {'Pack Verdict':<20} | {'Filter Reason':<25} |")
    report_lines.append(f"|{'-'*7}|{'-'*42}|{'-'*47}|{'-'*10}|{'-'*12}|{'-'*7}|{'-'*22}|{'-'*27}|")
    for _, row in verified_fo.sort_values('Adjusted_Profit', ascending=True).head(30).iterrows():
        report_lines.append(format_table_row(row, include_filter=True))
    report_lines.append("```")
else:
    report_lines.append("*No products in this category*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# HIGHLY LIKELY — RECOMMENDED
report_lines.append(f"## HIGHLY LIKELY — RECOMMENDED (count={len(highly_likely_rec)})")
report_lines.append("")
if len(highly_likely_rec) > 0:
    report_lines.append("```text")
    report_lines.append(f"| {'Row':>5} | {'SupplierTitle':<40} | {'AmazonTitle':<45} | {'Profit':>8} | {'AdjProfit':>10} | {'Sales':>5} | {'Pack Verdict':<20} | {'Evidence':<18} |")
    report_lines.append(f"|{'-'*7}|{'-'*42}|{'-'*47}|{'-'*10}|{'-'*12}|{'-'*7}|{'-'*22}|{'-'*20}|")
    for _, row in highly_likely_rec.sort_values('Adjusted_Profit', ascending=False).head(60).iterrows():
        report_lines.append(format_table_row(row))
    report_lines.append("```")
else:
    report_lines.append("*No products in this category*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# HIGHLY LIKELY — FILTERED OUT
report_lines.append(f"## HIGHLY LIKELY — FILTERED OUT (count={len(highly_likely_fo)})")
report_lines.append("")
if len(highly_likely_fo) > 0:
    report_lines.append("```text")
    report_lines.append(f"| {'Row':>5} | {'SupplierTitle':<40} | {'AmazonTitle':<45} | {'Profit':>8} | {'AdjProfit':>10} | {'Sales':>5} | {'Pack Verdict':<20} | {'Filter Reason':<25} |")
    report_lines.append(f"|{'-'*7}|{'-'*42}|{'-'*47}|{'-'*10}|{'-'*12}|{'-'*7}|{'-'*22}|{'-'*27}|")
    for _, row in highly_likely_fo.sort_values('Adjusted_Profit', ascending=True).head(40).iterrows():
        report_lines.append(format_table_row(row, include_filter=True))
    report_lines.append("```")
else:
    report_lines.append("*No products in this category*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# NEEDS VERIFICATION
report_lines.append(f"## NEEDS VERIFICATION (count={len(needs_verif)})")
report_lines.append("")
if len(needs_verif) > 0:
    report_lines.append("```text")
    report_lines.append(f"| {'Row':>5} | {'SupplierTitle':<40} | {'AmazonTitle':<45} | {'Profit':>8} | {'AdjProfit':>10} | {'Sales':>5} | {'Pack Verdict':<20} | {'What to Verify':<25} |")
    report_lines.append(f"|{'-'*7}|{'-'*42}|{'-'*47}|{'-'*10}|{'-'*12}|{'-'*7}|{'-'*22}|{'-'*27}|")
    for _, row in needs_verif.sort_values('Adjusted_Profit', ascending=False).head(60).iterrows():
        report_lines.append(format_table_row(row, include_filter=True))
    report_lines.append("```")
else:
    report_lines.append("*No products in this category*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Reconciliation
report_lines.append("## Reconciliation")
report_lines.append("")
report_lines.append(f"- Total rows in input: {len(df)}")
report_lines.append(f"- VERIFIED (total): {len(verified_rec) + len(verified_fo)}")
report_lines.append(f"- HIGHLY LIKELY (total): {len(highly_likely_rec) + len(highly_likely_fo)}")
report_lines.append(f"- NEEDS VERIFICATION: {len(needs_verif)}")
report_lines.append(f"- Rows categorized: {len(verified_rec) + len(verified_fo) + len(highly_likely_rec) + len(highly_likely_fo) + len(needs_verif)}")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("*Report generated by AG1 FBA Analysis System*")
report_lines.append(f"*Date: {datetime.now().strftime('%Y-%m-%d')}*")

# Save report
report_path = f"{OUTPUT_DIR}\\PHASEA_MANUAL_REPORT_{datetime.now().strftime('%Y%m%d')}.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f"Saved Markdown report: {report_path}")
print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
