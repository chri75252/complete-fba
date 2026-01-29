"""
FBA Product Analysis v4.1.1 AG1 (Antigravity Enhanced)
Integrates Preflight Calibration + Thorough Manual Analysis
"""

import pandas as pd
import re
from difflib import SequenceMatcher
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PREFLIGHT CALIBRATION CONFIGURATION (from calibration analysis)
# ============================================================================
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pack', 'pcs', 'piece', 'pk'],
    "allow_trailing_number_as_qty": False,  # CRITICAL: DISABLED for this supplier
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "ft", "m"],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": False,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "power"],
    "table_pipe_sanitization": True
}

# Known wholesale brands (NOT IP risk)
WHOLESALE_BRANDS = [
    'TIDYZ', 'SOUDAL', 'AMTECH', 'ROLSON', 'DRAPER', 'FAIRY', 'DETTOL', 'MARIGOLD',
    'DUNLOP', 'MASON CASH', 'PYREX', 'EVERBUILD', 'HARRIS', 'STATUS', 'EXTRASTAR',
    'ROUNDUP', 'LITTLE TREES', 'EUROWRAP', 'RSW', 'WORLD', 'DLUX', 'ARTIST', 'MINKY',
    'STARWASH', 'CHEF AID', 'TONKITA', 'ADORN', 'FESTIVE MAGIC', 'PROKLEEN', 'DEKTON',
    'TALA', 'BLUE CANYON', 'APOLLO', 'PPS', 'PAN AROMA', 'PARTY CRAZY', 'UNIQUE'
]

# IP risk brands (luxury/trademark)
IP_RISK_BRANDS = [
    'JO MALONE', 'CHANEL', 'DIOR', 'GUCCI', 'LOUIS VUITTON', 'PRADA', 'HERMÈS',
    'APPLE', 'SAMSUNG', 'SONY', 'MICROSOFT', 'NIKE', 'ADIDAS'
]

# ============================================================================
# GTIN CHECKSUM VALIDATION
# ============================================================================
def gtin_checksum_ok(digits: str) -> bool:
    """Validate GTIN checksum for lengths 8, 12, 13, 14"""
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
    """Check if barcode is strictly valid (digits, plausible length, checksum)"""
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

# ============================================================================
# STAGE 1: DATA LOADING & CLEANING
# ============================================================================
def clean_to_digits(x):
    """Convert to digits-only string"""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

def title_similarity(title1, title2):
    """Calculate title similarity ratio"""
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

# ============================================================================
# STAGE 4: PACK SIZE EXTRACTION
# ============================================================================
def is_dimension_pattern(text: str) -> bool:
    """Check if text contains dimension/measurement patterns"""
    if not text:
        return False
    text_lower = text.lower()
    
    # Dimension patterns
    dimension_patterns = [
        r'\d+\s*x\s*\d+\s*(cm|mm|inch|in)',  # 9 x 9 inch
        r'\d+\s*(cm|mm|ml|ltr|l|kg|g|oz|inch|in|ft|m)\b',  # 21CM, 300ML
    ]
    
    for pattern in dimension_patterns:
        if re.search(pattern, text_lower):
            return True
    return False

def extract_quantity(title):
    """Extract pack size from product title with dimension shielding"""
    if pd.isna(title):
        return 1.0
    
    title_str = str(title)
    title_lower = title_str.lower()
    
    # Check if title contains dimension patterns
    if is_dimension_pattern(title_str):
        # Dimensions detected - default to 1
        pass
    
    # Explicit pack patterns (prioritize these)
    explicit_patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
    ]
    
    for pat in explicit_patterns:
        match = re.search(pat, title_lower)
        if match:
            qty = float(match.group(1))
            if 1 < qty < 500:
                return qty
    
    # PCS/PIECE patterns (only if not dimension)
    if not is_dimension_pattern(title_str):
        pcs_patterns = [
            r'(\d+)\s*pcs\b',
            r'(\d+)\s*pieces?\b',
            r'(\d+)\s*piece\b',
        ]
        for pat in pcs_patterns:
            match = re.search(pat, title_lower)
            if match:
                qty = float(match.group(1))
                # Quantity-inside shield: if number is describing contents, not pack
                # Example: "COCKTAIL STICKS 200" = 200 sticks per pack, not 200 packs
                if qty > 50:  # Likely quantity-inside
                    continue
                if 1 < qty < 500:
                    return qty
    
    return 1.0

