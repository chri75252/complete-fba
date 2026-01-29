"""
Comprehensive Cross-Report Analysis Script v2
Analyzes all products from all reports and generates a unified report with justifications
"""

import pandas as pd
import re
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher

def calculate_similarity(str1, str2):
    """Calculate title similarity percentage"""
    if not str1 or not str2:
        return 0
    s1 = str(str1).upper().strip()
    s2 = str(str2).upper().strip()
    return SequenceMatcher(None, s1, s2).ratio() * 100

# Base paths
BASE_DIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec")
COMP_DIR = BASE_DIR / "final comp" / "comprehensible"
SOURCE_FILE = BASE_DIR / "part_30_dec.xlsx"

# Load source data
print("Loading source data...")
df_source = pd.read_excel(SOURCE_FILE)
print(f"Source file has {len(df_source)} rows")
print(f"Columns: {df_source.columns.tolist()}")

# Create a master tracking dictionary
master_products = defaultdict(lambda: {
    'appearances': [],
    'categories': [],
    'scores': [],
    'row_data': None,
    'disputes': []
})

def extract_row_id(text):
    """Extract row ID from various formats"""
    if pd.isna(text):
        return None
    text = str(text)
    
    match = re.search(r'RowID\s*=?\s*(\d+)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    match = re.search(r'\[(\d+)\]', text)
    if match:
        return int(match.group(1))
    
    match = re.search(r'\(Row\s*(\d+)\)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    return None

def parse_report_file(filepath, report_name):
    """Parse a report file and extract all products with their categories"""
    products = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return products
    
    lines = content.split('\n')
    current_category = None
    
    category_markers = {
        'VERIFIED — RECOMMENDED': 'VERIFIED_REC',
        'VERIFIED - RECOMMENDED': 'VERIFIED_REC',
        '## VERIFIED': 'VERIFIED_REC',
        '## ✅ VERIFIED': 'VERIFIED_REC',
        'VERIFIED — FILTERED': 'VERIFIED_FO',
        'VERIFIED - FILTERED': 'VERIFIED_FO',
        '## ⚠️ VERIFIED': 'VERIFIED_FO',
        'HIGHLY LIKELY — RECOMMENDED': 'HIGHLY_LIKELY_REC',
        'HIGHLY LIKELY - RECOMMENDED': 'HIGHLY_LIKELY_REC',
        '## 🔷 HIGHLY LIKELY': 'HIGHLY_LIKELY_REC',
        'HIGHLY LIKELY — FILTERED': 'HIGHLY_LIKELY_FO',
        'HIGHLY LIKELY - FILTERED': 'HIGHLY_LIKELY_FO',
        'NEEDS VERIFICATION': 'NEEDS_VERIFICATION',
        '## 🔶 NEEDS': 'NEEDS_VERIFICATION',
        'FILTERED OUT': 'FILTERED_OUT',
        '## ❌ FILTERED': 'FILTERED_OUT',
    }
    
    for line in lines:
        # Check for category headers
        for marker, cat in category_markers.items():
            if marker.upper() in line.upper():
                current_category = cat
                break
        
        if not current_category:
            continue
        if '|' not in line:
            continue
        if '---' in line or 'Verdict' in line.lower() or 'evidence' in line.lower():
            continue
        
        row_id = extract_row_id(line)
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) > 2 and not row_id:
            for part in parts[1:4]:
                clean = part.replace('.0', '').strip()
                if clean.isdigit() and len(clean) <= 5:
                    try:
                        row_id = int(clean)
                        break
                    except:
                        pass
        
        ean = None
        asin = None
        for part in parts:
            part = part.strip()
            clean = part.replace('.0', '').replace('.', '')
            if re.match(r'^\d{12,14}$', clean):
                ean = clean
            if re.match(r'^B0[A-Z0-9]{8}$', part):
                asin = part
        
        score = None
        for part in parts:
            part = part.strip()
            try:
                val = float(part.replace('%', '').replace('£', ''))
                if 0 < val <= 100:
                    score = val
                    break
            except:
                pass
        
        if row_id or (ean and asin):
            products.append({
                'row_id': row_id,
                'ean': ean,
                'asin': asin,
                'category': current_category,
                'score': score,
                'report': report_name,
            })
    
    return products

# Parse all reports
print("\nParsing all reports...")

reports_to_parse = [
    (COMP_DIR / "PHASEA_MANUAL_REPORT_FINAL_COMBINED_20251231_v2.md", "COMBINED_v2"),
    (COMP_DIR / "PHASEA_MANUAL_REPORT_CODEX_FINAL_20251231.md", "CODEX_FINAL"),
    (COMP_DIR / "PHASEA_MANUAL_REPORT_FINAL.md", "MY_FINAL"),
    (COMP_DIR / "PHASEA_MANUAL_REPORT_FINAL_20251231.md", "FINAL_20251231"),
]

# Also check subdirectories
for subdir in BASE_DIR.iterdir():
    if subdir.is_dir() and subdir.name not in ['final comp', '__pycache__']:
        for file in subdir.glob("PHASEA*.md"):
            reports_to_parse.append((file, f"{subdir.name}"))

all_products = []
for filepath, name in reports_to_parse:
    if filepath.exists():
        products = parse_report_file(filepath, name)
        all_products.extend(products)
        print(f"  {name}: {len(products)} products found")

print(f"\nTotal product entries across all reports: {len(all_products)}")

# Build master product dictionary
for prod in all_products:
    key = prod['row_id'] if prod['row_id'] else None
    if key:
        master_products[key]['appearances'].append(prod['report'])
        master_products[key]['categories'].append(prod['category'])
        if prod['score']:
            master_products[key]['scores'].append(prod['score'])

# Identify disputed products
disputed_products = {}
for key, data in master_products.items():
    if isinstance(key, int):
        unique_cats = set(data['categories'])
        if len(unique_cats) > 1:
            disputed_products[key] = {
                'categories': list(unique_cats),
                'appearances': data['appearances'],
                'scores': data['scores']
            }

print(f"\nDisputed products: {len(disputed_products)}")

def get_safe_value(row, col, default=0):
    """Safely get a value from a row"""
    try:
        val = row.get(col)
        if pd.isna(val):
            return default
        return val
    except:
        return default

def classify_product_v4(row_idx, row):
    """Apply strict v4.0 criteria"""
    
    try:
        sup_ean = str(get_safe_value(row, 'EAN', '')).replace('.0', '').strip()
        amz_ean = str(get_safe_value(row, 'EAN_OnPage', '')).replace('.0', '').strip()
        
        # Correct column name for profit
        net_profit = get_safe_value(row, 'NetProfit', 0)
        
        # Correct column name for sales
        sales = int(get_safe_value(row, 'bought_in_past_month', 0))
        
        # Similarity - may not exist in all source files
        similarity = get_safe_value(row, 'Similarity', 0)
        if similarity == 0:
            similarity = get_safe_value(row, 'TitleSimilarity', 0)
        
        sup_title = str(get_safe_value(row, 'SupplierTitle', '')).upper()
        amz_title = str(get_safe_value(row, 'AmazonTitle', '')).upper()
        
        # Supplier price - correct column name
        sup_price = get_safe_value(row, 'SupplierPrice_incVAT', 0)
        if sup_price == 0:
            sup_price = get_safe_value(row, 'SupplierPrice_exVAT', 0)
        
    except Exception as e:
        return None, f"Error: {e}"
    
    # Pack detection
    pack_sup = 1
    pack_amz = 1
    pack_patterns = [
        r'(\d+)\s*(?:PACK|PK|PC|PCS|PIECE)',
        r'PACK\s*(?:OF\s*)?(\d+)',
        r'SET\s*(?:OF\s*)?(\d+)',
        r'X\s*(\d+)\b',
    ]
    
    for pattern in pack_patterns:
        match = re.search(pattern, sup_title)
        if match:
            pack_sup = max(pack_sup, int(match.group(1)))
        match = re.search(pattern, amz_title)
        if match:
            pack_amz = max(pack_amz, int(match.group(1)))
    
    # Calculate adjusted profit
    adj_profit = net_profit
    if pack_amz > pack_sup and sup_price > 0:
        adj_profit = net_profit - (sup_price * (pack_amz - pack_sup))
    elif pack_sup > pack_amz and pack_sup > 0:
        adj_profit = net_profit / pack_sup * pack_amz
    
    # EAN matching
    ean_match = False
    if sup_ean and amz_ean and len(sup_ean) >= 8 and len(amz_ean) >= 8:
        sup_clean = sup_ean.lstrip('0')
        amz_clean = amz_ean.lstrip('0')
        ean_match = sup_clean == amz_clean or sup_ean == amz_ean
    
    # Brand extraction and matching
    brands_to_check = ['AMTECH', 'PYREX', 'MASON CASH', 'TIDYZ', 'KILNER', 'EVERBUILD', 
                       'FALCON', 'PAN AROMA', 'CHEF AID', 'BLUE CANYON', 'HARRIS', 
                       'DRAPER', 'ROLSON', 'APOLLO', 'WHAM', 'BEAUFORT', 'FAIRY',
                       'EXTRA SELECT', 'MARIGOLD', 'ROUNDUP', 'SUPERIOR', 'ULTRATAPE',
                       'KILROCK', 'SOUDAL', 'BACOFOIL', 'EXTRASTAR', 'STATUS', 'QUEST',
                       'LITTLE TREES', 'SMART CHOICE', 'DOFF', 'BAKER & SALT', 'PRICE & KENSINGTON']
    
    brand_match = False
    matched_brand = None
    for brand in brands_to_check:
        if brand in sup_title and brand in amz_title:
            brand_match = True
            matched_brand = brand
            break
        elif brand in sup_title:
            # Check if any word from brand appears in Amazon title
            brand_words = brand.split()
            if any(w in amz_title for w in brand_words if len(w) > 3):
                brand_match = True
                matched_brand = brand
                break
    
    # Classification
    if ean_match and sales > 0:
        if adj_profit > 0:
            return 'VERIFIED_REC', f"Exact EAN, profit £{adj_profit:.2f}, {sales} sales"
        else:
            return 'VERIFIED_FO', f"Exact EAN but adj profit £{adj_profit:.2f} (pack {pack_amz}x vs {pack_sup}x)"
    
    if brand_match and similarity >= 50 and sales > 0:
        if adj_profit > 0:
            return 'HIGHLY_LIKELY_REC', f"{matched_brand} brand, {similarity:.0f}% sim, profit £{adj_profit:.2f}"
        else:
            return 'HIGHLY_LIKELY_FO', f"{matched_brand} brand but adj profit £{adj_profit:.2f}"
    
    if (similarity >= 45 or brand_match) and adj_profit > 0.5 and sales > 0:
        return 'NEEDS_VERIFICATION', f"{similarity:.0f}% similarity, needs EAN/pack confirm"
    
    if ean_match or (brand_match and similarity >= 40):
        if adj_profit <= 0 or sales <= 0:
            return 'FILTERED_OUT', f"Match confirmed but {'no sales' if sales <= 0 else f'profit £{adj_profit:.2f}'}"
    
    return None, "Does not meet criteria"

# Run classification on all rows
print("\nClassifying all products...")
final_classifications = defaultdict(list)
disputed_justifications = []

for idx, row in df_source.iterrows():
    row_id = idx + 2  # Excel is 1-indexed + header
    
    my_cat, my_reason = classify_product_v4(row_id, row)
    
    if my_cat is None:
        continue
    
    is_disputed = row_id in disputed_products
    
    product_info = {
        'row_id': row_id,
        'source_row': row,
        'category': my_cat,
        'reason': my_reason,
        'disputed': is_disputed
    }
    
    if is_disputed:
        product_info['other_categories'] = disputed_products[row_id]['categories']
        product_info['appearances'] = disputed_products[row_id]['appearances']
        disputed_justifications.append(product_info)
    
    final_classifications[my_cat].append(product_info)

print("\nFinal counts:")
for cat in ['VERIFIED_REC', 'VERIFIED_FO', 'HIGHLY_LIKELY_REC', 'HIGHLY_LIKELY_FO', 'NEEDS_VERIFICATION', 'FILTERED_OUT']:
    print(f"  {cat}: {len(final_classifications[cat])}")

# Generate the report
output_file = COMP_DIR / "COMPREHENSIVE_ANALYSIS_FINAL.md"

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# 📊 COMPREHENSIVE CROSS-REPORT ANALYSIS (FINAL)\n\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    f.write(f"**Source File:** part_30_dec.xlsx\n")
    f.write(f"**Reports Analyzed:** {len(reports_to_parse)}\n")
    f.write(f"**Disputed Products Reviewed:** {len(disputed_products)}\n\n")
    
    f.write("## v4.0 Distribution Guidance\n\n")
    f.write("| Category | Expected | Actual | Status |\n")
    f.write("|----------|----------|--------|--------|\n")
    v_rec = len(final_classifications['VERIFIED_REC'])
    hl_rec = len(final_classifications['HIGHLY_LIKELY_REC'])
    nv = len(final_classifications['NEEDS_VERIFICATION'])
    fo_total = len(final_classifications['FILTERED_OUT']) + len(final_classifications['VERIFIED_FO']) + len(final_classifications['HIGHLY_LIKELY_FO'])
    f.write(f"| VERIFIED (Rec) | 15-50 | {v_rec} | {'✅' if 15 <= v_rec <= 50 else '⚠️'} |\n")
    f.write(f"| HIGHLY LIKELY (Rec) | 30-100 | {hl_rec} | {'✅' if 30 <= hl_rec <= 100 else '⚠️'} |\n")
    f.write(f"| NEEDS VERIFICATION | 50-150 | {nv} | {'✅' if 50 <= nv <= 150 else '⚠️'} |\n")
    f.write(f"| FILTERED OUT | 20-100 | {fo_total} | {'✅' if 20 <= fo_total <= 100 else '⚠️'} |\n\n")
    
    f.write("## Summary Counts\n\n")
    f.write(f"- **VERIFIED — RECOMMENDED:** {len(final_classifications['VERIFIED_REC'])}\n")
    f.write(f"- **VERIFIED — FILTERED OUT:** {len(final_classifications['VERIFIED_FO'])}\n")
    f.write(f"- **HIGHLY LIKELY — RECOMMENDED:** {len(final_classifications['HIGHLY_LIKELY_REC'])}\n")
    f.write(f"- **HIGHLY LIKELY — FILTERED OUT:** {len(final_classifications['HIGHLY_LIKELY_FO'])}\n")
    f.write(f"- **NEEDS VERIFICATION:** {len(final_classifications['NEEDS_VERIFICATION'])}\n")
    f.write(f"- **FILTERED OUT (Audit):** {len(final_classifications['FILTERED_OUT'])}\n")
    total = sum(len(v) for v in final_classifications.values())
    f.write(f"- **TOTAL ANALYZED:** {total}\n\n")
    
    f.write("---\n\n")
    
    # Disputed Products Section
    f.write("## 🔍 DISPUTED PRODUCTS - JUSTIFICATIONS\n\n")
    f.write(f"**{len(disputed_justifications)} products appear in different categories across reports:**\n\n")
    
    for prod in sorted(disputed_justifications[:30], key=lambda x: x['row_id']):
        row = prod['source_row']
        sup_title = str(get_safe_value(row, 'SupplierTitle', ''))[:50]
        f.write(f"### Row {prod['row_id']}: {sup_title}\n\n")
        f.write(f"- **My Classification:** `{prod['category']}`\n")
        f.write(f"- **Other Reports Said:** `{', '.join(set(prod['other_categories']))}`\n")
        f.write(f"- **Seen In:** {', '.join(set(prod['appearances']))}\n")
        f.write(f"- **My Justification:** {prod['reason']}\n")
        
        other_cats = set(prod['other_categories'])
        my_cat = prod['category']
        
        if 'VERIFIED_REC' in other_cats and my_cat != 'VERIFIED_REC':
            if 'FO' in my_cat or 'FILTERED' in my_cat:
                f.write(f"\n  > ⚠️ **Downgraded because:** Pack size difference creates negative adjusted profit.\n")
            else:
                f.write(f"\n  > ⚠️ **Downgraded because:** EAN doesn't exactly match or profit too low.\n")
        
        if 'NEEDS_VERIFICATION' in other_cats and my_cat in ['VERIFIED_REC', 'HIGHLY_LIKELY_REC']:
            f.write(f"\n  > ✅ **Upgraded because:** Strong evidence (EAN match or brand+similarity) supports higher confidence.\n")
        
        if 'HIGHLY_LIKELY_REC' in other_cats and my_cat == 'VERIFIED_REC':
            f.write(f"\n  > ✅ **Upgraded because:** Exact EAN match confirmed.\n")
        
        f.write("\n")
    
    f.write("---\n\n")
    
    # VERIFIED RECOMMENDED
    f.write("## ✅ VERIFIED — RECOMMENDED\n\n")
    f.write(f"**{len(final_classifications['VERIFIED_REC'])} products with exact EAN match and positive profit**\n\n")
    f.write("```text\n")
    f.write(f"| {'RowID':>6} | {'SupplierTitle':<45} | {'Supplier EAN':<15} | {'Amazon EAN':<15} | {'Profit':>8} | {'Sales':>5} |\n")
    f.write(f"|{'-'*8}|{'-'*47}|{'-'*17}|{'-'*17}|{'-'*10}|{'-'*7}|\n")
    
    for prod in sorted(final_classifications['VERIFIED_REC'], key=lambda x: -float(get_safe_value(x['source_row'], 'NetProfit', 0)))[:50]:
        row = prod['source_row']
        f.write(f"| {prod['row_id']:>6} | {str(get_safe_value(row, 'SupplierTitle', ''))[:45]:<45} | {str(get_safe_value(row, 'EAN', ''))[:15]:<15} | {str(get_safe_value(row, 'EAN_OnPage', ''))[:15]:<15} | £{get_safe_value(row, 'NetProfit', 0):>6.2f} | {int(get_safe_value(row, 'Sales', 0)):>5} |\n")
    f.write("```\n\n")
    
    # VERIFIED FILTERED
    if final_classifications['VERIFIED_FO']:
        f.write("## ⚠️ VERIFIED — FILTERED OUT\n\n")
        f.write(f"**{len(final_classifications['VERIFIED_FO'])} products with exact EAN but unprofitable**\n\n")
        f.write("```text\n")
        f.write(f"| {'RowID':>6} | {'SupplierTitle':<45} | {'Reason':<55} |\n")
        f.write(f"|{'-'*8}|{'-'*47}|{'-'*57}|\n")
        
        for prod in final_classifications['VERIFIED_FO'][:30]:
            row = prod['source_row']
            f.write(f"| {prod['row_id']:>6} | {str(get_safe_value(row, 'SupplierTitle', ''))[:45]:<45} | {prod['reason'][:55]:<55} |\n")
        f.write("```\n\n")
    
    # HIGHLY LIKELY RECOMMENDED
    f.write("## 🔷 HIGHLY LIKELY — RECOMMENDED\n\n")
    f.write(f"**{len(final_classifications['HIGHLY_LIKELY_REC'])} products with strong brand/title match**\n\n")
    f.write("```text\n")
    f.write(f"| {'RowID':>6} | {'SupplierTitle':<45} | {'Brand Match':<20} | {'Profit':>8} | {'Sales':>5} |\n")
    f.write(f"|{'-'*8}|{'-'*47}|{'-'*22}|{'-'*10}|{'-'*7}|\n")
    
    for prod in sorted(final_classifications['HIGHLY_LIKELY_REC'], key=lambda x: -float(get_safe_value(x['source_row'], 'NetProfit', 0)))[:60]:
        row = prod['source_row']
        reason_short = prod['reason'].split(',')[0][:20] if ',' in prod['reason'] else prod['reason'][:20]
        f.write(f"| {prod['row_id']:>6} | {str(get_safe_value(row, 'SupplierTitle', ''))[:45]:<45} | {reason_short:<20} | £{get_safe_value(row, 'NetProfit', 0):>6.2f} | {int(get_safe_value(row, 'Sales', 0)):>5} |\n")
    f.write("```\n\n")
    
    # HIGHLY LIKELY FILTERED
    if final_classifications['HIGHLY_LIKELY_FO']:
        f.write("## ⚠️ HIGHLY LIKELY — FILTERED OUT\n\n")
        f.write(f"**{len(final_classifications['HIGHLY_LIKELY_FO'])} products with brand match but unprofitable**\n\n")
        f.write("```text\n")
        f.write(f"| {'RowID':>6} | {'SupplierTitle':<45} | {'Reason':<55} |\n")
        f.write(f"|{'-'*8}|{'-'*47}|{'-'*57}|\n")
        
        for prod in final_classifications['HIGHLY_LIKELY_FO'][:20]:
            row = prod['source_row']
            f.write(f"| {prod['row_id']:>6} | {str(get_safe_value(row, 'SupplierTitle', ''))[:45]:<45} | {prod['reason'][:55]:<55} |\n")
        f.write("```\n\n")
    
    # NEEDS VERIFICATION
    f.write("## 🔶 NEEDS VERIFICATION (Strict - 1-2 Confirmations Needed)\n\n")
    f.write(f"**{len(final_classifications['NEEDS_VERIFICATION'])} products requiring minor verification**\n\n")
    f.write("```text\n")
    f.write(f"| {'RowID':>6} | {'SupplierTitle':<45} | {'Profit':>8} | {'Sales':>5} | {'What to Verify':<35} |\n")
    f.write(f"|{'-'*8}|{'-'*47}|{'-'*10}|{'-'*7}|{'-'*37}|\n")
    
    for prod in sorted(final_classifications['NEEDS_VERIFICATION'], key=lambda x: -float(get_safe_value(x['source_row'], 'NetProfit', 0)))[:80]:
        row = prod['source_row']
        f.write(f"| {prod['row_id']:>6} | {str(get_safe_value(row, 'SupplierTitle', ''))[:45]:<45} | £{get_safe_value(row, 'NetProfit', 0):>6.2f} | {int(get_safe_value(row, 'Sales', 0)):>5} | {prod['reason'][:35]:<35} |\n")
    f.write("```\n\n")
    
    # FILTERED OUT
    f.write("## ❌ FILTERED OUT (Audit - Confirmed Unprofitable)\n\n")
    f.write(f"**{len(final_classifications['FILTERED_OUT'])} confirmed matches that are unprofitable**\n\n")
    f.write("```text\n")
    f.write(f"| {'RowID':>6} | {'SupplierTitle':<45} | {'Filter Reason':<55} |\n")
    f.write(f"|{'-'*8}|{'-'*47}|{'-'*57}|\n")
    
    for prod in final_classifications['FILTERED_OUT'][:40]:
        row = prod['source_row']
        f.write(f"| {prod['row_id']:>6} | {str(get_safe_value(row, 'SupplierTitle', ''))[:45]:<45} | {prod['reason'][:55]:<55} |\n")
    f.write("```\n\n")
    
    f.write("---\n\n")
    f.write("*Report generated from comprehensive cross-analysis of all AI model reports with consistent v4.0 criteria.*\n")

print(f"\nReport saved to: {output_file}")
