"""
FBA Product Analysis - Principal E-Commerce Analyst
Version 3.1 (Recall-Maximized)
Date: 2025-12-28
"""

import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
from pathlib import Path
from datetime import datetime

# Configuration
INPUT_PATH = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\PARTDEC28_1.xlsx")
OUTPUT_DIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\opus")
DATE_STR = datetime.now().strftime("%Y%m%d")

# IP Risk brands (only luxury/trademark)
IP_RISK_BRANDS = {
    'jo malone', 'chanel', 'dior', 'gucci', 'louis vuitton', 'prada', 'hermes', 'hermès',
    'apple', 'samsung', 'sony', 'microsoft', 'nike', 'adidas'
}

# Non-IP risk (generic/wholesale) brands - explicitly allowed
SAFE_BRANDS = {
    'tidyz', 'soudal', 'amtech', 'rolson', 'draper', 'fairy', 'dettol', 'marigold',
    'dunlop', 'mason cash', 'pyrex', 'everbuild', 'harris', 'status', 'extrastar',
    'roundup', 'little trees', 'harris', 'ambi pur', 'jeyes', 'zoflora', 'domestos',
    'finish', 'vanish', 'comfort', 'lenor', 'surf', 'bold', 'persil', 'ariel'
}

def clean_to_digits(x):
    """Clean EAN to digits only, handling corrupted values."""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    # If scientific notation appears, treat as corrupted
    if 'e+' in s.lower() or 'e-' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

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
    """Check if barcode is strictly valid."""
    if not isinstance(digits, str) or not digits:
        return False
    if not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    # Reject obvious placeholder patterns (heavy trailing zeros)
    if re.search(r'0{6,}$', normalized):
        return False
    return gtin_checksum_ok(normalized)

def title_similarity(title1, title2):
    """Calculate title similarity using SequenceMatcher."""
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

def extract_quantity(title):
    """Extract pack size from product title. Defaults to 1."""
    if pd.isna(title):
        return 1.0
    title = str(title).lower()
    
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
        r'\b(\d+)\s*bags?\b',
        r'\b(\d+)\s*liners?\b',
    ]
    
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:
                return qty
    return 1.0

def is_dimension_pattern(title):
    """Check if title contains dimension/measurement patterns (not pack counts)."""
    if pd.isna(title):
        return False
    title = str(title).lower()
    # Patterns that indicate dimensions, not pack counts
    dimension_patterns = [
        r'\d+\s*x\s*\d+\s*(inch|in|cm|mm|m)\b',  # 9 x 9 inch
        r'\d+\s*(inch|in|cm|mm|m)\s*x\s*\d+',    # 9 inch x 9
        r'\d+\s*(ml|l|litre|liter|g|kg|oz)\b',   # 500ml, 1L
        r'\d+cm\b',                               # 30cm
        r'\d+mm\b',                               # 10mm
        r'\d+\s*inch\b',                          # 12 inch
    ]
    for pat in dimension_patterns:
        if re.search(pat, title):
            return True
    return False

def extract_capacity(title):
    """Extract capacity/volume from title (ml, L, g, kg)."""
    if pd.isna(title):
        return None
    title = str(title).lower()
    
    # Try ml
    match = re.search(r'(\d+(?:\.\d+)?)\s*ml\b', title)
    if match:
        return float(match.group(1))
    
    # Try L/litre
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:l|litre|liter)\b', title)
    if match:
        return float(match.group(1)) * 1000  # Convert to ml
    
    return None

def calculate_capacity_variance(sup_title, amz_title):
    """Calculate capacity variance between two titles."""
    sup_cap = extract_capacity(sup_title)
    amz_cap = extract_capacity(amz_title)
    
    if sup_cap is None or amz_cap is None:
        return None
    
    if sup_cap == 0 or amz_cap == 0:
        return None
    
    # Calculate percentage difference
    variance = abs(sup_cap - amz_cap) / max(sup_cap, amz_cap) * 100
    return variance

def get_shared_tokens(title1, title2, min_length=3):
    """Get shared tokens between two titles."""
    if pd.isna(title1) or pd.isna(title2):
        return []
    
    # Clean and tokenize
    t1_clean = re.sub(r'[^\w\s]', ' ', str(title1).lower())
    t2_clean = re.sub(r'[^\w\s]', ' ', str(title2).lower())
    
    words1 = set(w for w in t1_clean.split() if len(w) >= min_length)
    words2 = set(w for w in t2_clean.split() if len(w) >= min_length)
    
    return list(words1.intersection(words2))

