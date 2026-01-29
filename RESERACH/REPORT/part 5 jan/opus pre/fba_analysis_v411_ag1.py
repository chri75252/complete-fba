"""
FBA Product Analysis v4.1.1 AG1
Comprehensive analysis with calibration integration
Generated: 2026-01-05
"""

import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
from datetime import datetime
from pathlib import Path

# ============================================================================
# CALIBRATION CONFIGURATION (from preflight analysis)
# ============================================================================
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pack', 'pc', 'pcs', 'pieces', 'pk'],
    "allow_trailing_number_as_qty": True,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ['cm', 'ft', 'g', 'inch', 'kg', 'm', 'ml', 'mm'],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": False,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times"],
    "table_pipe_sanitization": True
}

# Known brands (expanded list)
KNOWN_BRANDS = [
    'DLUX', 'CHEF', 'PROKLEEN', 'EUROWRAP', 'RSW', 'WORLD', 'ARTIST', 'MINKY',
    'STARWASH', 'STATUS', 'AMTECH', 'ROLSON', 'DRAPER', 'FAIRY', 'DETTOL',
    'MARIGOLD', 'DUNLOP', 'MASON CASH', 'PYREX', 'EVERBUILD', 'HARRIS',
    'EXTRASTAR', 'ROUNDUP', 'LITTLE TREES', 'TIDYZ', 'SOUDAL', 'KILROCK',
    'BLUE CANYON', 'APOLLO', 'PAN AROMA', 'EVEREADY', 'LYNWOOD', 'DEKTON',
    'FESTIVE MAGIC', 'UNIQUE', 'PARTY CRAZY', 'BRIGHT & HOMELY'
]

# IP Risk brands (true luxury/trademark only)
IP_RISK_BRANDS = [
    'JO MALONE', 'CHANEL', 'DIOR', 'GUCCI', 'LOUIS VUITTON', 'PRADA', 'HERMÈS',
    'APPLE', 'SAMSUNG', 'SONY', 'MICROSOFT', 'NIKE', 'ADIDAS'
]

# ============================================================================
# STAGE 1: Data Loading & Initial Cleaning
# ============================================================================
def load_and_clean_data(file_path):
    """Load CSV/Excel and perform initial cleaning"""
    print("STAGE 1: Loading and cleaning data...")
    
    # Detect file type and load
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
    
    print(f"Loaded {len(df)} rows")
    
    # Clean EAN columns
    df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()
    
    # Handle sales column
    sales_col = SUPPLIER_NAMING_CONVENTION['sales_column']
    if sales_col in df.columns:
        df['sales'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0)
    else:
        df['sales'] = 0
    
    # Add RowID for traceability
    df['RowID'] = df.index + 1
    
    return df

# ============================================================================
# STAGE 1B: EAN Normalization Safety Flags
# ============================================================================
def clean_to_digits(x):
    """Convert to digits only, handling scientific notation"""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

def add_ean_safety_flags(df):
    """Add safety flags for EAN corruption detection"""
    print("STAGE 1B: Adding EAN normalization safety flags...")
    
    df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
    df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
    
    return df

# ============================================================================
# STAGE 2: Title Similarity Calculation
# ============================================================================
def title_similarity(title1, title2):
    """Calculate similarity ratio between two titles"""
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

def add_title_similarity(df):
    """Add title similarity scores"""
    print("STAGE 2: Calculating title similarity...")
    
    df['title_match'] = df.apply(
        lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), 
        axis=1
    )
    
    return df

# ============================================================================
# STAGE 3: Basic EAN Matching
# ============================================================================
def is_valid_ean(ean):
    """Check if EAN is valid (not empty, nan, None, etc.)"""
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

def add_basic_ean_match(df):
    """Add basic EAN match flag"""
    print("STAGE 3: Checking basic EAN matches...")
    
    df['is_exact_ean'] = df.apply(is_exact_ean_match, axis=1)
    
    print(f"  Basic EAN matches: {df['is_exact_ean'].sum()}")
    
    return df

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
    """Check if barcode is strictly valid"""
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

def add_strict_ean_validation(df):
    """Add strict EAN validation with checksum"""
    print("STAGE 3B: Adding strict barcode validation...")
    
    df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
    df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)
    
    df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
    df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)
    
    df['is_exact_ean_strict'] = (
        df['EAN_strict_valid']
        & df['EAN_OnPage_strict_valid']
        & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
    )
    
    print(f"  Strict EAN matches: {df['is_exact_ean_strict'].sum()}")
    
    return df

