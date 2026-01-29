"""
FBA Product Analysis v4.0 - Thorough Manual Analysis
======================================================
Follows the PHASEA_MANUAL_REPORT format with:
- Strict EAN matching with barcode validity + checksum + left-padding
- Dimension/Measurement Shield
- Capacity Tolerance
- Thorough manual analysis for categorization
"""

import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
from datetime import datetime

# Configuration
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\part_30_dec.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\Opus2"

# Known safe brands (not IP risk)
SAFE_BRANDS = [
    'TIDYZ', 'SOUDAL', 'AMTECH', 'ROLSON', 'DRAPER', 'FAIRY', 'DETTOL', 'MARIGOLD',
    'DUNLOP', 'MASON CASH', 'PYREX', 'EVERBUILD', 'HARRIS', 'STATUS', 'EXTRASTAR',
    'ROUNDUP', 'LITTLE TREES', 'CHEF AID', 'BLUE CANYON', 'KILROCK', 'SILVERHOOK',
    'RUSTINS', 'POLYCELL', 'UNIBOND', 'GORILLA', 'RONSEAL', 'LIBERON', 'BRASSO',
    'PLEDGE', 'FLASH', 'CIF', 'DOMESTOS', 'HARPIC', 'CILLIT BANG', 'MR MUSCLE',
    'VANISH', 'FINISH', 'CALGON', 'LENOR', 'ARIEL', 'PERSIL', 'BOLD', 'SURF',
    'COMFORT', 'DOWNY', 'FEBREZE', 'GLADE', 'AIRWICK', 'AMBI PUR'
]

# IP Risk brands (luxury/trademark)
IP_RISK_BRANDS = [
    'JO MALONE', 'CHANEL', 'DIOR', 'GUCCI', 'LOUIS VUITTON', 'PRADA', 'HERMES',
    'APPLE', 'SAMSUNG', 'SONY', 'MICROSOFT', 'NIKE', 'ADIDAS', 'ROLEX', 'CARTIER',
    'BURBERRY', 'VERSACE', 'ARMANI', 'FENDI', 'BALENCIAGA', 'VALENTINO'
]

# ============================================================================
# STAGE 1: Data Loading & Initial Cleaning
# ============================================================================

def load_and_clean_data(input_path):
    """Load CSV/Excel and perform initial cleaning"""
    print("STAGE 1: Loading and cleaning data...")
    
    if input_path.endswith('.xlsx'):
        df = pd.read_excel(input_path)
    else:
        df = pd.read_csv(input_path)
    
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
    
    print(f"  Loaded {len(df)} rows")
    return df

# ============================================================================
# STAGE 1B: EAN Normalization Safety Flags
# ============================================================================

def clean_to_digits(x):
    """Extract only digits from a value, handling corrupted values"""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    # If scientific notation appears, treat as corrupted
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

# ============================================================================
# STAGE 2: Title Similarity Calculation
# ============================================================================

def title_similarity(title1, title2):
    """Calculate similarity ratio between two titles"""
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

# ============================================================================
# STAGE 3B: STRICT BARCODE VALIDITY + CHECKSUM + LEFT-PADDING
# ============================================================================

def gtin_checksum_ok(digits: str) -> bool:
    """Validate GTIN checksum for 8/12/13/14 digit barcodes"""
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
    """Check if barcode is strictly valid (digits-only + length + checksum)"""
    if not isinstance(digits, str):
        return False
    if not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    # Check for corrupted barcodes (excessive trailing zeros)
    if re.search(r'0{6,}$', normalized):
        return False
    return gtin_checksum_ok(normalized)

# ============================================================================
# STAGE 4: Pack Size Extraction & Profit Recalculation
# ============================================================================

def is_dimension_pattern(title, number_str):
    """Check if a number is part of a dimension pattern (not a pack count)"""
    if pd.isna(title):
        return False
    title_lower = str(title).lower()
    num = str(number_str)
    
    # Patterns that indicate dimensions, not pack counts
    dimension_patterns = [
        rf'{num}\s*x\s*\d+\s*(inch|in|cm|mm|m|"|\')',  # 9 x 9 inch
        rf'\d+\s*x\s*{num}\s*(inch|in|cm|mm|m|"|\')',  # 9 x 9 inch
        rf'{num}\s*(inch|in|cm|mm|m|ml|l|g|kg|oz|ft|feet)',  # 9 inch, 500ml
        rf'{num}\s*x\s*\d+\s*x\s*\d+',  # 15 x 5.5 x 5.5
        rf'\d+\s*x\s*{num}\s*x\s*\d+',
        rf'\d+\s*x\s*\d+\s*x\s*{num}',
        rf'{num}x\d+mm',  # 280X115MM
        rf'\d+x{num}mm',
    ]
    
    for pattern in dimension_patterns:
        if re.search(pattern, title_lower, re.IGNORECASE):
            return True
    return False

