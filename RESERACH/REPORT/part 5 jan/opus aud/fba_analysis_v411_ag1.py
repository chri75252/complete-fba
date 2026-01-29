"""
FBA Product Analysis v4.1.1 AG1 (Antigravity Enhanced)
Applies calibration-specific configuration for thorough manual analysis
"""

import pandas as pd
import re
from datetime import datetime
from difflib import SequenceMatcher

# ============================================================================
# CALIBRATION CONFIGURATION (from preflight analysis)
# ============================================================================
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pack', 'pcs', 'piece', 'pk'],
    "allow_trailing_number_as_qty": False,  # ⚠️ CRITICAL: DISABLED for this supplier
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "ft", "m"],
    "brand_position": "start",  # 93% confidence
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": False,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "power"],
    "table_pipe_sanitization": True
}

# Known wholesale brands (NOT IP risk)
WHOLESALE_BRANDS = {
    'TIDYZ', 'SOUDAL', 'AMTECH', 'ROLSON', 'DRAPER', 'FAIRY', 'DETTOL', 
    'MARIGOLD', 'DUNLOP', 'MASON CASH', 'PYREX', 'EVERBUILD', 'HARRIS', 
    'STATUS', 'EXTRASTAR', 'ROUNDUP', 'LITTLE TREES', 'EUROWRAP', 'RSW',
    'WORLD', 'DLUX', 'ARTIST', 'STARWASH', 'CHEF AID', 'TONKITA', 'ADORN',
    'FESTIVE', 'DEKTON', 'TALA', 'PROKLEEN', 'BLUE CANYON', 'PAN AROMA'
}

# True luxury/trademark brands (IP risk)
IP_RISK_BRANDS = {
    'JO MALONE', 'CHANEL', 'DIOR', 'GUCCI', 'LOUIS VUITTON', 'PRADA', 
    'HERMÈS', 'APPLE', 'SAMSUNG', 'SONY', 'MICROSOFT', 'NIKE', 'ADIDAS'
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clean_to_digits(x):
    """Extract only digits from barcode, handling scientific notation"""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

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
    total = sum(d * (3 if i % 2 == 1 else 1) for i, d in enumerate(body_rev, start=1))
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
    """Check if barcode is strictly valid (digits, length, checksum, no trailing zeros)"""
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r'0{6,}$', normalized):
        return False
    return gtin_checksum_ok(normalized)

def title_similarity(title1, title2):
    """Calculate title similarity ratio"""
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

def is_dimension_pattern(text):
    """Check if text contains dimension patterns (from calibration)"""
    if pd.isna(text):
        return False
    text = str(text).lower()
    
    # Dimension patterns from calibration
    dim_patterns = [
        r'\d+\s*x\s*\d+\s*(cm|mm|inch|in|ft|m)\b',  # "9 x 9 inch", "30 x 36 cm"
        r'\d+\s*(cm|mm|ml|ltr|l|kg|g|oz|inch|ft|m)\b',  # "300ml", "40cm"
    ]
    
    for pattern in dim_patterns:
        if re.search(pattern, text):
            return True
    return False

def extract_brand(title):
    """Extract brand name from title (calibration: 93% brand at start)"""
    if pd.isna(title):
        return None
    
    title_str = str(title).strip()
    # First word if uppercase (calibration shows 93% brand-first)
    first_word = title_str.split()[0] if title_str.split() else ''
    if first_word.isupper() and len(first_word) > 2:
        return first_word.upper()
    
    # Check for known brands anywhere in title
    title_upper = title_str.upper()
    for brand in WHOLESALE_BRANDS | IP_RISK_BRANDS:
        if brand in title_upper:
            return brand
    
    return None