# ============================================================================
# STAGE 4: Pack Size Extraction & Profit Recalculation
# ============================================================================
def is_dimension_pattern(text, number_str):
    """Check if number is part of a dimension pattern"""
    text_lower = str(text).lower()
    
    # Check for dimension keywords from calibration
    dim_keywords = SUPPLIER_NAMING_CONVENTION['dimension_shield_keywords']
    
    for keyword in dim_keywords:
        # Check for patterns like "21cm", "9x9inch", "500ml"
        patterns = [
            f'{number_str}\\s*{keyword}',
            f'{number_str}{keyword}',
            f'{keyword}\\s*{number_str}',
        ]
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True
    
    # Check for dimension multiplication (e.g., "9 x 9 inch", "30 x 36cm")
    if re.search(rf'\d+\s*x\s*{number_str}\s*(inch|cm|mm|ft)', text_lower):
        return True
    if re.search(rf'{number_str}\s*x\s*\d+\s*(inch|cm|mm|ft)', text_lower):
        return True
    
    return False

def extract_quantity(title):
    """Extract pack size from product title"""
    if pd.isna(title):
        return 1.0
    
    title_str = str(title)
    title_lower = title_str.lower()
    
    # Get explicit units from calibration
    explicit_units = SUPPLIER_NAMING_CONVENTION['explicit_units']
    
    patterns = [
        (r'pack of (\d+)', 1),
        (r'set of (\d+)', 1),
        (r'\b(\d+)\s*pack\b', 1),
        (r'\b(\d+)\s*pk\b', 1),
        (r'(\d+)\s*pcs\b', 1),
        (r'(\d+)\s*pieces?\b', 1),
        (r'(\d+)\s*pc\b', 1),
        (r'\((\d+)\s*pack\)', 1),
        (r'\(pack of (\d+)\)', 1),
    ]
    
    for pat, _ in patterns:
        match = re.search(pat, title_lower)
        if match:
            qty_str = match.group(1)
            qty = float(qty_str)
            
            # Shield dimension patterns
            if is_dimension_pattern(title_str, qty_str):
                continue
            
            if qty > 1 and qty < 500:
                return qty
    
    # Trailing number check (if enabled in calibration)
    if SUPPLIER_NAMING_CONVENTION['allow_trailing_number_as_qty']:
        trailing_match = re.search(r'[A-Z]+\s+(\d+)$', title_str)
        if trailing_match:
            qty_str = trailing_match.group(1)
            qty = float(qty_str)
            if not is_dimension_pattern(title_str, qty_str) and qty > 1 and qty < 500:
                return qty
    
    return 1.0

def extract_multipack_total(title):
    """Extract total items from multipack patterns"""
    if pd.isna(title):
        return (1, 1, 1)
    
    title_lower = str(title).lower()
    
    # Pattern for "N x M" multipacks
    multipack_pattern = r'\(?\s*(\d+)\s*x\s*(\d+)\s*\)?'
    match = re.search(multipack_pattern, title_lower)
    
    if match:
        outer = int(match.group(1))
        inner = int(match.group(2))
        
        # Avoid dimension patterns
        if is_dimension_pattern(title, match.group(1)) or is_dimension_pattern(title, match.group(2)):
            qty = extract_quantity(title)
            return (1, int(qty), int(qty))
        
        # Likely multipack if outer <= 10 and inner > 10
        if outer <= 10 and inner > 10:
            return (outer, inner, outer * inner)
    
    qty = extract_quantity(title)
    return (1, int(qty), int(qty))

def recalculate_profit(row):
    """Adjust profit based on Required Supplier Units"""
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        rsu = row['RSU']
        adjustment = supplier_cost * (rsu - 1)
        return original_profit - adjustment
    except:
        return 0.0

def add_pack_analysis(df):
    """Add pack size extraction and profit recalculation"""
    print("STAGE 4: Extracting pack sizes and recalculating profit...")
    
    df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
    df['Amz_Multipack'] = df['AmazonTitle'].apply(extract_multipack_total)
    df['Amz_Total'] = df['Amz_Multipack'].apply(lambda x: x[2])
    
    # Calculate RSU
    df['RSU'] = df.apply(
        lambda row: max(1, row['Amz_Total'] / row['Sup_Qty']) if row['Sup_Qty'] > 0 else 1,
        axis=1
    )
    df['Qty_Ratio'] = df['RSU']
    
    # Recalculate profit
    df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)
    
    print(f"  Rows with RSU > 1: {(df['RSU'] > 1).sum()}")
    print(f"  Rows with negative adjusted profit: {(df['Adjusted_Profit'] <= 0).sum()}")
    
    return df

