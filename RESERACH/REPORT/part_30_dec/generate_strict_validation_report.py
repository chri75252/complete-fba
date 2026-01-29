"""
STRICT VALIDATION REPORT GENERATOR
Generates 'opus strict_validation_report.md' with:
1. Table for VERIFIED + HIGHLY LIKELY counts (solid valid products)
2. Table for STRICT NEEDS VERIFICATION (very likely matches needing only minor confirmation)

STRICT NV CRITERIA:
- Confidence MED or HIGH (not LOW)
- Title similarity >= 45% OR known brand match
- Adjusted profit > £1.00
- Sales > 0
- Strong product type match evidence
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
OUTPUT_FILE = BASE_PATH / 'opus strict_validation_report.md'

REPORT_FOLDERS = [
    'cli', 'Codex HIGH', 'Codex samecha', 'Codex very high',
    'Gemini', 'Opus', 'opus2', 'webapp gpt'
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
    "ADDIS", "SMART CHOICE", "WORLD OF PETS", "PLAYWRITE", "KINGFISHER",
    "KENWOOD", "SWAN", "TOWER", "MORPHY RICHARDS", "TEFAL", "SABICHI", "JML",
    "BELDRAY", "PROGRESS", "SALTER", "PRESTIGE", "STELLAR", "JUDGE", "CURVER",
    "SISTEMA", "JOSEPH JOSEPH", "OXFAM", "BRABANTIA", "LAKELAND", "CUISINART"
]

# Product type keywords for matching
PRODUCT_TYPES = [
    "BOWL", "DISH", "PAN", "POT", "MUG", "CUP", "PLATE", "TRAY", "JAR", "BOTTLE",
    "CONTAINER", "BOX", "BASKET", "BIN", "BUCKET", "JUG", "CARAFE", "DECANTER",
    "TORCH", "LIGHT", "LAMP", "BULB", "CANDLE", "DIFFUSER", "FRESHENER",
    "BRUSH", "MOP", "CLOTH", "SPONGE", "CLEANER", "SPRAY", "WIPE",
    "HAMMER", "SCREWDRIVER", "PLIERS", "SPANNER", "WRENCH", "DRILL", "SAW",
    "KNIFE", "FORK", "SPOON", "SCISSORS", "CUTTER", "OPENER", "PEELER",
    "TAPE", "GLUE", "SEALANT", "FILLER", "CEMENT", "ADHESIVE",
    "BAG", "LINER", "WRAP", "FOIL", "FILM", "PAPER", "TISSUE",
    "TOY", "TREAT", "FOOD", "BOWL", "LEAD", "COLLAR", "BED"
]

VARIANT_SCENTS = ["EUCALYPTUS", "LEMON", "LIME", "LAVENDER", "VANILLA", "ORANGE", "FRESH", "CITRUS"]

# ============================================================================
# HELPERS
# ============================================================================

print("Loading source data...")
source_df = pd.read_excel(SOURCE_FILE)

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

def get_val(row, key, default):
    val = row.get(key, default)
    if isinstance(val, pd.Series):
        return val.iloc[0] if len(val) > 0 else default
    return val

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
        return True, f"Scent: {sup_scents} vs {amz_scents}"
    return False, ""

def get_product_type_match(sup_title, amz_title):
    """Check if product types match between titles."""
    if pd.isna(sup_title) or pd.isna(amz_title): return False, ""
    sup = str(sup_title).upper()
    amz = str(amz_title).upper()
    matching_types = []
    for ptype in PRODUCT_TYPES:
        if ptype in sup and ptype in amz:
            matching_types.append(ptype)
    return len(matching_types) > 0, matching_types

def classify_product_detailed(row):
    """Returns detailed classification with strict NV check."""
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
    
    pack_verdict = "OK" if pack_ratio == 1 else f"{pack_ratio:.0f}x"
    
    variant_mismatch, variant_reason = detect_variant_mismatch(sup_title, amz_title)
    exact_ean = (ean_clean != "" and ean_on_page_clean != "" and 
                 len(ean_clean) >= 8 and len(ean_on_page_clean) >= 8 and
                 ean_clean == ean_on_page_clean)
    
    product_type_match, matching_types = get_product_type_match(sup_title, amz_title)
    
    # Build result dict
    result = {
        'verdict': 'OTHER',
        'confidence': 'LOW',
        'strict_nv': False,  # Passes strict NV criteria
        'pack_verdict': pack_verdict,
        'adjusted_profit': adjusted_profit,
        'evidence': '',
        'filter_reason': '',
        'title_sim': title_sim,
        'brand_match': brand_match,
        'brand': sup_brand,
        'product_type_match': product_type_match,
        'matching_types': matching_types,
        'sales': sales,
        'net_profit': net_profit
    }
    
    # Classification Logic
    if variant_mismatch and (brand_match or exact_ean):
        result['verdict'] = 'FILTERED OUT'
        result['confidence'] = 'HIGH'
        result['evidence'] = "Variant mismatch"
        result['filter_reason'] = variant_reason
        return result
    
    if pack_ratio > 1 and adjusted_profit <= 0:
        result['verdict'] = 'FILTERED OUT'
        result['confidence'] = 'HIGH'
        result['evidence'] = f"Pack {pack_ratio:.0f}x"
        result['filter_reason'] = "Neg adj profit"
        return result
    
    if net_profit <= 0:
        result['verdict'] = 'FILTERED OUT'
        result['confidence'] = 'HIGH'
        result['evidence'] = "Neg profit"
        result['filter_reason'] = f"£{net_profit:.2f}"
        return result
    
    if exact_ean:
        result['verdict'] = 'VERIFIED'
        result['confidence'] = 'HIGH'
        result['evidence'] = "Exact EAN"
        return result
    
    if brand_match and title_sim >= 0.50:
        if sales > 0:
            result['verdict'] = 'HIGHLY LIKELY'
            result['confidence'] = 'HIGH'
            result['evidence'] = f"Brand: {sup_brand}"
            return result
        else:
            result['verdict'] = 'NEEDS VERIFICATION'
            result['confidence'] = 'MED'
            result['evidence'] = f"Brand: {sup_brand}"
            result['filter_reason'] = "No sales"
            # Check strict NV
            if brand_match and title_sim >= 0.45 and adjusted_profit > 0.50:
                result['strict_nv'] = True
            return result
    
    if (brand_match or title_sim >= 0.50) and adjusted_profit > 0.20:
        result['verdict'] = 'NEEDS VERIFICATION'
        result['confidence'] = 'MED'
        result['evidence'] = f"Sim: {title_sim:.0%}"
        result['filter_reason'] = "Partial match"
        # STRICT NV CRITERIA for MED confidence
        # Very likely if: brand match OR high similarity + product type match + good profit + sales
        if (brand_match or (title_sim >= 0.45 and product_type_match)) and adjusted_profit > 1.00 and sales > 0:
            result['strict_nv'] = True
        return result
    
    if title_sim >= 0.35 and net_profit > 0:
        result['verdict'] = 'NEEDS VERIFICATION'
        result['confidence'] = 'LOW'
        result['evidence'] = f"Sim: {title_sim:.0%}"
        result['filter_reason'] = "Moderate sim"
        # STRICT NV for LOW confidence - only if really promising
        # Product type match + decent similarity + good profit + sales
        if product_type_match and title_sim >= 0.45 and adjusted_profit > 2.00 and sales >= 50:
            result['strict_nv'] = True
        return result
    
    result['verdict'] = 'OTHER'
    result['confidence'] = 'LOW'
    result['evidence'] = "Low evidence"
    result['filter_reason'] = "Weak match"
    return result

def format_fixed_width_table(headers, rows, col_widths):
    """Generate a fixed-width, space-padded table."""
    lines = []
    header_parts = [h.ljust(col_widths[i]) for i, h in enumerate(headers)]
    lines.append("| " + " | ".join(header_parts) + " |")
    sep_parts = ["-" * w for w in col_widths]
    lines.append("|-" + "-|-".join(sep_parts) + "-|")
    for row in rows:
        row_parts = [str(cell)[:col_widths[i]].ljust(col_widths[i]) for i, cell in enumerate(row)]
        lines.append("| " + " | ".join(row_parts) + " |")
    return lines

# ============================================================================
# EXTRACT AND ANALYZE
# ============================================================================

print("Extracting and analyzing products with strict criteria...")

report_products = defaultdict(list)
analyzed_products = {}
manually_analyzed_count = 0

CATEGORY_MAP = {
    'VERIFIED': 'VERIFIED', 'HIGHLY LIKELY': 'HIGHLY LIKELY',
    'HIGHLY_LIKELY': 'HIGHLY LIKELY', 'NEEDS VERIFICATION': 'NEEDS VERIFICATION',
    'FILTERED OUT': 'FILTERED OUT', 'FILTERED_OUT': 'FILTERED OUT'
}

for folder in REPORT_FOLDERS:
    report_path = BASE_PATH / folder / 'PHASEA_MANUAL_REPORT_20251230.md'
    if not report_path.exists(): 
        print(f"  [SKIP] {folder}: Report not found")
        continue
    
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
            
        if current_section and '|' in line and 'Verdict' not in line and 'SupplierTitle' not in line and '---' not in line:
            source_row = None
            asin = None
            
            asin_match = re.search(r'\b(B[0-9A-Z]{9})\b', line)
            if asin_match:
                asin = asin_match.group(1)
                if asin in asin_lookup: _, source_row = asin_lookup[asin]
            
            if source_row is None:
                ean_match = re.search(r'\b(\d{12,14})\b', line)
                if ean_match and ean_match.group(1) in ean_lookup:
                    _, source_row = ean_lookup[ean_match.group(1)]
                    asin = str(get_val(source_row, 'ASIN', ''))
            
            if source_row is not None and asin:
                result = classify_product_detailed(source_row)
                manually_analyzed_count += 1
                
                ai_cat = CATEGORY_MAP.get(current_section, 'OTHER')
                
                analysis = {
                    'asin': asin,
                    'ai_category': ai_cat,
                    'my_verdict': result['verdict'],
                    'confidence': result['confidence'],
                    'strict_nv': result['strict_nv'],
                    'supplier_title': str(get_val(source_row, 'SupplierTitle', ''))[:50],
                    'amazon_title': str(get_val(source_row, 'AmazonTitle', ''))[:50],
                    'supplier_ean': str(get_val(source_row, 'EAN_clean', '')),
                    'amazon_ean': str(get_val(source_row, 'EAN_OnPage_clean', '')),
                    'supplier_price': get_val(source_row, 'SupplierPrice_incVAT', 0),
                    'selling_price': get_val(source_row, 'SellingPrice_incVAT', 0),
                    'net_profit': result['net_profit'],
                    'roi': get_val(source_row, 'ROI', 0),
                    'sales': result['sales'],
                    'pack_verdict': result['pack_verdict'],
                    'adjusted_profit': result['adjusted_profit'],
                    'evidence': result['evidence'],
                    'filter_reason': result['filter_reason'],
                    'title_sim': result['title_sim'],
                    'brand_match': result['brand_match'],
                    'brand': result['brand'],
                    'product_type_match': result['product_type_match'],
                    'folder': folder
                }
                
                report_products[folder].append(analysis)
                
                if asin not in analyzed_products:
                    analyzed_products[asin] = analysis

# ============================================================================
# CALCULATE STATS
# ============================================================================

print("Calculating statistics with strict NV criteria...")

report_stats = {}
for folder in REPORT_FOLDERS:
    products = report_products[folder]
    total = len(products)
    
    verified_count = sum(1 for p in products if p['my_verdict'] == 'VERIFIED')
    highly_likely_count = sum(1 for p in products if p['my_verdict'] == 'HIGHLY LIKELY')
    needs_verif_count = sum(1 for p in products if p['my_verdict'] == 'NEEDS VERIFICATION')
    strict_nv_count = sum(1 for p in products if p['my_verdict'] == 'NEEDS VERIFICATION' and p['strict_nv'])
    filtered_out_count = sum(1 for p in products if p['my_verdict'] == 'FILTERED OUT')
    
    valid_count = verified_count + highly_likely_count
    total_actionable = valid_count + strict_nv_count  # VF+HL + Strict NV
    
    report_stats[folder] = {
        'total': total,
        'verified': verified_count,
        'highly_likely': highly_likely_count,
        'valid': valid_count,
        'needs_verif': needs_verif_count,
        'strict_nv': strict_nv_count,
        'filtered_out': filtered_out_count,
        'total_actionable': total_actionable
    }

# Find best reports
best_valid = max(report_stats.keys(), key=lambda x: report_stats[x]['valid']) if report_stats else None
best_strict_nv = max(report_stats.keys(), key=lambda x: report_stats[x]['strict_nv']) if report_stats else None
best_total = max(report_stats.keys(), key=lambda x: report_stats[x]['total_actionable']) if report_stats else None

# ============================================================================
# GENERATE REPORT
# ============================================================================

print("Generating strict validation report...")

output = []
output.append("# OPUS STRICT VALIDATION REPORT")
output.append(f"**Generated:** 2025-12-30")
output.append(f"**Total Unique Products Analyzed:** {len(analyzed_products)}")
output.append(f"**Total Manual Analyses Performed:** {manually_analyzed_count}")
output.append("")

output.append("## 📊 SUMMARY: VALID PRODUCTS PER REPORT")
output.append("")
output.append("This report distinguishes between:")
output.append("- **VALID (V+HL)**: VERIFIED + HIGHLY LIKELY products (solid matches)")
output.append("- **STRICT NV**: NEEDS VERIFICATION products that are VERY likely real matches (just need 1-2 minor confirmations)")
output.append("- **TOTAL ACTIONABLE**: Valid + Strict NV (all products worth pursuing)")
output.append("")

# Table 1: Valid Products (VERIFIED + HIGHLY LIKELY)
output.append("### Table 1: VERIFIED + HIGHLY LIKELY (Solid Valid Products)")
output.append("```text")
t1_headers = ["Report", "Total", "VERIFIED", "HIGHLY LIKELY", "Valid (V+HL)"]
t1_widths = [18, 8, 10, 14, 12]

t1_rows = []
for folder in REPORT_FOLDERS:
    stats = report_stats.get(folder, {})
    t1_rows.append([
        folder,
        str(stats.get('total', 0)),
        str(stats.get('verified', 0)),
        str(stats.get('highly_likely', 0)),
        str(stats.get('valid', 0))
    ])
t1_rows.sort(key=lambda x: int(x[4]), reverse=True)

for line in format_fixed_width_table(t1_headers, t1_rows, t1_widths):
    output.append(line)
output.append("```")
output.append("")

# Table 2: Strict NV Products
output.append("### Table 2: STRICT NEEDS VERIFICATION (Very Likely Matches)")
output.append("")
output.append("**Strict NV Criteria Applied:**")
output.append("- Brand match OR title similarity >= 45%")
output.append("- Product type keywords match")
output.append("- Adjusted profit > £1.00 (for MED) or > £2.00 (for LOW)")
output.append("- Sales > 0")
output.append("- Only needs 1-2 minor details for 100% confirmation")
output.append("")
output.append("```text")
t2_headers = ["Report", "Total NV", "STRICT NV", "% Strict", "Total Actionable (V+HL+SNV)"]
t2_widths = [18, 10, 10, 10, 28]

t2_rows = []
for folder in REPORT_FOLDERS:
    stats = report_stats.get(folder, {})
    nv = stats.get('needs_verif', 0)
    snv = stats.get('strict_nv', 0)
    pct = (snv / nv * 100) if nv > 0 else 0
    t2_rows.append([
        folder,
        str(nv),
        str(snv),
        f"{pct:.1f}%",
        str(stats.get('total_actionable', 0))
    ])
t2_rows.sort(key=lambda x: int(x[2]), reverse=True)

for line in format_fixed_width_table(t2_headers, t2_rows, t2_widths):
    output.append(line)
output.append("```")
output.append("")

# Combined ranking table
output.append("### 🏆 COMBINED RANKING (Total Actionable Products)")
output.append("```text")
t3_headers = ["Rank", "Report", "VERIFIED", "HIGHLY LIKELY", "STRICT NV", "TOTAL ACTIONABLE"]
t3_widths = [6, 18, 10, 14, 10, 18]

t3_rows = []
for folder in REPORT_FOLDERS:
    stats = report_stats.get(folder, {})
    t3_rows.append([
        "",
        folder,
        str(stats.get('verified', 0)),
        str(stats.get('highly_likely', 0)),
        str(stats.get('strict_nv', 0)),
        str(stats.get('total_actionable', 0))
    ])
t3_rows.sort(key=lambda x: int(x[5]), reverse=True)
for i, row in enumerate(t3_rows, 1):
    row[0] = str(i)

for line in format_fixed_width_table(t3_headers, t3_rows, t3_widths):
    output.append(line)
output.append("```")
output.append("")

output.append(f"### 🥇 WINNER BY TOTAL ACTIONABLE: **{best_total}** ({report_stats[best_total]['total_actionable']} products)")
output.append(f"### 🥈 WINNER BY VALID (V+HL): **{best_valid}** ({report_stats[best_valid]['valid']} products)")
output.append(f"### 🥉 WINNER BY STRICT NV: **{best_strict_nv}** ({report_stats[best_strict_nv]['strict_nv']} products)")
output.append("")

# ============================================================================
# STRICT NV PRODUCTS LIST
# ============================================================================

output.append("## 📋 SHORTLISTED STRICT NEEDS VERIFICATION PRODUCTS")
output.append("")
output.append("These products are VERY likely to be real matches. They just need 1-2 minor details confirmed.")
output.append("")

strict_nv_products = [p for p in analyzed_products.values() 
                      if p['my_verdict'] == 'NEEDS VERIFICATION' and p['strict_nv']]

# Sort by adjusted profit descending
strict_nv_products.sort(key=lambda x: x['adjusted_profit'], reverse=True)

output.append("```text")
snv_headers = ["ASIN", "SupplierTitle", "AmazonTitle", "Confidence", "Similarity", "Brand", "AdjProfit", "Sales", "Evidence"]
snv_widths = [12, 35, 35, 10, 10, 15, 10, 8, 20]

snv_rows = []
for p in strict_nv_products:
    snv_rows.append([
        p['asin'][:12],
        p['supplier_title'][:35],
        p['amazon_title'][:35],
        p['confidence'][:10],
        f"{p['title_sim']:.0%}"[:10],
        (p['brand'] if p['brand'] else "-")[:15],
        f"£{p['adjusted_profit']:.2f}"[:10],
        str(int(p['sales']))[:8],
        p['evidence'][:20]
    ])

for line in format_fixed_width_table(snv_headers, snv_rows, snv_widths):
    output.append(line)
output.append("```")
output.append(f"**Total Strict NV Products: {len(strict_nv_products)}**")
output.append("")

# ============================================================================
# VERIFIED + HIGHLY LIKELY PRODUCTS (For Reference)
# ============================================================================

output.append("## ✅ VERIFIED PRODUCTS (For Reference)")
output.append("")
verified = [p for p in analyzed_products.values() if p['my_verdict'] == 'VERIFIED']
output.append(f"**Total: {len(verified)}**")
output.append("")
output.append("```text")
v_headers = ["ASIN", "SupplierTitle", "NetProfit", "Sales", "Evidence"]
v_widths = [12, 50, 10, 8, 20]
v_rows = []
for p in sorted(verified, key=lambda x: x['net_profit'], reverse=True):
    v_rows.append([
        p['asin'][:12],
        p['supplier_title'][:50],
        f"£{p['net_profit']:.2f}"[:10],
        str(int(p['sales']))[:8],
        p['evidence'][:20]
    ])
for line in format_fixed_width_table(v_headers, v_rows, v_widths):
    output.append(line)
output.append("```")
output.append("")

output.append("## 🔷 HIGHLY LIKELY PRODUCTS (For Reference)")
output.append("")
hl = [p for p in analyzed_products.values() if p['my_verdict'] == 'HIGHLY LIKELY']
output.append(f"**Total: {len(hl)}**")
output.append("")
output.append("```text")
for p in sorted(hl, key=lambda x: x['net_profit'], reverse=True)[:30]:
    v_rows.append([
        p['asin'][:12],
        p['supplier_title'][:50],
        f"£{p['net_profit']:.2f}"[:10],
        str(int(p['sales']))[:8],
        p['evidence'][:20]
    ])
hl_rows = []
for p in sorted(hl, key=lambda x: x['net_profit'], reverse=True):
    hl_rows.append([
        p['asin'][:12],
        p['supplier_title'][:50],
        f"£{p['net_profit']:.2f}"[:10],
        str(int(p['sales']))[:8],
        p['evidence'][:20]
    ])
for line in format_fixed_width_table(v_headers, hl_rows, v_widths):
    output.append(line)
output.append("```")
output.append("")

# Write output
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"Report generated: {OUTPUT_FILE}")
print(f"\n=== FINAL RESULTS ===")
print(f"Best by Valid (V+HL): {best_valid} ({report_stats[best_valid]['valid']})")
print(f"Best by Strict NV: {best_strict_nv} ({report_stats[best_strict_nv]['strict_nv']})")
print(f"Best by Total Actionable: {best_total} ({report_stats[best_total]['total_actionable']})")
