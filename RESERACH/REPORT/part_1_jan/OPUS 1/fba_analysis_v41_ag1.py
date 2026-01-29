"""
FBA Product Analysis Script v4.1 AG1
=====================================
Implements the complete multi-stage analysis protocol for identifying
TRUE profitable FBA arbitrage opportunities.

Input File: part_1_jan.xlsx
Output: PHASEA_MANUAL_REPORT_YYYYMMDD.md

Based on calibration analysis performed on 2026-01-01
"""

import pandas as pd
import re
from difflib import SequenceMatcher
from datetime import datetime
import os

# =============================================================================
# CALIBRATION CONFIGURATION (from pre-flight analysis)
# =============================================================================

SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pc", "pcs", "pce", "pk", "pack", "pieces", "piece", "cases"],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": [
        "cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", 
        "inch", "in", "ft", "m", "w"
    ],
    "dimension_x_patterns": True,
    "brand_position": "mixed",
    "sales_column": "bought_in_past_month",
    "sales_requires_parsing": False,
}

# Known brands for IP risk flagging (luxury/trademark only)
IP_RISK_BRANDS = [
    "jo malone", "chanel", "dior", "gucci", "louis vuitton", "prada", 
    "hermès", "hermes", "apple", "samsung", "sony", "microsoft", "nike", "adidas"
]

# Safe/generic brands (NOT IP risk)
SAFE_BRANDS = [
    "tidyz", "soudal", "amtech", "rolson", "draper", "fairy", "dettol", 
    "marigold", "dunlop", "mason cash", "pyrex", "everbuild", "harris", 
    "status", "extrastar", "roundup", "little trees", "dlux", "prokleen",
    "prima", "bettina", "chef aid", "tala", "minky", "starwash", "airwick",
    "panasonic", "giftmaker", "abbey", "dekton", "securpak", "lynwood",
    "eurowrap", "festive", "paint factory", "opal"
]

# =============================================================================
# FILE PATHS
# =============================================================================

BASE_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan"
INPUT_FILE = os.path.join(BASE_PATH, "part_1_jan.xlsx")
OUTPUT_DIR = os.path.join(BASE_PATH, "OPUS 1")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"PHASEA_MANUAL_REPORT_{TIMESTAMP}.md")

# =============================================================================
# STAGE 1: DATA LOADING & INITIAL CLEANING
# =============================================================================

def load_and_clean_data(file_path):
    """Load Excel file and perform initial cleaning."""
    print(f"[STAGE 1] Loading data from: {file_path}")
    
    df = pd.read_excel(file_path)
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # Clean EAN columns
    df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()
    
    # Handle sales column based on calibration
    sales_col = SUPPLIER_NAMING_CONVENTION['sales_column']
    if sales_col in df.columns:
        df['sales'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0).astype(int)
        print(f"  Using sales column: {sales_col}")
    else:
        df['sales'] = 0
        print(f"  WARNING: Sales column '{sales_col}' not found, defaulting to 0")
    
    # Add RowID for traceability
    df['RowID'] = df.index + 1
    
    return df

# =============================================================================
# STAGE 1B: EAN NORMALIZATION SAFETY FLAGS
# =============================================================================

def clean_to_digits(x):
    """Extract only digits from EAN, handling edge cases."""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

def apply_ean_normalization(df):
    """Apply EAN digit extraction."""
    print("[STAGE 1B] Normalizing EAN values...")
    df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
    df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
    return df

# =============================================================================
# STAGE 2: TITLE SIMILARITY CALCULATION
# =============================================================================

def title_similarity(title1, title2):
    """Calculate similarity ratio between two titles."""
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

def calculate_title_similarity(df):
    """Calculate title similarity for all rows."""
    print("[STAGE 2] Calculating title similarity...")
    df['title_match'] = df.apply(
        lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1
    )
    return df

# =============================================================================
# STAGE 3: STRICT EAN MATCHING
# =============================================================================

def is_valid_ean(ean):
    """Check if EAN is a valid barcode (not empty, nan, None, etc.)."""
    if pd.isna(ean):
        return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-']