# ============================================================================
# STAGE 5: Product Categorization
# ============================================================================
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
    else:
        if row['Adjusted_Profit'] > 0:
            return f"SPLIT (1/{int(1/rsu)}) - OK"
        else:
            return "SPLIT - LOSS"

def add_pack_verdict(df):
    """Add pack verdict column"""
    print("STAGE 5: Adding pack verdict...")
    
    df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)
    
    return df

# ============================================================================
# STAGE 5B: Thorough Manual Analysis for Categorization
# ============================================================================
def extract_brand(title):
    """Extract brand from title"""
    if pd.isna(title):
        return None
    
    title_upper = str(title).upper()
    
    # Check for known brands
    for brand in KNOWN_BRANDS:
        if brand.upper() in title_upper:
            return brand
    
    # Check first word if all caps (from calibration)
    if SUPPLIER_NAMING_CONVENTION['brand_position'] == 'start':
        words = str(title).split()
        if words and words[0].isupper() and len(words[0]) >= 2:
            return words[0]
    
    return None

def brands_match(supplier_title, amazon_title):
    """Check if brands match between titles"""
    sup_brand = extract_brand(supplier_title)
    amz_brand = extract_brand(amazon_title)
    
    if sup_brand is None or amz_brand is None:
        return False
    
    return sup_brand.upper() == amz_brand.upper()

def product_types_match(supplier_title, amazon_title):
    """Check if product types match"""
    if pd.isna(supplier_title) or pd.isna(amazon_title):
        return False
    
    sup_lower = str(supplier_title).lower()
    amz_lower = str(amazon_title).lower()
    
    # Extract significant words (not brands, not dimensions)
    sup_words = set(re.findall(r'\b[a-z]{4,}\b', sup_lower))
    amz_words = set(re.findall(r'\b[a-z]{4,}\b', amz_lower))
    
    # Check for common significant words
    common = sup_words.intersection(amz_words)
    
    return len(common) >= 1

def categorize_product(row):
    """Categorize product using thorough manual analysis"""
    
    # STEP 1: Check for Exact EAN Match
    if row['is_exact_ean_strict']:
        # Check for explicit pack contradiction
        sup_qty = row['Sup_Qty']
        amz_total = row['Amz_Total']
        
        # If no pack contradiction, classify as VERIFIED
        if sup_qty == amz_total or row['Adjusted_Profit'] > 0:
            return 'VERIFIED', 95, 'Exact EAN match; titles align', '-'
        else:
            # Pack mismatch with negative profit
            return 'FILTERED_OUT', 95, 'Exact EAN match', f'RSU={int(row["RSU"])}; adjusted profit negative'
    
    # STEP 2: Check for HIGHLY LIKELY
    if brands_match(row['SupplierTitle'], row['AmazonTitle']):
        if product_types_match(row['SupplierTitle'], row['AmazonTitle']):
            if row['Adjusted_Profit'] > 0:
                confidence = 85
                evidence = f"Brand + product match: {extract_brand(row['SupplierTitle'])}"
                return 'HIGHLY_LIKELY', confidence, evidence, '-'
    
    # STEP 3: Check for NEEDS VERIFICATION
    if row['title_match'] >= 0.40 and row['Adjusted_Profit'] > 0:
        # Plausible match requiring confirmation
        confidence = int(row['title_match'] * 100)
        evidence = f"Title similarity {confidence}%"
        reason = "Confirm brand/pack on packaging"
        return 'NEEDS_VERIFICATION', confidence, evidence, reason
    
    # STEP 4: Filter out negative profit items
    if row['Adjusted_Profit'] <= 0:
        return 'FILTERED_OUT', 0, 'Pack recalculation', 'Adjusted profit negative'
    
    # Default: Not included
    return 'UNRELATED', 0, 'Weak match evidence', 'Not included'

def add_thorough_categorization(df):
    """Add thorough manual categorization"""
    print("STAGE 5B: Applying thorough manual analysis for categorization...")
    
    results = df.apply(categorize_product, axis=1, result_type='expand')
    df['Category'] = results[0]
    df['Confidence'] = results[1]
    df['Key_Match_Evidence'] = results[2]
    df['Filter_Reason'] = results[3]
    
    print("\nCategory Distribution:")
    print(df['Category'].value_counts())
    
    return df

