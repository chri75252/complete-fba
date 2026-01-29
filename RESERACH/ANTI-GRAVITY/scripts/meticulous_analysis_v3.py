"""
METICULOUS FBA REPORT GENERATOR v3
- Thoroughly analyzes ALL rows including EAN matches for pack size mismatches
- Calculates ADJUSTED PROFIT when pack sizes differ
- Includes branded matches with pack differences
- Much stricter classification
"""
import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
from datetime import datetime

# Load source data
print("Loading data...")
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx')
df['RowID'] = df.index + 1

# Clean EANs
df['EAN_clean'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage_clean'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# =====================================
# METICULOUS HELPER FUNCTIONS
# =====================================

def is_valid_ean(ean):
    """Check if EAN is a valid barcode"""
    if pd.isna(ean) or str(ean).strip() in ['nan', '', 'None', 'NaN', '0', '-']:
        return False
    s = str(ean).strip()
    return s.isdigit() and len(s) >= 8

def eans_match(row):
    """Check if supplier and amazon EANs match exactly"""
    ean1 = row['EAN_clean']
    ean2 = row['EAN_OnPage_clean']
    return is_valid_ean(ean1) and is_valid_ean(ean2) and ean1 == ean2

def title_similarity(t1, t2):
    """Calculate title similarity ratio"""
    if pd.isna(t1) or pd.isna(t2):
        return 0.0
    return SequenceMatcher(None, str(t1).lower(), str(t2).lower()).ratio()

def get_brand_from_title(title):
    """Extract brand from title - first word or known brand patterns"""
    if pd.isna(title):
        return ""
    title_upper = str(title).upper()
    words = title_upper.split()
    
    # Known brand patterns (multi-word brands)
    multi_word_brands = [
        'BLUE CANYON', 'MASON CASH', 'PRICE & KENSINGTON', 'CHEF AID',
        'BAKER & SALT', 'AIR WICK', 'FIRE UP', 'HEAT HOLDERS',
        'SCHOTT ZWIESEL', 'LITTLE TREES', 'FIRST STEPS', 'HOUSE MATE',
        'ELBOW GREASE'
    ]
    
    for brand in multi_word_brands:
        if brand in title_upper:
            return brand
    
    # Single word brands
    return words[0] if words else ""

def extract_pack_quantity(title):
    """
    METICULOUS pack quantity extraction
    Returns (quantity, confidence, method)
    """
    if pd.isna(title):
        return (1, 0, 'default')
    
    title = str(title).lower()
    
    # Patterns in order of confidence
    patterns = [
        # "X x Y" pattern - e.g., "4 x 50" means 4 packs of 50
        (r'(\d+)\s*x\s*(\d+)', 'multiply', 0.9),
        # "Pack of X" or "X Pack"
        (r'pack\s*of\s*(\d+)', 'direct', 0.95),
        (r'(\d+)\s*pack\b', 'direct', 0.9),
        (r'(\d+)\s*pk\b', 'direct', 0.9),
        # "X pieces" or "X pcs"
        (r'(\d+)\s*pcs\b', 'direct', 0.85),
        (r'(\d+)\s*pieces?\b', 'direct', 0.85),
        # "Set of X"
        (r'set\s*of\s*(\d+)', 'direct', 0.9),
        # "X count"
        (r'(\d+)\s*count\b', 'direct', 0.85),
        # Parenthetical quantities like "(3)"
        (r'\((\d+)\)', 'direct', 0.7),
        # Leading quantity like "3 x Brand"
        (r'^(\d+)\s*x\s+\w', 'direct', 0.85),
    ]
    
    for pattern, method, confidence in patterns:
        match = re.search(pattern, title)
        if match:
            if method == 'multiply' and len(match.groups()) >= 2:
                qty = int(match.group(1)) * int(match.group(2))
                if 1 < qty < 1000:
                    return (qty, confidence, f'{match.group(1)}x{match.group(2)}')
            else:
                qty = int(match.group(1))
                if 1 <= qty < 500:
                    return (qty, confidence, pattern)
    
    return (1, 0.5, 'default')

def extract_unit_size(title):
    """
    Extract unit size (ml, L, kg, g, cm, mm, etc.)
    Returns list of (value, unit) tuples
    """
    if pd.isna(title):
        return []
    
    title = str(title).lower()
    
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(ml)\b',
        r'(\d+(?:\.\d+)?)\s*(l|ltr|litre|liter)\b',
        r'(\d+(?:\.\d+)?)\s*(kg)\b',
        r'(\d+(?:\.\d+)?)\s*(g)\b',
        r'(\d+(?:\.\d+)?)\s*(oz)\b',
        r'(\d+(?:\.\d+)?)\s*(cm)\b',
        r'(\d+(?:\.\d+)?)\s*(mm)\b',
        r'(\d+(?:\.\d+)?)\s*(inch|in|")\b',
        r'(\d+(?:\.\d+)?)\s*(ft)\b',
        r'(\d+(?:\.\d+)?)\s*(sq\s*ft)\b',
        r'(\d+(?:\.\d+)?)\s*(cup)\b',
    ]
    
    results = []
    for pattern in patterns:
        matches = re.findall(pattern, title)
        for m in matches:
            results.append((float(m[0]), m[1].lower().strip()))
    
    return results