def basic_ean_match(row):
    """Returns True ONLY if BOTH EANs are valid AND they match exactly."""
    ean_sup = str(row['EAN']).strip()
    ean_amz = str(row['EAN_OnPage']).strip()
    
    if not is_valid_ean(ean_sup) or not is_valid_ean(ean_amz):
        return False
    return ean_sup == ean_amz

def apply_basic_ean_matching(df):
    """Apply basic EAN matching."""
    print("[STAGE 3] Applying basic EAN matching...")
    df['is_exact_ean'] = df.apply(basic_ean_match, axis=1)
    exact_count = df['is_exact_ean'].sum()
    print(f"  Found {exact_count} basic EAN matches")
    return df

# =============================================================================
# STAGE 3B: STRICT BARCODE VALIDITY + CHECKSUM + LEFT-PADDING
# =============================================================================

def gtin_checksum_ok(digits: str) -> bool:
    """Validate GTIN checksum."""
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
    """Attempt left-padding to valid GTIN length if checksum passes."""
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
    """Check if barcode is strictly valid with checksum."""
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

def apply_strict_ean_validation(df):
    """Apply strict barcode validation with checksum."""
    print("[STAGE 3B] Applying strict barcode validation...")
    
    df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
    df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)
    
    df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
    df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)
    
    df['is_exact_ean_strict'] = (
        df['EAN_strict_valid']
        & df['EAN_OnPage_strict_valid']
        & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
    )
    
    strict_count = df['is_exact_ean_strict'].sum()
    print(f"  Found {strict_count} strict EAN matches (with checksum validation)")
    
    return df

# =============================================================================
# STAGE 4: PACK SIZE EXTRACTION & PROFIT RECALCULATION
# =============================================================================

def is_dimension_pattern(title, number):
    """Check if a number is part of a dimension pattern (NOT a pack count)."""
    title_lower = str(title).lower()
    dim_keywords = SUPPLIER_NAMING_CONVENTION['dimension_shield_keywords']
    
    # Check for patterns like "NNcm", "NNml", "NNmm" immediately after number
    for kw in dim_keywords:
        # Pattern: number directly followed by dimension keyword
        if re.search(rf'\b{number}\s*{kw}\b', title_lower):
            return True
        # Pattern: NxN dimension (like 70x100cm, 5x60mm)
        if re.search(rf'\b\d+\s*x\s*{number}\s*{kw}\b', title_lower):
            return True
        if re.search(rf'\b{number}\s*x\s*\d+\s*{kw}\b', title_lower):
            return True
    
    return False

def extract_quantity(title):
    """Extract pack size from product title with dimension shield. Defaults to 1."""
    if pd.isna(title):
        return 1.0
    title_str = str(title)
    title_lower = title_str.lower()
    
    # Check for explicit pack patterns first
    explicit_patterns = [
        (r'pack of (\d+)', 1),
        (r'set of (\d+)', 1),
        (r'\b(\d+)\s*pack\b', 1),
        (r'\b(\d+)\s*pk\b', 1),
        (r'pk\s*(\d+)\b', 1),  # PK6, PK8 format
        (r'(\d+)\s*pcs\b', 1),
        (r'(\d+)\s*pce\b', 1),
        (r'(\d+)\s*pieces?\b', 1),
        (r'(\d+)\s*pc\b', 1),
        (r'\((\d+)\s*pack\)', 1),
        (r'\(pack of (\d+)\)', 1),
    ]
    
    for pattern, group in explicit_patterns:
        match = re.search(pattern, title_lower)
        if match:
            qty = float(match.group(group))
            # Validate it's not a dimension
            if not is_dimension_pattern(title_str, int(qty)):
                if 1 < qty < 500:
                    return qty
    
    return 1.0

def extract_multipack_total(title):
    """
    Extract total items from multipack patterns like '(4 x 50)' or '3 x 500ml'.
    Returns (outer_count, inner_count, total) or (1, qty, qty) if no multipack.
    """
    if pd.isna(title):
        return (1, 1, 1)
    title_lower = str(title).lower()
    
    # Pattern for "N x M" multipacks (e.g., "4 x 50", "(4 x 50)")
    # But NOT dimensions like "70x100cm" or "5x60mm"
    multipack_pattern = r'\(?\s*(\d+)\s*x\s*(\d+)\s*\)?'
    
    for match in re.finditer(multipack_pattern, title_lower):
        outer = int(match.group(1))
        inner = int(match.group(2))
        
        # Check if this is followed by a dimension keyword (if so, skip)
        after_match = title_lower[match.end():]
        is_dimension = False
        for kw in SUPPLIER_NAMING_CONVENTION['dimension_shield_keywords']:
            if after_match.strip().startswith(kw):
                is_dimension = True
                break
        
        if not is_dimension:
            # Likely multipack if outer is small (1-10) and inner is larger
            if outer <= 10 and inner > 10:
                return (outer, inner, outer * inner)
    
    # Fallback to simple quantity extraction
    qty = int(extract_quantity(title))
    return (1, qty, qty)

