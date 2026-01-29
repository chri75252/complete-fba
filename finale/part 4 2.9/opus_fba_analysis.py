"""
FBA Product Analysis Script - OPUS Edition
Multi-stage analysis following the PROMPT_V3_RECALL_MAXIMIZED methodology
"""

import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
from datetime import datetime

# Configuration
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.csv"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 4 2.9"
DATE_STR = datetime.now().strftime("%Y%m%d")

print("=" * 80)
print("FBA PRODUCT ANALYSIS - OPUS EDITION")
print("=" * 80)

# =============================================================================
# STAGE 1: Data Loading & Initial Cleaning
# =============================================================================
print("\n[STAGE 1] Loading and cleaning data...")

df = pd.read_csv(INPUT_PATH)
print(f"  Loaded {len(df)} rows")

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

print(f"  Sales column created. Non-zero sales: {(df['sales'] > 0).sum()}")

# =============================================================================
# STAGE 1B: EAN Normalization Safety Flags
# =============================================================================
print("\n[STAGE 1B] EAN normalization and safety flags...")

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    # If scientific notation appears, treat as corrupted
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

# =============================================================================
# STAGE 2: Title Similarity Calculation
# =============================================================================
print("\n[STAGE 2] Calculating title similarity...")

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)
print(f"  Average title similarity: {df['title_match'].mean():.3f}")

# =============================================================================
# STAGE 3: Basic EAN Matching
# =============================================================================
print("\n[STAGE 3] Basic EAN matching...")

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
print(f"  Basic exact EAN matches: {df['is_exact_ean'].sum()}")

# =============================================================================
# STAGE 3B: Strict Barcode Validity + Checksum + Left-Padding
# =============================================================================
print("\n[STAGE 3B] Strict barcode validation with checksum...")

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

df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)
df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)

df['is_exact_ean_strict'] = (
    df['EAN_strict_valid']
    & df['EAN_OnPage_strict_valid']
    & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
)
print(f"  Strict exact EAN matches: {df['is_exact_ean_strict'].sum()}")

# =============================================================================
# STAGE 4: Pack Size Extraction & Profit Recalculation
# =============================================================================
print("\n[STAGE 4] Pack size extraction and profit adjustment...")

def extract_quantity(title):
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
        r'\b(\d+)\s*piece\b',
    ]
    
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:
                return qty
    return 1.0

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']

def recalculate_profit(row):
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        adjustment = supplier_cost * (ratio - 1)
        return original_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# =============================================================================
# STAGE 5: Product Categorization
# =============================================================================
print("\n[STAGE 5] Categorizing products...")

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

# =============================================================================
# STAGE 5B: Manual Match Likelihood Score (MLS)
# =============================================================================
print("\n[STAGE 5B] Computing Match Likelihood Score (MLS)...")

def compute_mls(row):
    """
    Compute Match Likelihood Score based on title analysis.
    This is a heuristic implementation of the manual scoring rubric.
    """
    sup_title = str(row['SupplierTitle']).lower() if pd.notna(row['SupplierTitle']) else ''
    amz_title = str(row['AmazonTitle']).lower() if pd.notna(row['AmazonTitle']) else ''
    
    if not sup_title or not amz_title:
        return 0
    
    base_score = row['title_match'] * 100  # Start with title similarity
    
    # Extract tokens
    sup_tokens = set(re.findall(r'\b[a-z]{3,}\b', sup_title))
    amz_tokens = set(re.findall(r'\b[a-z]{3,}\b', amz_title))
    
    # Common tokens boost
    common_tokens = sup_tokens & amz_tokens
    token_boost = min(len(common_tokens) * 3, 20)
    
    # Brand detection (common brands in both titles)
    brands = ['minky', 'fairy', 'dekton', 'apollo', 'bettina', 'status', 'dunlop', 
              'kingfisher', 'extrastar', 'rolson', 'draper', 'amtech', 'pyrex',
              'premier', 'mason', 'everbuild', 'harris', 'roundup', 'tidyz']
    
    for brand in brands:
        if brand in sup_title and brand in amz_title:
            token_boost += 15
            break
    
    # Product type match detection
    product_types = ['mop', 'brush', 'plate', 'bowl', 'cup', 'mug', 'candle', 'light',
                    'tool', 'knife', 'spoon', 'fork', 'bag', 'box', 'lamp', 'cable',
                    'sponge', 'cleaner', 'towel', 'cloth', 'tape', 'glue', 'paint']
    
    for ptype in product_types:
        if ptype in sup_title and ptype in amz_title:
            token_boost += 10
            break
    
    # Penalty for completely different product categories
    contradiction_penalty = 0
    if any(word in amz_title for word in ['blender', 'engine', 'motor', 'tablet', 'laptop', 'phone', 'watch', 'headset', 'camera']):
        if not any(word in sup_title for word in ['blender', 'engine', 'motor', 'tablet', 'laptop', 'phone', 'watch', 'headset', 'camera']):
            contradiction_penalty = 40
    
    mls = min(100, max(0, base_score + token_boost - contradiction_penalty))
    return int(mls)