def extract_quantity(title):
    """Extract pack size from title (respecting calibration config)"""
    if pd.isna(title):
        return 1.0
    
    title_lower = str(title).lower()
    
    # Check for dimension patterns first (shield from calibration)
    if is_dimension_pattern(title):
        # Has dimensions, be more cautious with pack extraction
        pass
    
    # Explicit unit patterns from calibration
    explicit_units = SUPPLIER_NAMING_CONVENTION['explicit_units']
    for unit in explicit_units:
        pattern = rf'(\d+)\s*{unit}\b'
        match = re.search(pattern, title_lower)
        if match:
            qty = float(match.group(1))
            if 1 < qty < 500:
                return qty
    
    # Standard pack patterns
    pack_patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)',
    ]
    
    for pat in pack_patterns:
        match = re.search(pat, title_lower)
        if match:
            qty = float(match.group(1))
            if 1 < qty < 500:
                return qty
    
    # Trailing number - DISABLED for this supplier per calibration
    if SUPPLIER_NAMING_CONVENTION['allow_trailing_number_as_qty']:
        trail_match = re.search(r'\s+(\d+)$', title_lower)
        if trail_match:
            qty = float(trail_match.group(1))
            if 1 < qty < 500:
                return qty
    
    return 1.0

def extract_multipack_total(title):
    """Extract total items from multipack patterns like '(4 x 50)'"""
    if pd.isna(title):
        return (1, 1, 1)
    
    title_lower = str(title).lower()
    
    # Check for dimension patterns first
    if is_dimension_pattern(title):
        # Don't treat dimensions as multipacks
        qty = extract_quantity(title)
        return (1, int(qty), int(qty))
    
    # Pattern for "N x M" multipacks (e.g., "4 x 50", "3 x 500ml")
    multipack_pattern = r'\(?\s*(\d+)\s*x\s*(\d+)\s*\)?'
    match = re.search(multipack_pattern, title_lower)
    if match:
        outer = int(match.group(1))
        inner = int(match.group(2))
        # Avoid dimension patterns (small numbers with units nearby)
        if outer <= 10 and inner > 10:
            return (outer, inner, outer * inner)
    
    # Fallback to simple quantity
    qty = extract_quantity(title)
    return (1, int(qty), int(qty))