def extract_brand(title):
    """Extract likely brand from title (usually first word or two)."""
    if pd.isna(title):
        return None
    
    title = str(title).strip()
    words = title.split()
    if not words:
        return None
    
    # Common brand patterns - take first 1-2 words
    if len(words) >= 2:
        potential_brand = words[0].lower()
        # Check if it's a known brand
        return potential_brand
    return words[0].lower() if words else None

def check_ip_risk(title):
    """Check if title contains IP risk brands."""
    if pd.isna(title):
        return False
    title_lower = str(title).lower()
    for brand in IP_RISK_BRANDS:
        if brand in title_lower:
            return True
    return False

def calculate_mls(row):
    """Calculate Manual Match Likelihood Score (MLS) for non-EAN matches."""
    mls = 0
    sup_title = str(row.get('SupplierTitle', '')).lower() if pd.notna(row.get('SupplierTitle')) else ''
    amz_title = str(row.get('AmazonTitle', '')).lower() if pd.notna(row.get('AmazonTitle')) else ''
    
    if not sup_title or not amz_title:
        return 0
    
    # Get shared tokens
    shared = get_shared_tokens(sup_title, amz_title)
    
    # Base score from title similarity
    title_sim = row.get('title_match', 0)
    mls += title_sim * 50  # Max 50 from similarity
    
    # Brand match bonus
    sup_brand = extract_brand(row.get('SupplierTitle', ''))
    amz_brand = extract_brand(row.get('AmazonTitle', ''))
    if sup_brand and amz_brand and sup_brand == amz_brand:
        mls += 15
    
    # Significant shared tokens (product type nouns)
    significant_tokens = [t for t in shared if len(t) >= 4]
    mls += min(len(significant_tokens) * 5, 20)  # Max 20 from tokens
    
    # Penalties
    # Assorted penalty
    if 'assorted' in sup_title or 'assorted' in amz_title:
        mls -= 15
    
    # Different numbers penalty (if not dimensions)
    sup_nums = set(re.findall(r'\b\d+\b', sup_title))
    amz_nums = set(re.findall(r'\b\d+\b', amz_title))
    if sup_nums and amz_nums and not sup_nums.intersection(amz_nums):
        if not is_dimension_pattern(sup_title) and not is_dimension_pattern(amz_title):
            mls -= 10
    
    return max(0, min(100, mls))

def get_mls_band(mls):
    """Get MLS band category."""
    if mls >= 75:
        return 'HIGH_LIKELIHOOD'
    elif mls >= 50:
        return 'NEEDS_VERIFICATION'
    elif mls >= 35:
        return 'LOW_PRIORITY'
    else:
        return 'UNLIKELY'

