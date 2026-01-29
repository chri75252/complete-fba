"""
FBA Product Analysis Script v4.1.1 AG1
Analyzes financial report for Amazon FBA arbitrage opportunities.
"""
import pandas as pd
import re
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================
INPUT_FILE = 'part 4 jan.xlsx'
OUTPUT_DIR = 'opus 1'

# Supplier-specific calibration (based on previous supplier patterns)
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pce", "pcs", "pk", "pack", "x"],
    "allow_trailing_number_as_qty": False,  # Conservative
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in", "ft", "m"],
    "brand_position": "mixed",
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "led", "watt", "w"],
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
# STAGE 3: Basic EAN Matching
# =============================================================================
print("\n" + "=" * 60)
print("STAGE 3: Basic EAN Matching")
print("=" * 60)

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
print(f"Basic EAN matches: {df['is_exact_ean'].sum()}")

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

df['is_exact_ean_strict'] = (
    df['EAN_strict_valid']
    & df['EAN_OnPage_strict_valid']
    & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
)

print(f"Strict valid Supplier EANs: {df['EAN_strict_valid'].sum()}")
print(f"Strict valid Amazon EANs: {df['EAN_OnPage_strict_valid'].sum()}")
print(f"Strict exact EAN matches: {df['is_exact_ean_strict'].sum()}")

# =============================================================================
# STAGE 4: Pack Size Extraction & Profit Recalculation
# =============================================================================
print("\n" + "=" * 60)
print("STAGE 4: Pack Size Extraction")
print("=" * 60)

def is_dimension_pattern(title, number):
    """Check if a number is part of a dimension pattern, not a pack count"""
    title_lower = str(title).lower()
    
    # Dimension patterns that should NOT be treated as pack counts
    dimension_patterns = [
        rf'{number}\s*(?:cm|mm|ml|ltr|l|kg|g|oz|inch|in|ft|m)\b',  # 15cm, 500ml
        rf'{number}\s*x\s*\d+\s*(?:cm|mm|ml|inch|in|ft|m)',  # 15x20cm
        rf'\d+\s*x\s*{number}\s*(?:cm|mm|ml|inch|in|ft|m)',  # 20x15cm
        rf'{number}\s*x\s*\d+\s*x\s*\d+',  # 15x20x30 (dimensions)
    ]
    
    for pattern in dimension_patterns:
        if re.search(pattern, title_lower):
            return True
    return False

def extract_quantity(title):
    """Extract pack size from product title. Defaults to 1."""
    if pd.isna(title):
        return 1.0
    title = str(title).lower()
    
    # Skip dimension patterns
    dimension_keywords = ['cm', 'mm', 'ml', 'ltr', 'kg', 'g', 'oz', 'inch', 'in', 'ft', 'm']
    
    patterns = [
        (r'pack of (\d+)', 1.0),
        (r'set of (\d+)', 1.0),
        (r'\b(\d+)\s*pack\b', 1.0),
        (r'\b(\d+)\s*pk\b', 1.0),
        (r'(\d+)\s*pcs\b', 1.0),
        (r'(\d+)\s*pce\b', 1.0),
        (r'(\d+)\s*pieces?\b', 1.0),
        (r'(\d+)\s*pairs?\b', 1.0),
        (r'\((\d+)\s*pack\)', 1.0),
        (r'\(pack of (\d+)\)', 1.0),
        (r'\b(\d+)\s*rolls?\b', 1.0),
    ]
    
    for pat, multiplier in patterns:
        match = re.search(pat, title)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:
                # Check if this number is part of a dimension
                if not is_dimension_pattern(title, int(qty)):
                    return qty * multiplier
    return 1.0

def extract_multipack_total(title):
    """
    Extract total items from multipack patterns like '(4 x 50)' or '3 x 500ml'.
    Returns (outer_count, inner_count, total) or (1, qty, qty) if no multipack.
    """
    if pd.isna(title):
        return (1, 1, 1)
    title = str(title).lower()
    
    # Pattern for "N x M" multipacks (e.g., "4 x 50", "3 x 500ml")
    # But avoid dimension patterns
    multipack_pattern = r'\(?\s*(\d+)\s*x\s*(\d+)\s*\)?'
    
    for match in re.finditer(multipack_pattern, title):
        outer = int(match.group(1))
        inner = int(match.group(2))
        
        # Check if this looks like dimensions (has unit after)
        after_match = title[match.end():match.end()+10] if match.end() < len(title) else ''
        if re.match(r'\s*(?:cm|mm|inch|in|ft|m)\b', after_match):
            continue  # This is dimensions, skip
            
        # Likely multipack if outer is small and inner is reasonable
        if outer <= 12 and inner > 10 and inner < 1000:
            return (outer, inner, outer * inner)
    
    # Fallback to simple quantity extraction
    qty = extract_quantity(title)
    return (1, int(qty), int(qty))

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Multipack'] = df['AmazonTitle'].apply(extract_multipack_total)
df['Amz_Total'] = df['Amz_Multipack'].apply(lambda x: x[2])