def analyze_pack_match(sup_title, amz_title):
    """
    Thoroughly analyze pack size match between supplier and Amazon
    Returns: (pack_verdict, sup_pack, amz_pack, pack_ratio, notes)
    """
    sup_pack, sup_conf, sup_method = extract_pack_quantity(sup_title)
    amz_pack, amz_conf, amz_method = extract_pack_quantity(amz_title)
    
    # Calculate ratio
    if sup_pack > 0:
        pack_ratio = amz_pack / sup_pack
    else:
        pack_ratio = 1.0
    
    # Determine verdict
    if sup_pack == amz_pack:
        verdict = '1:1 Match'
        notes = ''
    elif pack_ratio > 1:
        verdict = f'Pack Mismatch ({sup_pack}→{amz_pack})'
        notes = f'Amazon sells {amz_pack}x vs Supplier {sup_pack}x (ratio: {pack_ratio:.1f}x)'
    else:
        verdict = f'Pack Mismatch ({sup_pack}→{amz_pack})'
        notes = f'Supplier sells more: {sup_pack}x vs Amazon {amz_pack}x'
    
    return (verdict, sup_pack, amz_pack, pack_ratio, notes)

def analyze_size_match(sup_title, amz_title):
    """
    Analyze size/weight match between supplier and Amazon
    Returns: (match, notes)
    """
    sup_sizes = extract_unit_size(sup_title)
    amz_sizes = extract_unit_size(amz_title)
    
    if not sup_sizes or not amz_sizes:
        return (None, '')
    
    # Group by unit type
    sup_dict = {}
    for val, unit in sup_sizes:
        sup_dict[unit] = val
    
    amz_dict = {}
    for val, unit in amz_sizes:
        amz_dict[unit] = val
    
    # Compare matching units
    mismatches = []
    for unit in set(sup_dict.keys()) & set(amz_dict.keys()):
        if sup_dict[unit] != amz_dict[unit]:
            mismatches.append(f'{unit}: {sup_dict[unit]} vs {amz_dict[unit]}')
    
    if mismatches:
        return (False, '; '.join(mismatches))
    
    return (True, '')

def calculate_adjusted_profit(row, pack_ratio, original_profit, sup_price, sell_price):
    """
    Calculate adjusted profit when pack sizes differ
    If Amazon sells 4x what supplier sells, multiply supplier cost by 4
    """
    if pack_ratio == 1.0:
        return original_profit
    
    # Recalculate based on pack ratio
    # If Amazon sells pack of 4 and supplier sells single, need 4 supplier units
    adjusted_cost = sup_price * pack_ratio
    
    # Estimate FBA fees as ~30% of selling price (rough approximation)
    fba_fees = sell_price * 0.30
    
    adjusted_profit = sell_price - adjusted_cost - fba_fees
    
    return adjusted_profit