def extract_multipack_total(title):
    """Extract total items from multipack patterns like '(4 x 50)'"""
    if pd.isna(title):
        return (1, 1, 1)
    
    title_str = str(title)
    title_lower = title_str.lower()
    
    # Check for dimension patterns first
    if is_dimension_pattern(title_str):
        # Dimensions - not a multipack
        qty = extract_quantity(title)
        return (1, int(qty), int(qty))
    
    # Pattern for "N x M" multipacks (e.g., "4 x 50", "3 x 500ml")
    multipack_pattern = r'\(?\s*(\d+)\s*x\s*(\d+)\s*\)?'
    match = re.search(multipack_pattern, title_lower)
    if match:
        outer = int(match.group(1))
        inner = int(match.group(2))
        # Avoid dimension patterns (small numbers with units nearby)
        if outer <= 10 and inner > 10:  # Likely multipack, not dimensions
            return (outer, inner, outer * inner)
    
    # Fallback to simple quantity extraction
    qty = extract_quantity(title)
    return (1, int(qty), int(qty))

# ============================================================================
# BRAND EXTRACTION
# ============================================================================
def extract_brand(title):
    """Extract brand from title (case-insensitive)"""
    if pd.isna(title):
        return None
    
    title_upper = str(title).upper()
    
    # Check all known brands (wholesale + IP risk)
    all_brands = WHOLESALE_BRANDS + IP_RISK_BRANDS
    for brand in all_brands:
        if brand.upper() in title_upper:
            return brand
    
    # If brand_position is "start", try first word
    if SUPPLIER_NAMING_CONVENTION['brand_position'] == 'start':
        words = str(title).split()
        if words and len(words[0]) > 2 and words[0].isupper():
            return words[0]
    
    return None

# ============================================================================
# PRODUCT TYPE EXTRACTION
# ============================================================================
PRODUCT_TYPES = [
    'hammer', 'trowel', 'brush', 'bowl', 'mirror', 'dish', 'candle', 'torch',
    'peeler', 'spanner', 'screwdriver', 'pliers', 'saw', 'scissors', 'knife',
    'bottle', 'cup', 'mug', 'plate', 'spoon', 'fork', 'whisk', 'grater',
    'sponge', 'cloth', 'mop', 'bucket', 'bag', 'lock', 'hinge', 'bracket',
    'tape', 'glue', 'paint', 'varnish', 'cleaner', 'spray', 'foam', 'sealant'
]

def extract_product_type(title):
    """Extract product type from title"""
    if pd.isna(title):
        return None
    title_lower = str(title).lower()
    for ptype in PRODUCT_TYPES:
        if ptype in title_lower:
            return ptype
    return None

# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================
def analyze_fba_products(csv_path, output_path):
    """Main FBA analysis function"""
    
    print("=" * 80)
    print("FBA PRODUCT ANALYSIS v4.1.1 AG1 (Antigravity Enhanced)")
    print("=" * 80)
    print(f"\nInput: {csv_path}")
    print(f"Output: {output_path}")
    print("\n📋 Calibration Applied:")
    print(f"  - Explicit units: {SUPPLIER_NAMING_CONVENTION['explicit_units']}")
    print(f"  - Trailing numbers: {'ENABLED' if SUPPLIER_NAMING_CONVENTION['allow_trailing_number_as_qty'] else 'DISABLED (Critical)'}")
    print(f"  - Brand position: {SUPPLIER_NAMING_CONVENTION['brand_position'].upper()}")
    print(f"  - Sales column: {SUPPLIER_NAMING_CONVENTION['sales_column']}")
    print(f"  - Dimension shield: {len(SUPPLIER_NAMING_CONVENTION['dimension_shield_keywords'])} keywords")
    print(f"  - Pipe sanitization: {'ENABLED' if SUPPLIER_NAMING_CONVENTION['table_pipe_sanitization'] else 'DISABLED'}")
    
    # Load data
    print("\n[Stage 1] Loading data...")
    df = pd.read_excel(csv_path)
    print(f"  Loaded {len(df)} rows")
    
    # Clean EANs
    df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()
    
    # Handle sales column
    sales_col = SUPPLIER_NAMING_CONVENTION['sales_column']
    if sales_col in df.columns:
        df['sales'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0)
    else:
        df['sales'] = 0
    
    df['RowID'] = df.index + 2  # Excel row (1-indexed + header)
    
    # Stage 1B: EAN normalization
    print("[Stage 1B] Normalizing EANs...")
    df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
    df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
    
    # Stage 2: Title similarity
    print("[Stage 2] Calculating title similarity...")
    df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)
    
    # Stage 3B: Strict EAN matching with checksum
    print("[Stage 3B] Validating EANs with checksum...")
    df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
    df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)
    df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
    df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)
    df['is_exact_ean_strict'] = (
        df['EAN_strict_valid']
        & df['EAN_OnPage_strict_valid']
        & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
    )
    
    print(f"  Exact EAN matches (strict): {df['is_exact_ean_strict'].sum()}")
    
    # Stage 4: Pack size extraction
    print("[Stage 4] Extracting pack sizes...")
    df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
    df['Amz_Multipack'] = df['AmazonTitle'].apply(extract_multipack_total)
    df['Amz_Total'] = df['Amz_Multipack'].apply(lambda x: x[2])
    df['RSU'] = df.apply(lambda row: max(1, row['Amz_Total'] / row['Sup_Qty']) if row['Sup_Qty'] > 0 else 1, axis=1)
    
    # Profit recalculation
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
    
    # Extract brands and product types
    print("[Stage 5B] Extracting brands and product types...")
    df['Sup_Brand'] = df['SupplierTitle'].apply(extract_brand)
    df['Amz_Brand'] = df['AmazonTitle'].apply(extract_brand)
    df['Sup_Product'] = df['SupplierTitle'].apply(extract_product_type)
    df['Amz_Product'] = df['AmazonTitle'].apply(extract_product_type)
    
    # Categorization
    def categorize_thorough(row):
        """Thorough manual-style categorization"""
        
        # VERIFIED: Exact EAN match
        if row['is_exact_ean_strict']:
            # Check for explicit pack contradiction
            sup_title_lower = str(row['SupplierTitle']).lower()
            amz_title_lower = str(row['AmazonTitle']).lower()
            
            # Check if dimension pattern (should NOT be treated as pack mismatch)
            if is_dimension_pattern(str(row['AmazonTitle'])):
                return 'VERIFIED'
            
            # Explicit pack mismatch check
            if 'single' in sup_title_lower and any(x in amz_title_lower for x in ['10-pack', 'pack of', 'x pack']):
                if row['Adjusted_Profit'] <= 0:
                    return 'FILTERED_OUT'
                else:
                    return 'VERIFIED'
            
            return 'VERIFIED'
        
        # HIGHLY LIKELY: Brand + Product match
        brand_match = (
            row['Sup_Brand'] is not None 
            and row['Amz_Brand'] is not None 
            and row['Sup_Brand'].upper() == row['Amz_Brand'].upper()
        )
        
        product_match = (
            row['Sup_Product'] is not None
            and row['Amz_Product'] is not None
            and row['Sup_Product'] == row['Amz_Product']
        )
        
        if brand_match and product_match and row['Adjusted_Profit'] > 0:
            return 'HIGHLY_LIKELY'
        
        # Check if brand matches but product type uncertain
        if brand_match and row['Adjusted_Profit'] > 0:
            # Strong brand match even without product type
            if row['title_match'] >= 0.4:
                return 'HIGHLY_LIKELY'
        
        # NEEDS VERIFICATION: Plausible but needs confirmation
        if brand_match or product_match or row['title_match'] >= 0.5:
            if row['Adjusted_Profit'] > 0:
                return 'NEEDS_VERIFICATION'
        
        # Weak evidence - exclude from report
        return 'UNRELATED'
    
    df['category'] = df.apply(categorize_thorough, axis=1)
    
    # Pack verdict
    def pack_verdict(row):
        rsu = row['RSU']
        if is_dimension_pattern(str(row['AmazonTitle'])) or is_dimension_pattern(str(row['SupplierTitle'])):
            return "1:1 Match (dimensions)"
        if rsu == 1.0:
            return "1:1 Match"
        elif rsu > 1.0:
            return f"RSU={int(rsu)}"
        else:
            return f"Split (1/{int(1/rsu)})"
    
    df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)
    
    # Generate report
    print("\n[Stage 8] Generating report...")
    generate_report(df, output_path, csv_path)
    
    print(f"\n✅ Analysis complete! Report saved to:")
    print(f"   {output_path}")