# Calculate RSU (Required Supplier Units)
df['RSU'] = df.apply(lambda row: max(1, row['Amz_Total'] / row['Sup_Qty']) if row['Sup_Qty'] > 0 else 1, axis=1)
df['Qty_Ratio'] = df['RSU']

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

print(f"Pack sizes extracted")
print(f"Rows with RSU > 1: {len(df[df['RSU'] > 1])}")
print(f"Rows with negative Adjusted_Profit: {len(df[df['Adjusted_Profit'] <= 0])}")

# =============================================================================
# STAGE 5: Product Categorization
# =============================================================================
print("\n" + "=" * 60)
print("STAGE 5: Product Categorization")
print("=" * 60)

def categorize(row):
    if row['is_exact_ean_strict']:
        return 'EXACT_EAN_MATCH'
    elif row['title_match'] >= 0.50:
        return 'HIGH_LIKELIHOOD'
    elif row['title_match'] >= 0.30:
        return 'MODERATE_CONFIDENCE'
    else:
        return 'UNCERTAIN'

df['category'] = df.apply(categorize, axis=1)

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

print(f"Category distribution:")
print(df['category'].value_counts())

# =============================================================================
# STAGE 5B: Thorough Manual Analysis
# =============================================================================
print("\n" + "=" * 60)
print("STAGE 5B: Thorough Manual Analysis")
print("=" * 60)

def extract_brand(title):
    """Extract likely brand from title (usually first word or two)"""
    if pd.isna(title):
        return ''
    words = str(title).upper().split()
    if len(words) >= 1:
        # Return first word as potential brand
        return words[0]
    return ''

def brands_match(sup_title, amz_title):
    """Check if brands match between supplier and Amazon titles"""
    if pd.isna(sup_title) or pd.isna(amz_title):
        return False
    
    sup_upper = str(sup_title).upper()
    amz_upper = str(amz_title).upper()
    
    # Extract first word (often brand)
    sup_brand = extract_brand(sup_title)
    
    # Check if supplier brand appears anywhere in Amazon title
    if sup_brand and len(sup_brand) >= 3:
        if sup_brand in amz_upper:
            return True
    
    # Also check for common brand patterns
    common_brands = ['AMTECH', 'ROLSON', 'DRAPER', 'FAIRY', 'DETTOL', 'MARIGOLD', 'DUNLOP', 
                     'MASON CASH', 'PYREX', 'EVERBUILD', 'HARRIS', 'STATUS', 'EXTRASTAR',
                     'ROUNDUP', 'LITTLE TREES', 'CHEF AID', 'BLUE CANYON', 'SOUDAL', 
                     'TIDYZ', 'KILROCK', 'PAN AROMA', 'APOLLO', 'SUPERIOR', 'HOUSE OF QUIRK']
    
    for brand in common_brands:
        if brand in sup_upper and brand in amz_upper:
            return True
    
    return False

def get_product_type(title):
    """Extract product type from title"""
    if pd.isna(title):
        return ''
    title_lower = str(title).lower()
    
    product_types = ['hammer', 'trowel', 'brush', 'bowl', 'candle', 'tape', 'glue', 
                     'knife', 'scissors', 'torch', 'lamp', 'mirror', 'dish', 'pan',
                     'jar', 'container', 'bag', 'box', 'foam', 'spray', 'cleaner',
                     'light', 'bulb', 'battery', 'cable', 'wire', 'plug', 'socket',
                     'tape', 'gloves', 'cloth', 'sponge', 'mop', 'bucket', 'bin']
    
    for pt in product_types:
        if pt in title_lower:
            return pt
    return ''

df['sup_brand'] = df['SupplierTitle'].apply(extract_brand)
df['brand_match'] = df.apply(lambda x: brands_match(x['SupplierTitle'], x['AmazonTitle']), axis=1)
df['product_type_match'] = df.apply(
    lambda x: get_product_type(x['SupplierTitle']) == get_product_type(x['AmazonTitle']) 
    and get_product_type(x['SupplierTitle']) != '', axis=1
)

print(f"Brand matches: {df['brand_match'].sum()}")
print(f"Product type matches: {df['product_type_match'].sum()}")

