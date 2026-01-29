"""
FBA Product Analysis Script v4.1
Implements all stages from the FBA PRODUCT ANALYSIS MASTER PROMPT V4.1
Generated: 2025-12-31
"""

import pandas as pd
import re
import json
from difflib import SequenceMatcher
from pathlib import Path
from datetime import datetime

# Configuration
INPUT_PATH = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx")
OUTPUT_DIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\OPUS V2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# IP Risk brands (luxury/trademark only per v4.1)
IP_RISK_BRANDS = {
    'jo malone', 'chanel', 'dior', 'gucci', 'louis vuitton', 'prada', 'hermes', 'hermès',
    'apple', 'samsung', 'sony', 'microsoft', 'nike', 'adidas'
}

# Brand color whitelist (v4.1) - these are brand names, not color variants
BRAND_COLOR_WHITELIST = {
    'blue canyon', 'green flash', 'red bull', 'blue harbour', 'green works',
    'black & decker', 'black+decker', 'red devil', 'blue magic', 'green mountain'
}

# ============================================================================
# STAGE 1: Data Loading & Initial Cleaning
# ============================================================================

print("=" * 80)
print("FBA ANALYSIS v4.1 - THOROUGH MANUAL ANALYSIS")
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

print(f"Sales column populated. Non-zero sales: {(df['sales'] > 0).sum()}")

# ============================================================================
# STAGE 1B: EAN Normalization Safety Flags
# ============================================================================

def clean_to_digits(x):
    """Clean value to digits only, handling scientific notation corruption"""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    # If scientific notation appears, treat as corrupted
    if 'e+' in s.lower() or 'e-' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

# ============================================================================
# STAGE 2: Title Similarity Calculation
# ============================================================================

def title_similarity(title1, title2):
    """Calculate similarity ratio between two titles"""
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# ============================================================================
# STAGE 3: Basic EAN Matching
# ============================================================================

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

# ============================================================================
# STAGE 3B: Strict Barcode Validity + Checksum + Left-Padding
# ============================================================================

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
    """Check if barcode is strictly valid (digits, length, checksum)"""
    if not isinstance(digits, str):
        return False
    if not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    # Check for suspicious trailing zeros (corrupted)
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

# ============================================================================
# STAGE 4: Pack Size Extraction & Profit Recalculation (v4.1 Enhanced)
# ============================================================================

def extract_quantity(title):
    """
    Extract pack size from product title. Defaults to 1.
    v4.1 ENHANCEMENTS:
    - Nested pack detection: "(4 x 50)" = 4 packs of 50 = 200 TOTAL
    - Dimension shield: Remove dimension patterns before pack detection
    """
    if pd.isna(title):
        return 1.0
    title_orig = str(title)
    title = title_orig.lower()
    
    # v4.1: Nested pack patterns like "(4 x 50)" = 200 TOTAL items
    nested_pattern = r'\((\d+)\s*x\s*(\d+)\)'
    nested_match = re.search(nested_pattern, title)
    if nested_match:
        outer = float(nested_match.group(1))
        inner = float(nested_match.group(2))
        # Check if this is dimensions, not nested pack
        context = title[max(0, nested_match.start()-5):nested_match.end()+10]
        if any(unit in context for unit in ['cm', 'mm', 'inch', 'in', 'm ', 'ft']):
            pass  # It's dimensions, don't treat as nested pack
        else:
            return outer * inner
    
    # v4.1: Dimension Shield - Remove dimension patterns before pack detection
    dimension_patterns = [
        r'\d+\s*x\s*\d+\s*(?:x\s*\d+\s*)?(?:cm|mm|inch|in|m|ft)\b',
        r'\d+(?:\.\d+)?\s*(?:cm|mm|inch|in|m|ml|l|ltr|g|kg|oz)\b',
        r'\d+\s*x\s*\d+\s*x\s*\d+',  # Any AxBxC pattern
    ]
    title_clean = title
    for dim_pat in dimension_patterns:
        title_clean = re.sub(dim_pat, '', title_clean, flags=re.IGNORECASE)
    
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*pairs?\b',
        r'\bx\s*(\d+)\b',
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)',
        r'\b(\d+)\s*rolls?\b',
        r'\b(\d+)\s*piece\b',
        r'\b(\d+)\s*bags?\b',
        r'\b(\d+)\s*sheets\b',
    ]
    
    for pat in patterns:
        match = re.search(pat, title_clean)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:
                return qty
    return 1.0

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']