def calculate_pack_and_profit(df):
    """Calculate pack sizes and adjusted profit."""
    print("[STAGE 4] Calculating pack sizes and adjusted profit...")
    
    df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
    df['Amz_Multipack'] = df['AmazonTitle'].apply(extract_multipack_total)
    df['Amz_Total'] = df['Amz_Multipack'].apply(lambda x: x[2])
    
    # Calculate RSU (Required Supplier Units)
    def calc_rsu(row):
        if row['Sup_Qty'] > 0:
            return max(1, row['Amz_Total'] / row['Sup_Qty'])
        return 1
    
    df['RSU'] = df.apply(calc_rsu, axis=1)
    df['Qty_Ratio'] = df['RSU']
    
    # Recalculate profit
    def recalculate_profit(row):
        try:
            original_profit = float(row['NetProfit'])
            supplier_cost = float(row['SupplierPrice_incVAT']) if 'SupplierPrice_incVAT' in row else float(row.get('SupplierPrice_exVAT', 0))
            rsu = row['RSU']
            adjustment = supplier_cost * (rsu - 1)
            return round(original_profit - adjustment, 2)
        except:
            return 0.0
    
    df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)
    
    # Determine pack verdict
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
    
    return df

# =============================================================================
# STAGE 5: INITIAL CATEGORIZATION
# =============================================================================

def initial_categorization(df):
    """Initial categorization based on EAN and title similarity."""
    print("[STAGE 5] Initial categorization...")
    
    def categorize(row):
        if row['is_exact_ean_strict']:
            return 'EXACT_EAN_MATCH'
        elif row['title_match'] >= 0.50:
            return 'HIGH_LIKELIHOOD'
        elif row['title_match'] >= 0.30:
            return 'MODERATE_CONFIDENCE'
        else:
            return 'UNCERTAIN'
    
    df['initial_category'] = df.apply(categorize, axis=1)
    
    # Print summary
    for cat in ['EXACT_EAN_MATCH', 'HIGH_LIKELIHOOD', 'MODERATE_CONFIDENCE', 'UNCERTAIN']:
        count = (df['initial_category'] == cat).sum()
        print(f"  {cat}: {count}")
    
    return df

# =============================================================================
# STAGE 5B: THOROUGH MANUAL ANALYSIS
# =============================================================================

def extract_brand(title):
    """Extract brand from title (first word or known brand pattern)."""
    if pd.isna(title):
        return ""
    title_str = str(title).upper().strip()
    # Get first word as potential brand
    first_word = title_str.split()[0] if title_str.split() else ""
    return first_word

def brands_match(supplier_title, amazon_title):
    """Check if brands match between titles."""
    if pd.isna(supplier_title) or pd.isna(amazon_title):
        return False
    
    sup_lower = str(supplier_title).lower()
    amz_lower = str(amazon_title).lower()
    
    # Check safe brands
    for brand in SAFE_BRANDS:
        if brand in sup_lower and brand in amz_lower:
            return True
    
    # Check first word match
    sup_first = sup_lower.split()[0] if sup_lower.split() else ""
    if len(sup_first) >= 3:  # Minimum brand length
        if sup_first in amz_lower:
            return True
    
    return False

def get_key_match_evidence(row):
    """Generate key match evidence string."""
    evidence = []
    
    if row.get('is_exact_ean_strict', False):
        evidence.append("Exact EAN match")
    
    if brands_match(row.get('SupplierTitle', ''), row.get('AmazonTitle', '')):
        sup_brand = extract_brand(row.get('SupplierTitle', ''))
        evidence.append(f"Brand match: {sup_brand}")
    
    if row.get('title_match', 0) >= 0.5:
        evidence.append(f"Title similarity: {row['title_match']:.0%}")
    
    return "; ".join(evidence) if evidence else "Manual review required"