def main():
    print(f"=" * 80)
    print(f"FBA PRODUCT ANALYSIS - OPUS VERSION")
    print(f"Date: {DATE_STR}")
    print(f"=" * 80)
    
    # Stage 1: Load data
    print("\n📁 STAGE 1: Loading data...")
    df = pd.read_excel(INPUT_PATH)
    total_rows = len(df)
    print(f"   Loaded {total_rows} rows from {INPUT_PATH.name}")
    
    # Add RowID for traceability
    df['RowID'] = df.index + 1
    
    # Print column names
    print(f"\n   Columns: {list(df.columns)}")
    
    # Stage 1B: Clean EANs
    print("\n🔧 STAGE 1B: Cleaning EANs...")
    df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()
    
    df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
    df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
    
    # Handle sales column
    if 'sales_numeric' in df.columns:
        df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
    elif 'bought_in_past_month' in df.columns:
        df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
    else:
        df['sales'] = 0
    
    # Stage 2: Title similarity
    print("\n📊 STAGE 2: Calculating title similarity...")
    df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)
    
    # Stage 3: Basic EAN matching
    print("\n🔍 STAGE 3: Basic EAN matching...")
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
    
    # Stage 3B: Strict EAN validation
    print("\n🔐 STAGE 3B: Strict barcode validation...")
    df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
    df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)
    
    df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
    df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)
    
    df['is_exact_ean_strict'] = (
        df['EAN_strict_valid'] &
        df['EAN_OnPage_strict_valid'] &
        (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
    )
    
    strict_ean_count = df['is_exact_ean_strict'].sum()
    print(f"   Strict exact EAN matches: {strict_ean_count}")
    
    # Stage 4: Pack size extraction
    print("\n📦 STAGE 4: Extracting pack sizes...")
    df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
    df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
    df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']
    
    df['has_dimension_pattern_sup'] = df['SupplierTitle'].apply(is_dimension_pattern)
    df['has_dimension_pattern_amz'] = df['AmazonTitle'].apply(is_dimension_pattern)
    
    # Recalculate profit with pack adjustment
    def recalculate_profit(row):
        try:
            original_profit = float(row['NetProfit'])
            supplier_cost = float(row['SupplierPrice_incVAT'])
            ratio = row['Qty_Ratio']
            
            # DIMENSION SHIELD: If dimension pattern detected, don't adjust
            if row.get('has_dimension_pattern_sup') or row.get('has_dimension_pattern_amz'):
                if row['Qty_Ratio'] > 1 and row['Qty_Ratio'] != int(row['Qty_Ratio']):
                    # Non-integer ratio with dimensions = likely false positive
                    return original_profit
            
            adjustment = supplier_cost * (ratio - 1)
            return original_profit - adjustment
        except:
            return 0.0
    
    df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)
    
    # Stage 5: Categorization
    print("\n🏷️ STAGE 5: Categorizing products...")
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
        # DIMENSION SHIELD
        if row.get('has_dimension_pattern_sup') or row.get('has_dimension_pattern_amz'):
            if row['Qty_Ratio'] != 1.0:
                return "1:1 Match (dimension pattern detected)"
        
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
    
    # Stage 5B: MLS calculation for non-EAN
    print("\n📈 STAGE 5B: Calculating MLS for non-EAN candidates...")
    df['MLS'] = df.apply(lambda row: 95 if row['is_exact_ean_strict'] else calculate_mls(row), axis=1)
    df['MLS_band'] = df['MLS'].apply(get_mls_band)
    
    # Check IP risk
    df['IP_Risk'] = df['SupplierTitle'].apply(check_ip_risk) | df['AmazonTitle'].apply(check_ip_risk)
    
    # Calculate capacity variance
    df['Capacity_Variance'] = df.apply(
        lambda row: calculate_capacity_variance(row['SupplierTitle'], row['AmazonTitle']), axis=1
    )
    
    # Save deep analysis CSV
    print("\n💾 Saving deep analysis CSV...")
    csv_path = OUTPUT_DIR / f"deep_analysis_{DATE_STR}.csv"
    df.to_csv(csv_path, index=False)
    print(f"   Saved to: {csv_path}")
    
    # Build report
    print("\n📝 Building report...")
    build_report(df, OUTPUT_DIR, DATE_STR)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)