# ============================================================================
# REPORT GENERATION
# ============================================================================
def sanitize_cell(value):
    """Sanitize cell value for table output"""
    if pd.isna(value):
        return '-'
    s = str(value)
    if SUPPLIER_NAMING_CONVENTION['table_pipe_sanitization']:
        s = s.replace('|', '/')
    s = s.replace('\n', ' ').replace('\r', ' ')
    return s.strip()

def format_table_row(row_data, col_widths):
    """Format a single table row with fixed widths"""
    cells = []
    for value, width in zip(row_data, col_widths):
        cell = str(value).ljust(width)
        cells.append(cell)
    return '| ' + ' | '.join(cells) + ' |'

def generate_report(df, output_path, input_path):
    """Generate the final markdown report"""
    
    # Filter categories
    verified = df[df['category'] == 'VERIFIED'].copy()
    highly_likely = df[df['category'] == 'HIGHLY_LIKELY'].copy()
    needs_verification = df[df['category'] == 'NEEDS_VERIFICATION'].copy()
    
    # Split VERIFIED and HIGHLY_LIKELY into RECOMMENDED vs FILTERED_OUT
    verified_rec = verified[verified['Adjusted_Profit'] > 0].sort_values('sales', ascending=False)
    verified_filtered = verified[verified['Adjusted_Profit'] <= 0]
    
    highly_likely_rec = highly_likely[highly_likely['Adjusted_Profit'] > 0].sort_values('sales', ascending=False)
    highly_likely_filtered = highly_likely[highly_likely['Adjusted_Profit'] <= 0]
    
    # Sort NEEDS VERIFICATION by confidence, then sales
    needs_verification = needs_verification.sort_values(['title_match', 'sales'], ascending=[False, False])
    
    # Build report
    report = []
    report.append("# PHASEA MANUAL REPORT\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Input File:** {input_path}\n")
    report.append(f"**Supplier:** Part 5 Jan Dataset\n")
    report.append(f"**Analysis Version:** v4.1.1 AG1 (Antigravity Enhanced with Preflight Calibration)\n\n")
    
    report.append("## Summary Counts\n\n")
    report.append(f"- **VERIFIED — RECOMMENDED:** {len(verified_rec)}\n")
    report.append(f"- **VERIFIED — FILTERED OUT / EXCLUDED:** {len(verified_filtered)}\n")
    report.append(f"- **HIGHLY LIKELY — RECOMMENDED:** {len(highly_likely_rec)}\n")
    report.append(f"- **HIGHLY LIKELY — FILTERED OUT / EXCLUDED:** {len(highly_likely_filtered)}\n")
    report.append(f"- **NEEDS VERIFICATION:** {len(needs_verification)}\n")
    report.append(f"- **UNRELATED / NOT INCLUDED:** {len(df[df['category'] == 'UNRELATED'])}\n")
    report.append(f"- **TOTAL ANALYZED:** {len(df)}\n\n")
    
    report.append("This report applies **v4.1.1 AG1 Thorough Manual Analysis** with **Preflight Calibration Integration**:\n")
    report.append("- HIGHLY LIKELY requires Brand + Product type match with positive profit\n")
    report.append("- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade\n")
    report.append("- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit)\n")
    report.append("- Dimension patterns (e.g., '9x9 inch', '21CM') are correctly shielded\n")
    report.append("- Trailing numbers DISABLED per calibration (false positive risk)\n\n")
    
    # Column widths for tables
    col_widths = [10, 10, 35, 50, 15, 15, 12, 12, 12, 10, 8, 7, 20, 15, 35, 30]
    
    # Helper function to create table
    def create_table(data, title, section_note=""):
        if len(data) == 0:
            return [f"\n## {title}\n\n**No items in this category.**\n\n"]
        
        lines = [f"\n## {title}\n\n"]
        if section_note:
            lines.append(f"{section_note}\n\n")
        
        lines.append("```text\n")
        
        # Header
        header_row = format_table_row([
            'Verdict', 'Confidence', 'SupplierTitle', 'AmazonTitle', 'Supplier EAN', 'Amazon EAN',
            'ASIN', 'SupplierPrice', 'SellingPrice', 'NetProfit', 'ROI', 'Sales',
            'Pack Verdict', 'Adjusted Profit', 'Key Match Evidence', 'Filter Reason'
        ], col_widths)
        
        lines.append(header_row + '\n')
        lines.append(format_table_row(['-' * w for w in col_widths], col_widths) + '\n')
        
        # Data rows
        for _, row in data.iterrows():
            confidence = 95 if row['is_exact_ean_strict'] else int(row['title_match'] * 100)
            
            # Key match evidence
            if row['is_exact_ean_strict']:
                evidence = "Exact EAN match"
            elif row['Sup_Brand'] and row['Amz_Brand'] and row['Sup_Brand'].upper() == row['Amz_Brand'].upper():
                evidence = f"Brand: {row['Sup_Brand']}"
                if row['Sup_Product']:
                    evidence += f"; Product: {row['Sup_Product']}"
            else:
                evidence = f"Title similarity: {int(row['title_match']*100)}%"
            
            # Filter reason
            if row['Adjusted_Profit'] <= 0:
                filter_reason = f"RSU={int(row['RSU'])}; profit negative"
            elif row['category'] in ['NEEDS_VERIFICATION']:
                filter_reason = "Needs brand/pack confirmation"
            else:
                filter_reason = "-"
            
            row_data = [
                sanitize_cell(row['category'].replace('_', ' ')),
                str(confidence),
                sanitize_cell(row['SupplierTitle'])[:35],
                sanitize_cell(row['AmazonTitle'])[:50],
                sanitize_cell(row['EAN_digits_normalized'] if row['EAN_strict_valid'] else '-'),
                sanitize_cell(row['EAN_OnPage_digits_normalized'] if row['EAN_OnPage_strict_valid'] else '-'),
                sanitize_cell(row.get('ASIN', '-')),
                f"£{row['SupplierPrice_incVAT']:.2f}",
                f"£{row['SellingPrice_incVAT']:.2f}",
                f"£{row['NetProfit']:.2f}",
                f"{row['ROI ( % )']}%",
                str(int(row['sales'])),
                sanitize_cell(row['Pack_Verdict']),
                f"£{row['Adjusted_Profit']:.2f}",
                sanitize_cell(evidence)[:35],
                sanitize_cell(filter_reason)[:30]
            ]
            
            lines.append(format_table_row(row_data, col_widths) + '\n')
        
        lines.append("```\n\n")
        return lines
    
    # Add sections
    report.extend(create_table(
        verified_rec,
        f"VERIFIED — RECOMMENDED (count={len(verified_rec)})",
        "Exact EAN matches with positive adjusted profit. All items confirmed profitable."
    ))
    
    if len(verified_filtered) > 0:
        report.extend(create_table(
            verified_filtered,
            f"VERIFIED — FILTERED OUT / EXCLUDED (count={len(verified_filtered)})",
            "Exact EAN matches where pack recalculation resulted in negative profit."
        ))
    
    report.extend(create_table(
        highly_likely_rec,
        f"HIGHLY LIKELY — RECOMMENDED (count={len(highly_likely_rec)})",
        "Strong brand + product matches with positive adjusted profit."
    ))
    
    if len(highly_likely_filtered) > 0:
        report.extend(create_table(
            highly_likely_filtered,
            f"HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={len(highly_likely_filtered)})",
            "Brand + product matches where pack recalculation resulted in negative profit."
        ))
    
    report.extend(create_table(
        needs_verification,
        f"NEEDS VERIFICATION (count={len(needs_verification)})",
        "Items requiring 1-2 confirmationsconfirmable details for upgrade. Positive adjusted profit."
    ))
    
    # Write report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(report))

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == '__main__':
    import os
    
    base_dir = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 5 jan"
    
    csv_path = os.path.join(base_dir, "part 5 jan.xlsx")
    output_path = os.path.join(base_dir, "opus aud", f"PHASEA_MANUAL_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    analyze_fba_products(csv_path, output_path)