def format_currency(val):
    """Format value as currency"""
    if pd.isna(val) or val is None:
        return "-"
    return f"£{float(val):.2f}"

# =====================================
# USER'S VERIFIED ASINs (from their review)
# =====================================

USER_HIGHLY_LIKELY_ASINS = {
    'B01CMHNDKC',  # BLUE CANYON ROUND WALL MIRROR
    'B0DN1HXF9B',  # PYREX AIR FRYER SQUARE DISH
    'B006A7D1O4',  # ROLSON PLASTERING TROWEL
    'B08G1Q1L46',  # BAKER & SALT SWISS ROLL TRAY
    'B07NNY768K',  # FALCON ENAMEL ROUND PIE DISH
    'B0815B7FBY',  # HARRIS PUTTY KNIFE
    'B0BYKDX25N',  # FAIRY MAX POWER SOAP DISPENSING DISH BRUSH
}

USER_FALSE_POSITIVES = {350, 861, 1243, 1386}
USER_SPEC_MISMATCH_ROWS = {1155, 1402, 971}

# =====================================
# METICULOUS ANALYSIS
# =====================================

print("Performing meticulous analysis of all rows...")

results = []
for idx, row in df.iterrows():
    row_id = row['RowID']
    sup_title = str(row.get('SupplierTitle', ''))
    amz_title = str(row.get('AmazonTitle', ''))
    
    # Get values
    sup_ean = row['EAN_clean']
    amz_ean = row['EAN_OnPage_clean']
    asin = row.get('ASIN', '')
    sup_price = row.get('SupplierPrice_incVAT', row.get('SupplierPrice', 0))
    sell_price = row.get('SellingPrice_incVAT', row.get('SellingPrice', 0))
    profit = row.get('NetProfit', 0)
    roi = row.get('ROI', 0)
    sales = row.get('sales_numeric', row.get('bought_in_past_month', 0))
    
    if pd.isna(profit): profit = 0
    if pd.isna(roi): roi = 0
    if pd.isna(sales): sales = 0
    if pd.isna(sup_price): sup_price = 0
    if pd.isna(sell_price): sell_price = 0
    
    # Analysis
    exact_ean = eans_match(row)
    sim = title_similarity(sup_title, amz_title)
    
    sup_brand = get_brand_from_title(sup_title)
    amz_brand = get_brand_from_title(amz_title)
    brand_match = sup_brand and amz_brand and (
        sup_brand == amz_brand or 
        sup_brand in str(amz_title).upper() or 
        amz_brand in str(sup_title).upper()
    )
    
    # METICULOUS PACK ANALYSIS
    pack_verdict, sup_pack, amz_pack, pack_ratio, pack_notes = analyze_pack_match(sup_title, amz_title)
    size_match, size_notes = analyze_size_match(sup_title, amz_title)
    
    # Calculate adjusted profit
    if pack_ratio != 1.0:
        adjusted_profit = calculate_adjusted_profit(row, pack_ratio, profit, sup_price, sell_price)
    else:
        adjusted_profit = profit
    
    # Determine category with meticulous analysis
    category = 'NEEDS_VERIFICATION'
    confidence = 0
    verdict = 'NEEDS VERIFICATION'
    evidence = ''
    risks = ''
    
    # Check for false positives first
    if row_id in USER_FALSE_POSITIVES:
        category = 'FALSE_POSITIVE'
        confidence = 0
        verdict = 'FALSE POSITIVE'
        evidence = f'Similarity={sim:.2f}'
        risks = 'Completely unrelated products'
    
    # EXACT EAN MATCH - but still check pack sizes!
    elif exact_ean:
        evidence = f'Exact EAN match ({sup_ean})'
        
        if pack_ratio == 1.0:
            if profit > 0:
                category = 'VERIFIED'
                confidence = 95
                verdict = 'VERIFIED (Exact EAN, 1:1 Pack)'
                risks = ''
            else:
                category = 'VERIFIED_FILTERED'
                confidence = 85
                verdict = 'VERIFIED (Exact EAN) - Low Profit'
                risks = f'NetProfit=£{profit:.2f}'
        else:
            # EAN matches but pack differs - needs careful attention
            if adjusted_profit > 0:
                category = 'VERIFIED_PACK_MISMATCH'
                confidence = 85
                verdict = 'VERIFIED (Exact EAN, Pack Mismatch)'
                risks = pack_notes
            else:
                category = 'VERIFIED_FILTERED'
                confidence = 75
                verdict = 'VERIFIED (Exact EAN) - Pack Issue, Low Adj. Profit'
                risks = f'{pack_notes}; Adj. Profit=£{adjusted_profit:.2f}'
    
    # User verified HIGHLY LIKELY
    elif asin in USER_HIGHLY_LIKELY_ASINS:
        category = 'HIGHLY_LIKELY'
        confidence = 80
        verdict = 'HIGHLY LIKELY'
        evidence = f'Similarity={sim:.2f}; Brand aligned'
        risks = 'Verify variant before purchasing'
    
    # Check for spec mismatches flagged by user
    elif row_id in USER_SPEC_MISMATCH_ROWS:
        category = 'NEEDS_VERIFICATION'
        confidence = 50
        verdict = 'NEEDS VERIFICATION (Spec Mismatch)'
        evidence = f'Similarity={sim:.2f}'
        risks = 'Known spec mismatch'
    
    # BRAND MATCH WITH PACK DIFFERENCE - HIGHLY LIKELY candidates
    # This catches cases like KILROCK
    elif brand_match and sim >= 0.4 and profit > 0:
        if pack_ratio != 1.0 and adjusted_profit > 0:
            category = 'HIGHLY_LIKELY_PACK_DIFF'
            confidence = 75
            verdict = 'HIGHLY LIKELY (Brand Match, Pack Diff)'
            evidence = f'Similarity={sim:.2f}; Same brand: {sup_brand}'
            risks = f'{pack_notes}; Verify pack/variant'
        elif pack_ratio == 1.0:
            category = 'HIGHLY_LIKELY_CANDIDATE'
            confidence = 70
            verdict = 'POSSIBLY HIGH LIKELIHOOD'
            evidence = f'Similarity={sim:.2f}; Brand: {sup_brand}'
            risks = 'Manual verification recommended'
        else:
            category = 'NEEDS_VERIFICATION'
            confidence = 55
            evidence = f'Similarity={sim:.2f}'
            risks = 'Brand match but pack/profit unclear'
    
    # Everything else
    else:
        category = 'NEEDS_VERIFICATION'
        if sim >= 0.5:
            confidence = 45
        elif sim >= 0.4:
            confidence = 40
        else:
            confidence = 20
        evidence = f'Similarity={sim:.2f}'
        risks = 'Moderate/low similarity'
    
    results.append({
        'RowID': row_id,
        'Category': category,
        'Verdict': verdict,
        'Confidence': confidence,
        'SupplierTitle': sup_title,
        'AmazonTitle': amz_title,
        'Supplier_EAN': sup_ean if is_valid_ean(sup_ean) else '-',
        'Amazon_EAN': amz_ean if is_valid_ean(amz_ean) else '-',
        'ASIN': asin,
        'SupplierPrice': sup_price,
        'SellingPrice': sell_price,
        'NetProfit': profit,
        'ROI': roi,
        'Sales': sales,
        'Pack_Verdict': pack_verdict,
        'Sup_Pack': sup_pack,
        'Amz_Pack': amz_pack,
        'Pack_Ratio': pack_ratio,
        'Adjusted_Profit': adjusted_profit,
        'Evidence': evidence,
        'Risks': risks,
        'Similarity': sim,
        'Brand': sup_brand,
        'Brand_Match': brand_match,
    })

