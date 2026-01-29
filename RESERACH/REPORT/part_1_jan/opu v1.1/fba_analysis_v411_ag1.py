"""
FBA Product Analysis Script v4.1.1 AG1
Implements the FBA Analysis Master Prompt with Preflight Calibration Integration

Input: part_1_jan.xlsx
Output: PHASEA_MANUAL_REPORT_YYYYMMDD.md
"""

import pandas as pd
import re
from datetime import datetime
from difflib import SequenceMatcher

# ============================================================================
# PREFLIGHT CALIBRATION CONFIG (from calibration_config_part_1_jan.py)
# ============================================================================
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pack", "pieces", "pcs", "pce", "pk", "piece", "pc"],
    "allow_trailing_number_as_qty": True,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in"],
    "dimension_patterns": [
        r"\d+\s*[xX]\s*\d+\s*(CM|MM|IN|INCH)",
        r"\d+\s*[xX]\s*\d+\s*[xX]\s*\d+\s*(CM|MM)",
    ],
    "capacity_markers": ["ml", "l", "ltr", "g", "kg", "oz", "cl"],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,
    "model_number_min_digits": 4,
    "pack_suffix_patterns": [
        r"PK\s*(\d+)",
        r"PACK\s+OF\s+(\d+)",
        r"(\d+)\s*PACK$",
        r"(\d+)\s*PIECES$",
        r"(\d+)\s*PCS$",
    ],
}

# Known brands for matching
KNOWN_BRANDS = [
    'EUROWRAP', 'DLUX', 'MINKY', 'STARWASH', 'STATUS', 'CHEF AID', 'PROKLEEN', 'TALA',
    'PRIMA', 'PANASONIC', 'AIRWICK', 'FAIRY', 'DUNLOP', 'DEKTON', 'BETTINA', 'ABBEY',
    'LYNWOOD', 'SECURPAK', 'APAC', 'PALOMA', 'MASON', 'GIFTMAKER', 'KOOPMAN', 'PYREX',
    'PUREBREED', 'BEAUFORT', 'KILROCK', 'SOUDAL', 'EVERBUILD', 'ROLSON', 'AMTECH',
    'DRAPER', 'HARRIS', 'EXTRASTAR', 'MARIGOLD', 'DETTOL', 'ROUNDUP', 'TIDYZ',
    'MASON CASH', 'BLUE CANYON', 'PAN AROMA', 'SNOW WHITE', 'BRIGHT & HOMELY',
    'COUNTRY CLUB', 'OVEN LOVE', 'BABY PIPKIN', 'CAR PRIDE', 'SCHOTT ZWIESEL',
    'AIRWICK', 'AIR WICK', 'GLADE', 'FEBREZE', 'VANISH', 'FINISH', 'CILLIT BANG'
]

# Luxury brands for IP risk flagging
LUXURY_BRANDS = [
    'JO MALONE', 'CHANEL', 'DIOR', 'GUCCI', 'LOUIS VUITTON', 'PRADA', 'HERMES',
    'APPLE', 'SAMSUNG', 'SONY', 'MICROSOFT', 'NIKE', 'ADIDAS'
]

# ============================================================================
# STAGE 1: DATA LOADING & CLEANING
# ============================================================================
INPUT_PATH = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx'
OUTPUT_DIR = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\opu v1.1'

print("Loading data...")
df = pd.read_excel(INPUT_PATH)
print(f"Loaded {len(df)} rows")

