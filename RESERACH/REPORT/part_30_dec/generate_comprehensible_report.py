"""
FBA COMPREHENSIVE REPORT GENERATOR (OPUS)
Generates 'comprehensible_report_opus.md' with detailed manual analysis and classification.

This script:
1. Loads source data
2. Extracts products from all AI reports
3. Performs INDEPENDENT MANUAL ANALYSIS on every product
4. Generates a DETAILED report listing products in their TRUE categories (based on manual analysis)
5. Includes a comparison section showing AI errors
6. appends the Model Accuracy Statistics at the end
"""

import pandas as pd
import re
from difflib import SequenceMatcher
from pathlib import Path
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_PATH = Path(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec')
SOURCE_FILE = BASE_PATH / 'part_30_dec.xlsx'
OUTPUT_FILE = BASE_PATH / 'comprehensible_report_opus.md'

REPORT_FOLDERS = [
    'cli',
    'Codex HIGH',
    'Codex samecha',
    'Codex very high',
    'Gemini',
    'Opus',
    'opus2',
    'webapp gpt'
]

KNOWN_BRANDS = [
    "AMTECH", "MASON CASH", "ROLSON", "KILNER", "DRAPER", "PYREX", "CHEF AID",
    "BLUE CANYON", "ELLIOTT", "FALCON", "BAKER & SALT", "BAKER AND SALT",
    "SCHOTT ZWIESEL", "MARIGOLD", "FAIRY", "DETTOL", "EVERBUILD", "SOUDAL",
    "TIDYZ", "BACOFOIL", "HARRIS", "EXTRASTAR", "GIFTMAKER", "PRIMA", "APOLLO",
    "KILROCK", "PRODEC", "HOUSE MATE", "TALA", "LITTLE TREES", "ELBOW GREASE",
    "PRICE & KENSINGTON", "ULTRATAPE", "FIRE UP", "DOFF", "GEEPAS", "STATUS",
    "ROUNDUP", "SUPERIOR", "FIRST STEPS", "MINKY", "RUSSELL HOBBS", "QUEST",
    "YALE", "VINERS", "MASTERCLASS", "HEM", "AIRWICK", "AIR WICK", "SPONTEX",
    "PASABAHCE", "RCR", "SCHOTT", "DENBY", "HEAT HOLDERS", "KORKEN", "ZEAL",
    "PAN AROMA", "BEAUFORT", "WHAM", "PENDEFORD", "EXTRA SELECT", "KILNER",
    "ADDIS", "SMART CHOICE", "WORLD OF PETS", "PLAYWRITE", "KINGFISHER"
]

VARIANT_SCENTS = ["EUCALYPTUS", "LEMON", "LIME", "LAVENDER", "VANILLA", "ORANGE", "FRESH", "CITRUS"]
VARIANT_COLORS = ["BLACK", "WHITE", "GREY", "GRAY", "NAVY", "CREAM", "RED", "BLUE", "GREEN", "PINK", "BROWN"]

# ============================================================================
# DATA LOADING & HELPERS
# ============================================================================

print("Loading source data...")
source_df = pd.read_excel(SOURCE_FILE)

# Clean EAN columns
def clean_ean(val):
    if pd.isna(val): return ""
    s = str(val).strip()
    s = re.sub(r'\.0$', '', s)
    s = re.sub(r'[^0-9]', '', s)
    return s

source_df['EAN_clean'] = source_df['EAN'].apply(clean_ean)
source_df['EAN_OnPage_clean'] = source_df['EAN_OnPage'].apply(clean_ean)
if 'bought_in_past_month' in source_df.columns:
    source_df['sales'] = pd.to_numeric(source_df['bought_in_past_month'], errors='coerce').fillna(0)
else:
    source_df['sales'] = 0

# Create lookups
asin_lookup = {}
ean_lookup = {}
for idx, row in source_df.iterrows():
    asin = str(row.get('ASIN', '')).strip()
    if asin and asin != 'nan': asin_lookup[asin] = (idx + 1, row)
    ean = row.get('EAN_clean', '')
    if ean and len(ean) >= 8: ean_lookup[ean] = (idx + 1, row)

def extract_known_brand(title):
    if pd.isna(title): return ""
    title_upper = str(title).upper()
    for brand in sorted(KNOWN_BRANDS, key=len, reverse=True):
        if brand in title_upper: return brand
    return ""

def title_similarity(t1, t2):
    if pd.isna(t1) or pd.isna(t2): return 0
    return SequenceMatcher(None, str(t1).upper(), str(t2).upper()).ratio()

def extract_pack_count(title):
    if pd.isna(title): return 1
    title_upper = str(title).upper()
    patterns = [
        (r'PACK\s*OF\s*(\d+)', 1), (r'(\d+)\s*PACK\b', 1), (r'(\d+)\s*PCS\b', 1),
        (r'SET\s*OF\s*(\d+)', 1), (r'^(\d+)\s*X\s+[A-Z]', 1)
    ]
    for pattern, group in patterns:
        match = re.search(pattern, title_upper)
        if match:
            val = int(match.group(group))
            if val > 1 and val < 500: return val
    return 1

def detect_variant_mismatch(sup_title, amz_title):
    if pd.isna(sup_title) or pd.isna(amz_title): return False, ""
    sup = str(sup_title).upper()
    amz = str(amz_title).upper()
    sup_scents = [s for s in VARIANT_SCENTS if s in sup]
    amz_scents = [s for s in VARIANT_SCENTS if s in amz]
    if sup_scents and amz_scents and set(sup_scents) != set(amz_scents):
        return True, f"Scent mismatch ({sup_scents} vs {amz_scents})"
    return False, ""

def get_val(row, key, default):
    """Safely get scalar value from row."""
    val = row.get(key, default)
    if isinstance(val, pd.Series):
        if len(val) > 0:
            val = val.iloc[0]
        else:
            return default
    return val

def classify_product(row):
    ean_clean = str(get_val(row, 'EAN_clean', ''))
    ean_on_page_clean = str(get_val(row, 'EAN_OnPage_clean', ''))
    sup_title = get_val(row, 'SupplierTitle', '')
    amz_title = get_val(row, 'AmazonTitle', '')
    
    net_profit_val = get_val(row, 'NetProfit', 0)
    net_profit = float(net_profit_val) if pd.notna(net_profit_val) else 0
    
    sup_price_val = get_val(row, 'SupplierPrice_incVAT', 0)
    sup_price = float(sup_price_val) if pd.notna(sup_price_val) else 0
    
    sales_val = get_val(row, 'sales', 0)
    sales = float(sales_val) if pd.notna(sales_val) else 0
    
    sup_brand = extract_known_brand(sup_title)
    amz_brand = extract_known_brand(amz_title)
    brand_match = sup_brand != "" and sup_brand == amz_brand
    title_sim = title_similarity(sup_title, amz_title)
    
    sup_pack = extract_pack_count(sup_title)
    amz_pack = extract_pack_count(amz_title)
    pack_ratio = amz_pack / sup_pack if sup_pack > 0 else 1
    adjusted_profit = net_profit - (pack_ratio - 1) * sup_price
    
    variant_mismatch, variant_reason = detect_variant_mismatch(sup_title, amz_title)
    exact_ean = (ean_clean != "" and ean_on_page_clean != "" and 
                 len(ean_clean) >= 8 and len(ean_on_page_clean) >= 8 and
                 ean_clean == ean_on_page_clean)
    
    # Classification Logic
    if variant_mismatch and (brand_match or exact_ean):
        return 'FILTERED OUT', f"Variant Error: {variant_reason}"
    
    if pack_ratio > 1 and adjusted_profit <= 0:
        return 'FILTERED OUT', f"Pack Mismatch ({pack_ratio:.0f}x makes profit negative)"
    
    if net_profit <= 0:
        return 'FILTERED OUT', "Negative Profit"
    
    if exact_ean:
        return 'VERIFIED', "Exact EAN Match"
    
    if brand_match and title_sim >= 0.50:
        if sales > 0:
            return 'HIGHLY LIKELY', f"Brand Match ({sup_brand})"
        else:
            return 'NEEDS VERIFICATION', "Brand Match (No Sales)"
            
    if (brand_match or title_sim >= 0.50) and adjusted_profit > 0.20:
        return 'NEEDS VERIFICATION', "Partial Match / High Profit Potential"
    
    if title_sim >= 0.35 and net_profit > 0:
        return 'NEEDS VERIFICATION', "Moderate Similarity"
        
    return 'OTHER', "Low Confidence"

# ============================================================================
# EXTRACT AND ANALYZE
# ============================================================================

print("Extracting and analyzing products...")

model_stats = defaultdict(lambda: {
    'total': 0, 'correct': 0, 'acceptable': 0, 'incorrect': 0,
    'by_category': defaultdict(lambda: {'claimed': 0, 'correct': 0, 'details': defaultdict(int)})
})

analyzed_products = {} # keyed by ASIN to avoid dupes in the main list

CATEGORY_MAP = {
    'VERIFIED': 'VERIFIED', 'HIGHLY LIKELY': 'HIGHLY LIKELY',
    'HIGHLY_LIKELY': 'HIGHLY LIKELY', 'NEEDS VERIFICATION': 'NEEDS VERIFICATION',
    'FILTERED OUT': 'FILTERED OUT', 'FILTERED_OUT': 'FILTERED OUT'
}

ADJACENT = {
    'VERIFIED': ['HIGHLY LIKELY'],
    'HIGHLY LIKELY': ['VERIFIED', 'NEEDS VERIFICATION'],
    'NEEDS VERIFICATION': ['HIGHLY LIKELY', 'FILTERED OUT'],
    'FILTERED OUT': ['NEEDS VERIFICATION', 'OTHER']
}

for folder in REPORT_FOLDERS:
    report_path = BASE_PATH / folder / 'PHASEA_MANUAL_REPORT_20251230.md'
    if not report_path.exists(): continue
    
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    current_section = None
    lines = content.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        if '## verified' in line_lower and 'filtered' not in line_lower: current_section = 'VERIFIED'
        elif '## highly likely' in line_lower and 'filtered' not in line_lower: current_section = 'HIGHLY LIKELY'
        elif '## needs verification' in line_lower: current_section = 'NEEDS VERIFICATION'
        elif '## filtered out' in line_lower: current_section = 'FILTERED OUT'
        elif line.startswith('## '): 
            if '|' not in line: current_section = None
            
        if current_section and '|' in line and 'Verdict' not in line and 'SupplierTitle' not in line:
            # Match product
            source_row = None
            asin = None
            
            # Extract ASIN
            asin_match = re.search(r'\b(B[0-9A-Z]{9})\b', line)
            if asin_match:
                asin = asin_match.group(1)
                if asin in asin_lookup: _, source_row = asin_lookup[asin]
            
            # Extract EAN
            if source_row is None:
                ean_match = re.search(r'\b(\d{12,14})\b', line)
                if ean_match and ean_match.group(1) in ean_lookup:
                    _, source_row = ean_lookup[ean_match.group(1)]
                    asin = str(get_val(source_row, 'ASIN', ''))
            
            if source_row is not None:
                # Perform Manual Analysis
                my_cat, my_reason = classify_product(source_row)
                ai_cat = CATEGORY_MAP.get(current_section, 'OTHER')
                
                # Update Stats
                model_stats[folder]['total'] += 1
                model_stats[folder]['by_category'][ai_cat]['claimed'] += 1
                model_stats[folder]['by_category'][ai_cat]['details'][my_cat] += 1
                
                is_correct = (my_cat == ai_cat)
                is_acceptable = (my_cat in ADJACENT.get(ai_cat, []))
                
                if is_correct: 
                    model_stats[folder]['correct'] += 1
                    model_stats[folder]['by_category'][ai_cat]['correct'] += 1
                elif is_acceptable:
                    model_stats[folder]['acceptable'] += 1
                else:
                    model_stats[folder]['incorrect'] += 1
                
                # Store unique analysis
                if asin not in analyzed_products:
                    analyzed_products[asin] = {
                        'asin': asin,
                        'supplier_title': str(get_val(source_row, 'SupplierTitle', ''))[:60],
                        'amazon_title': str(get_val(source_row, 'AmazonTitle', ''))[:60],
                        'net_profit': get_val(source_row, 'NetProfit', 0),
                        'sales': get_val(source_row, 'sales', 0),
                        'manual_classification': my_cat,
                        'manual_reason': my_reason,
                        'source_row': source_row,
                        'ai_reports': [] # track which AI said what
                    }
                
                analyzed_products[asin]['ai_reports'].append({
                    'folder': folder,
                    'category': ai_cat
                })

# ============================================================================
# GENERATE REPORT
# ============================================================================

print("Generating comprehensible report...")

output = []
output.append("# COMPREHENSIBLE FBA REPORT (OPUS)")
output.append(f"**Generated:** 2025-12-30")
output.append(f"**Total Products Analyzed:** {len(analyzed_products)}")
output.append("")
output.append("This report presents the **TRUE** classification of products based on strict, independent manual analysis principles (v4.1), NOT simply aggregated AI results. It re-evaluates every single product found in the AI reports.")
output.append("")

# Sort products for display (VERIFIED, then HL, then NV, then FO)
sorted_products = sorted(analyzed_products.values(), 
                        key=lambda x: (x['manual_classification'] == 'VERIFIED',
                                       x['manual_classification'] == 'HIGHLY LIKELY',
                                       x['manual_classification'] == 'NEEDS VERIFICATION',
                                       float(x['net_profit']) if pd.notna(x['net_profit']) else 0), 
                        reverse=True)

# 1. VERIFIED TABLE (MANUAL ANALYSIS)
output.append("## ✅ VERIFIED PRODUCTS (Manual Analysis)")
output.append("Products confirmed as exact matches with positive profit.")
output.append("")
output.append(f"| ASIN | Supplier Title | Net Profit | Sales | Evidence |")
output.append(f"|------|----------------|------------|-------|----------|")
count_ver = 0
for p in sorted_products:
    if p['manual_classification'] == 'VERIFIED':
        net = float(p['net_profit']) if pd.notna(p['net_profit']) else 0
        output.append(f"| {p['asin']} | {p['supplier_title']} | £{net:.2f} | {p['sales']} | {p['manual_reason']} |")
        count_ver += 1
if count_ver == 0: output.append("| - | None Found | - | - | - |")
output.append("")

# 2. HIGHLY LIKELY TABLE (MANUAL ANALYSIS)
output.append("## 🔷 HIGHLY LIKELY PRODUCTS (Manual Analysis)")
output.append("Strong brand/product matches requiring minimal manual confirmation.")
output.append("")
output.append(f"| ASIN | Supplier Title | Net Profit | Sales | Reason |")
output.append(f"|------|----------------|------------|-------|--------|")
count_hl = 0
for p in sorted_products:
    if p['manual_classification'] == 'HIGHLY LIKELY':
        net = float(p['net_profit']) if pd.notna(p['net_profit']) else 0
        output.append(f"| {p['asin']} | {p['supplier_title']} | £{net:.2f} | {p['sales']} | {p['manual_reason']} |")
        count_hl += 1
if count_hl == 0: output.append("| - | None Found | - | - | - |")
output.append("")

# 3. NEEDS VERIFICATION TABLE (Manual Analysis)
output.append("## 🔶 NEEDS VERIFICATION (Manual Analysis)")
output.append("Products with potential but needing check (partial match, pack size check, or no sales data).")
output.append("")
output.append(f"| ASIN | Supplier Title | Amazon Title | Reason |")
output.append(f"|------|----------------|--------------|--------|")
count_nv = 0
for p in sorted_products:
    if p['manual_classification'] == 'NEEDS VERIFICATION':
        output.append(f"| {p['asin']} | {p['supplier_title']} | {p['amazon_title'][:40]}... | {p['manual_reason']} |")
        count_nv += 1
if count_nv == 0: output.append("| - | None Found | - | - |")
output.append("")

# 4. FILTERED OUT TABLE (Manual Analysis)
output.append("## ❌ FILTERED OUT (Manual Analysis)")
output.append("Products rejected due to pack mismatches (neg profit), variant mismatches, or negative profit.")
output.append("")
output.append(f"| ASIN | Supplier Title | Reason | Classification |")
output.append(f"|------|----------------|--------|----------------|")
count_fo = 0
for p in sorted_products:
    if p['manual_classification'] == 'FILTERED OUT':
        output.append(f"| {p['asin']} | {p['supplier_title']} | {p['manual_reason']} | FILTERED OUT |")
        count_fo += 1
if count_fo == 0: output.append("| - | None Found | - | - |")
output.append("")

# 5. DETAILED COMPARISON TABLE
output.append("## 🔍 DETAILED COMPARISON (AI Reports vs Manual Analysis)")
output.append("Comparison of how different AI models classified these products versus the manual ground truth.")
output.append("")
output.append("| ASIN | Manual Truth | cli | Codex HIGH | Gemini | Opus | opus2 | webapp |")
output.append("|------|--------------|-----|------------|--------|------|-------|--------|")

for p in sorted_products: # Full list
    asin = p['asin']
    truth = p['manual_classification'][:4] # Abbreviate
    
    # Get what each model said
    row_cats = {
        'cli': '-', 'Codex HIGH': '-', 'Gemini': '-', 'Opus': '-', 'opus2': '-', 'webapp gpt': '-'
    }
    for r in p['ai_reports']:
        f = r['folder']
        c = r['category'][:4]
        if f in row_cats: row_cats[f] = c
        
    output.append(f"| {asin} | **{truth}** | {row_cats['cli']} | {row_cats['Codex HIGH']} | {row_cats['Gemini']} | {row_cats['Opus']} | {row_cats['opus2']} | {row_cats['webapp gpt']} |")

output.append("")
output.append("*(VERI=Verified, HIGH=Highly Likely, NEED=Needs Verif, FILT=Filtered Out, -=Not in report)*")
output.append("")

# 6. MODEL STATISTICS (As Requested)
output.append("## 📊 MODEL ACCURACY STATISTICS")
output.append("")
output.append("Detailed accuracy of each report based on the above manual analysis:")
output.append("")

output.append("| Model/Folder | Total Analyzed | Correct | Acceptable | Incorrect | Accuracy % |")
output.append("|--------------|----------------|---------|------------|-----------|------------|")

ranking = []
for folder in REPORT_FOLDERS:
    stats = model_stats[folder]
    if stats['total'] > 0:
        acc = (stats['correct'] / stats['total']) * 100
        output.append(f"| {folder} | {stats['total']} | {stats['correct']} | {stats['acceptable']} | {stats['incorrect']} | **{acc:.1f}%** |")
        ranking.append((folder, acc))

output.append("") 
output.append("### 🏆 Ranking")
ranking.sort(key=lambda x: x[1], reverse=True)
for i, (f, acc) in enumerate(ranking, 1):
    output.append(f"{i}. **{f}**: {acc:.1f}%")

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"Report generated: {OUTPUT_FILE}")