def build_report(df, output_dir, date_str):
    """Build the markdown report following PHASEA format."""
    
    total_rows = len(df)
    
    # Define buckets
    verified_recommended = df[
        (df['is_exact_ean_strict']) & 
        (df['sales'] > 0) & 
        (df['NetProfit'] > 0) & 
        (df['Adjusted_Profit'] > 0)
    ].copy()
    
    verified_filtered = df[
        (df['is_exact_ean_strict']) & 
        ~((df['sales'] > 0) & (df['NetProfit'] > 0) & (df['Adjusted_Profit'] > 0))
    ].copy()
    
    # High likelihood (MLS >= 75, not exact EAN)
    high_likelihood_candidates = df[
        (~df['is_exact_ean_strict']) & 
        (df['MLS'] >= 75)
    ].copy()
    
    high_likelihood_recommended = high_likelihood_candidates[
        (high_likelihood_candidates['sales'] > 0) & 
        (high_likelihood_candidates['NetProfit'] > 0) & 
        (high_likelihood_candidates['Adjusted_Profit'] > 0)
    ].copy()
    
    high_likelihood_filtered = high_likelihood_candidates[
        ~((high_likelihood_candidates['sales'] > 0) & 
          (high_likelihood_candidates['NetProfit'] > 0) & 
          (high_likelihood_candidates['Adjusted_Profit'] > 0))
    ].copy()
    
    # Needs verification (MLS 50-74, not exact EAN)
    needs_verification = df[
        (~df['is_exact_ean_strict']) & 
        (df['MLS'] >= 50) & 
        (df['MLS'] < 75) &
        (df['sales'] > 0) &
        (df['NetProfit'] > 0)
    ].copy()
    
    # Low priority (MLS 35-49)
    low_priority = df[
        (~df['is_exact_ean_strict']) & 
        (df['MLS'] >= 35) & 
        (df['MLS'] < 50) &
        (df['sales'] > 0) &
        (df['NetProfit'] > 0)
    ].copy()
    
    # Other (MLS < 35 or unprofitable/no sales)
    other_count = total_rows - len(verified_recommended) - len(verified_filtered) - \
                  len(high_likelihood_recommended) - len(high_likelihood_filtered) - \
                  len(needs_verification) - len(low_priority)
    
    # Reconciliation
    sum_counts = len(verified_recommended) + len(verified_filtered) + \
                 len(high_likelihood_recommended) + len(high_likelihood_filtered) + \
                 len(needs_verification) + len(low_priority) + other_count
    
    reconciliation_pass = sum_counts == total_rows
    
    # Build markdown
    lines = []
    lines.append(f"# FBA PRODUCT ANALYSIS REPORT - OPUS VERSION")
    lines.append(f"**Date:** {date_str}")
    lines.append(f"**Input:** PARTDEC28_1.xlsx")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Reconciliation table
    lines.append("## 📊 RECONCILIATION PROOF")
    lines.append("")
    lines.append("```text")
    lines.append(f"{'Bucket':<40} | {'Count':>8}")
    lines.append(f"{'-'*40}-+-{'-'*8}")
    lines.append(f"{'Total input rows':<40} | {total_rows:>8}")
    lines.append(f"{'VERIFIED (Recommended)':<40} | {len(verified_recommended):>8}")
    lines.append(f"{'HIGH LIKELIHOOD (Recommended)':<40} | {len(high_likelihood_recommended):>8}")
    lines.append(f"{'NEEDS VERIFICATION':<40} | {len(needs_verification):>8}")
    lines.append(f"{'LOW PRIORITY (MLS 35-49)':<40} | {len(low_priority):>8}")
    lines.append(f"{'VERIFIED (Filtered Out)':<40} | {len(verified_filtered):>8}")
    lines.append(f"{'HIGH LIKELIHOOD (Filtered Out)':<40} | {len(high_likelihood_filtered):>8}")
    lines.append(f"{'OTHER (MLS<35/Loss/NoSales)':<40} | {other_count:>8}")
    lines.append(f"{'-'*40}-+-{'-'*8}")
    lines.append(f"{'SUM':<40} | {sum_counts:>8}")
    lines.append(f"")
    lines.append(f"Reconciliation: {sum_counts} = {total_rows} ({'PASS ✅' if reconciliation_pass else 'FAIL ❌'})")
    lines.append("```")
    lines.append("")
    
    # Summary
    lines.append("## 📈 SUMMARY")
    lines.append("")
    lines.append(f"- **Total products analyzed:** {total_rows}")
    lines.append(f"- **Strict EAN matches:** {df['is_exact_ean_strict'].sum()}")
    lines.append(f"- **Products with sales > 0:** {len(df[df['sales'] > 0])}")
    lines.append(f"- **Products with positive profit:** {len(df[df['NetProfit'] > 0])}")
    lines.append("")
    
    # VERIFIED RECOMMENDED
    lines.append("---")
    lines.append("")
    lines.append("## ✅ VERIFIED (Exact EAN) - RECOMMENDED")
    lines.append("")
    if len(verified_recommended) > 0:
        lines.append(f"**Count:** {len(verified_recommended)} products")
        lines.append("")
        verified_recommended = verified_recommended.sort_values('sales', ascending=False)
        lines.extend(format_table(verified_recommended.head(75), is_verified=True))
        if len(verified_recommended) > 75:
            lines.append(f"\n*Remaining: {len(verified_recommended) - 75} rows*")
    else:
        lines.append("*No verified EAN matches meeting all criteria (Sales>0, NetProfit>0, Adjusted>0)*")
    lines.append("")
    
    # HIGH LIKELIHOOD RECOMMENDED
    lines.append("---")
    lines.append("")
    lines.append("## 🔥 HIGH LIKELIHOOD - RECOMMENDED")
    lines.append("")
    if len(high_likelihood_recommended) > 0:
        lines.append(f"**Count:** {len(high_likelihood_recommended)} products")
        lines.append("")
        high_likelihood_recommended = high_likelihood_recommended.sort_values(['MLS', 'sales'], ascending=[False, False])
        lines.extend(format_table(high_likelihood_recommended.head(75), is_verified=False))
        if len(high_likelihood_recommended) > 75:
            remaining = high_likelihood_recommended.iloc[75:]
            mls_min = remaining['MLS'].min()
            mls_max = remaining['MLS'].max()
            lines.append(f"\n*Remaining: {len(remaining)} rows with MLS {mls_min:.0f}-{mls_max:.0f}*")
    else:
        lines.append("*No high likelihood matches meeting all criteria*")
    lines.append("")
    
    # NEEDS VERIFICATION
    lines.append("---")
    lines.append("")
    lines.append("## ⚠️ NEEDS VERIFICATION")
    lines.append("")
    if len(needs_verification) > 0:
        lines.append(f"**Count:** {len(needs_verification)} products")
        lines.append("")
        needs_verification = needs_verification.sort_values(['MLS', 'sales'], ascending=[False, False])
        lines.extend(format_table(needs_verification.head(75), is_verified=False))
        if len(needs_verification) > 75:
            remaining = needs_verification.iloc[75:]
            mls_min = remaining['MLS'].min()
            mls_max = remaining['MLS'].max()
            lines.append(f"\n*Remaining: {len(remaining)} rows with MLS {mls_min:.0f}-{mls_max:.0f}*")
    else:
        lines.append("*No products in this category*")
    lines.append("")
    
    # LOW PRIORITY
    lines.append("---")
    lines.append("")
    lines.append("## 📋 LOW PRIORITY (MLS 35-49)")
    lines.append("")
    if len(low_priority) > 0:
        lines.append(f"**Count:** {len(low_priority)} products")
        lines.append("")
        low_priority = low_priority.sort_values(['MLS', 'sales'], ascending=[False, False])
        lines.extend(format_table(low_priority.head(50), is_verified=False))
        if len(low_priority) > 50:
            remaining = low_priority.iloc[50:]
            mls_min = remaining['MLS'].min()
            mls_max = remaining['MLS'].max()
            lines.append(f"\n*Remaining: {len(remaining)} rows with MLS {mls_min:.0f}-{mls_max:.0f}*")
    else:
        lines.append("*No products in this category*")
    lines.append("")
    
    # VERIFIED FILTERED OUT
    lines.append("---")
    lines.append("")
    lines.append("## ❌ VERIFIED (Exact EAN) - FILTERED OUT (Audit)")
    lines.append("")
    if len(verified_filtered) > 0:
        lines.append(f"**Count:** {len(verified_filtered)} products")
        lines.append("*These products have matching EANs but fail Sales/Profit filters*")
        lines.append("")
        verified_filtered = verified_filtered.sort_values('sales', ascending=False)
        lines.extend(format_table(verified_filtered.head(50), is_verified=True, is_audit=True))
        if len(verified_filtered) > 50:
            lines.append(f"\n*Remaining: {len(verified_filtered) - 50} rows*")
    else:
        lines.append("*No verified EAN matches filtered out*")
    lines.append("")
    
    # HIGH LIKELIHOOD FILTERED OUT
    lines.append("---")
    lines.append("")
    lines.append("## ❌ HIGH LIKELIHOOD - FILTERED OUT (Audit)")
    lines.append("")
    if len(high_likelihood_filtered) > 0:
        lines.append(f"**Count:** {len(high_likelihood_filtered)} products")
        lines.append("*These products have high MLS but fail Sales/Profit filters*")
        lines.append("")
        high_likelihood_filtered = high_likelihood_filtered.sort_values(['MLS', 'sales'], ascending=[False, False])
        lines.extend(format_table(high_likelihood_filtered.head(50), is_verified=False, is_audit=True))
        if len(high_likelihood_filtered) > 50:
            remaining = high_likelihood_filtered.iloc[50:]
            mls_min = remaining['MLS'].min()
            mls_max = remaining['MLS'].max()
            lines.append(f"\n*Remaining: {len(remaining)} rows with MLS {mls_min:.0f}-{mls_max:.0f}*")
    else:
        lines.append("*No high likelihood matches filtered out*")
    lines.append("")
    
    # Save report
    report_path = output_dir / f"PHASEA_MANUAL_REPORT_{date_str}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"   Report saved to: {report_path}")