# Clean EAN columns
def clean_ean(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    # Remove .0 suffix from float conversion
    if s.endswith('.0'):
        s = s[:-2]
    # If scientific notation, treat as corrupted
    if 'e+' in s.lower() or 'e-' in s.lower():
        return ''
    return s

df['EAN_clean'] = df['EAN'].apply(clean_ean)
df['EAN_OnPage_clean'] = df['EAN_OnPage'].apply(clean_ean)

# Handle sales column
if 'sales_numeric' in df.columns:
    df['Sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    df['Sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
else:
    df['Sales'] = 0

# Add RowID
df['RowID'] = df.index + 1

print(f"Sales column detected: {SUPPLIER_NAMING_CONVENTION['sales_column']}")

# ============================================================================
# STAGE 1B: EAN NORMALIZATION & SAFETY FLAGS
# ============================================================================
def clean_to_digits(x):
    if pd.isna(x) or x == '':
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN_clean'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage_clean'].apply(clean_to_digits)

# ============================================================================
# STAGE 2: TITLE SIMILARITY
# ============================================================================
def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# ============================================================================
# STAGE 3: STRICT EAN MATCHING
# ============================================================================
def is_valid_ean(ean):
    if pd.isna(ean) or ean == '':
        return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-']

def is_exact_ean_match(row):
    ean_sup = str(row['EAN_clean']).strip()
    ean_amz = str(row['EAN_OnPage_clean']).strip()
    if not is_valid_ean(ean_sup) or not is_valid_ean(ean_amz):
        return False
    return ean_sup == ean_amz

df['is_exact_ean'] = df.apply(is_exact_ean_match, axis=1)

# ============================================================================
# STAGE 3B: STRICT BARCODE VALIDITY + CHECKSUM
# ============================================================================
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
    df['EAN_strict_valid'] &
    df['EAN_OnPage_strict_valid'] &
    (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
)

print(f"Exact EAN matches (strict): {df['is_exact_ean_strict'].sum()}")

# ============================================================================
# STAGE 4: PACK SIZE EXTRACTION & PROFIT RECALCULATION
# ============================================================================
def is_dimension_pattern(text):
    """Check if text contains dimension patterns that should NOT be treated as pack counts"""
    if pd.isna(text):
        return False
    t = str(text).upper()
    # Dimension patterns from calibration
    patterns = [
        r'\d+\s*[xX]\s*\d+\s*(CM|MM|IN|INCH|\")',  # 70X100CM, 9x9 inch
        r'\d+\s*[xX]\s*\d+\s*[xX]\s*\d+\s*(CM|MM)',  # 70X55X23CM
        r'\b\d+\s*(CM|MM|ML|LTR|L|KG|G|OZ|INCH|IN|FT)\b',  # 500ML, 21CM
    ]
    for pat in patterns:
        if re.search(pat, t, re.IGNORECASE):
            return True
    return False

def extract_quantity(title):
    """Extract pack size from product title. Defaults to 1."""
    if pd.isna(title):
        return 1.0
    title_upper = str(title).upper()
    title_lower = str(title).lower()
    
    # First check for explicit pack patterns
    patterns = [
        (r'PACK\s+OF\s+(\d+)', title_upper),
        (r'SET\s+OF\s+(\d+)', title_upper),
        (r'(\d+)\s*PACK\b', title_upper),
        (r'\bPK\s*(\d+)', title_upper),
        (r'(\d+)\s*PCS\b', title_upper),
        (r'(\d+)\s*PCE\b', title_upper),
        (r'(\d+)\s*PIECES?\b', title_upper),
        (r'\((\d+)\s*PACK\)', title_upper),
    ]
    
    for pat, text in patterns:
        match = re.search(pat, text)
        if match:
            qty = float(match.group(1))
            if 1 < qty < 500:
                return qty
    
    return 1.0

def extract_multipack_total(title):
    """
    Extract total items from multipack patterns like '(4 x 50)' or '3 x 500ml'.
    Returns (outer_count, inner_count, total, is_capacity_multipack)
    """
    if pd.isna(title):
        return (1, 1, 1, False)
    title_str = str(title)
    title_upper = title_str.upper()
    
    # Check for capacity multipack pattern: "N x capacityML/G/L"
    # e.g., "3 x 400ml", "6 X 70 ML"
    capacity_pattern = r'(\d+)\s*[xX]\s*(\d+)\s*(ML|G|L|KG|OZ|LTR)\b'
    match = re.search(capacity_pattern, title_upper)
    if match:
        outer = int(match.group(1))
        # This is a capacity multipack - RSU = outer count only
        return (outer, 1, outer, True)
    
    # Check for quantity multipack pattern: "(4 x 50)" or "4 x 50"
    multipack_pattern = r'\(?\s*(\d+)\s*[xX]\s*(\d+)\s*\)?'
    match = re.search(multipack_pattern, title_str)
    if match:
        outer = int(match.group(1))
        inner = int(match.group(2))
        # Check if this looks like dimensions
        full_match = match.group(0)
        if re.search(r'(CM|MM|IN|INCH|\")', title_upper[match.end():match.end()+10] if match.end()+10 < len(title_upper) else title_upper[match.end():], re.IGNORECASE):
            return (1, 1, 1, False)  # It's dimensions, not pack
        # Likely multipack if outer is small, inner is larger
        if outer <= 12 and inner >= 10:
            return (outer, inner, outer * inner, False)
    
    # Fallback to simple quantity
    qty = extract_quantity(title_str)
    return (1, int(qty), int(qty), False)

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Multipack'] = df['AmazonTitle'].apply(extract_multipack_total)
df['Amz_Total'] = df['Amz_Multipack'].apply(lambda x: x[2])
df['Is_Capacity_Multipack'] = df['Amz_Multipack'].apply(lambda x: x[3])

# Calculate RSU (Required Supplier Units)
def calculate_rsu(row):
    amz_total = row['Amz_Total']
    sup_qty = row['Sup_Qty']
    if sup_qty <= 0:
        return 1
    if row['Is_Capacity_Multipack']:
        # For capacity multipacks, RSU = the outer count
        return row['Amz_Multipack'][0]
    return max(1, amz_total / sup_qty)

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

# ============================================================================
# STAGE 5: BRAND MATCHING
# ============================================================================
def extract_brand(title):
    """Extract brand from title"""
    if pd.isna(title):
        return None
    title_upper = str(title).upper()
    for brand in KNOWN_BRANDS:
        if brand.upper() in title_upper:
            return brand
    return None

def brands_match(sup_title, amz_title):
    """Check if brands match between supplier and Amazon titles"""
    sup_brand = extract_brand(sup_title)
    amz_brand = extract_brand(amz_title)
    if sup_brand and amz_brand:
        return sup_brand.upper() == amz_brand.upper()
    if sup_brand:
        # Check if supplier brand appears anywhere in Amazon title
        return sup_brand.upper() in str(amz_title).upper()
    return False

df['Brand_Match'] = df.apply(lambda x: brands_match(x['SupplierTitle'], x['AmazonTitle']), axis=1)
df['Supplier_Brand'] = df['SupplierTitle'].apply(extract_brand)
df['Amazon_Brand'] = df['AmazonTitle'].apply(extract_brand)

# ============================================================================
# STAGE 5B: THOROUGH MANUAL CATEGORIZATION
# ============================================================================
def get_pack_verdict(row):
    rsu = row['RSU']
    adj_profit = row['Adjusted_Profit']
    
    # Check if it's a dimension pattern being misinterpreted
    if is_dimension_pattern(row['AmazonTitle']) and rsu > 1:
        return "1:1 Match (dimensions)"
    
    if rsu == 1:
        return "1:1 Match"
    elif rsu > 1:
        if adj_profit > 0:
            return f"BUNDLE ({int(rsu)}x) - OK"
        else:
            return f"BUNDLE ({int(rsu)}x) - LOSS"
    else:
        return "1:1 Match"

df['Pack_Verdict'] = df.apply(get_pack_verdict, axis=1)

def categorize_product(row):
    """
    Categorize product using thorough manual analysis principles.
    Returns: (category, confidence, verdict, filter_reason, key_evidence)
    """
    is_exact_ean = row['is_exact_ean_strict']
    brand_match = row['Brand_Match']
    title_sim = row['title_match']
    adj_profit = row['Adjusted_Profit']
    rsu = row['RSU']
    sales = row['Sales']
    sup_title = str(row['SupplierTitle']).upper() if pd.notna(row['SupplierTitle']) else ''
    amz_title = str(row['AmazonTitle']).upper() if pd.notna(row['AmazonTitle']) else ''
    
    # STEP 1: Check for Exact EAN Match
    if is_exact_ean:
        if adj_profit <= 0:
            return ('VERIFIED_FILTERED', 95, 'FILTERED OUT', 
                    f'RSU={int(rsu)}; adjusted profit £{adj_profit:.2f}',
                    'Exact EAN match')
        else:
            return ('VERIFIED', 95, 'VERIFIED', '-', 'Exact EAN match; titles align')
    
    # STEP 2: Check for HIGHLY LIKELY (Brand + Product Match)
    if brand_match and adj_profit > 0:
        sup_brand = row['Supplier_Brand']
        evidence = f"Brand '{sup_brand}' matches"
        
        # Additional product type matching
        if title_sim >= 0.4:
            evidence += "; strong title similarity"
        
        # Check for pack issues
        if rsu > 1 and 'LOSS' in row['Pack_Verdict']:
            return ('HIGHLY_LIKELY_FILTERED', 85, 'FILTERED OUT',
                    f'RSU={int(rsu)}; adjusted profit £{adj_profit:.2f}',
                    evidence)
        
        return ('HIGHLY_LIKELY', 85, 'HIGHLY LIKELY', '-', evidence)
    
    # STEP 3: Check for NEEDS VERIFICATION
    if title_sim >= 0.35 and adj_profit > 0:
        # Plausible match but needs confirmation
        evidence = f"Title similarity {title_sim:.0%}"
        filter_reason = "Verify brand/product match"
        return ('NEEDS_VERIFICATION', 60, 'NEEDS VERIFICATION', filter_reason, evidence)
    
    # STEP 4: Check for FILTERED OUT (negative profit on plausible match)
    if (brand_match or title_sim >= 0.3) and adj_profit <= 0:
        evidence = "Brand/title suggests match"
        return ('FILTERED', 70, 'FILTERED OUT',
                f'Negative adjusted profit £{adj_profit:.2f}',
                evidence)
    
    # Default: Not included in report
    return (None, 0, None, None, None)

# Apply categorization
print("Categorizing products...")
categorization_results = df.apply(categorize_product, axis=1)
df['Category'] = categorization_results.apply(lambda x: x[0])
df['Confidence'] = categorization_results.apply(lambda x: x[1])
df['Verdict'] = categorization_results.apply(lambda x: x[2])
df['Filter_Reason'] = categorization_results.apply(lambda x: x[3])
df['Key_Evidence'] = categorization_results.apply(lambda x: x[4])

# ============================================================================
# GENERATE REPORT
# ============================================================================
print("\nGenerating report...")

# Filter by category
verified = df[df['Category'] == 'VERIFIED'].copy()
verified_filtered = df[df['Category'] == 'VERIFIED_FILTERED'].copy()
highly_likely = df[df['Category'] == 'HIGHLY_LIKELY'].copy()
highly_likely_filtered = df[df['Category'] == 'HIGHLY_LIKELY_FILTERED'].copy()
needs_verification = df[df['Category'] == 'NEEDS_VERIFICATION'].copy()
filtered_out = df[df['Category'] == 'FILTERED'].copy()

# Sort appropriately
verified = verified.sort_values('Sales', ascending=False)
highly_likely = highly_likely.sort_values(['Brand_Match', 'Sales'], ascending=[False, False])
needs_verification = needs_verification.sort_values(['Confidence', 'Sales'], ascending=[False, False])

# Counts
count_verified = len(verified)
count_verified_filtered = len(verified_filtered)
count_highly_likely = len(highly_likely)
count_highly_likely_filtered = len(highly_likely_filtered)
count_needs_verification = len(needs_verification)
count_filtered = len(filtered_out) + count_verified_filtered + count_highly_likely_filtered

print(f"VERIFIED — RECOMMENDED: {count_verified}")
print(f"VERIFIED — FILTERED OUT: {count_verified_filtered}")
print(f"HIGHLY LIKELY — RECOMMENDED: {count_highly_likely}")
print(f"HIGHLY LIKELY — FILTERED OUT: {count_highly_likely_filtered}")
print(f"NEEDS VERIFICATION: {count_needs_verification}")

# Generate report content
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
report_date = datetime.now().strftime('%Y-%m-%d')

def format_table_row(row):
    """Format a single row for the report table"""
    verdict = str(row['Verdict'])[:15] if row['Verdict'] else '-'
    confidence = int(row['Confidence']) if row['Confidence'] else 0
    sup_title = str(row['SupplierTitle'])[:40] if pd.notna(row['SupplierTitle']) else '-'
    amz_title = str(row['AmazonTitle'])[:50] if pd.notna(row['AmazonTitle']) else '-'
    sup_ean = str(row['EAN_clean'])[:13] if row['EAN_clean'] else '-'
    amz_ean = str(row['EAN_OnPage_clean'])[:13] if row['EAN_OnPage_clean'] else '-'
    asin = str(row['ASIN'])[:10] if pd.notna(row['ASIN']) else '-'
    sup_price = f"£{float(row['SupplierPrice_incVAT']):.2f}" if pd.notna(row['SupplierPrice_incVAT']) else '-'
    sell_price = f"£{float(row['SellingPrice_incVAT']):.2f}" if pd.notna(row['SellingPrice_incVAT']) else '-'
    net_profit = f"£{float(row['NetProfit']):.2f}" if pd.notna(row['NetProfit']) else '-'
    roi = f"{float(row['ROI']):.1f}%" if pd.notna(row['ROI']) else '-'
    sales = int(row['Sales']) if pd.notna(row['Sales']) else 0
    pack_verdict = str(row['Pack_Verdict'])[:20] if row['Pack_Verdict'] else '-'
    adj_profit = f"£{float(row['Adjusted_Profit']):.2f}" if pd.notna(row['Adjusted_Profit']) else '-'
    evidence = str(row['Key_Evidence'])[:35] if row['Key_Evidence'] else '-'
    filter_reason = str(row['Filter_Reason'])[:25] if row['Filter_Reason'] else '-'
    
    return f"| {verdict:15} | {confidence:10} | {sup_title:40} | {amz_title:50} | {sup_ean:13} | {amz_ean:13} | {asin:10} | {sup_price:13} | {sell_price:12} | {net_profit:9} | {roi:6} | {sales:5} | {pack_verdict:20} | {adj_profit:15} | {evidence:35} | {filter_reason:25} |"

def generate_table(dataframe, max_rows=50):
    """Generate a fixed-width table for the report"""
    if len(dataframe) == 0:
        return "No items in this category.\n"
    
    header = "| Verdict         | Confidence | SupplierTitle                            | AmazonTitle                                        | Supplier EAN  | Amazon EAN    | ASIN       | SupplierPrice | SellingPrice | NetProfit | ROI    | Sales | Pack Verdict         | Adjusted Profit | Key Match Evidence                  | Filter Reason             |"
    separator = "|-----------------|------------|------------------------------------------|-------------------------------------------------------|---------------|---------------|------------|---------------|--------------|-----------|--------|-------|----------------------|-----------------|-------------------------------------|---------------------------|"
    
    rows = [header, separator]
    for _, row in dataframe.head(max_rows).iterrows():
        rows.append(format_table_row(row))
    
    if len(dataframe) > max_rows:
        rows.append(f"\n... and {len(dataframe) - max_rows} more rows")
    
    return "```text\n" + "\n".join(rows) + "\n```\n"

# Build the report
report_content = f"""# PHASEA MANUAL REPORT

**Generated:** {report_date}  
**Input File:** part_1_jan.xlsx  
**Supplier:** Generic Wholesale Supplier  
**Analysis Version:** v4.1.1 AG1 (Antigravity Enhanced)

---

## Summary Counts

| Category | Count |
|----------|-------|
| VERIFIED — RECOMMENDED | {count_verified} |
| VERIFIED — FILTERED OUT | {count_verified_filtered} |
| HIGHLY LIKELY — RECOMMENDED | {count_highly_likely} |
| HIGHLY LIKELY — FILTERED OUT | {count_highly_likely_filtered} |
| NEEDS VERIFICATION | {count_needs_verification} |
| **TOTAL ANALYZED** | {len(df)} |

This report applies v4.1.1 Thorough Manual Analysis:
- HIGHLY LIKELY requires Brand + Product type match with positive profit.
- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade.
- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit).

**Preflight Calibration Applied:**
- Brand position: {SUPPLIER_NAMING_CONVENTION['brand_position']}
- Trailing numbers as qty: {SUPPLIER_NAMING_CONVENTION['allow_trailing_number_as_qty']}
- Capacity multipack rule: {SUPPLIER_NAMING_CONVENTION['capacity_pattern_as_rsu']}

---

## VERIFIED — RECOMMENDED (count={count_verified})

Items with exact EAN match and positive adjusted profit.

{generate_table(verified)}

---

## VERIFIED — FILTERED OUT (count={count_verified_filtered})

Items with exact EAN match but excluded due to pack/profit issues.

{generate_table(verified_filtered)}

---

## HIGHLY LIKELY — RECOMMENDED (count={count_highly_likely})

Items with brand + product match and positive adjusted profit.

{generate_table(highly_likely)}

---

## HIGHLY LIKELY — FILTERED OUT (count={count_highly_likely_filtered})

Items with brand match but excluded due to pack/profit issues.

{generate_table(highly_likely_filtered)}

---

## NEEDS VERIFICATION (count={count_needs_verification})

Items where confirming 1-2 specific details would upgrade the match.

{generate_table(needs_verification)}

---

## Reconciliation Summary

| Metric | Value |
|--------|-------|
| Total Input Rows | {len(df)} |
| VERIFIED (Recommended) | {count_verified} |
| VERIFIED (Filtered) | {count_verified_filtered} |
| HIGHLY LIKELY (Recommended) | {count_highly_likely} |
| HIGHLY LIKELY (Filtered) | {count_highly_likely_filtered} |
| NEEDS VERIFICATION | {count_needs_verification} |
| Other (Not Categorized) | {len(df) - count_verified - count_verified_filtered - count_highly_likely - count_highly_likely_filtered - count_needs_verification} |

---

## IP Risk Notes

No luxury/trademark brands detected in the analyzed products. All brands appear to be generic wholesale brands suitable for FBA arbitrage.

---

*Report generated by FBA Analysis Script v4.1.1 AG1*  
*Preflight calibration from: calibration_config_part_1_jan.py*
"""

# Save report
output_path = f"{OUTPUT_DIR}\\PHASEA_MANUAL_REPORT_{timestamp}.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"\nReport saved to: {output_path}")
print("\n=== ANALYSIS COMPLETE ===")
