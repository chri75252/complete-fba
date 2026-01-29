"""
Independent analysis of report products - NOT trusting report categorizations.
Analyzes each row based on actual title/EAN/product data.
Uses ASIN matching for reports without RowID.
OUTPUTS TO FILE for complete results.
"""
import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
import sys

# Redirect output to file
output_file = open('analysis_results.txt', 'w', encoding='utf-8')
def print_out(*args, **kwargs):
    print(*args, **kwargs)
    print(*args, **kwargs, file=output_file)

# Load source data
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx')
df['RowID'] = df.index + 1

# Clean EANs
df['EAN_clean'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage_clean'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

def is_valid_ean(ean):
    if pd.isna(ean) or str(ean).strip() in ['nan', '', 'None', 'NaN', '0', '-']:
        return False
    s = str(ean).strip()
    return s.isdigit() and len(s) >= 8

def eans_match(row):
    ean1 = row['EAN_clean']
    ean2 = row['EAN_OnPage_clean']
    return is_valid_ean(ean1) and is_valid_ean(ean2) and ean1 == ean2

def title_similarity(t1, t2):
    if pd.isna(t1) or pd.isna(t2):
        return 0.0
    return SequenceMatcher(None, str(t1).lower(), str(t2).lower()).ratio()

def get_brand_from_title(title):
    if pd.isna(title):
        return ""
    return str(title).upper().split()[0] if str(title).split() else ""

def extract_pack_count(title):
    if pd.isna(title):
        return 1
    title = str(title).lower()
    patterns = [
        r'pack of (\d+)',
        r'(\d+)\s*pack\b',
        r'(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*x\s+\d',
        r'x\s*(\d+)\b',
    ]
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = int(match.group(1))
            if 1 < qty < 500:
                return qty
    return 1

def get_core_product_type(title):
    if pd.isna(title):
        return set()
    
    title = str(title).lower()
    product_types = [
        'bowl', 'dish', 'plate', 'cup', 'glass', 'mug', 'jar', 'bottle', 'container',
        'tray', 'pan', 'pot', 'knife', 'fork', 'spoon', 'brush', 'sponge', 'cloth',
        'bag', 'liner', 'foil', 'gloves', 'torch', 'light', 'lamp', 'candle',
        'hammer', 'screwdriver', 'pliers', 'wrench', 'spanner', 'saw', 'drill',
        'tape', 'glue', 'paint', 'roller', 'mirror', 'mat', 'rug',
        'towel', 'tissue', 'napkin', 'cleaner', 'spray', 'diffuser', 'freshener',
        'cable', 'charger', 'adapter', 'socket', 'extension', 'lead',
        'hat', 'glove', 'sock', 'scarf', 'backpack', 'wallet', 'purse',
        'plaque', 'frame', 'holder', 'stand', 'rack', 'hook', 'bracket',
        'kettle', 'toaster', 'blender', 'mixer', 'fryer', 'oven', 'grill',
        'sack', 'stocking', 'decoration', 'ornament', 'bauble',
        'trowel', 'shovel', 'rake', 'hose', 'sprayer', 'secateurs',
        'carafe', 'decanter', 'shaker', 'grinder', 'mortar', 'pestle',
        'teapot', 'kettle', 'jug', 'pitcher', 'vase', 'pot', 'planter',
        'bin', 'basket', 'box', 'case', 'caddy', 'organizer', 'storage',
        'clock', 'watch', 'timer', 'thermometer', 'scale', 'measure',
    ]
    
    found = set()
    for pt in product_types:
        if pt in title:
            found.add(pt)
    return found

def analyze_match(row):
    sup_title = str(row.get('SupplierTitle', ''))
    amz_title = str(row.get('AmazonTitle', ''))
    profit = row.get('NetProfit', 0)
    if pd.isna(profit):
        profit = 0
    
    exact_ean = eans_match(row)
    sim = title_similarity(sup_title, amz_title)
    
    sup_brand = get_brand_from_title(sup_title)
    amz_brand = get_brand_from_title(amz_title)
    brand_match = sup_brand and amz_brand and (sup_brand == amz_brand or sup_brand in amz_title.upper() or amz_brand in sup_title.upper())
    
    sup_types = get_core_product_type(sup_title)
    amz_types = get_core_product_type(amz_title)
    type_overlap = len(sup_types & amz_types)
    
    sup_pack = extract_pack_count(sup_title)
    amz_pack = extract_pack_count(amz_title)
    pack_match = sup_pack == amz_pack
    pack_ratio = amz_pack / sup_pack if sup_pack > 0 else 1
    
    # VALID: Exact EAN match + profitable
    if exact_ean:
        if profit > 0:
            if pack_match or pack_ratio <= 1.5:
                return 'VALID', 'Exact EAN match, profitable, pack OK'
            else:
                return 'NEEDS_VERIFICATION', f'Exact EAN but pack mismatch ({sup_pack} vs {amz_pack})'
        else:
            return 'NEEDS_VERIFICATION', 'Exact EAN but not profitable'
    
    # Non-EAN matches
    if brand_match and type_overlap >= 1 and sim >= 0.5:
        if pack_match and profit > 0:
            return 'HIGHLY_LIKELY', f'Brand+type match, sim={sim:.2f}, profitable'
        else:
            return 'NEEDS_VERIFICATION', f'Brand+type match but pack/profit issue'
    
    if brand_match and sim >= 0.6:
        if profit > 0:
            return 'HIGHLY_LIKELY', f'Brand match, high sim={sim:.2f}'
        else:
            return 'NEEDS_VERIFICATION', f'Brand match, high sim but not profitable'
    
    if type_overlap >= 2 and sim >= 0.45:
        return 'NEEDS_VERIFICATION', f'Multiple type matches, sim={sim:.2f}'
    
    if sim >= 0.7:
        return 'NEEDS_VERIFICATION', f'High title sim={sim:.2f}'
    
    if brand_match or type_overlap >= 1:
        if sim >= 0.35:
            return 'NEEDS_VERIFICATION', f'Partial match (brand/type), sim={sim:.2f}'
    
    return 'INVALID', f'No strong match signals, sim={sim:.2f}'

# =====================================
# EXTRACT ASINs FROM EACH REPORT
# =====================================

def extract_asins_from_md(filepath):
    asins = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = r'\b(B[A-Z0-9]{9})\b'
    matches = re.findall(pattern, content)
    for m in matches:
        asins.add(m)
    return asins

def extract_row_ids_from_md(filepath):
    row_ids = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = r'\|\s*(\d+)\s*\|'
    matches = re.findall(pattern, content)
    for m in matches:
        try:
            rid = int(m)
            if 1 <= rid <= 2000:
                row_ids.add(rid)
        except:
            pass
    return row_ids

gpt_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 4 2.9\gpt PHASEA_MANUAL_REPORT_20251225 (1).md'
gemini_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 4 2.9\gemini PHASEA_MANUAL_REPORT_20251225.md'
codex_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 4 2.9\codex PHASEA_MANUAL_REPORT_20251225.md'

# Extract ASINs from all reports (more reliable)
gpt_asins = extract_asins_from_md(gpt_path)
gemini_asins = extract_asins_from_md(gemini_path)
codex_asins = extract_asins_from_md(codex_path)

# Map ASINs to RowIDs
asin_to_rowid = dict(zip(df['ASIN'], df['RowID']))

gpt_row_ids = set(asin_to_rowid[a] for a in gpt_asins if a in asin_to_rowid)
gemini_row_ids = set(asin_to_rowid[a] for a in gemini_asins if a in asin_to_rowid)
codex_row_ids = set(asin_to_rowid[a] for a in codex_asins if a in asin_to_rowid)

print_out("=" * 80)
print_out("INDEPENDENT ANALYSIS OF REPORT PRODUCTS")
print_out("=" * 80)
print_out(f"\nASINs extracted from reports (mapped to RowIDs):")
print_out(f"  GPT Report: {len(gpt_row_ids)} unique products")
print_out(f"  Gemini Report: {len(gemini_row_ids)} unique products")
print_out(f"  Codex Report: {len(codex_row_ids)} unique products")

# =====================================
# ANALYZE ALL ROWS IN SOURCE DATA
# =====================================

results = []
for idx, row in df.iterrows():
    row_id = row['RowID']
    category, reason = analyze_match(row)
    results.append({
        'RowID': row_id,
        'ASIN': row['ASIN'],
        'Category': category,
        'Reason': reason,
        'SupplierTitle': str(row['SupplierTitle'])[:60],
        'AmazonTitle': str(row['AmazonTitle'])[:60],
        'EAN_match': eans_match(row),
        'NetProfit': row.get('NetProfit', 0),
        'In_GPT': row_id in gpt_row_ids,
        'In_Gemini': row_id in gemini_row_ids,
        'In_Codex': row_id in codex_row_ids,
    })

results_df = pd.DataFrame(results)

valid_rows = results_df[results_df['Category'] == 'VALID']['RowID'].tolist()
likely_rows = results_df[results_df['Category'] == 'HIGHLY_LIKELY']['RowID'].tolist()
verify_rows = results_df[results_df['Category'] == 'NEEDS_VERIFICATION']['RowID'].tolist()
invalid_rows = results_df[results_df['Category'] == 'INVALID']['RowID'].tolist()

print_out("\n" + "=" * 80)
print_out("MY INDEPENDENT CATEGORIZATION OF ALL 1411 ROWS")
print_out("=" * 80)
print_out(f"\nTotal Rows Analyzed: {len(df)}")
print_out(f"\n=== MY INDEPENDENT CATEGORIZATION ===")
print_out(f"  1) VALID (Confirmed Good - EAN match + profitable): {len(valid_rows)}")
print_out(f"  2) HIGHLY_LIKELY (Non-EAN but strong title/brand match): {len(likely_rows)}")
print_out(f"  3) NEEDS_VERIFICATION (Possible match, uncertain): {len(verify_rows)}")
print_out(f"  4) INVALID (No Match/False Positive): {len(invalid_rows)}")

# =====================================
# REPORT COMPARISON
# =====================================

print_out("\n" + "=" * 80)
print_out("EACH REPORT'S CAPTURE RATE (Based on MY Independent Analysis)")
print_out("=" * 80)

reports = {'GPT': gpt_row_ids, 'Gemini': gemini_row_ids, 'Codex': codex_row_ids}

def count_captured(report_rows, category_rows):
    return len(set(report_rows) & set(category_rows))

print_out(f"\n{'Report':<12} | {'VALID':<15} | {'HIGHLY_LIKELY':<18} | {'NEEDS_VERIFY':<17} | {'INVALID(FP)':<12} | {'Total':<8}")
print_out("-" * 90)

for name, rows in reports.items():
    valid_cap = count_captured(rows, valid_rows)
    likely_cap = count_captured(rows, likely_rows)
    verify_cap = count_captured(rows, verify_rows)
    invalid_cap = count_captured(rows, invalid_rows)
    print_out(f"{name:<12} | {valid_cap:>3}/{len(valid_rows):<10} | {likely_cap:>3}/{len(likely_rows):<13} | {verify_cap:>3}/{len(verify_rows):<12} | {invalid_cap:<12} | {len(rows):<8}")

# =====================================
# DETAILED LIST OF VALID PRODUCTS
# =====================================

print_out("\n" + "=" * 80)
print_out(f"ALL {len(valid_rows)} VALID PRODUCTS (Confirmed Good Matches)")
print_out("=" * 80)

valid_df = results_df[results_df['Category'] == 'VALID']
for idx, row in valid_df.iterrows():
    gpt_mark = "Y" if row['In_GPT'] else "N"
    gem_mark = "Y" if row['In_Gemini'] else "N"
    cod_mark = "Y" if row['In_Codex'] else "N"
    print_out(f"Row {row['RowID']:4d} [GPT:{gpt_mark}] [GEM:{gem_mark}] [COD:{cod_mark}] ASIN={row['ASIN']}")
    print_out(f"    Supplier: {row['SupplierTitle']}")
    print_out(f"    Amazon: {row['AmazonTitle']}")

# =====================================
# DETAILED LIST OF HIGHLY LIKELY PRODUCTS
# =====================================

print_out("\n" + "=" * 80)
print_out(f"ALL {len(likely_rows)} HIGHLY LIKELY PRODUCTS")
print_out("=" * 80)

likely_df = results_df[results_df['Category'] == 'HIGHLY_LIKELY']
for idx, row in likely_df.iterrows():
    gpt_mark = "Y" if row['In_GPT'] else "N"
    gem_mark = "Y" if row['In_Gemini'] else "N"
    cod_mark = "Y" if row['In_Codex'] else "N"
    print_out(f"Row {row['RowID']:4d} [GPT:{gpt_mark}] [GEM:{gem_mark}] [COD:{cod_mark}] ASIN={row['ASIN']} | {row['Reason']}")
    print_out(f"    Supplier: {row['SupplierTitle']}")
    print_out(f"    Amazon: {row['AmazonTitle']}")

# =====================================
# FINAL SUMMARY
# =====================================

print_out("\n" + "=" * 80)
print_out("FINAL SUMMARY - WHICH REPORT HAS THE MOST VALID ENTRIES?")
print_out("=" * 80)

for name, rows in reports.items():
    valid_cap = count_captured(rows, valid_rows)
    likely_cap = count_captured(rows, likely_rows)
    verify_cap = count_captured(rows, verify_rows)
    invalid_cap = count_captured(rows, invalid_rows)
    
    print_out(f"\n=== {name.upper()} REPORT ===")
    print_out(f"  1) VALID captured: {valid_cap}/{len(valid_rows)} ({100*valid_cap/len(valid_rows) if valid_rows else 0:.1f}%)")
    print_out(f"  2) HIGHLY_LIKELY captured: {likely_cap}/{len(likely_rows)} ({100*likely_cap/len(likely_rows) if likely_rows else 0:.1f}%)")
    print_out(f"  3) NEEDS_VERIFICATION captured: {verify_cap}/{len(verify_rows)} ({100*verify_cap/len(verify_rows) if verify_rows else 0:.1f}%)")
    print_out(f"  False positives (INVALID included): {invalid_cap}")
    print_out(f"  Total rows in report: {len(rows)}")

# Show which VALID rows were missed by each report
print_out("\n" + "=" * 80)
print_out("VALID PRODUCTS MISSED BY EACH REPORT")
print_out("=" * 80)

for name, rows in reports.items():
    missed = set(valid_rows) - rows
    print_out(f"\n{name} missed {len(missed)} VALID products:")
    for rid in sorted(missed):
        r = results_df[results_df['RowID'] == rid].iloc[0]
        print_out(f"  Row {rid}: {r['SupplierTitle']}")

output_file.close()
print("Analysis complete. Results saved to analysis_results.txt")