results_df = pd.DataFrame(results)

# =====================================
# GENERATE METICULOUS REPORT
# =====================================

print("Generating meticulous report...")

report_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\METICULOUS_ANALYSIS_REPORT_v3.md'

with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# METICULOUS FBA ANALYSIS REPORT (v3)\n\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"**Source Data:** PART3.xlsx (1411 rows)\n\n")
    f.write("**Key Improvements in This Version:**\n")
    f.write("- Thorough pack size analysis for ALL rows including EAN matches\n")
    f.write("- Adjusted Profit calculation when pack sizes differ\n")
    f.write("- Brand matches with pack differences included in HIGHLY LIKELY\n")
    f.write("- Meticulous verification of every product\n\n")
    f.write("---\n\n")
    
    # Categorize
    verified_ok = results_df[results_df['Category'] == 'VERIFIED']
    verified_pack = results_df[results_df['Category'] == 'VERIFIED_PACK_MISMATCH']
    verified_filtered = results_df[results_df['Category'] == 'VERIFIED_FILTERED']
    highly_likely = results_df[results_df['Category'] == 'HIGHLY_LIKELY']
    highly_likely_pack = results_df[results_df['Category'] == 'HIGHLY_LIKELY_PACK_DIFF']
    highly_likely_cand = results_df[results_df['Category'] == 'HIGHLY_LIKELY_CANDIDATE']
    needs_verify = results_df[results_df['Category'] == 'NEEDS_VERIFICATION']
    false_positives = results_df[results_df['Category'] == 'FALSE_POSITIVE']
    
    # Summary
    f.write("## EXECUTIVE SUMMARY\n\n")
    f.write("| Category | Count | Description |\n")
    f.write("|:---|---:|:---|\n")
    f.write(f"| **VERIFIED (Exact EAN, 1:1 Pack)** | {len(verified_ok)} | Perfect match |\n")
    f.write(f"| **VERIFIED (Exact EAN, Pack Mismatch)** | {len(verified_pack)} | Same product, different pack size |\n")
    f.write(f"| **HIGHLY LIKELY (User Verified)** | {len(highly_likely)} | Strong non-EAN match |\n")
    f.write(f"| **HIGHLY LIKELY (Brand Match, Pack Diff)** | {len(highly_likely_pack)} | Same brand, pack adjustment needed |\n")
    f.write(f"| POSSIBLY HIGH LIKELIHOOD | {len(highly_likely_cand)} | Strong signals, needs verification |\n")
    f.write(f"| VERIFIED - Filtered (Low Profit) | {len(verified_filtered)} | EAN match but not profitable |\n")
    f.write(f"| NEEDS VERIFICATION | {len(needs_verify)} | Uncertain |\n")
    f.write(f"| FALSE POSITIVES | {len(false_positives)} | Obvious mismatches |\n")
    total_actionable = len(verified_ok) + len(verified_pack) + len(highly_likely) + len(highly_likely_pack)
    f.write(f"| **Total Actionable** | {total_actionable} | |\n")
    f.write("\n---\n\n")
    
    # Table header for all sections
    table_header = "| RowID | Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks / Notes |\n"
    table_divider = "| ----: | :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |\n"
    
    def write_row(f, row):
        adj_profit = f"£{row['Adjusted_Profit']:.2f}" if row['Adjusted_Profit'] != row['NetProfit'] else f"£{row['NetProfit']:.2f}"
        f.write(f"| {row['RowID']} | {row['Verdict']} | {row['Confidence']} | {row['SupplierTitle'][:60]} | {row['AmazonTitle'][:60]} | {row['Supplier_EAN']} | {row['Amazon_EAN']} | {row['ASIN']} | £{row['SupplierPrice']:.2f} | £{row['SellingPrice']:.2f} | £{row['NetProfit']:.2f} | {row['ROI']:.1f}% | {int(row['Sales'])} | {row['Pack_Verdict']} | {adj_profit} | {row['Evidence']} | {row['Risks']} |\n")
    
    # =====================================
    # SECTION 1: VERIFIED (1:1 Pack)
    # =====================================
    f.write("## 1. VERIFIED (Exact EAN, 1:1 Pack Match)\n\n")
    f.write(f"**{len(verified_ok)} products** with exact EAN match AND matching pack sizes.\n\n")
    
    if len(verified_ok) > 0:
        f.write(table_header)
        f.write(table_divider)
        for _, row in verified_ok.sort_values('NetProfit', ascending=False).iterrows():
            write_row(f, row)
    
    f.write("\n---\n\n")
    
    # =====================================
    # SECTION 2: VERIFIED (Pack Mismatch)
    # =====================================
    f.write("## 2. VERIFIED (Exact EAN, Pack Mismatch) — Requires Pack Adjustment\n\n")
    f.write(f"**{len(verified_pack)} products** with exact EAN match BUT different pack sizes.\n")
    f.write("*Adjusted Profit is calculated based on the pack ratio.*\n\n")
    
    if len(verified_pack) > 0:
        f.write(table_header)
        f.write(table_divider)
        for _, row in verified_pack.sort_values('Adjusted_Profit', ascending=False).iterrows():
            write_row(f, row)
    
    f.write("\n---\n\n")
    
    # =====================================
    # SECTION 3: HIGHLY LIKELY (User Verified)
    # =====================================
    f.write("## 3. HIGHLY LIKELY (Non-EAN, User Verified)\n\n")
    f.write(f"**{len(highly_likely)} products** verified by user as strong matches.\n\n")
    
    if len(highly_likely) > 0:
        f.write(table_header)
        f.write(table_divider)
        for _, row in highly_likely.sort_values('NetProfit', ascending=False).iterrows():
            write_row(f, row)
    
    f.write("\n---\n\n")
    
    # =====================================
    # SECTION 4: HIGHLY LIKELY (Brand Match, Pack Diff)
    # =====================================
    f.write("## 4. HIGHLY LIKELY (Brand Match, Pack Difference)\n\n")
    f.write(f"**{len(highly_likely_pack)} products** with same brand but different pack sizes.\n")
    f.write("*These are strong matches that require pack adjustment.*\n\n")
    
    if len(highly_likely_pack) > 0:
        f.write(table_header)
        f.write(table_divider)
        for _, row in highly_likely_pack.sort_values('Adjusted_Profit', ascending=False).head(50).iterrows():
            write_row(f, row)
    
    f.write("\n---\n\n")
    
    # =====================================
    # SECTION 5: POSSIBLY HIGH LIKELIHOOD
    # =====================================
    f.write("## 5. POSSIBLY HIGH LIKELIHOOD (Strong Signals)\n\n")
    f.write(f"**{len(highly_likely_cand)} products** with strong brand/type match.\n\n")
    
    if len(highly_likely_cand) > 0:
        f.write(table_header)
        f.write(table_divider)
        for _, row in highly_likely_cand.sort_values('NetProfit', ascending=False).head(30).iterrows():
            write_row(f, row)
    
    f.write("\n---\n\n")
    
    # =====================================
    # FILTERED OUT: VERIFIED Low Profit
    # =====================================
    f.write("## FILTERED OUT: VERIFIED (Low/Negative Profit)\n\n")
    f.write(f"**{len(verified_filtered)} products** with exact EAN but not profitable.\n\n")
    
    if len(verified_filtered) > 0:
        f.write(table_header)
        f.write(table_divider)
        for _, row in verified_filtered.iterrows():
            write_row(f, row)
    
    f.write("\n---\n\n")
    
    # =====================================
    # FILTERED OUT: FALSE POSITIVES
    # =====================================
    f.write("## FILTERED OUT: FALSE POSITIVES\n\n")
    f.write(f"**{len(false_positives)} products** flagged as obvious mismatches.\n\n")
    
    if len(false_positives) > 0:
        f.write("| RowID | SupplierTitle | AmazonTitle | ASIN | Evidence | Reason |\n")
        f.write("| ---: | :--- | :--- | :--- | :--- | :--- |\n")
        for _, row in false_positives.iterrows():
            f.write(f"| {row['RowID']} | {row['SupplierTitle'][:50]} | {row['AmazonTitle'][:50]} | {row['ASIN']} | {row['Evidence']} | {row['Risks']} |\n")
    
    f.write("\n---\n\n")
    
    # =====================================
    # RECONCILIATION
    # =====================================
    f.write("## RECONCILIATION PROOF\n\n")
    f.write("| Category | Count |\n")
    f.write("|:---|---:|\n")
    f.write(f"| Total Input Rows | 1411 |\n")
    f.write(f"| VERIFIED (1:1 Pack) | {len(verified_ok)} |\n")
    f.write(f"| VERIFIED (Pack Mismatch) | {len(verified_pack)} |\n")
    f.write(f"| HIGHLY LIKELY (User Verified) | {len(highly_likely)} |\n")
    f.write(f"| HIGHLY LIKELY (Brand, Pack Diff) | {len(highly_likely_pack)} |\n")
    f.write(f"| POSSIBLY HIGH LIKELIHOOD | {len(highly_likely_cand)} |\n")
    f.write(f"| VERIFIED - Filtered | {len(verified_filtered)} |\n")
    f.write(f"| NEEDS VERIFICATION | {len(needs_verify)} |\n")
    f.write(f"| FALSE POSITIVES | {len(false_positives)} |\n")
    total = len(verified_ok) + len(verified_pack) + len(highly_likely) + len(highly_likely_pack) + len(highly_likely_cand) + len(verified_filtered) + len(needs_verify) + len(false_positives)
    f.write(f"| **TOTAL** | **{total}** |\n")
    
    f.write("\n---\n\n")
    f.write("*Report generated with meticulous pack size analysis and adjusted profit calculations.*\n")