df['MLS'] = df.apply(compute_mls, axis=1)

# Assign MLS bands
def mls_band(mls):
    if mls >= 75:
        return 'HIGH_LIKELIHOOD'
    elif mls >= 50:
        return 'NEEDS_VERIFICATION'
    elif mls >= 35:
        return 'POSSIBLE'
    else:
        return 'UNLIKELY'

df['MLS_band'] = df['MLS'].apply(mls_band)

print(f"  MLS distribution:")
print(f"    HIGH_LIKELIHOOD (>=75): {(df['MLS'] >= 75).sum()}")
print(f"    NEEDS_VERIFICATION (50-74): {((df['MLS'] >= 50) & (df['MLS'] < 75)).sum()}")
print(f"    POSSIBLE (35-49): {((df['MLS'] >= 35) & (df['MLS'] < 50)).sum()}")
print(f"    UNLIKELY (<35): {(df['MLS'] < 35).sum()}")

# =============================================================================
# STAGE 6/6B: Filtering and Classification
# =============================================================================
print("\n[STAGE 6] Applying filters and creating buckets...")

# NetProfit as numeric
df['NetProfit'] = pd.to_numeric(df['NetProfit'], errors='coerce').fillna(0)

# Create buckets
# VERIFIED: Strict exact EAN match, Sales > 0, NetProfit > 0
verified_recommended = df[
    (df['is_exact_ean_strict'] == True) &
    (df['sales'] > 0) &
    (df['NetProfit'] > 0) &
    (df['Adjusted_Profit'] > 0)
].copy()

# VERIFIED filtered out: Strict exact EAN but fails profitability/sales
verified_filtered = df[
    (df['is_exact_ean_strict'] == True) &
    ((df['sales'] <= 0) | (df['NetProfit'] <= 0) | (df['Adjusted_Profit'] <= 0))
].copy()

# HIGH_LIKELIHOOD: MLS >= 75, not strict EAN, Sales > 0, NetProfit > 0
high_likelihood_recommended = df[
    (df['is_exact_ean_strict'] == False) &
    (df['MLS'] >= 75) &
    (df['sales'] > 0) &
    (df['NetProfit'] > 0) &
    (df['Adjusted_Profit'] > 0)
].copy()

# HIGH_LIKELIHOOD filtered out
high_likelihood_filtered = df[
    (df['is_exact_ean_strict'] == False) &
    (df['MLS'] >= 75) &
    ((df['sales'] <= 0) | (df['NetProfit'] <= 0) | (df['Adjusted_Profit'] <= 0))
].copy()

# NEEDS VERIFICATION: MLS 50-74, not strict EAN
needs_verification = df[
    (df['is_exact_ean_strict'] == False) &
    (df['MLS'] >= 50) &
    (df['MLS'] < 75) &
    (df['sales'] > 0) &
    (df['NetProfit'] > 0)
].copy()

# LOW PRIORITY: MLS 35-49
low_priority = df[
    (df['is_exact_ean_strict'] == False) &
    (df['MLS'] >= 35) &
    (df['MLS'] < 50) &
    (df['sales'] > 0) &
    (df['NetProfit'] > 0)
].copy()

# OTHER bucket: MLS < 35 OR (Sales = 0 AND MLS < 50) OR (NetProfit <= 0 AND no EAN match)
other_bucket = df[
    (df['MLS'] < 35) |
    ((df['sales'] <= 0) & (df['MLS'] < 50)) |
    ((df['NetProfit'] <= 0) & (df['is_exact_ean_strict'] == False))
].copy()
other_bucket = other_bucket[~other_bucket['RowID'].isin(verified_recommended['RowID'])]
other_bucket = other_bucket[~other_bucket['RowID'].isin(verified_filtered['RowID'])]
other_bucket = other_bucket[~other_bucket['RowID'].isin(high_likelihood_recommended['RowID'])]
other_bucket = other_bucket[~other_bucket['RowID'].isin(high_likelihood_filtered['RowID'])]
other_bucket = other_bucket[~other_bucket['RowID'].isin(needs_verification['RowID'])]
other_bucket = other_bucket[~other_bucket['RowID'].isin(low_priority['RowID'])]