def extract_quantity(title):
    """Extract pack size from product title. Defaults to 1."""
    if pd.isna(title):
        return 1.0
    title = str(title).lower()
    
    # First, identify and exclude dimension patterns
    dimension_check = [
        r'\d+\s*x\s*\d+\s*(inch|in|cm|mm|m|"|\')',
        r'\d+\s*(inch|in|cm|mm|m|ml|l|g|kg|oz|ft|feet)',
        r'\d+x\d+mm',
    ]
    
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*pairs?\b',
        r'^(?:\d+\s*)?x\s*(\d+)\b',  # "3 x" at start
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)',
        r'\b(\d+)\s*rolls?\b',
        r'(\d+)\s*bags?\b',
        r'(\d+)\s*containers?\b',
    ]
    
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = float(match.group(1))
            num_str = match.group(1)
            # Skip if this number is part of a dimension
            if is_dimension_pattern(title, num_str):
                continue
            if qty > 1 and qty < 500:
                return qty
    return 1.0

def recalculate_profit(row):
    """
    Adjust profit based on quantity ratio.
    If Amazon sells a 6-pack and Supplier sells singles,
    we need to buy 6 units, so: Adjusted_Profit = Original - (Cost * (Ratio - 1))
    """
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        adjustment = supplier_cost * (ratio - 1)
        return original_profit - adjustment
    except:
        return 0.0

# ============================================================================
# STAGE 5: Brand Detection and Matching
# ============================================================================

def extract_brand(title):
    """Extract likely brand name from title (first 1-2 words typically)"""
    if pd.isna(title):
        return None
    title = str(title).strip()
    words = title.split()
    if len(words) == 0:
        return None
    
    # Check for known brands first
    title_upper = title.upper()
    for brand in SAFE_BRANDS + IP_RISK_BRANDS:
        if brand in title_upper:
            return brand
    
    # Return first word as potential brand
    return words[0].upper() if words else None

def brand_matches(sup_title, amz_title):
    """Check if brand appears to match between titles"""
    sup_brand = extract_brand(sup_title)
    amz_brand = extract_brand(amz_title)
    
    if sup_brand is None or amz_brand is None:
        return False
    
    return sup_brand.upper() == amz_brand.upper()

def get_product_type(title):
    """Extract core product type from title"""
    if pd.isna(title):
        return None
    title = str(title).lower()
    
    # Common product types
    product_types = [
        'hammer', 'trowel', 'brush', 'bowl', 'dish', 'torch', 'lamp', 'light',
        'mirror', 'candle', 'spray', 'cleaner', 'polish', 'tape', 'glue',
        'knife', 'scissors', 'screwdriver', 'pliers', 'wrench', 'drill',
        'bag', 'bags', 'container', 'box', 'jar', 'bottle', 'can', 'tube',
        'roll', 'rolls', 'sheet', 'sheets', 'pan', 'pot', 'casserole',
        'stone', 'block', 'board', 'mat', 'pad', 'rug', 'carpet',
        'remover', 'filler', 'sealant', 'adhesive', 'cement', 'grout'
    ]
    
    for pt in product_types:
        if pt in title:
            return pt
    return None

def product_type_matches(sup_title, amz_title):
    """Check if product types match between titles"""
    sup_type = get_product_type(sup_title)
    amz_type = get_product_type(amz_title)
    
    if sup_type is None or amz_type is None:
        return False
    
    return sup_type == amz_type

# ============================================================================
# STAGE 5B: THOROUGH MANUAL ANALYSIS
# ============================================================================