def recalculate_profit(row):
    """
    Adjust profit based on quantity ratio.
    v4.1: No "splittable" scenario - must supply all units Amazon sells
    """
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        adjustment = supplier_cost * (ratio - 1)
        return original_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# ============================================================================
# STAGE 5: Product Categorization
# ============================================================================

def pack_verdict(row):
    """Generate pack verdict string"""
    ratio = row['Qty_Ratio']
    adj_profit = row['Adjusted_Profit']
    
    if ratio == 1.0:
        return "1:1 Match"
    elif ratio > 1.0:
        if adj_profit > 0:
            return f"BUNDLE ({int(ratio)}x) - OK"
        else:
            return f"BUNDLE ({int(ratio)}x) - LOSS"
    else:
        if adj_profit > 0:
            return f"SPLIT (1/{int(1/ratio)}) - OK"
        else:
            return "SPLIT - LOSS"

df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)

# ============================================================================
# STAGE 5B: Thorough Manual Analysis for Categorization (v4.0 Enhanced)
# ============================================================================

def extract_brand(title):
    """Extract potential brand from title (usually first word(s))"""
    if pd.isna(title):
        return ''
    title = str(title).strip()
    # Common words that aren't brands
    non_brand_words = {'the', 'a', 'an', 'new', 'original', 'genuine', 'premium', 'professional'}
    words = title.split()
    if not words:
        return ''
    
    # Try first 1-3 words as potential brand
    for i in range(min(3, len(words)), 0, -1):
        candidate = ' '.join(words[:i]).lower().strip('()[]')
        if candidate not in non_brand_words:
            return candidate
    return words[0].lower() if words else ''

def check_brand_match(sup_title, amz_title):
    """Check if brand names match between titles"""
    if pd.isna(sup_title) or pd.isna(amz_title):
        return False, '', ''
    
    sup_lower = str(sup_title).lower()
    amz_lower = str(amz_title).lower()
    
    # Extract potential brands
    sup_brand = extract_brand(sup_title)
    amz_brand = extract_brand(amz_title)
    
    # Direct brand match
    if sup_brand and amz_brand and sup_brand == amz_brand:
        return True, sup_brand, amz_brand
    
    # Check if supplier brand appears in Amazon title (or vice versa)
    if sup_brand and len(sup_brand) > 2 and sup_brand in amz_lower:
        return True, sup_brand, sup_brand
    if amz_brand and len(amz_brand) > 2 and amz_brand in sup_lower:
        return True, amz_brand, amz_brand
    
    # Check for brand color whitelist
    for brand in BRAND_COLOR_WHITELIST:
        if brand in sup_lower and brand in amz_lower:
            return True, brand, brand
    
    return False, sup_brand, amz_brand