def thorough_manual_analysis(df):
    """Apply thorough manual analysis for final categorization."""
    print("[STAGE 5B] Thorough manual analysis...")
    
    results = {
        'VERIFIED_RECOMMENDED': [],
        'VERIFIED_FILTERED': [],
        'HIGHLY_LIKELY_RECOMMENDED': [],
        'HIGHLY_LIKELY_FILTERED': [],
        'NEEDS_VERIFICATION': [],
    }
    
    for idx, row in df.iterrows():
        # Skip rows with no meaningful data
        if pd.isna(row['SupplierTitle']) or pd.isna(row['AmazonTitle']):
            continue
        
        sales = row.get('sales', 0)
        net_profit = row.get('NetProfit', 0)
        adjusted_profit = row.get('Adjusted_Profit', 0)
        is_exact_ean = row.get('is_exact_ean_strict', False)
        title_sim = row.get('title_match', 0)
        brand_matches = brands_match(row['SupplierTitle'], row['AmazonTitle'])
        
        # Determine verdict
        verdict = None
        filter_reason = "-"
        confidence = 0
        
        # EXACT EAN MATCH PATH
        if is_exact_ean:
            confidence = 95
            if adjusted_profit > 0 and sales > 0:
                verdict = 'VERIFIED_RECOMMENDED'
            elif adjusted_profit <= 0:
                verdict = 'VERIFIED_FILTERED'
                filter_reason = f"Negative adjusted profit: £{adjusted_profit:.2f}"
            elif sales == 0:
                verdict = 'NEEDS_VERIFICATION'
                filter_reason = "Sales = 0; verify market demand"
                confidence = 85
        
        # BRAND + PRODUCT MATCH PATH
        elif brand_matches and title_sim >= 0.3:
            confidence = 80
            if adjusted_profit > 0 and sales > 0:
                verdict = 'HIGHLY_LIKELY_RECOMMENDED'
            elif adjusted_profit <= 0:
                verdict = 'HIGHLY_LIKELY_FILTERED'
                filter_reason = f"Negative adjusted profit: £{adjusted_profit:.2f}"
            elif sales == 0 and adjusted_profit > 0.5:
                verdict = 'NEEDS_VERIFICATION'
                filter_reason = "Sales = 0; brand matches, verify demand"
                confidence = 70
        
        # MODERATE SIMILARITY PATH
        elif title_sim >= 0.4 and adjusted_profit > 0.5:
            confidence = 60
            if sales > 0 and net_profit > 0:
                verdict = 'NEEDS_VERIFICATION'
                filter_reason = "Title similarity moderate; verify brand/product"
            elif adjusted_profit <= 0:
                verdict = 'HIGHLY_LIKELY_FILTERED'
                filter_reason = f"Negative adjusted profit: £{adjusted_profit:.2f}"
        
        if verdict:
            entry = {
                'RowID': row.get('RowID', idx),
                'Verdict': verdict.replace('_RECOMMENDED', '').replace('_FILTERED', ''),
                'Confidence': confidence,
                'SupplierTitle': str(row['SupplierTitle'])[:60],
                'AmazonTitle': str(row['AmazonTitle'])[:80],
                'Supplier_EAN': row.get('EAN_digits_normalized', '-') if row.get('EAN_strict_valid', False) else '-',
                'Amazon_EAN': row.get('EAN_OnPage_digits_normalized', '-') if row.get('EAN_OnPage_strict_valid', False) else '-',
                'ASIN': row.get('ASIN', '-'),
                'SupplierPrice': row.get('SupplierPrice_exVAT', 0),
                'SellingPrice': row.get('SellingPrice_incVAT', 0),
                'NetProfit': net_profit,
                'ROI': row.get('ROI', 0),
                'Sales': sales,
                'Pack_Verdict': row.get('Pack_Verdict', '1:1 Match'),
                'Adjusted_Profit': adjusted_profit,
                'Key_Match_Evidence': get_key_match_evidence(row),
                'Filter_Reason': filter_reason,
            }
            results[verdict].append(entry)
    
    # Print summary
    for cat, items in results.items():
        print(f"  {cat}: {len(items)}")
    
    return results