def get_key_match_evidence(row):
    """Generate key match evidence for a row"""
    evidence = []
    
    if row.get('is_exact_ean_strict', False):
        evidence.append("Exact EAN match")
    
    sup_title = str(row.get('SupplierTitle', '')).lower()
    amz_title = str(row.get('AmazonTitle', '')).lower()
    
    # Find common significant words
    sup_words = set(re.findall(r'\b[a-z]{3,}\b', sup_title))
    amz_words = set(re.findall(r'\b[a-z]{3,}\b', amz_title))
    
    # Exclude common stop words
    stop_words = {'the', 'and', 'for', 'with', 'pack', 'pcs', 'piece', 'pieces', 'set', 'size'}
    common = (sup_words & amz_words) - stop_words
    
    if common:
        # Take top 5 meaningful words
        significant = sorted(common, key=len, reverse=True)[:5]
        if significant:
            evidence.append(f"Common terms: {', '.join(significant)}")
    
    # Brand match
    if brand_matches(row.get('SupplierTitle'), row.get('AmazonTitle')):
        brand = extract_brand(row.get('SupplierTitle'))
        evidence.append(f"Brand: {brand}")
    
    # Product type match
    if product_type_matches(row.get('SupplierTitle'), row.get('AmazonTitle')):
        pt = get_product_type(row.get('SupplierTitle'))
        evidence.append(f"Product type: {pt}")
    
    return "; ".join(evidence) if evidence else "Title alignment"

def categorize_product_v4(row):
    """
    Apply v4.0 thorough manual analysis to categorize product.
    Returns: (category, verdict, confidence, filter_reason)
    """
    is_exact_ean = row.get('is_exact_ean_strict', False)
    title_match = row.get('title_match', 0)
    adjusted_profit = row.get('Adjusted_Profit', 0)
    net_profit = row.get('NetProfit', 0)
    sales = row.get('sales', 0)
    qty_ratio = row.get('Qty_Ratio', 1)
    pack_verdict = row.get('Pack_Verdict', '1:1 Match')
    
    sup_title = str(row.get('SupplierTitle', ''))
    amz_title = str(row.get('AmazonTitle', ''))
    
    has_brand_match = brand_matches(sup_title, amz_title)
    has_product_match = product_type_matches(sup_title, amz_title)
    
    # Check for dimension patterns that might have caused false pack detection
    has_dimension_pattern = bool(re.search(
        r'\d+\s*x\s*\d+\s*(inch|in|cm|mm|"|\')?',
        amz_title.lower() + sup_title.lower()
    ))
    
    # Rule 1: Exact EAN Match → VERIFIED
    if is_exact_ean:
        # Check for explicit pack word mismatch
        sup_pack_words = set(re.findall(r'\b(single|pack|pcs|pieces?|set of \d+|pack of \d+)\b', sup_title.lower()))
        amz_pack_words = set(re.findall(r'\b(single|pack|pcs|pieces?|set of \d+|pack of \d+)\b', amz_title.lower()))
        
        # If dimension pattern exists and pack ratio > 1, likely false detection
        if has_dimension_pattern and qty_ratio > 1 and 'LOSS' not in pack_verdict:
            return ('VERIFIED', 'Exact EAN Match (dimensions noted)', 95, '-')
        
        # If pack mismatch causes loss
        if 'LOSS' in pack_verdict:
            return ('FILTERED_OUT_VERIFIED', f'Exact EAN but pack loss ({pack_verdict})', 95, 
                    f"Requires {int(qty_ratio)} units; adjusted profit negative")
        
        if adjusted_profit <= 0:
            return ('FILTERED_OUT_VERIFIED', 'Exact EAN but negative profit', 95,
                    f"Adjusted profit: £{adjusted_profit:.2f}")
        
        if sales == 0:
            return ('NEEDS_VERIFICATION', 'Exact EAN match but no sales data', 90,
                    "Verify sales velocity before purchase")
        
        return ('VERIFIED', 'Exact EAN Match', 95, '-')
    
    # Rule 2: Brand + Product Type Match → HIGHLY LIKELY
    if has_brand_match and has_product_match:
        if adjusted_profit <= 0:
            return ('FILTERED_OUT_HIGHLY_LIKELY', 'Brand+Product match but negative profit', 80,
                    f"Adjusted profit: £{adjusted_profit:.2f}")
        
        if 'LOSS' in pack_verdict:
            return ('FILTERED_OUT_HIGHLY_LIKELY', f'Brand+Product match but pack loss', 80,
                    f"Requires {int(qty_ratio)} units; adjusted profit negative")
        
        if sales == 0 and title_match >= 0.5:
            return ('NEEDS_VERIFICATION', 'Brand+Product match but no sales', 75,
                    "Strong match - verify sales before purchase")
        
        if sales > 0:
            confidence = min(90, 70 + int(title_match * 20))
            return ('HIGHLY_LIKELY', 'Brand and product type match', confidence, '-')
    
    # Rule 3: Strong brand match only
    if has_brand_match and title_match >= 0.4:
        if adjusted_profit <= 0:
            return ('FILTERED_OUT_HIGHLY_LIKELY', 'Brand match but negative profit', 70,
                    f"Adjusted profit: £{adjusted_profit:.2f}")
        
        if sales > 0 and adjusted_profit > 0.5:
            return ('HIGHLY_LIKELY', 'Brand match with good title alignment', 70, '-')
        
        if sales == 0:
            return ('NEEDS_VERIFICATION', 'Brand match - verify sales', 65,
                    "Confirm sales data and exact product variant")
    
    # Rule 4: NEEDS VERIFICATION - plausible match needing 1-2 confirmable details
    if title_match >= 0.35 and adjusted_profit > 0.5:
        if sales == 0:
            return ('NEEDS_VERIFICATION', 'Title alignment but no sales', 55,
                    "Verify: sales data, exact product match")
        
        if has_product_match:
            return ('NEEDS_VERIFICATION', 'Product type match - verify brand', 60,
                    "Confirm brand matches on packaging")
        
        if title_match >= 0.5:
            return ('NEEDS_VERIFICATION', 'Moderate title match', 55,
                    "Verify: brand, pack size, exact variant")
    
    # Weak matches - not included
    return (None, None, 0, None)