def extract_product_type(title):
    """Extract core product type from title"""
    if pd.isna(title):
        return ''
    title = str(title).lower()
    
    # Common product types
    product_types = [
        'hammer', 'trowel', 'brush', 'screwdriver', 'pliers', 'wrench', 'saw',
        'bowl', 'dish', 'plate', 'cup', 'mug', 'jar', 'container', 'box',
        'candle', 'lamp', 'light', 'torch', 'lantern',
        'bag', 'sack', 'pouch', 'wrapper',
        'tape', 'glue', 'adhesive', 'sealant', 'filler',
        'spray', 'cleaner', 'remover', 'polish',
        'mat', 'rug', 'carpet', 'pad',
        'hook', 'hanger', 'rail', 'rack', 'shelf',
        'mirror', 'frame', 'picture',
        'pen', 'pencil', 'marker', 'highlighter',
        'knife', 'scissors', 'cutter', 'blade',
        'rope', 'cord', 'string', 'wire', 'cable',
        'pegs', 'clips', 'pins', 'staples',
        'bucket', 'bin', 'basket', 'tray',
        'sponge', 'cloth', 'wipe', 'towel', 'tissue',
        'brush', 'broom', 'mop', 'duster',
        'shovel', 'spade', 'rake', 'fork', 'hoe',
        'pot', 'pan', 'kettle', 'jug', 'pitcher',
        'lock', 'padlock', 'chain', 'bolt',
        'valve', 'tap', 'faucet', 'pipe', 'fitting',
        'screw', 'nail', 'bolt', 'nut', 'washer',
        'gloves', 'mask', 'goggles', 'apron',
        'battery', 'charger', 'adapter', 'cable',
        'file', 'rasp', 'sandpaper', 'grinder',
        'drill', 'bit', 'socket', 'ratchet',
    ]
    
    for pt in product_types:
        if pt in title:
            return pt
    return ''

def check_product_type_match(sup_title, amz_title):
    """Check if product types match"""
    sup_pt = extract_product_type(sup_title)
    amz_pt = extract_product_type(amz_title)
    
    if sup_pt and amz_pt and sup_pt == amz_pt:
        return True, sup_pt
    return False, sup_pt or amz_pt

def has_dimension_pattern(title):
    """Check if title contains dimension patterns (not pack counts)"""
    if pd.isna(title):
        return False
    title = str(title).lower()
    dim_patterns = [
        r'\d+\s*x\s*\d+\s*(?:x\s*\d+\s*)?(?:cm|mm|inch|in|m|ft)',
        r'\d+(?:\.\d+)?\s*x\s*\d+(?:\.\d+)?\s*(?:cm|mm|inch|in|m)',
        r'\d+(?:\.\d+)?(?:cm|mm|inch|in|m|ml|l|ltr|g|kg|oz)\b',
    ]
    for pat in dim_patterns:
        if re.search(pat, title, re.IGNORECASE):
            return True
    return False

def check_ip_risk(sup_title, amz_title):
    """Check for IP risk brands"""
    combined = (str(sup_title) + ' ' + str(amz_title)).lower()
    for brand in IP_RISK_BRANDS:
        if brand in combined:
            return True, brand
    return False, None

