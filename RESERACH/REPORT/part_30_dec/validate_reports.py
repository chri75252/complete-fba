"""
FBA REPORT VALIDATION ANALYSIS v3
Matches products by ASIN/EAN/title since Row ID format varies across reports
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
# STEP 1: LOAD SOURCE DATA
# ============================================================================

print("="*80)
print("STEP 1: LOADING SOURCE DATA")
print("="*80)

source_df = pd.read_excel(SOURCE_FILE)
print(f"Loaded {len(source_df)} rows from source dataset")

# Clean EAN columns
def clean_ean(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    s = re.sub(r'\.0$', '', s)
    s = re.sub(r'[^0-9]', '', s)
    return s

source_df['EAN_clean'] = source_df['EAN'].apply(clean_ean)
source_df['EAN_OnPage_clean'] = source_df['EAN_OnPage'].apply(clean_ean)

# Handle sales column
if 'bought_in_past_month' in source_df.columns:
    source_df['sales'] = pd.to_numeric(source_df['bought_in_past_month'], errors='coerce').fillna(0)
else:
    source_df['sales'] = 0

# Create lookup dictionaries
asin_lookup = {}
ean_lookup = {}
for idx, row in source_df.iterrows():
    asin = str(row.get('ASIN', '')).strip()
    if asin and asin != 'nan':
        asin_lookup[asin] = (idx + 1, row)
    
    ean = row.get('EAN_clean', '')
    if ean and len(ean) >= 8:
        ean_lookup[ean] = (idx + 1, row)

print(f"Created lookups: {len(asin_lookup)} ASINs, {len(ean_lookup)} EANs")

# ============================================================================
# STEP 2: EXTRACT PRODUCTS FROM AI REPORTS
# ============================================================================

print()
print("="*80)
print("STEP 2: EXTRACTING PRODUCTS FROM AI REPORTS")
print("="*80)

def parse_report(filepath):
    """Parse a markdown report and extract products by category."""
    products = {
        'VERIFIED': [],
        'HIGHLY LIKELY': [],
        'NEEDS VERIFICATION': [],
        'FILTERED OUT': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return products
    
    current_section = None
    lines = content.split('\n')
    
    for line in lines:
        # Detect section headers
        line_lower = line.lower()
        if '## verified' in line_lower and 'filtered' not in line_lower and 'excluded' not in line_lower:
            current_section = 'VERIFIED'
        elif '## highly likely' in line_lower and 'filtered' not in line_lower and 'excluded' not in line_lower:
            current_section = 'HIGHLY LIKELY'
        elif '## needs verification' in line_lower:
            current_section = 'NEEDS VERIFICATION'
        elif '## filtered out' in line_lower or ('highly likely' in line_lower and 'filtered' in line_lower):
            current_section = 'FILTERED OUT'
        elif line.startswith('## ') and 'summary' not in line_lower and 'reconciliation' not in line_lower:
            # Another section, but check if it's a sub-section
            if '```' not in line and '|' not in line:
                current_section = None
            
        # Parse table rows
        if current_section and '|' in line and not line.startswith('|--') and not line.startswith('| --'):
            # Skip header rows
            if 'Verdict' in line or 'Confidence' in line or 'SupplierTitle' in line:
                continue
                
            # Extract ASIN - look for standard ASIN format (B followed by alphanumeric)
            asin_match = re.search(r'\b(B[0-9A-Z]{9})\b', line)
            asin = asin_match.group(1) if asin_match else None
            
            # Also extract Row ID if present
            row_match = re.search(r'\(Row\s*(\d+)\)', line)
            row_id = int(row_match.group(1)) if row_match else None
            
            # Extract EAN (13-digit number)
            ean_match = re.search(r'\b(\d{12,14})\b', line)
            ean = ean_match.group(1) if ean_match else None
            
            if asin or row_id or ean:
                products[current_section].append({
                    'asin': asin,
                    'row_id': row_id,
                    'ean': ean,
                    'raw_line': line[:150]
                })
    
    return products

all_reports = {}
for folder in REPORT_FOLDERS:
    report_path = BASE_PATH / folder / 'PHASEA_MANUAL_REPORT_20251230.md'
    if report_path.exists():
        products = parse_report(report_path)
        all_reports[folder] = products
        total = sum(len(v) for v in products.values())
        print(f"{folder}: {total} products extracted")
        for cat, items in products.items():
            if len(items) > 0:
                print(f"  - {cat}: {len(items)}")
    else:
        print(f"{folder}: Report not found")

# ============================================================================
# STEP 3: ANALYSIS FUNCTIONS
# ============================================================================

def extract_known_brand(title):
    """Extract brand from KNOWN_BRANDS list."""
    if pd.isna(title):
        return ""
    title_upper = str(title).upper()
    for brand in sorted(KNOWN_BRANDS, key=len, reverse=True):
        if brand in title_upper:
            return brand
    return ""

def title_similarity(t1, t2):
    """Calculate title similarity."""
    if pd.isna(t1) or pd.isna(t2):
        return 0
    return SequenceMatcher(None, str(t1).upper(), str(t2).upper()).ratio()

def extract_pack_count(title):
    """Extract pack count from title."""
    if pd.isna(title):
        return 1
    title_upper = str(title).upper()
    
    patterns = [
        (r'PACK\s*OF\s*(\d+)', 1),
        (r'(\d+)\s*PACK\b', 1),
        (r'(\d+)\s*PCS\b', 1),
        (r'SET\s*OF\s*(\d+)', 1),
        (r'^(\d+)\s*X\s+[A-Z]', 1),
    ]
    
    for pattern, group in patterns:
        match = re.search(pattern, title_upper)
        if match:
            val = int(match.group(group))
            if val > 1 and val < 500:
                return val
    return 1

def detect_variant_mismatch(sup_title, amz_title):
    """Detect variant mismatch (scent/color)."""
    if pd.isna(sup_title) or pd.isna(amz_title):
        return False, ""
    
    sup_upper = str(sup_title).upper()
    amz_upper = str(amz_title).upper()
    
    sup_scents = [s for s in VARIANT_SCENTS if s in sup_upper]
    amz_scents = [s for s in VARIANT_SCENTS if s in amz_upper]
    if sup_scents and amz_scents and set(sup_scents) != set(amz_scents):
        return True, f"Scent: {sup_scents} vs {amz_scents}"
    
    return False, ""

def classify_product(row):
    """Independently classify a product based on analysis."""
    ean_clean = str(row.get('EAN_clean', ''))
    ean_on_page_clean = str(row.get('EAN_OnPage_clean', ''))
    sup_title = row.get('SupplierTitle', '')
    amz_title = row.get('AmazonTitle', '')
    net_profit = float(row.get('NetProfit', 0)) if pd.notna(row.get('NetProfit')) else 0
    sup_price = float(row.get('SupplierPrice_incVAT', 0)) if pd.notna(row.get('SupplierPrice_incVAT')) else 0
    sales = float(row.get('sales', 0))
    
    # Calculate metrics
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
    
    # Classification
    if variant_mismatch and (brand_match or exact_ean):
        return 'FILTERED_OUT', f"Variant: {variant_reason}"
    
    if pack_ratio > 1 and adjusted_profit <= 0:
        return 'FILTERED_OUT', f"Pack {pack_ratio:.0f}x neg profit"
    
    if net_profit <= 0:
        return 'FILTERED_OUT', "Neg profit"
    
    if exact_ean:
        return 'VERIFIED', "Exact EAN"
    
    if brand_match and title_sim >= 0.50:
        if sales > 0:
            return 'HIGHLY_LIKELY', f"Brand: {sup_brand}"
        else:
            return 'NEEDS_VERIFICATION', "Brand match, no sales"
    
    if (brand_match or title_sim >= 0.50) and adjusted_profit > 0.20:
        return 'NEEDS_VERIFICATION', "Partial match"
    
    if title_sim >= 0.35 and net_profit > 0:
        return 'NEEDS_VERIFICATION', "Title similarity"
    
    if title_sim >= 0.25 and net_profit > 0:
        return 'LOW_PRIORITY', "Weak match"
    
    return 'OTHER', "Insufficient evidence"

# ============================================================================
# STEP 4: ANALYZE AND VALIDATE ALL PRODUCTS
# ============================================================================

print()
print("="*80)
print("STEP 4: ANALYZING AND VALIDATING PRODUCTS")
print("="*80)

validation_results = []
model_stats = defaultdict(lambda: {
    'total': 0,
    'correct': 0,
    'acceptable': 0,
    'incorrect': 0,
    'by_category': defaultdict(lambda: {'claimed': 0, 'correct': 0, 'details': defaultdict(int)})
})

CATEGORY_MAP = {
    'VERIFIED': 'VERIFIED',
    'HIGHLY LIKELY': 'HIGHLY_LIKELY',
    'HIGHLY_LIKELY': 'HIGHLY_LIKELY', 
    'NEEDS VERIFICATION': 'NEEDS_VERIFICATION',
    'NEEDS_VERIFICATION': 'NEEDS_VERIFICATION',
    'FILTERED OUT': 'FILTERED_OUT',
    'FILTERED_OUT': 'FILTERED_OUT'
}

ADJACENT_CATEGORIES = {
    'VERIFIED': ['HIGHLY_LIKELY'],
    'HIGHLY_LIKELY': ['VERIFIED', 'NEEDS_VERIFICATION'],
    'NEEDS_VERIFICATION': ['HIGHLY_LIKELY', 'LOW_PRIORITY', 'FILTERED_OUT'],
    'FILTERED_OUT': ['NEEDS_VERIFICATION', 'LOW_PRIORITY', 'OTHER'],
}

for folder, report_data in all_reports.items():
    print(f"\nAnalyzing {folder}...")
    folder_count = 0
    matched_count = 0
    
    for ai_category, products in report_data.items():
        ai_cat_normalized = CATEGORY_MAP.get(ai_category, ai_category)
        
        for product in products:
            folder_count += 1
            source_row = None
            row_id = None
            
            # Try to find matching source row by Row ID first
            if product.get('row_id'):
                row_id = product['row_id']
                if row_id <= len(source_df):
                    source_row = source_df.iloc[row_id - 1]
            
            # Try ASIN lookup
            if source_row is None and product.get('asin'):
                if product['asin'] in asin_lookup:
                    row_id, source_row = asin_lookup[product['asin']]
            
            # Try EAN lookup
            if source_row is None and product.get('ean'):
                if product['ean'] in ean_lookup:
                    row_id, source_row = ean_lookup[product['ean']]
            
            if source_row is not None:
                matched_count += 1
                
                # Independent classification
                my_category, my_reason = classify_product(source_row)
                
                # Compare
                is_correct = (my_category == ai_cat_normalized)
                is_acceptable = (my_category in ADJACENT_CATEGORIES.get(ai_cat_normalized, []))
                
                # Record stats
                model_stats[folder]['total'] += 1
                model_stats[folder]['by_category'][ai_category]['claimed'] += 1
                model_stats[folder]['by_category'][ai_category]['details'][my_category] += 1
                
                if is_correct:
                    model_stats[folder]['correct'] += 1
                    model_stats[folder]['by_category'][ai_category]['correct'] += 1
                elif is_acceptable:
                    model_stats[folder]['acceptable'] += 1
                else:
                    model_stats[folder]['incorrect'] += 1
                
                validation_results.append({
                    'folder': folder,
                    'row_id': row_id,
                    'asin': product.get('asin', ''),
                    'ai_category': ai_category,
                    'my_category': my_category,
                    'my_reason': my_reason,
                    'is_correct': is_correct,
                    'is_acceptable': is_acceptable,
                    'sup_title': str(source_row.get('SupplierTitle', ''))[:35],
                    'net_profit': source_row.get('NetProfit', 0)
                })
    
    print(f"  Products in report: {folder_count}, Matched to source: {matched_count}")

print(f"\nTotal validations performed: {len(validation_results)}")

# ============================================================================
# STEP 5: GENERATE REPORT
# ============================================================================

print()
print("="*80)
print("STEP 5: GENERATING VALIDATION REPORT")
print("="*80)

output = []
output.append("# FBA REPORT VALIDATION ANALYSIS")
output.append("")
output.append("**Generated:** 2025-12-30")
output.append(f"**Source Dataset:** part_30_dec.xlsx ({len(source_df)} rows)")
output.append(f"**Reports Analyzed:** {len(all_reports)} folders")
output.append(f"**Total Products Validated:** {len(validation_results)}")
output.append("")

# Executive Summary
output.append("## Executive Summary")
output.append("")
total_products = sum(s['total'] for s in model_stats.values())
total_correct = sum(s['correct'] for s in model_stats.values())
total_acceptable = sum(s['acceptable'] for s in model_stats.values())
total_incorrect = sum(s['incorrect'] for s in model_stats.values())
overall_accuracy = (total_correct / total_products * 100) if total_products > 0 else 0

output.append(f"- **Total products analyzed:** {total_products}")
output.append(f"- **Correctly categorized:** {total_correct} ({overall_accuracy:.1f}%)")
output.append(f"- **Acceptably categorized (adjacent):** {total_acceptable}")
output.append(f"- **Incorrectly categorized:** {total_incorrect}")
output.append(f"- **Combined accuracy (correct + acceptable):** {((total_correct + total_acceptable) / total_products * 100) if total_products > 0 else 0:.1f}%")
output.append("")

# Model Accuracy Statistics
output.append("## 📈 MODEL ACCURACY STATISTICS")
output.append("")
output.append("### Overall Accuracy by Model/Folder")
output.append("")
output.append("| Model/Folder | Total | Correct | Acceptable | Incorrect | Accuracy % | Combined % |")
output.append("|--------------|-------|---------|------------|-----------|------------|------------|")

model_rankings = []
for folder in REPORT_FOLDERS:
    if folder in model_stats and model_stats[folder]['total'] > 0:
        stats = model_stats[folder]
        accuracy = (stats['correct'] / stats['total'] * 100)
        combined = ((stats['correct'] + stats['acceptable']) / stats['total'] * 100)
        output.append(f"| {folder} | {stats['total']} | {stats['correct']} | {stats['acceptable']} | {stats['incorrect']} | {accuracy:.1f}% | {combined:.1f}% |")
        model_rankings.append((folder, accuracy, combined, stats['total'], stats['correct']))

output.append("")

# Category breakdown
output.append("### Category-Level Accuracy")
output.append("")

for category in ['VERIFIED', 'HIGHLY LIKELY', 'NEEDS VERIFICATION', 'FILTERED OUT']:
    output.append(f"#### {category}")
    output.append("")
    output.append("| Model | Claimed | → VERIFIED | → HIGHLY_LIKELY | → NEEDS_VERIF | → FILTERED_OUT | → OTHER | Accuracy |")
    output.append("|-------|---------|------------|-----------------|---------------|----------------|---------|----------|")
    
    for folder in REPORT_FOLDERS:
        if folder in model_stats:
            cat_stats = model_stats[folder]['by_category'].get(category, {'claimed': 0, 'correct': 0, 'details': {}})
            if cat_stats['claimed'] > 0:
                d = cat_stats['details']
                acc = (cat_stats['correct'] / cat_stats['claimed'] * 100)
                output.append(f"| {folder} | {cat_stats['claimed']} | {d.get('VERIFIED',0)} | {d.get('HIGHLY_LIKELY',0)} | {d.get('NEEDS_VERIFICATION',0)} | {d.get('FILTERED_OUT',0)} | {d.get('OTHER',0)+d.get('LOW_PRIORITY',0)} | {acc:.0f}% |")
    output.append("")

# Model Ranking
output.append("### 🏆 Ranking by Accuracy")
output.append("")
model_rankings.sort(key=lambda x: x[1], reverse=True)
output.append("| Rank | Model/Folder | Accuracy | Combined | Total |")
output.append("|------|--------------|----------|----------|-------|")
for i, (folder, acc, comb, total, correct) in enumerate(model_rankings, 1):
    output.append(f"| {i} | **{folder}** | {acc:.1f}% | {comb:.1f}% | {total} |")

output.append("")

# Sample misclassifications
output.append("## Sample Misclassifications")
output.append("")
incorrect_samples = [r for r in validation_results if not r['is_correct'] and not r['is_acceptable']][:30]
output.append(f"Showing {len(incorrect_samples)} examples of incorrect categorizations:")
output.append("")
output.append("| Folder | ASIN | AI Said | Should Be | Title | Reason |")
output.append("|--------|------|---------|-----------|-------|--------|")
for r in incorrect_samples:
    output.append(f"| {r['folder']} | {r['asin'][:10] if r['asin'] else '-'} | {r['ai_category']} | {r['my_category']} | {r['sup_title'][:25]} | {r['my_reason']} |")

output.append("")

# Recommendations
output.append("## Recommendations")
output.append("")
if model_rankings:
    best = model_rankings[0]
    worst = model_rankings[-1]
    output.append(f"1. **Best Model:** `{best[0]}` with {best[1]:.1f}% accuracy")
    output.append(f"2. **Worst Model:** `{worst[0]}` with {worst[1]:.1f}% accuracy")

# Save
report_path = BASE_PATH / 'COMPREHENSIVE_VALIDATION_REPORT_20251230.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"\nReport saved to: {report_path}")

# Console summary
print()
print("="*80)
print("SUMMARY")
print("="*80)
print(f"Total products validated: {total_products}")
print(f"Overall accuracy: {overall_accuracy:.1f}%")
print(f"Combined accuracy: {((total_correct + total_acceptable) / total_products * 100) if total_products > 0 else 0:.1f}%")
print()
print("Model Rankings (by accuracy):")
for i, (folder, acc, comb, total, correct) in enumerate(model_rankings, 1):
    print(f"  {i}. {folder}: {acc:.1f}% accuracy, {comb:.1f}% combined ({correct}/{total})")