print(f"\nReport saved to: {report_path}")

# Print summary
print("\n" + "=" * 80)
print("METICULOUS ANALYSIS SUMMARY")
print("=" * 80)
print(f"  VERIFIED (1:1 Pack): {len(verified_ok)}")
print(f"  VERIFIED (Pack Mismatch): {len(verified_pack)}")
print(f"  HIGHLY LIKELY (User Verified): {len(highly_likely)}")
print(f"  HIGHLY LIKELY (Brand, Pack Diff): {len(highly_likely_pack)}")
print(f"  POSSIBLY HIGH LIKELIHOOD: {len(highly_likely_cand)}")
print(f"  VERIFIED - Filtered: {len(verified_filtered)}")
print(f"  NEEDS VERIFICATION: {len(needs_verify)}")
print(f"  FALSE POSITIVES: {len(false_positives)}")
print(f"\n  Total Actionable: {total_actionable}")

# Print detailed pack analysis for EAN matches
print("\n" + "=" * 80)
print("PACK ANALYSIS FOR EAN MATCHES")
print("=" * 80)
ean_matches = results_df[results_df['Category'].str.startswith('VERIFIED')]
for _, row in ean_matches.iterrows():
    status = "✓ 1:1" if row['Pack_Ratio'] == 1.0 else f"⚠ {row['Pack_Ratio']:.1f}x"
    print(f"Row {row['RowID']:4d}: {status} | Sup:{row['Sup_Pack']}→Amz:{row['Amz_Pack']} | Orig:£{row['NetProfit']:.2f} Adj:£{row['Adjusted_Profit']:.2f}")
    print(f"         {row['SupplierTitle'][:50]}")
    print(f"         {row['AmazonTitle'][:50]}")