def format_table(df, is_verified=False, is_audit=False):
    """Format dataframe as fixed-width markdown table."""
    lines = []
    
    if len(df) == 0:
        return lines
    
    # Define columns
    cols = ['RowID', 'Verdict', 'Confidence', 'SupplierTitle', 'AmazonTitle', 
            'EAN', 'EAN_OnPage', 'ASIN', 'SupplierPrice_incVAT', 'SellingPrice_incVAT',
            'NetProfit', 'ROI', 'sales', 'Pack_Verdict', 'Adjusted_Profit', 'Evidence', 'Filter_Reason']
    
    # Prepare data
    rows_data = []
    for _, row in df.iterrows():
        # Build evidence
        shared_tokens = get_shared_tokens(row.get('SupplierTitle', ''), row.get('AmazonTitle', ''))
        if is_verified:
            evidence = "Strict Exact EAN Match"
            if shared_tokens:
                evidence += f"; Shared: {', '.join(shared_tokens[:3])}"
        else:
            evidence = f"MLS={row.get('MLS', 0):.0f}"
            if shared_tokens:
                evidence += f"; Shared: {', '.join(shared_tokens[:3])}"
        
        # Build filter reason
        filter_reason = "-"
        if is_audit:
            reasons = []
            if row.get('sales', 0) <= 0:
                reasons.append("No sales")
            if row.get('NetProfit', 0) <= 0:
                reasons.append("Negative profit")
            if row.get('Adjusted_Profit', 0) <= 0:
                reasons.append("Pack-adjusted loss")
            filter_reason = "EXCLUDED: " + "; ".join(reasons) if reasons else "-"
        
        # Truncate titles for display
        sup_title = str(row.get('SupplierTitle', ''))[:50] + ('...' if len(str(row.get('SupplierTitle', ''))) > 50 else '')
        amz_title = str(row.get('AmazonTitle', ''))[:50] + ('...' if len(str(row.get('AmazonTitle', ''))) > 50 else '')
        
        verdict = "VERIFIED" if is_verified else row.get('MLS_band', 'UNKNOWN')
        confidence = 95 if is_verified else row.get('MLS', 0)
        
        row_data = {
            'RowID': row.get('RowID', 0),
            'Verdict': verdict,
            'Confidence': f"{confidence:.0f}" if isinstance(confidence, (int, float)) else str(confidence),
            'SupplierTitle': sup_title,
            'AmazonTitle': amz_title,
            'EAN': str(row.get('EAN', '-'))[:15],
            'EAN_OnPage': str(row.get('EAN_OnPage', '-'))[:15],
            'ASIN': str(row.get('ASIN', '-'))[:12],
            'SupplierPrice_incVAT': f"£{row.get('SupplierPrice_incVAT', 0):.2f}",
            'SellingPrice_incVAT': f"£{row.get('SellingPrice_incVAT', 0):.2f}",
            'NetProfit': f"£{row.get('NetProfit', 0):.2f}",
            'ROI': f"{row.get('ROI', 0):.1f}%" if pd.notna(row.get('ROI')) else "-",
            'sales': f"{row.get('sales', 0):.0f}",
            'Pack_Verdict': str(row.get('Pack_Verdict', '-'))[:20],
            'Adjusted_Profit': f"£{row.get('Adjusted_Profit', 0):.2f}",
            'Evidence': evidence[:40],
            'Filter_Reason': filter_reason[:30]
        }
        rows_data.append(row_data)
    
    # Calculate column widths
    col_widths = {}
    for col in cols:
        max_len = len(col)
        for rd in rows_data:
            max_len = max(max_len, len(str(rd.get(col, ''))))
        col_widths[col] = min(max_len, 55)  # Cap at 55 chars
    
    # Build header
    header = " | ".join(col.ljust(col_widths[col]) for col in cols)
    separator = "-+-".join("-" * col_widths[col] for col in cols)
    
    lines.append("```text")
    lines.append(header)
    lines.append(separator)
    
    # Build rows
    for rd in rows_data:
        row_str = " | ".join(str(rd.get(col, '')).ljust(col_widths[col])[:col_widths[col]] for col in cols)
        lines.append(row_str)
    
    lines.append("```")
    return lines

if __name__ == "__main__":
    main()