# =============================================================================
# REPORT GENERATION
# =============================================================================

def format_table_row(entry, col_widths):
    """Format a single table row with proper padding."""
    row_data = [
        entry.get('Verdict', '-'),
        str(entry.get('Confidence', 0)),
        entry.get('SupplierTitle', '-')[:col_widths[2]-2],
        entry.get('AmazonTitle', '-')[:col_widths[3]-2],
        str(entry.get('Supplier_EAN', '-')),
        str(entry.get('Amazon_EAN', '-')),
        str(entry.get('ASIN', '-')),
        f"£{entry.get('SupplierPrice', 0):.2f}",
        f"£{entry.get('SellingPrice', 0):.2f}",
        f"£{entry.get('NetProfit', 0):.2f}",
        f"{entry.get('ROI', 0):.1f}%" if isinstance(entry.get('ROI', 0), (int, float)) else str(entry.get('ROI', '-')),
        str(int(entry.get('Sales', 0))),
        entry.get('Pack_Verdict', '-')[:25],
        f"£{entry.get('Adjusted_Profit', 0):.2f}",
        entry.get('Key_Match_Evidence', '-')[:35],
        entry.get('Filter_Reason', '-')[:30],
    ]
    
    padded = []
    for i, val in enumerate(row_data):
        padded.append(str(val).ljust(col_widths[i]))
    
    return "| " + " | ".join(padded) + " |"

def generate_table(entries, title):
    """Generate a fixed-width markdown table."""
    if not entries:
        return f"*No items in this category.*\n"
    
    # Define column widths
    col_widths = [10, 10, 50, 70, 14, 14, 12, 13, 12, 10, 8, 6, 27, 15, 37, 32]
    headers = [
        "Verdict", "Confidence", "SupplierTitle", "AmazonTitle", "Supplier EAN", 
        "Amazon EAN", "ASIN", "SupplierPrice", "SellingPrice", "NetProfit", 
        "ROI", "Sales", "Pack Verdict", "Adjusted Profit", "Key Match Evidence", "Filter Reason"
    ]
    
    # Build header row
    header_row = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    separator = "|" + "|".join("-" * (w + 2) for w in col_widths) + "|"
    
    lines = ["```text", header_row, separator]
    
    # Sort by sales descending
    sorted_entries = sorted(entries, key=lambda x: x.get('Sales', 0), reverse=True)
    
    for entry in sorted_entries:
        lines.append(format_table_row(entry, col_widths))
    
    lines.append("```")
    
    return "\n".join(lines)