def analyze_row(row):
    """
    Thorough manual analysis for categorization per v4.0/v4.1
    Returns: (category, confidence, evidence, filter_reason, rsu)
    """
    is_exact_ean = row['is_exact_ean_strict']
    sales = row['sales']
    net_profit = row['NetProfit']
    adj_profit = row['Adjusted_Profit']
    title_sim = row['title_match']
    qty_ratio = row['Qty_Ratio']
    sup_title = str(row['SupplierTitle']) if not pd.isna(row['SupplierTitle']) else ''
    amz_title = str(row['AmazonTitle']) if not pd.isna(row['AmazonTitle']) else ''
    
    # Extract analysis components
    brand_match, sup_brand, amz_brand = check_brand_match(sup_title, amz_title)
    product_match, product_type = check_product_type_match(sup_title, amz_title)
    has_dims = has_dimension_pattern(sup_title) or has_dimension_pattern(amz_title)
    ip_risk, ip_brand = check_ip_risk(sup_title, amz_title)
    
    # Calculate Required Supplier Units
    rsu = max(1, int(qty_ratio)) if qty_ratio > 1 else 1
    
    # Build evidence string
    evidence_parts = []
    if is_exact_ean:
        evidence_parts.append("Exact EAN match")
    if brand_match:
        evidence_parts.append(f"Brand: {sup_brand}")
    if product_match:
        evidence_parts.append(f"Product: {product_type}")
    if title_sim >= 0.5:
        evidence_parts.append(f"Title sim: {title_sim:.0%}")
    evidence = "; ".join(evidence_parts) if evidence_parts else "-"
    
    # =========================================================================
    # CATEGORIZATION DECISION TREE (v4.0/v4.1)
    # =========================================================================
    
    # Step 1: Check for Exact EAN Match
    if is_exact_ean:
        # Default to VERIFIED unless explicit contradiction
        
        # Check for explicit pack mismatch (not dimension patterns)
        explicit_pack_mismatch = False
        if qty_ratio > 1 and not has_dims:
            # Check for explicit pack words
            pack_words_sup = any(w in sup_title.lower() for w in ['single', '1 piece', '1 pack', 'each'])
            pack_words_amz = re.search(r'\b(10|12|15|20|24|30|36|48|50|100)\s*(pack|pk|pcs|pieces)\b', amz_title.lower())
            if pack_words_sup and pack_words_amz:
                explicit_pack_mismatch = True
        
        # Check profit after pack adjustment
        if explicit_pack_mismatch and adj_profit <= 0:
            return ('VERIFIED_EXCLUDED', 90, evidence, f"Pack mismatch: {int(qty_ratio)}x required, Adj Profit=£{adj_profit:.2f}", rsu)
        
        if adj_profit <= 0 and qty_ratio > 1:
            return ('VERIFIED_EXCLUDED', 90, evidence, f"Bundle {int(qty_ratio)}x unprofitable: Adj Profit=£{adj_profit:.2f}", rsu)
        
        if sales == 0:
            return ('NEEDS_VERIFICATION', 85, evidence, "Exact EAN but Sales=0 - verify demand", rsu)
        
        if adj_profit <= 0:
            return ('VERIFIED_EXCLUDED', 90, evidence, f"Exact EAN but unprofitable: Adj Profit=£{adj_profit:.2f}", rsu)
        
        # Valid VERIFIED
        confidence = 95
        return ('VERIFIED', confidence, evidence, "-", rsu)
    
    # Step 2: Check for HIGHLY LIKELY (brand + product match + profit positive)
    if brand_match and product_match and adj_profit > 0:
        if sales == 0:
            return ('NEEDS_VERIFICATION', 75, evidence, "Strong match but Sales=0 - verify demand", rsu)
        if ip_risk:
            return ('NEEDS_VERIFICATION', 70, evidence, f"Potential IP risk: {ip_brand}", rsu)
        if qty_ratio > 1 and not has_dims:
            return ('HIGHLY_LIKELY', 80, evidence + f"; RSU={rsu}", "-", rsu)
        return ('HIGHLY_LIKELY', 85, evidence, "-", rsu)
    
    if brand_match and adj_profit > 0 and title_sim >= 0.4:
        if sales == 0:
            return ('NEEDS_VERIFICATION', 70, evidence, "Brand match but Sales=0", rsu)
        return ('HIGHLY_LIKELY', 75, evidence, "-", rsu)
    
    # Step 3: Check for NEEDS VERIFICATION eligibility
    if adj_profit > 0.5 and (brand_match or product_match or title_sim >= 0.35):
        # Upgradeable with 1-2 confirmations
        if sales == 0:
            filter_reason = "Verify demand: Sales=0"
        elif not brand_match and product_match:
            filter_reason = "Confirm brand on packaging"
        elif brand_match and not product_match:
            filter_reason = "Confirm product variant"
        elif title_sim >= 0.35:
            filter_reason = "Verify match: moderate title similarity"
        else:
            filter_reason = "Verify: plausible match needs confirmation"
        
        confidence = int(50 + title_sim * 30)
        return ('NEEDS_VERIFICATION', confidence, evidence, filter_reason, rsu)
    
    # Step 4: Check for FILTERED OUT
    if adj_profit <= 0:
        if brand_match or product_match:
            return ('HIGHLY_LIKELY_EXCLUDED', 60, evidence, f"Match confirmed but unprofitable: Adj Profit=£{adj_profit:.2f}", rsu)
        return ('FILTERED', 40, evidence, f"Unprofitable: Adj Profit=£{adj_profit:.2f}", rsu)
    
    # Step 5: Default - weak evidence, don't include
    return ('EXCLUDED', 30, evidence if evidence != "-" else "Weak evidence", "Insufficient match evidence", rsu)