print(f"\n  Bucket counts:")
print(f"    VERIFIED (Recommended): {len(verified_recommended)}")
print(f"    HIGH LIKELIHOOD (Recommended): {len(high_likelihood_recommended)}")
print(f"    NEEDS VERIFICATION: {len(needs_verification)}")
print(f"    LOW PRIORITY (35-49 MLS): {len(low_priority)}")
print(f"    VERIFIED Filtered Out: {len(verified_filtered)}")
print(f"    HIGH LIKELIHOOD Filtered Out: {len(high_likelihood_filtered)}")
print(f"    OTHER: {len(other_bucket)}")

# Reconciliation check
total_accounted = (len(verified_recommended) + len(high_likelihood_recommended) + 
                   len(needs_verification) + len(low_priority) +
                   len(verified_filtered) + len(high_likelihood_filtered) + len(other_bucket))

# =============================================================================
# Save outputs
# =============================================================================
print("\n[OUTPUT] Saving analysis files...")

# Save full analysis CSV
csv_path = f"{OUTPUT_DIR}/opus_deep_analysis_{DATE_STR}.csv"
df.to_csv(csv_path, index=False)
print(f"  Saved: {csv_path}")

# =============================================================================
# Generate Markdown Report
# =============================================================================
print("\n[OUTPUT] Generating Markdown report...")

def format_table_row(row, is_verified=False):
    """Format a single row for the markdown table"""
    verdict = "VERIFIED" if is_verified else "NEEDS VERIFICATION"
    confidence = 95 if is_verified else row['MLS']
    
    sup_ean = row['EAN_digits'] if row['EAN_digits'] else '-'
    amz_ean = row['EAN_OnPage_digits'] if row['EAN_OnPage_digits'] else '-'
    
    # Key match evidence
    if is_verified:
        evidence = "Strict Exact EAN Match"
    else:
        evidence = f"MLS={row['MLS']}; title_sim={row['title_match']:.2f}"
    
    # Key risks
    risks = []
    if row['Qty_Ratio'] != 1.0:
        risks.append(f"Pack ratio: {row['Qty_Ratio']:.1f}x")
    if not row['EAN_strict_valid']:
        risks.append("Supplier EAN invalid/missing")
    if not row['EAN_OnPage_strict_valid']:
        risks.append("Amazon EAN invalid/missing")
    
    risk_str = "; ".join(risks) if risks else "Standard match"
    
    return f"| {verdict} | {confidence} | {row['SupplierTitle'][:60]}... | {row['AmazonTitle'][:60]}... | {sup_ean} | {amz_ean} | {row['ASIN']} | £{row['SupplierPrice_incVAT']:.2f} | £{row['SellingPrice_incVAT']:.2f} | £{row['NetProfit']:.2f} | {row['ROI']:.1f}% | {int(row['sales'])} | {row['Pack_Verdict']} | £{row['Adjusted_Profit']:.2f} | {evidence} | {risk_str} |"

# Build report
report_lines = []
report_lines.append(f"# PHASEA_MANUAL_REPORT - OPUS Analysis")
report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Asia/Dubai)")
report_lines.append(f"**Input File:** PART3.xlsx")
report_lines.append(f"**Total Rows:** {len(df)}")
report_lines.append("")

# Reconciliation
report_lines.append("## 📊 Reconciliation Proof")
report_lines.append("")
report_lines.append("| Bucket | Count |")
report_lines.append("|:--|--:|")
report_lines.append(f"| Total input rows | {len(df)} |")
report_lines.append(f"| VERIFIED (Recommended) | {len(verified_recommended)} |")
report_lines.append(f"| HIGH LIKELIHOOD (Recommended) | {len(high_likelihood_recommended)} |")
report_lines.append(f"| NEEDS VERIFICATION | {len(needs_verification)} |")
report_lines.append(f"| LOW PRIORITY (MLS 35-49) | {len(low_priority)} |")
report_lines.append(f"| VERIFIED Filtered Out | {len(verified_filtered)} |")
report_lines.append(f"| HIGH LIKELIHOOD Filtered Out | {len(high_likelihood_filtered)} |")
report_lines.append(f"| OTHER (Low MLS/Sales=0/Loss) | {len(other_bucket)} |")
report_lines.append(f"| **SUM** | **{total_accounted}** |")
report_lines.append("")
if total_accounted == len(df):
    report_lines.append("✅ **Reconciliation: PASS**")