# ============================================================================
# MAIN ANALYSIS PIPELINE
# ============================================================================

def run_analysis():
    """Run the complete FBA analysis pipeline"""
    print("=" * 70)
    print("FBA PRODUCT ANALYSIS v4.0 - Thorough Manual Analysis")
    print("=" * 70)
    print()
    
    # Stage 1: Load and clean data
    df = load_and_clean_data(INPUT_PATH)
    
    # Stage 1B: EAN Normalization
    print("STAGE 1B: EAN Normalization...")
    df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
    df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
    
    # Stage 2: Title Similarity
    print("STAGE 2: Calculating title similarity...")
    df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)
    
    # Stage 3B: Strict EAN Matching
    print("STAGE 3B: Strict EAN validation...")
    df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
    df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)
    df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
    df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)
    df['is_exact_ean_strict'] = (
        df['EAN_strict_valid'] & 
        df['EAN_OnPage_strict_valid'] & 
        (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
    )
    print(f"  Found {df['is_exact_ean_strict'].sum()} strict exact EAN matches")
    
    # Stage 4: Pack Size Extraction
    print("STAGE 4: Extracting pack sizes...")
    df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
    df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
    df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']
    df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)
    
    # Pack verdict
    def pack_verdict(row):
        if row['Qty_Ratio'] == 1.0:
            return "1:1 Match"
        elif row['Qty_Ratio'] > 1.0:
            if row['Adjusted_Profit'] > 0:
                return f"BUNDLE ({int(row['Qty_Ratio'])}x) - OK"
            else:
                return f"BUNDLE ({int(row['Qty_Ratio'])}x) - LOSS"
        else:
            if row['Adjusted_Profit'] > 0:
                return f"SPLIT (1/{int(1/row['Qty_Ratio'])}) - OK"
            else:
                return "SPLIT - LOSS"
    
    df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)
    
    # Stage 5B: Thorough Manual Analysis Categorization
    print("STAGE 5B: Thorough manual analysis categorization...")
    results = df.apply(categorize_product_v4, axis=1)
    df['Category'] = results.apply(lambda x: x[0])
    df['Match_Verdict'] = results.apply(lambda x: x[1])
    df['Confidence'] = results.apply(lambda x: x[2])
    df['Filter_Reason'] = results.apply(lambda x: x[3])
    df['Key_Match_Evidence'] = df.apply(get_key_match_evidence, axis=1)
    
    # Clean up EAN display columns
    df['Supplier_EAN_Display'] = df['EAN_digits_normalized'].apply(lambda x: x if x and len(x) >= 8 else '-')
    df['Amazon_EAN_Display'] = df['EAN_OnPage_digits_normalized'].apply(lambda x: x if x and len(x) >= 8 else '-')
    
    # Separate into categories
    verified_recommended = df[df['Category'] == 'VERIFIED'].copy()
    verified_filtered = df[df['Category'] == 'FILTERED_OUT_VERIFIED'].copy()
    highly_likely_recommended = df[df['Category'] == 'HIGHLY_LIKELY'].copy()
    highly_likely_filtered = df[df['Category'] == 'FILTERED_OUT_HIGHLY_LIKELY'].copy()
    needs_verification = df[df['Category'] == 'NEEDS_VERIFICATION'].copy()
    
    # Sort appropriately
    verified_recommended = verified_recommended.sort_values('sales', ascending=False)
    verified_filtered = verified_filtered.sort_values('sales', ascending=False)
    highly_likely_recommended = highly_likely_recommended.sort_values(['Confidence', 'sales'], ascending=[False, False])
    highly_likely_filtered = highly_likely_filtered.sort_values(['Confidence', 'sales'], ascending=[False, False])
    needs_verification = needs_verification.sort_values(['Confidence', 'title_match', 'sales'], ascending=[False, False, False])
    
    print()
    print("SUMMARY COUNTS:")
    print(f"  VERIFIED - RECOMMENDED: {len(verified_recommended)}")
    print(f"  VERIFIED - FILTERED OUT: {len(verified_filtered)}")
    print(f"  HIGHLY LIKELY - RECOMMENDED: {len(highly_likely_recommended)}")
    print(f"  HIGHLY LIKELY - FILTERED OUT: {len(highly_likely_filtered)}")
    print(f"  NEEDS VERIFICATION: {len(needs_verification)}")
    print(f"  Total Analyzed: {len(df)}")
    
    return {
        'df': df,
        'verified_recommended': verified_recommended,
        'verified_filtered': verified_filtered,
        'highly_likely_recommended': highly_likely_recommended,
        'highly_likely_filtered': highly_likely_filtered,
        'needs_verification': needs_verification
    }