# Apply analysis to all rows
print("\nApplying thorough manual analysis to all rows...")
results = df.apply(analyze_row, axis=1)
df['Category'] = results.apply(lambda x: x[0])
df['Confidence'] = results.apply(lambda x: x[1])
df['Key_Match_Evidence'] = results.apply(lambda x: x[2])
df['Filter_Reason'] = results.apply(lambda x: x[3])
df['RSU'] = results.apply(lambda x: x[4])

# ============================================================================
# Summary Statistics
# ============================================================================

print("\n" + "=" * 80)
print("ANALYSIS SUMMARY")
print("=" * 80)

category_counts = df['Category'].value_counts()
print(f"\nCategory Distribution:")
for cat, count in category_counts.items():
    print(f"  {cat}: {count}")

# Separate recommended vs excluded
verified_rec = df[df['Category'] == 'VERIFIED']
verified_exc = df[df['Category'] == 'VERIFIED_EXCLUDED']
highly_likely_rec = df[df['Category'] == 'HIGHLY_LIKELY']
highly_likely_exc = df[df['Category'] == 'HIGHLY_LIKELY_EXCLUDED']
needs_verification = df[df['Category'] == 'NEEDS_VERIFICATION']
filtered_out = df[df['Category'].isin(['FILTERED', 'EXCLUDED'])]

print(f"\n--- Recommended Categories ---")
print(f"VERIFIED — RECOMMENDED: {len(verified_rec)}")
print(f"HIGHLY LIKELY — RECOMMENDED: {len(highly_likely_rec)}")
print(f"\n--- Excluded Categories ---")
print(f"VERIFIED — FILTERED OUT: {len(verified_exc)}")
print(f"HIGHLY LIKELY — FILTERED OUT: {len(highly_likely_exc)}")
print(f"\n--- Needs Review ---")
print(f"NEEDS VERIFICATION: {len(needs_verification)}")
print(f"\n--- Other ---")
print(f"FILTERED/EXCLUDED (weak evidence): {len(filtered_out)}")

# ============================================================================
# Generate Markdown Report
# ============================================================================

def format_price(val):
    """Format price as £X.XX"""
    try:
        return f"£{float(val):.2f}"
    except:
        return "-"

def format_pct(val):
    """Format as percentage"""
    try:
        return f"{float(val)*100:.1f}%"
    except:
        return "-"

def truncate_str(s, max_len=50):
    """Truncate string to max length"""
    s = str(s) if not pd.isna(s) else "-"
    if len(s) > max_len:
        return s[:max_len-3] + "..."
    return s

def format_ean(ean):
    """Format EAN for display"""
    if pd.isna(ean) or str(ean).strip() in ['nan', '', 'None', 'NaN']:
        return "-"
    return str(ean).replace('.0', '')