else:
    report_lines.append(f"⚠️ **Reconciliation: MISMATCH** (Expected {len(df)}, Got {total_accounted})")
report_lines.append("")

# Summary counts table
report_lines.append("## 📈 Summary")
report_lines.append("")
report_lines.append("| Category | Profitable & Sellable | Total in Category |")
report_lines.append("|:--|--:|--:|")
report_lines.append(f"| Strict Exact EAN Match | {len(verified_recommended)} | {df['is_exact_ean_strict'].sum()} |")
report_lines.append(f"| High Likelihood (MLS ≥ 75) | {len(high_likelihood_recommended)} | {(df['MLS'] >= 75).sum()} |")
report_lines.append(f"| Needs Verification (MLS 50-74) | {len(needs_verification)} | {((df['MLS'] >= 50) & (df['MLS'] < 75)).sum()} |")
report_lines.append("")

# Table header
table_header = """| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|:--|--:|:--|:--|--:|--:|:--|:--|:--|:--|:--|--:|:--|:--|:--|:--|"""

# VERIFIED RECOMMENDED
if len(verified_recommended) > 0:
    report_lines.append("---")
    report_lines.append("## ✅ VERIFIED (Exact EAN) — RECOMMENDED")
    report_lines.append(f"**Count:** {len(verified_recommended)}")
    report_lines.append("")
    report_lines.append(table_header)
    
    # Sort by sales desc
    verified_sorted = verified_recommended.sort_values('sales', ascending=False).head(75)
    for _, row in verified_sorted.iterrows():
        report_lines.append(format_table_row(row, is_verified=True))
    
    if len(verified_recommended) > 75:
        report_lines.append(f"\n*Showing top 75 of {len(verified_recommended)} rows. Remaining {len(verified_recommended) - 75} rows sorted by Sales desc.*")
    report_lines.append("")

# HIGH LIKELIHOOD RECOMMENDED
if len(high_likelihood_recommended) > 0:
    report_lines.append("---")
    report_lines.append("## 🔶 HIGH LIKELIHOOD (MLS ≥ 75) — RECOMMENDED")
    report_lines.append(f"**Count:** {len(high_likelihood_recommended)}")
    report_lines.append("")
    report_lines.append(table_header)
    
    # Sort by MLS desc, then sales desc
    hl_sorted = high_likelihood_recommended.sort_values(['MLS', 'sales'], ascending=[False, False]).head(75)
    for _, row in hl_sorted.iterrows():
        report_lines.append(format_table_row(row, is_verified=False))
    
    if len(high_likelihood_recommended) > 75:
        remaining = len(high_likelihood_recommended) - 75
        min_mls = high_likelihood_recommended.sort_values('MLS', ascending=True).iloc[0]['MLS']
        max_mls = high_likelihood_recommended.sort_values('MLS', ascending=False).iloc[74]['MLS'] if len(high_likelihood_recommended) > 74 else min_mls
        report_lines.append(f"\n*Showing top 75 of {len(high_likelihood_recommended)} rows. Remaining {remaining} rows with MLS {min_mls}-{max_mls}.*")
    report_lines.append("")

# NEEDS VERIFICATION
if len(needs_verification) > 0:
    report_lines.append("---")
    report_lines.append("## 🔍 NEEDS VERIFICATION (MLS 50-74)")
    report_lines.append(f"**Count:** {len(needs_verification)}")
    report_lines.append("")
    report_lines.append(table_header)
    
    nv_sorted = needs_verification.sort_values(['MLS', 'sales'], ascending=[False, False]).head(75)
    for _, row in nv_sorted.iterrows():
        report_lines.append(format_table_row(row, is_verified=False))
    
    if len(needs_verification) > 75:
        remaining = len(needs_verification) - 75
        report_lines.append(f"\n*Showing top 75 of {len(needs_verification)} rows. Remaining {remaining} rows with MLS 50-74.*")
    report_lines.append("")