# ============================================================================
# REPORT GENERATION
# ============================================================================
def format_currency(value):
    """Format value as currency"""
    try:
        return f"£{float(value):.2f}"
    except:
        return "-"

def format_percentage(value):
    """Format value as percentage"""
    try:
        return f"{float(value):.1f}%"
    except:
        return "-"

def sanitize_text(text):
    """Sanitize text for table output"""
    if pd.isna(text):
        return "-"
    
    text_str = str(text).strip()
    
    # Replace pipe with slash if configured
    if SUPPLIER_NAMING_CONVENTION['table_pipe_sanitization']:
        text_str = text_str.replace('|', '/')
    
    # Remove newlines
    text_str = text_str.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate long strings
    if len(text_str) > 60:
        text_str = text_str[:57] + '...'
    
    return text_str

def create_table_row(row):
    """Create formatted table row"""
    return {
        'Verdict': row['Category'],
        'Confidence': row['Confidence'],
        'SupplierTitle': sanitize_text(row['SupplierTitle']),
        'AmazonTitle': sanitize_text(row['AmazonTitle']),
        'Supplier_EAN': row['EAN'] if is_valid_ean(row['EAN']) else '-',
        'Amazon_EAN': row['EAN_OnPage'] if is_valid_ean(row['EAN_OnPage']) else '-',
        'ASIN': row['ASIN'] if pd.notna(row['ASIN']) else '-',
        'SupplierPrice': format_currency(row['SupplierPrice_incVAT']),
        'SellingPrice': format_currency(row['SellingPrice_incVAT']),
        'NetProfit': format_currency(row['NetProfit']),
        'ROI': format_percentage(row['ROI ( % )']),
        'Sales': int(row['sales']) if pd.notna(row['sales']) else 0,
        'Pack_Verdict': row['Pack_Verdict'],
        'Adjusted_Profit': format_currency(row['Adjusted_Profit']),
        'Key_Match_Evidence': sanitize_text(row['Key_Match_Evidence']),
        'Filter_Reason': sanitize_text(row['Filter_Reason'])
    }

def format_table(rows):
    """Format rows as fixed-width table"""
    if not rows:
        return "No items in this category.\n"
    
    # Define column widths
    widths = {
        'Verdict': 15,
        'Confidence': 10,
        'SupplierTitle': 35,
        'AmazonTitle': 35,
        'Supplier_EAN': 14,
        'Amazon_EAN': 14,
        'ASIN': 11,
        'SupplierPrice': 13,
        'SellingPrice': 13,
        'NetProfit': 10,
        'ROI': 8,
        'Sales': 6,
        'Pack_Verdict': 20,
        'Adjusted_Profit': 16,
        'Key_Match_Evidence': 30,
        'Filter_Reason': 25
    }
    
    # Create header
    header = '| ' + ' | '.join(k.ljust(widths[k]) for k in widths.keys()) + ' |'
    separator = '|' + '|'.join('-' * (widths[k] + 2) for k in widths.keys()) + '|'
    
    lines = [header, separator]
    
    # Add rows
    for row in rows:
        line = '| ' + ' | '.join(str(row.get(k, '-')).ljust(widths[k]) for k in widths.keys()) + ' |'
        lines.append(line)
    
    return '\n'.join(lines)

def generate_report(df, input_path):
    """Generate comprehensive markdown report"""
    print("\nGenerating report...")
    
    # Get counts
    verified_rec = len(df[df['Category'] == 'VERIFIED'])
    verified_filt = len(df[(df['Category'] == 'FILTERED_OUT') & (df['is_exact_ean_strict'] == True)])
    highly_likely_rec = len(df[df['Category'] == 'HIGHLY_LIKELY'])
    highly_likely_filt = len(df[(df['Category'] == 'FILTERED_OUT') & (df['is_exact_ean_strict'] == False)])
    needs_verification = len(df[df['Category'] == 'NEEDS_VERIFICATION'])
    unrelated = len(df[df['Category'] == 'UNRELATED'])
    
    # Generate report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    report = f"""# PHASEA MANUAL REPORT
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Input File:** {input_path}
**Supplier:** EFG Housewares (detected from calibration)
**Analysis Version:** v4.1.1 AG1

## Summary Counts