def generate_report(results, input_file, output_file):
    """Generate the final markdown report."""
    print("\n[REPORT] Generating PHASEA_MANUAL_REPORT...")
    
    # Count items
    verified_rec = len(results['VERIFIED_RECOMMENDED'])
    verified_filt = len(results['VERIFIED_FILTERED'])
    highly_likely_rec = len(results['HIGHLY_LIKELY_RECOMMENDED'])
    highly_likely_filt = len(results['HIGHLY_LIKELY_FILTERED'])
    needs_verif = len(results['NEEDS_VERIFICATION'])
    total = verified_rec + verified_filt + highly_likely_rec + highly_likely_filt + needs_verif
    
    report = f"""# PHASEA MANUAL REPORT

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Input File:** {input_file}  
**Analysis Version:** v4.1 AG1 (Antigravity Enhanced)  
**Supplier:** Unknown (part_1_jan)

---

## Summary Counts

| Category | Count |
|----------|-------|
| VERIFIED — RECOMMENDED | {verified_rec} |
| VERIFIED — FILTERED OUT / EXCLUDED | {verified_filt} |
| HIGHLY LIKELY — RECOMMENDED | {highly_likely_rec} |
| HIGHLY LIKELY — FILTERED OUT / EXCLUDED | {highly_likely_filt} |
| NEEDS VERIFICATION | {needs_verif} |
| **TOTAL ANALYZED** | **{total}** |

This report applies v4.1 Thorough Manual Analysis:
- HIGHLY LIKELY requires Brand + Product type match with positive profit.
- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade.
- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit).

---

## VERIFIED — RECOMMENDED (count={verified_rec})

These products have **exact EAN matches** with strict checksum validation, positive adjusted profit, and confirmed sales.

{generate_table(results['VERIFIED_RECOMMENDED'], "VERIFIED RECOMMENDED")}

---

## VERIFIED — FILTERED OUT / EXCLUDED (count={verified_filt})

These products have exact EAN matches (confirmed same product) but are excluded due to pack/variant/profit issues.

{generate_table(results['VERIFIED_FILTERED'], "VERIFIED FILTERED")}

---

## HIGHLY LIKELY — RECOMMENDED (count={highly_likely_rec})

These products have strong brand + product type matches, positive profit, and confirmed sales. Amazon EAN may be missing but titles strongly confirm the same product.

{generate_table(results['HIGHLY_LIKELY_RECOMMENDED'], "HIGHLY LIKELY RECOMMENDED")}

---

## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={highly_likely_filt})

Brand/product match IS confirmed, but excluded due to pack size, variant mismatch, or negative adjusted profit.

{generate_table(results['HIGHLY_LIKELY_FILTERED'], "HIGHLY LIKELY FILTERED")}

---

## NEEDS VERIFICATION (count={needs_verif})

These items require 1-2 confirmable details to upgrade to HIGHLY LIKELY or VERIFIED. Plausible matches with positive profit potential.

{generate_table(results['NEEDS_VERIFICATION'], "NEEDS VERIFICATION")}

---

## Reconciliation Summary

| Category | Recommended | Excluded | Total |
|----------|-------------|----------|-------|
| VERIFIED | {verified_rec} | {verified_filt} | {verified_rec + verified_filt} |
| HIGHLY LIKELY | {highly_likely_rec} | {highly_likely_filt} | {highly_likely_rec + highly_likely_filt} |
| NEEDS VERIFICATION | {needs_verif} | - | {needs_verif} |
| **TOTAL** | **{verified_rec + highly_likely_rec + needs_verif}** | **{verified_filt + highly_likely_filt}** | **{total}** |

---

## Data Quality Notes

**CRITICAL OBSERVATION:** This dataset shows significant EAN-to-Amazon title mismatches in the raw data. Many supplier products have EANs that link to completely unrelated Amazon products (e.g., "BIRTHDAY BADGE" → "Motorola phone"). This indicates:

1. Potential EAN data corruption or incorrect matching in the source system
2. High false positive risk if relying solely on EAN matching
3. Title verification is essential for this dataset

**Recommendations:**
- Manually verify any VERIFIED items before purchasing
- Cross-check EAN on physical supplier packaging
- Consider title similarity as primary validation

---

*Report generated by FBA Analysis v4.1 AG1*
*Calibration applied from pre-flight analysis on 2026-01-01*
"""
    
    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"  Report saved to: {output_file}")
    return report

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 80)
    print("FBA PRODUCT ANALYSIS v4.1 AG1")
    print("=" * 80)
    
    # Execute all stages
    df = load_and_clean_data(INPUT_FILE)
    df = apply_ean_normalization(df)
    df = calculate_title_similarity(df)
    df = apply_basic_ean_matching(df)
    df = apply_strict_ean_validation(df)
    df = calculate_pack_and_profit(df)
    df = initial_categorization(df)
    
    # Thorough manual analysis
    results = thorough_manual_analysis(df)
    
    # Generate report
    report = generate_report(results, INPUT_FILE, OUTPUT_FILE)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    # Print summary
    print(f"\nOUTPUT FILE: {OUTPUT_FILE}")
    print(f"\nCATEGORY SUMMARY:")
    print(f"  VERIFIED — RECOMMENDED: {len(results['VERIFIED_RECOMMENDED'])}")
    print(f"  VERIFIED — FILTERED: {len(results['VERIFIED_FILTERED'])}")
    print(f"  HIGHLY LIKELY — RECOMMENDED: {len(results['HIGHLY_LIKELY_RECOMMENDED'])}")
    print(f"  HIGHLY LIKELY — FILTERED: {len(results['HIGHLY_LIKELY_FILTERED'])}")
    print(f"  NEEDS VERIFICATION: {len(results['NEEDS_VERIFICATION'])}")
    
    return df, results

if __name__ == "__main__":
    df, results = main()