# LOW PRIORITY
if len(low_priority) > 0:
    report_lines.append("---")
    report_lines.append("## ⚪ LOW PRIORITY (MLS 35-49)")
    report_lines.append(f"**Count:** {len(low_priority)}")
    report_lines.append("")
    report_lines.append(table_header)
    
    lp_sorted = low_priority.sort_values(['MLS', 'sales'], ascending=[False, False]).head(50)
    for _, row in lp_sorted.iterrows():
        report_lines.append(format_table_row(row, is_verified=False))
    
    if len(low_priority) > 50:
        remaining = len(low_priority) - 50
        report_lines.append(f"\n*Showing top 50 of {len(low_priority)} rows. Remaining {remaining} rows with MLS 35-49.*")
    report_lines.append("")

# VERIFIED FILTERED OUT (Audit)
if len(verified_filtered) > 0:
    report_lines.append("---")
    report_lines.append("## ❌ VERIFIED (Exact EAN) — FILTERED OUT (Audit)")
    report_lines.append(f"**Count:** {len(verified_filtered)}")
    report_lines.append("*These rows have strict exact EAN match but fail profitability/sales criteria.*")
    report_lines.append("")
    report_lines.append(table_header)
    
    vf_sorted = verified_filtered.sort_values('sales', ascending=False).head(50)
    for _, row in vf_sorted.iterrows():
        reasons = []
        if row['sales'] <= 0:
            reasons.append("Sales=0")
        if row['NetProfit'] <= 0:
            reasons.append("NetProfit<=0")
        if row['Adjusted_Profit'] <= 0:
            reasons.append("Adjusted_Profit<=0")
        reason_str = "; ".join(reasons)
        
        line = format_table_row(row, is_verified=True)
        line = line.replace("Standard match", f"EXCLUDED: {reason_str}")
        report_lines.append(line)
    report_lines.append("")

# HIGH LIKELIHOOD FILTERED OUT (Audit)
if len(high_likelihood_filtered) > 0:
    report_lines.append("---")
    report_lines.append("## ❌ HIGH LIKELIHOOD — FILTERED OUT (Audit)")
    report_lines.append(f"**Count:** {len(high_likelihood_filtered)}")
    report_lines.append("*These rows have MLS >= 75 but fail profitability/sales criteria.*")
    report_lines.append("")
    report_lines.append(table_header)
    
    hlf_sorted = high_likelihood_filtered.sort_values(['MLS', 'sales'], ascending=[False, False]).head(50)
    for _, row in hlf_sorted.iterrows():
        reasons = []
        if row['sales'] <= 0:
            reasons.append("Sales=0")
        if row['NetProfit'] <= 0:
            reasons.append("NetProfit<=0")
        if row['Adjusted_Profit'] <= 0:
            reasons.append("Adjusted_Profit<=0")
        reason_str = "; ".join(reasons)
        
        line = format_table_row(row, is_verified=False)
        line = line.replace("Standard match", f"EXCLUDED: {reason_str}")
        report_lines.append(line)
    report_lines.append("")

# Footer
report_lines.append("---")
report_lines.append("## 📝 Notes")
report_lines.append("")
report_lines.append("- **VERIFIED** rows have strict exact EAN match (both barcodes valid and identical)")
report_lines.append("- **HIGH LIKELIHOOD** rows have MLS >= 75 based on title analysis")
report_lines.append("- **NEEDS VERIFICATION** rows have MLS 50-74 and require manual review")
report_lines.append("- **LOW PRIORITY** rows have MLS 35-49")
report_lines.append("- **OTHER** bucket contains rows with MLS < 35 or Sales=0 with low MLS")
report_lines.append("")
report_lines.append(f"*Report generated by OPUS FBA Analysis Script v1.0*")

# Save markdown report
md_path = f"{OUTPUT_DIR}/opus_PHASEA_MANUAL_REPORT_{DATE_STR}.md"
with open(md_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

print(f"  Saved: {md_path}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print(f"\nOutput files:")
print(f"  1. {csv_path}")
print(f"  2. {md_path}")
print(f"\nKey findings:")
print(f"  - Total rows analyzed: {len(df)}")
print(f"  - Strict exact EAN matches: {df['is_exact_ean_strict'].sum()}")
print(f"  - VERIFIED recommended: {len(verified_recommended)}")
print(f"  - HIGH LIKELIHOOD recommended: {len(high_likelihood_recommended)}")
print(f"  - NEEDS VERIFICATION: {len(needs_verification)}")