def generate_table_rows(subset, verdict):
    """Generate table rows for a category"""
    rows = []
    for _, row in subset.iterrows():
        rows.append({
            'Verdict': verdict,
            'Confidence': int(row['Confidence']),
            'SupplierTitle': truncate_str(row['SupplierTitle'], 40),
            'AmazonTitle': truncate_str(row['AmazonTitle'], 50),
            'Supplier_EAN': format_ean(row['EAN']),
            'Amazon_EAN': format_ean(row['EAN_OnPage']),
            'ASIN': str(row['ASIN']) if not pd.isna(row['ASIN']) else "-",
            'SupplierPrice': format_price(row['SupplierPrice_incVAT']),
            'SellingPrice': format_price(row['SellingPrice_incVAT']),
            'NetProfit': format_price(row['NetProfit']),
            'ROI': format_pct(row['ROI']),
            'Sales': int(row['sales']),
            'Pack_Verdict': row['Pack_Verdict'],
            'Adjusted_Profit': format_price(row['Adjusted_Profit']),
            'Key_Match_Evidence': truncate_str(row['Key_Match_Evidence'], 35),
            'Filter_Reason': row['Filter_Reason']
        })
    return rows

# Sort subsets
verified_rec_sorted = verified_rec.sort_values('sales', ascending=False)
verified_exc_sorted = verified_exc.sort_values('Adjusted_Profit', ascending=False)
highly_likely_rec_sorted = highly_likely_rec.sort_values(['Confidence', 'sales'], ascending=[False, False])
highly_likely_exc_sorted = highly_likely_exc.sort_values('Adjusted_Profit', ascending=False)
needs_verification_sorted = needs_verification.sort_values(['Confidence', 'sales'], ascending=[False, False])

# Generate report content
report_date = datetime.now().strftime('%Y-%m-%d')
report_content = f"""# PHASEA MANUAL REPORT

**Generated:** {report_date}
**Input File:** {INPUT_PATH.name}
**Analysis Version:** v4.1 (Thorough Manual Analysis)

---

## Summary Counts

| Category | Count |
|----------|-------|
| VERIFIED — RECOMMENDED | {len(verified_rec)} |
| VERIFIED — FILTERED OUT | {len(verified_exc)} |
| HIGHLY LIKELY — RECOMMENDED | {len(highly_likely_rec)} |
| HIGHLY LIKELY — FILTERED OUT | {len(highly_likely_exc)} |
| NEEDS VERIFICATION | {len(needs_verification)} |
| TOTAL ANALYZED | {len(df)} |

This report applies v4.1 Thorough Manual Analysis:
- HIGHLY LIKELY requires Brand + Product type match with positive profit.
- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade.
- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit).

---

"""

# Add VERIFIED — RECOMMENDED section
if len(verified_rec) > 0:
    report_content += f"## VERIFIED — RECOMMENDED (count={len(verified_rec)})\n\n"
    report_content += "All items have exact EAN match, positive Adjusted Profit, and Sales > 0.\n\n"
    
    rows = generate_table_rows(verified_rec_sorted, 'VERIFIED')
    
    # Build table
    headers = ['Verdict', 'Conf', 'SupplierTitle', 'AmazonTitle', 'Supplier EAN', 'Amazon EAN', 'ASIN', 'SupPrice', 'SellPrice', 'NetProfit', 'ROI', 'Sales', 'Pack Verdict', 'Adj Profit', 'Key Evidence', 'Filter Reason']
    
    report_content += "```text\n"
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "|" + "|".join(["-" * (len(h) + 2) for h in headers]) + "|"
    report_content += header_line + "\n"
    report_content += sep_line + "\n"
    
    for r in rows:
        row_vals = [
            r['Verdict'], str(r['Confidence']), r['SupplierTitle'], r['AmazonTitle'],
            r['Supplier_EAN'], r['Amazon_EAN'], r['ASIN'], r['SupplierPrice'],
            r['SellingPrice'], r['NetProfit'], r['ROI'], str(r['Sales']),
            r['Pack_Verdict'], r['Adjusted_Profit'], r['Key_Match_Evidence'], r['Filter_Reason']
        ]
        report_content += "| " + " | ".join(row_vals) + " |\n"
    report_content += "```\n\n---\n\n"