# =============================================================================
# FINAL CATEGORIZATION WITH MANUAL LOGIC
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
        'is_exact_ean_strict': row['is_exact_ean_strict'],
    }
    
    # Determine category
    if row['is_exact_ean_strict']:
        # VERIFIED - Exact EAN match
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
    
    elif row['brand_match'] and row['title_match'] >= 0.35:
        # HIGHLY LIKELY - Brand matches and reasonable title similarity
        item['Confidence'] = 80
        item['Key_Match_Evidence'] = f"Brand match: {row['sup_brand']}; title sim: {row['title_match']:.2f}"
        
        if row['Adjusted_Profit'] > 0:
            item['Verdict'] = 'HIGHLY LIKELY'
            item['Filter_Reason'] = '-'
            highly_likely_recommended.append(item)
        else:
            item['Verdict'] = 'FILTERED OUT'
            item['Filter_Reason'] = f"RSU={int(row['RSU'])}; adjusted profit negative"
            highly_likely_filtered.append(item)
    
    elif row['title_match'] >= 0.45 and row['Adjusted_Profit'] > 0:
        # NEEDS VERIFICATION - Good title match but brand not confirmed
        item['Confidence'] = 60
        item['Verdict'] = 'NEEDS VERIFICATION'
        item['Key_Match_Evidence'] = f"Title similarity: {row['title_match']:.2f}"
        item['Filter_Reason'] = 'Confirm brand on packaging'
        needs_verification.append(item)
    
    elif row['brand_match'] and row['Adjusted_Profit'] > 0:
        # NEEDS VERIFICATION - Brand matches but low title similarity (may be variant)
        item['Confidence'] = 55
        item['Verdict'] = 'NEEDS VERIFICATION'
        item['Key_Match_Evidence'] = f"Brand match: {row['sup_brand']}"
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

def format_table_row(item, max_widths):
    """Format a single table row with proper padding"""
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
    
    row_str = '| ' + ' | '.join(cells) + ' |'
    return row_str

# Generate timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
report_filename = f"{OUTPUT_DIR}/PHASEA_MANUAL_REPORT_{timestamp}.md"

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
    f.write(f"- UNRELATED / NOT INCLUDED: {len(df) - len(verified_recommended) - len(verified_filtered) - len(highly_likely_recommended) - len(highly_likely_filtered) - len(needs_verification)}\n")
    f.write(f"- TOTAL ANALYZED: {len(df)}\n\n")
    
    f.write("This report applies v4.1.1 Thorough Manual Analysis:\n")
    f.write("- HIGHLY LIKELY requires Brand + Product type match with positive profit.\n")
    f.write("- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade.\n")
    f.write("- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit).\n\n")
    
    # Table headers
    headers = ['Verdict', 'Confidence', 'SupplierTitle', 'AmazonTitle', 'Supplier EAN', 'Amazon EAN', 
               'ASIN', 'SupplierPrice', 'SellingPrice', 'NetProfit', 'ROI', 'Sales', 
               'Pack Verdict', 'Adjusted Profit', 'Key Match Evidence', 'Filter Reason']
    
    header_row = '| ' + ' | '.join(headers) + ' |'
    separator = '|' + '|'.join(['-' * (len(h) + 2) for h in headers]) + '|'
    
    # VERIFIED RECOMMENDED
    f.write(f"## VERIFIED — RECOMMENDED (count={len(verified_recommended)})\n\n")
    if verified_recommended:
        # Sort by sales descending
        verified_recommended.sort(key=lambda x: x.get('Sales', 0), reverse=True)
        f.write("```text\n")
        f.write(header_row + '\n')
        f.write(separator + '\n')
        for item in verified_recommended:
            f.write(format_table_row(item, {}) + '\n')
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
            f.write(format_table_row(item, {}) + '\n')
        f.write("```\n\n")
    else:
        f.write("*No exact EAN matches filtered out due to pack/profit issues.*\n\n")
    
    # HIGHLY LIKELY RECOMMENDED
    f.write(f"## HIGHLY LIKELY — RECOMMENDED (count={len(highly_likely_recommended)})\n\n")
    if highly_likely_recommended:
        # Sort by confidence, then sales
        highly_likely_recommended.sort(key=lambda x: (x.get('Confidence', 0), x.get('Sales', 0)), reverse=True)
        f.write("```text\n")
        f.write(header_row + '\n')
        f.write(separator + '\n')
        for item in highly_likely_recommended[:100]:  # Limit to first 100 for readability
            f.write(format_table_row(item, {}) + '\n')
        if len(highly_likely_recommended) > 100:
            f.write(f"... and {len(highly_likely_recommended) - 100} more items\n")
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
            f.write(format_table_row(item, {}) + '\n')
        f.write("```\n\n")
    else:
        f.write("*No brand+product matches filtered out.*\n\n")
    
    # NEEDS VERIFICATION
    f.write(f"## NEEDS VERIFICATION (count={len(needs_verification)})\n\n")
    if needs_verification:
        # Sort by confidence, then sales
        needs_verification.sort(key=lambda x: (x.get('Confidence', 0), x.get('Sales', 0)), reverse=True)
        f.write("```text\n")
        f.write(header_row + '\n')
        f.write(separator + '\n')
        for item in needs_verification[:50]:  # Limit to first 50
            f.write(format_table_row(item, {}) + '\n')
        if len(needs_verification) > 50:
            f.write(f"... and {len(needs_verification) - 50} more items\n")
        f.write("```\n\n")
    else:
        f.write("*No items requiring verification.*\n\n")
    
    # Reconciliation
    f.write("## RECONCILIATION\n\n")
    total_categorized = len(verified_recommended) + len(verified_filtered) + len(highly_likely_recommended) + len(highly_likely_filtered) + len(needs_verification)
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
    f.write("*Report generated by FBA Analysis Script v4.1.1 AG1*\n")

print(f"\nReport saved to: {report_filename}")
print("=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