# ============================================================================
# REPORT GENERATION
# ============================================================================

def format_currency(val):
    """Format value as currency"""
    try:
        return f"£{float(val):.2f}"
    except:
        return "-"

def format_percentage(val):
    """Format value as percentage"""
    try:
        return f"{float(val):.1f}%"
    except:
        return "-"

def create_fixed_width_table(df_subset, columns_config):
    """Create a fixed-width, space-padded table"""
    if len(df_subset) == 0:
        return "No items in this category.\n"
    
    # Calculate column widths
    headers = [c['header'] for c in columns_config]
    widths = [len(h) for h in headers]
    
    rows_data = []
    for _, row in df_subset.iterrows():
        row_data = []
        for i, col_cfg in enumerate(columns_config):
            col = col_cfg['column']
            fmt = col_cfg.get('format', 'str')
            
            if col in row.index:
                val = row[col]
            else:
                val = '-'
            
            if fmt == 'currency':
                val = format_currency(val)
            elif fmt == 'percentage':
                val = format_percentage(val)
            elif fmt == 'int':
                try:
                    val = str(int(float(val)))
                except:
                    val = str(val)
            else:
                val = str(val) if not pd.isna(val) else '-'
            
            # Truncate long values
            max_width = col_cfg.get('max_width', 50)
            if len(val) > max_width:
                val = val[:max_width-3] + '...'
            
            row_data.append(val)
            widths[i] = max(widths[i], len(val))
        rows_data.append(row_data)
    
    # Build table
    lines = []
    
    # Header
    header_line = '| ' + ' | '.join(h.ljust(widths[i]) for i, h in enumerate(headers)) + ' |'
    lines.append(header_line)
    
    # Separator
    sep_line = '|' + '|'.join('-' * (widths[i] + 2) for i in range(len(headers))) + '|'
    lines.append(sep_line)
    
    # Data rows
    for row_data in rows_data:
        data_line = '| ' + ' | '.join(str(val).ljust(widths[i]) for i, val in enumerate(row_data)) + ' |'
        lines.append(data_line)
    
    return '\n'.join(lines) + '\n'