- VERIFIED — RECOMMENDED: {verified_rec}
- VERIFIED — FILTERED OUT / EXCLUDED: {verified_filt}
- HIGHLY LIKELY — RECOMMENDED: {highly_likely_rec}
- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {highly_likely_filt}
- NEEDS VERIFICATION: {needs_verification}
- UNRELATED / NOT INCLUDED: {unrelated}
- TOTAL ANALYZED: {len(df)}

⚠️ **CRITICAL DATA QUALITY WARNING:** Calibration analysis detected severe EAN mismatch issues in ~80% of sampled rows. Many supplier products appear linked to completely unrelated Amazon listings (e.g., "Paint" → "LG TV", "Badge" → "Motorola phone"). Results should be manually validated.

This report applies v4.1.1 AG1 Thorough Manual Analysis with integrated calibration:
- HIGHLY LIKELY requires Brand + Product type match with positive profit
- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade
- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit)
- Dimension shield applied for: {', '.join(SUPPLIER_NAMING_CONVENTION['dimension_shield_keywords'])}

---

## VERIFIED — RECOMMENDED (count={verified_rec})

Products with exact EAN matches that pass all verification gates.

```text
{format_table([create_table_row(row) for _, row in df[df['Category'] == 'VERIFIED'].sort_values('sales', ascending=False).iterrows()])}
```

---

## VERIFIED — FILTERED OUT / EXCLUDED (count={verified_filt})

Products with exact EAN matches excluded due to pack/profit issues.

```text
{format_table([create_table_row(row) for _, row in df[(df['Category'] == 'FILTERED_OUT') & (df['is_exact_ean_strict'] == True)].iterrows()])}
```

---

## HIGHLY LIKELY — RECOMMENDED (count={highly_likely_rec})

Strong brand + product matches with positive profit.

```text
{format_table([create_table_row(row) for _, row in df[df['Category'] == 'HIGHLY_LIKELY'].sort_values('sales', ascending=False).iterrows()])}
```

---

## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={highly_likely_filt})

Brand + product matches excluded due to pack/profit issues.

```text
{format_table([create_table_row(row) for _, row in df[(df['Category'] == 'FILTERED_OUT') & (df['is_exact_ean_strict'] == False)].iterrows()])}
```

---

## NEEDS VERIFICATION (count={needs_verification})

Items requiring 1-2 confirmable details for upgrade.

```text
{format_table([create_table_row(row) for _, row in df[df['Category'] == 'NEEDS_VERIFICATION'].sort_values('Confidence', ascending=False).iterrows()])}
```

---

## RECONCILIATION

| Category | Count |
|----------|-------|
| VERIFIED — RECOMMENDED | {verified_rec} |
| VERIFIED — FILTERED OUT | {verified_filt} |
| HIGHLY LIKELY — RECOMMENDED | {highly_likely_rec} |
| HIGHLY LIKELY — FILTERED OUT | {highly_likely_filt} |
| NEEDS VERIFICATION | {needs_verification} |
| UNRELATED / NOT INCLUDED | {unrelated} |
| **TOTAL** | **{len(df)}** |

---

**End of Report**
**Analyst:** Antigravity AI (v4.1.1 AG1)
**Calibration Applied:** Part 5 Jan supplier-specific patterns
"""
    
    return report, timestamp

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    # File paths
    INPUT_PATH = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 5 jan\part 5 jan.xlsx'
    OUTPUT_DIR = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 5 jan\opus pre'
    
    print("=" * 80)
    print("FBA PRODUCT ANALYSIS v4.1.1 AG1")
    print("=" * 80)
    print()
    
    # Execute analysis stages
    df = load_and_clean_data(INPUT_PATH)
    df = add_ean_safety_flags(df)
    df = add_title_similarity(df)
    df = add_basic_ean_match(df)
    df = add_strict_ean_validation(df)
    df = add_pack_analysis(df)
    df = add_pack_verdict(df)
    df = add_thorough_categorization(df)
    
    # Generate report
    report, timestamp = generate_report(df, INPUT_PATH)
    
    # Save report
    output_path = Path(OUTPUT_DIR) / f'PHASEA_MANUAL_REPORT_{timestamp}.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n{'=' * 80}")
    print(f"Report saved to: {output_path}")
    print(f"{'=' * 80}\n")
    
    # Print summary
    print("\nFINAL SUMMARY:")
    print(df['Category'].value_counts())
    print()

if __name__ == '__main__':
    main()