else:
    report_content += "## VERIFIED — RECOMMENDED (count=0)\n\nNo items qualified for this category.\n\n---\n\n"

# Add VERIFIED — FILTERED OUT section
if len(verified_exc) > 0:
    report_content += f"## VERIFIED — FILTERED OUT / EXCLUDED (count={len(verified_exc)})\n\n"
    report_content += "Items with exact EAN match but excluded due to pack/variant/profit issues.\n\n"
    
    rows = generate_table_rows(verified_exc_sorted, 'FILTERED')
    
    report_content += "```text\n"
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "|" + "|".join(["-" * (len(h) + 2) for h in headers]) + "|"
    report_content += header_line + "\n"
    report_content += sep_line + "\n"
    
    for r in rows:
        row_vals = [
            r['Verdict'], str(r['Confidence']), r['SupplierTitle'], r['AmazonTitle'],
            r['Supplier_EAN'], r['Amazon_EAN'], r['ASIN'], r['SupplierPrice'],
            r['SellingPrice'], r['NetProfit'], r['ROI'], str(r['Sales']),
            r['Pack_Verdict'], r['Adjusted_Profit'], r['Key_Match_Evidence'], r['Filter_Reason']
        ]
        report_content += "| " + " | ".join(row_vals) + " |\n"
    report_content += "```\n\n---\n\n"
else:
    report_content += "## VERIFIED — FILTERED OUT / EXCLUDED (count=0)\n\nNo items in this category.\n\n---\n\n"

# Add HIGHLY LIKELY — RECOMMENDED section
if len(highly_likely_rec) > 0:
    report_content += f"## HIGHLY LIKELY — RECOMMENDED (count={len(highly_likely_rec)})\n\n"
    report_content += "Strong brand + product matches with positive profit.\n\n"
    
    rows = generate_table_rows(highly_likely_rec_sorted, 'HIGHLY LIKELY')
    
    report_content += "```text\n"
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "|" + "|".join(["-" * (len(h) + 2) for h in headers]) + "|"
    report_content += header_line + "\n"
    report_content += sep_line + "\n"
    
    for r in rows:
        row_vals = [
            r['Verdict'], str(r['Confidence']), r['SupplierTitle'], r['AmazonTitle'],
            r['Supplier_EAN'], r['Amazon_EAN'], r['ASIN'], r['SupplierPrice'],
            r['SellingPrice'], r['NetProfit'], r['ROI'], str(r['Sales']),
            r['Pack_Verdict'], r['Adjusted_Profit'], r['Key_Match_Evidence'], r['Filter_Reason']
        ]
        report_content += "| " + " | ".join(row_vals) + " |\n"
    report_content += "```\n\n---\n\n"
else:
    report_content += "## HIGHLY LIKELY — RECOMMENDED (count=0)\n\nNo items qualified for this category.\n\n---\n\n"

# Add HIGHLY LIKELY — FILTERED OUT section
if len(highly_likely_exc) > 0:
    report_content += f"## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={len(highly_likely_exc)})\n\n"
    report_content += "Brand/product matches confirmed but excluded due to pack/variant/profit issues.\n\n"
    
    rows = generate_table_rows(highly_likely_exc_sorted, 'FILTERED')
    
    report_content += "```text\n"
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "|" + "|".join(["-" * (len(h) + 2) for h in headers]) + "|"
    report_content += header_line + "\n"
    report_content += sep_line + "\n"
    
    for r in rows[:50]:  # Limit to 50 for readability
        row_vals = [
            r['Verdict'], str(r['Confidence']), r['SupplierTitle'], r['AmazonTitle'],
            r['Supplier_EAN'], r['Amazon_EAN'], r['ASIN'], r['SupplierPrice'],
            r['SellingPrice'], r['NetProfit'], r['ROI'], str(r['Sales']),
            r['Pack_Verdict'], r['Adjusted_Profit'], r['Key_Match_Evidence'], r['Filter_Reason']
        ]
        report_content += "| " + " | ".join(row_vals) + " |\n"
    
    if len(highly_likely_exc) > 50:
        report_content += f"\n... and {len(highly_likely_exc) - 50} more items\n"
    report_content += "```\n\n---\n\n"