def sanitize_for_table(text):
    """Sanitize text for markdown table (pipe chars, newlines)"""
    if pd.isna(text):
        return "-"
    text = str(text)
    if SUPPLIER_NAMING_CONVENTION['table_pipe_sanitization']:
        text = text.replace('|', '/')
    text = text.replace('\n', ' ').replace('\r', ' ')
    return text.strip()

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_fba_report(input_path, output_dir):
    """Execute complete FBA analysis with calibration config"""
    
    print("\n" + "="*80)
    print("FBA PRODUCT ANALYSIS v4.1.1 AG1 (Antigravity Enhanced)")
    print("="*80)
    print(f"\nInput: {input_path}")
    print(f"Output: {output_dir}")
    print(f"\nCalibration Applied:")
    print(f"  - Brand Position: {SUPPLIER_NAMING_CONVENTION['brand_position']}")
    print(f"  - Trailing Numbers: {SUPPLIER_NAMING_CONVENTION['allow_trailing_number_as_qty']}")
    print(f"  - Sales Column: {SUPPLIER_NAMING_CONVENTION['sales_column']}")
    print(f"  - Dimension Shield: {len(SUPPLIER_NAMING_CONVENTION['dimension_shield_keywords'])} keywords")
    
    # STAGE 1: Load and clean data
    print("\n[STAGE 1] Loading data...")
    df = pd.read_excel(input_path)
    
    print(f"Loaded {len(df)} rows")
    print(f"Columns: {', '.join(df.columns.tolist())}")
    
    # Clean EANs
    df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()
    
    # Handle sales column (from calibration)
    sales_col = SUPPLIER_NAMING_CONVENTION['sales_column']
    if sales_col in df.columns:
        df['sales'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0)
    else:
        df['sales'] = 0
    
    df['RowID'] = df.index + 2  # Excel row (1-indexed + header)
    
    # STAGE 1B: EAN normalization
    print("\n[STAGE 1B] Normalizing EANs...")
    df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
    df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
    
    # STAGE 2: Title similarity
    print("\n[STAGE 2] Calculating title similarity...")
    df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)
    
    # STAGE 3B: Strict EAN matching with checksum
    print("\n[STAGE 3B] Strict EAN validation...")
    df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
    df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)
    
    df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
    df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)
    
    df['is_exact_ean_strict'] = (
        df['EAN_strict_valid']
        & df['EAN_OnPage_strict_valid']
        & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
    )
    
    exact_ean_count = df['is_exact_ean_strict'].sum()
    print(f"Exact EAN matches (strict): {exact_ean_count}")
    
    # STAGE 4: Pack size extraction
    print("\n[STAGE 4] Extracting pack sizes...")
    df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
    df['Amz_Multipack'] = df['AmazonTitle'].apply(extract_multipack_total)
    df['Amz_Total'] = df['Amz_Multipack'].apply(lambda x: x[2])
    
    # Calculate RSU
    df['RSU'] = df.apply(
        lambda row: max(1, row['Amz_Total'] / row['Sup_Qty']) if row['Sup_Qty'] > 0 else 1, 
        axis=1
    )
    
    # Recalculate profit
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
    
    # Extract brands
    df['Sup_Brand'] = df['SupplierTitle'].apply(extract_brand)
    df['Amz_Brand'] = df['AmazonTitle'].apply(extract_brand)
    df['Brand_Match'] = df.apply(
        lambda row: row['Sup_Brand'] == row['Amz_Brand'] if row['Sup_Brand'] and row['Amz_Brand'] else False,
        axis=1
    )
    
    # STAGE 5B: Thorough Manual Analysis
    print("\n[STAGE 5B] Conducting thorough manual analysis...")
    
    verified_recommended = []
    verified_excluded = []
    highly_likely_recommended = []
    highly_likely_excluded = []
    needs_verification = []
    
    for idx, row in df.iterrows():
        # Skip if clearly unrelated (very low title match and no EAN)
        if not row['is_exact_ean_strict'] and row['title_match'] < 0.20:
            continue
        
        supplier_title = str(row['SupplierTitle'])
        amazon_title = str(row['AmazonTitle'])
        
        # Categorize
        category = None
        confidence = 50
        match_evidence = []
        filter_reason = "-"
        
        # VERIFIED (Exact EAN)
        if row['is_exact_ean_strict']:
            category = 'VERIFIED'
            confidence = 95
            match_evidence.append("Exact EAN match")
            
            # Check for explicit pack contradiction
            if row['RSU'] > 1:
                if row['Adjusted_Profit'] <= 0:
                    category = 'VERIFIED_EXCLUDED'
                    filter_reason = f"RSU={int(row['RSU'])}; adjusted profit is negative"
                else:
                    match_evidence.append(f"RSU={int(row['RSU'])} (profitable)")
            
            # Check for dimension patterns (not pack contradiction)
            if is_dimension_pattern(supplier_title) or is_dimension_pattern(amazon_title):
                match_evidence.append("Dimensions detected (not pack issue)")
        
        # HIGHLY LIKELY (Brand + Product match)
        elif row['Brand_Match'] and row['Adjusted_Profit'] > 0:
            category = 'HIGHLY_LIKELY'
            confidence = 85
            match_evidence.append(f"Brand: {row['Sup_Brand']}")
            
            # Check for shared product type
            sup_lower = supplier_title.lower()
            amz_lower = amazon_title.lower()
            
            # Common product types
            product_types = ['hammer', 'trowel', 'brush', 'bowl', 'mirror', 'dish', 
                           'candle', 'holder', 'rack', 'basket', 'bin', 'mat']
            for ptype in product_types:
                if ptype in sup_lower and ptype in amz_lower:
                    match_evidence.append(f"Product: {ptype}")
                    break
            
            if row['RSU'] > 1 and row['Adjusted_Profit'] > 0:
                match_evidence.append(f"RSU={int(row['RSU'])} (profitable)")
            elif row['RSU'] > 1 and row['Adjusted_Profit'] <= 0:
                category = 'HIGHLY_LIKELY_EXCLUDED'
                filter_reason = f"RSU={int(row['RSU'])}; adjusted profit is negative"
        
        # NEEDS VERIFICATION
        elif row['title_match'] >= 0.30 and row['Adjusted_Profit'] > 0:
            # Check if brand appears in one title but not the other
            if row['Sup_Brand'] or row['Amz_Brand']:
                category = 'NEEDS_VERIFICATION'
                confidence = 60
                if row['Sup_Brand']:
                    match_evidence.append(f"Supplier brand: {row['Sup_Brand']}")
                if row['Amz_Brand']:
                    match_evidence.append(f"Amazon brand: {row['Amz_Brand']}")
                filter_reason = "Brand verification needed"
        
        # Assemble row data
        if category:
            row_data = {
                'Verdict': category,
                'Confidence': confidence,
                'SupplierTitle': sanitize_for_table(supplier_title),
                'AmazonTitle': sanitize_for_table(amazon_title),
                'Supplier_EAN': row['EAN_digits_normalized'] if row['EAN_strict_valid'] else '-',
                'Amazon_EAN': row['EAN_OnPage_digits_normalized'] if row['EAN_OnPage_strict_valid'] else '-',
                'ASIN': sanitize_for_table(row.get('ASIN', '-')),
                'SupplierPrice': f"£{row['SupplierPrice_incVAT']:.2f}" if pd.notna(row['SupplierPrice_incVAT']) else '-',
                'SellingPrice': f"£{row['SellingPrice_incVAT']:.2f}" if pd.notna(row['SellingPrice_incVAT']) else '-',
                'NetProfit': f"£{row['NetProfit']:.2f}" if pd.notna(row['NetProfit']) else '-',
                'ROI': f"{row['ROI ( % )']}%" if pd.notna(row.get('ROI ( % )')) else '-',
                'Sales': int(row['sales']),
                'Pack_Verdict': f"RSU={int(row['RSU'])}" if row['RSU'] > 1 else "1:1",
                'Adjusted_Profit': f"£{row['Adjusted_Profit']:.2f}",
                'Match_Evidence': "; ".join(match_evidence),
                'Filter_Reason': filter_reason,
                'RowID': int(row['RowID'])
            }
            
            # Route to appropriate list
            if category == 'VERIFIED':
                verified_recommended.append(row_data)
            elif category == 'VERIFIED_EXCLUDED':
                verified_excluded.append(row_data)
            elif category == 'HIGHLY_LIKELY':
                highly_likely_recommended.append(row_data)
            elif category == 'HIGHLY_LIKELY_EXCLUDED':
                highly_likely_excluded.append(row_data)
            elif category == 'NEEDS_VERIFICATION':
                needs_verification.append(row_data)
    
    # Sort lists
    verified_recommended.sort(key=lambda x: x['Sales'], reverse=True)
    highly_likely_recommended.sort(key=lambda x: (x['Confidence'], x['Sales']), reverse=True)
    needs_verification.sort(key=lambda x: (x['Confidence'], x['Sales']), reverse=True)
    
    # Generate report
    print("\n[REPORT] Generating markdown report...")
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    report_path = f"{output_dir}/PHASEA_MANUAL_REPORT_{timestamp}.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# PHASEA MANUAL REPORT\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Input File:** part 5 jan.xlsx\n")
        f.write(f"**Total Rows Analyzed:** {len(df)}\n\n")
        
        f.write("## Summary Counts\n\n")
        f.write(f"- **VERIFIED — RECOMMENDED:** {len(verified_recommended)}\n")
        f.write(f"- **VERIFIED — AUDITED OUT / EXCLUDED:** {len(verified_excluded)}\n")
        f.write(f"- **HIGHLY LIKELY — RECOMMENDED:** {len(highly_likely_recommended)}\n")
        f.write(f"- **HIGHLY LIKELY — AUDITED OUT / EXCLUDED:** {len(highly_likely_excluded)}\n")
        f.write(f"- **NEEDS VERIFICATION:** {len(needs_verification)}\n\n")
        
        f.write("**Analysis Method:** v4.1.1 AG1 with calibration-specific configuration\n")
        f.write("- Trailing number detection: DISABLED (calibration warning)\n")
        f.write("- Dimension shielding: ENABLED (prevents false pack calculations)\n")
        f.write("- Brand position: START (93% confidence)\n\n")
        
        # Helper function to write table
        def write_table(items, section_name):
            if not items:
                f.write(f"## {section_name}\n\n")
                f.write("*No items in this category*\n\n")
                return
            
            f.write(f"## {section_name} (count={len(items)})\n\n")
            f.write("```text\n")
            
            # Calculate column widths
            headers = ['Verdict', 'Conf', 'SupplierTitle', 'AmazonTitle', 'Supplier EAN', 
                      'Amazon EAN', 'ASIN', 'SupPrice', 'SellPrice', 'NetProfit', 'ROI', 
                      'Sales', 'Pack', 'AdjProfit', 'Match Evidence', 'Filter Reason']
            
            widths = [max(len(str(headers[i])), max([len(str(item[k])) for item in items])) 
                     for i, k in enumerate(['Verdict', 'Confidence', 'SupplierTitle', 'AmazonTitle',
                                           'Supplier_EAN', 'Amazon_EAN', 'ASIN', 'SupplierPrice',
                                           'SellingPrice', 'NetProfit', 'ROI', 'Sales', 'Pack_Verdict',
                                           'Adjusted_Profit', 'Match_Evidence', 'Filter_Reason'])]
            
            # Write header
            header_row = "| " + " | ".join([headers[i].ljust(widths[i]) for i in range(len(headers))]) + " |"
            f.write(header_row + "\n")
            f.write("|" + "|".join(["-" * (widths[i] + 2) for i in range(len(headers))]) + "|\n")
            
            # Write rows
            for item in items[:50]:  # Limit to first 50 for readability
                row_values = [
                    str(item['Verdict']).ljust(widths[0]),
                    str(item['Confidence']).ljust(widths[1]),
                    str(item['SupplierTitle'])[:40].ljust(widths[2]),
                    str(item['AmazonTitle'])[:40].ljust(widths[3]),
                    str(item['Supplier_EAN']).ljust(widths[4]),
                    str(item['Amazon_EAN']).ljust(widths[5]),
                    str(item['ASIN']).ljust(widths[6]),
                    str(item['SupplierPrice']).ljust(widths[7]),
                    str(item['SellingPrice']).ljust(widths[8]),
                    str(item['NetProfit']).ljust(widths[9]),
                    str(item['ROI']).ljust(widths[10]),
                    str(item['Sales']).ljust(widths[11]),
                    str(item['Pack_Verdict']).ljust(widths[12]),
                    str(item['Adjusted_Profit']).ljust(widths[13]),
                    str(item['Match_Evidence'])[:30].ljust(widths[14]),
                    str(item['Filter_Reason'])[:30].ljust(widths[15])
                ]
                f.write("| " + " | ".join(row_values) + " |\n")
            
            f.write("```\n\n")
        
        # Write each section
        write_table(verified_recommended, "VERIFIED — RECOMMENDED")
        write_table(verified_excluded, "VERIFIED — AUDITED OUT / EXCLUDED")
        write_table(highly_likely_recommended, "HIGHLY LIKELY — RECOMMENDED")
        write_table(highly_likely_excluded, "HIGHLY LIKELY — AUDITED OUT / EXCLUDED")
        write_table(needs_verification, "NEEDS VERIFICATION")
        
        f.write("---\n\n")
        f.write("*Report generated with FBA Analysis v4.1.1 AG1 (Antigravity Enhanced)*\n")
    
    print(f"\n✅ Report saved: {report_path}")
    print(f"\nSummary:")
    print(f"  - VERIFIED RECOMMENDED: {len(verified_recommended)}")
    print(f"  - VERIFIED EXCLUDED: {len(verified_excluded)}")
    print(f"  - HIGHLY LIKELY RECOMMENDED: {len(highly_likely_recommended)}")
    print(f"  - HIGHLY LIKELY EXCLUDED: {len(highly_likely_excluded)}")
    print(f"  - NEEDS VERIFICATION: {len(needs_verification)}")
    
    return report_path

# ============================================================================
# EXECUTE
# ============================================================================

if __name__ == "__main__":
    input_file = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 5 jan\part 5 jan.xlsx"
    output_directory = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 5 jan\opus aud"
    
    analyze_fba_report(input_file, output_directory)