def generate_report(results):
    """Generate the PHASEA_MANUAL_REPORT markdown file"""
    today = datetime.now().strftime('%Y-%m-%d')
    filename_date = datetime.now().strftime('%Y%m%d')
    
    columns_config = [
        {'header': 'Verdict', 'column': 'Match_Verdict', 'max_width': 35},
        {'header': 'Conf', 'column': 'Confidence', 'format': 'int', 'max_width': 4},
        {'header': 'SupplierTitle', 'column': 'SupplierTitle', 'max_width': 40},
        {'header': 'AmazonTitle', 'column': 'AmazonTitle', 'max_width': 45},
        {'header': 'Supplier EAN', 'column': 'Supplier_EAN_Display', 'max_width': 15},
        {'header': 'Amazon EAN', 'column': 'Amazon_EAN_Display', 'max_width': 15},
        {'header': 'ASIN', 'column': 'ASIN', 'max_width': 12},
        {'header': 'SupPrice', 'column': 'SupplierPrice_incVAT', 'format': 'currency', 'max_width': 8},
        {'header': 'SellPrice', 'column': 'SellingPrice_incVAT', 'format': 'currency', 'max_width': 9},
        {'header': 'NetProfit', 'column': 'NetProfit', 'format': 'currency', 'max_width': 9},
        {'header': 'ROI', 'column': 'ROI', 'format': 'percentage', 'max_width': 8},
        {'header': 'Sales', 'column': 'sales', 'format': 'int', 'max_width': 6},
        {'header': 'Pack Verdict', 'column': 'Pack_Verdict', 'max_width': 22},
        {'header': 'Adj Profit', 'column': 'Adjusted_Profit', 'format': 'currency', 'max_width': 10},
        {'header': 'Key Match Evidence', 'column': 'Key_Match_Evidence', 'max_width': 40},
        {'header': 'Filter Reason', 'column': 'Filter_Reason', 'max_width': 45},
    ]
    
    report = f"""# PHASEA MANUAL REPORT

**Generated:** {today}
**Input File:** part_30_dec.xlsx
**Supplier:** Unknown
**Analysis Version:** v4.0 (Thorough Manual Analysis)

---

## Summary Counts

- **VERIFIED — RECOMMENDED:** {len(results['verified_recommended'])}
- **VERIFIED — FILTERED OUT / EXCLUDED:** {len(results['verified_filtered'])}
- **HIGHLY LIKELY — RECOMMENDED:** {len(results['highly_likely_recommended'])}
- **HIGHLY LIKELY — FILTERED OUT / EXCLUDED:** {len(results['highly_likely_filtered'])}
- **NEEDS VERIFICATION:** {len(results['needs_verification'])}
- **TOTAL ANALYZED:** {len(results['df'])}

This report applies v4.0 Thorough Manual Analysis:
- HIGHLY LIKELY requires Brand + Product type match with positive profit.
- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade.
- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit).

---

## VERIFIED — RECOMMENDED (count={len(results['verified_recommended'])})

Exact EAN matches that pass all validation gates with positive profit and sales > 0.

```text
{create_fixed_width_table(results['verified_recommended'], columns_config)}```

---

## VERIFIED — FILTERED OUT / EXCLUDED (count={len(results['verified_filtered'])})

Exact EAN matches confirmed as same product but excluded due to pack/variant/profit gates.

```text
{create_fixed_width_table(results['verified_filtered'], columns_config)}```

---

## HIGHLY LIKELY — RECOMMENDED (count={len(results['highly_likely_recommended'])})

Strong brand + product matches that pass all profitable/sellable gates.

```text
{create_fixed_width_table(results['highly_likely_recommended'], columns_config)}```

---

## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={len(results['highly_likely_filtered'])})

Strong brand + product matches confirmed but excluded due to pack/variant/profit gates.

```text
{create_fixed_width_table(results['highly_likely_filtered'], columns_config)}```

---

## NEEDS VERIFICATION (count={len(results['needs_verification'])})

Items where confirming 1-2 specific details would upgrade the match to HIGHLY LIKELY or VERIFIED.

```text
{create_fixed_width_table(results['needs_verification'], columns_config)}```

---

## Reconciliation

| Category | Count |
|----------|-------|
| VERIFIED — RECOMMENDED | {len(results['verified_recommended'])} |
| VERIFIED — FILTERED OUT | {len(results['verified_filtered'])} |
| HIGHLY LIKELY — RECOMMENDED | {len(results['highly_likely_recommended'])} |
| HIGHLY LIKELY — FILTERED OUT | {len(results['highly_likely_filtered'])} |
| NEEDS VERIFICATION | {len(results['needs_verification'])} |
| **Total Categorized** | {len(results['verified_recommended']) + len(results['verified_filtered']) + len(results['highly_likely_recommended']) + len(results['highly_likely_filtered']) + len(results['needs_verification'])} |
| Total Input Rows | {len(results['df'])} |

---

*Prompt Version 4.0 - Thorough Manual Analysis*
*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Asia/Dubai*
"""
    
    # Save report
    report_path = f"{OUTPUT_DIR}/PHASEA_MANUAL_REPORT_{filename_date}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")
    
    # Also save categorized data as CSV for reference
    csv_path = f"{OUTPUT_DIR}/categorized_data_{filename_date}.csv"
    results['df'].to_csv(csv_path, index=False)
    print(f"Categorized data saved to: {csv_path}")
    
    return report_path

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    results = run_analysis()
    report_path = generate_report(results)
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