else:
    report_content += "## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count=0)\n\nNo items in this category.\n\n---\n\n"

# Add NEEDS VERIFICATION section
if len(needs_verification) > 0:
    report_content += f"## NEEDS VERIFICATION (count={len(needs_verification)})\n\n"
    report_content += "Items where confirming 1-2 specific details would upgrade the match.\n\n"
    
    rows = generate_table_rows(needs_verification_sorted, 'NEEDS VERIFICATION')
    
    report_content += "```text\n"
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "|" + "|".join(["-" * (len(h) + 2) for h in headers]) + "|"
    report_content += header_line + "\n"
    report_content += sep_line + "\n"
    
    for r in rows[:100]:  # Limit to 100 for readability
        row_vals = [
            r['Verdict'], str(r['Confidence']), r['SupplierTitle'], r['AmazonTitle'],
            r['Supplier_EAN'], r['Amazon_EAN'], r['ASIN'], r['SupplierPrice'],
            r['SellingPrice'], r['NetProfit'], r['ROI'], str(r['Sales']),
            r['Pack_Verdict'], r['Adjusted_Profit'], r['Key_Match_Evidence'], r['Filter_Reason']
        ]
        report_content += "| " + " | ".join(row_vals) + " |\n"
    
    if len(needs_verification) > 100:
        report_content += f"\n... and {len(needs_verification) - 100} more items\n"
    report_content += "```\n\n---\n\n"
else:
    report_content += "## NEEDS VERIFICATION (count=0)\n\nNo items in this category.\n\n---\n\n"

# Add Reconciliation section
report_content += f"""## Reconciliation

| Metric | Value |
|--------|-------|
| Total rows in input | {len(df)} |
| VERIFIED — RECOMMENDED | {len(verified_rec)} |
| VERIFIED — FILTERED OUT | {len(verified_exc)} |
| HIGHLY LIKELY — RECOMMENDED | {len(highly_likely_rec)} |
| HIGHLY LIKELY — FILTERED OUT | {len(highly_likely_exc)} |
| NEEDS VERIFICATION | {len(needs_verification)} |
| Other (weak evidence/excluded) | {len(filtered_out)} |
| **Total categorized** | {len(verified_rec) + len(verified_exc) + len(highly_likely_rec) + len(highly_likely_exc) + len(needs_verification) + len(filtered_out)} |

---

*Report generated by FBA Analysis v4.1*
*Prompt Version: 4.1 (Thorough Manual Analysis with Nested Pack Fix, Capacity Tolerance Fix, Brand Color Fix)*
"""

# Write report
report_path = OUTPUT_DIR / f"PHASEA_MANUAL_REPORT_{datetime.now().strftime('%Y%m%d')}.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"\n✅ Report saved to: {report_path}")

# Also save detailed CSV for further analysis
csv_path = OUTPUT_DIR / f"analysis_details_{datetime.now().strftime('%Y%m%d')}.csv"
export_cols = ['RowID', 'Category', 'Confidence', 'EAN', 'EAN_OnPage', 'ASIN', 
               'SupplierTitle', 'AmazonTitle', 'SupplierPrice_incVAT', 'SellingPrice_incVAT',
               'NetProfit', 'ROI', 'sales', 'Sup_Qty', 'Amz_Qty', 'Qty_Ratio', 
               'Adjusted_Profit', 'Pack_Verdict', 'Key_Match_Evidence', 'Filter_Reason',
               'is_exact_ean_strict', 'title_match']
df[export_cols].to_csv(csv_path, index=False, encoding='utf-8')
print(f"✅ Detailed CSV saved to: {csv_path}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
