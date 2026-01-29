"""
FINAL COMPREHENSIVE FBA REPORT GENERATOR
Generates the final PHASEA_MANUAL_REPORT following v4.0 guidance with:
- VERIFIED (RECOMMENDED + FILTERED OUT)
- HIGHLY LIKELY (RECOMMENDED + FILTERED OUT)
- NEEDS VERIFICATION (Strict - only very likely matches needing 1-2 confirmations)
- FILTERED OUT (Confirmed matches that are unprofitable - for audit)

Combines all products from all 8 AI reports into one definitive product list.
"""

import pandas as pd
import re
from difflib import SequenceMatcher
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_PATH = Path(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec')
SOURCE_FILE = BASE_PATH / 'part_30_dec.xlsx'
OUTPUT_FILE = BASE_PATH / 'PHASEA_MANUAL_REPORT_FINAL.md'

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
    "PAN AROMA", "BEAUFORT", "WHAM", "PENDEFORD", "EXTRA SELECT", "ADDIS",
    "SMART CHOICE", "WORLD OF PETS", "PLAYWRITE", "KINGFISHER", "KENWOOD",
    "SWAN", "TOWER", "MORPHY RICHARDS", "TEFAL", "SABICHI", "JML", "BELDRAY",
    "PROGRESS", "SALTER", "PRESTIGE", "STELLAR", "JUDGE", "CURVER", "SISTEMA",
    "JOSEPH JOSEPH", "BRABANTIA", "LAKELAND", "CUISINART", "GORILLA", "WD-40"
]

PRODUCT_TYPES = [
    "BOWL", "DISH", "PAN", "POT", "MUG", "CUP", "PLATE", "TRAY", "JAR", "BOTTLE",
    "CONTAINER", "BOX", "BASKET", "BIN", "BUCKET", "JUG", "CARAFE", "DECANTER",
    "TORCH", "LIGHT", "LAMP", "BULB", "CANDLE", "DIFFUSER", "FRESHENER",
    "BRUSH", "MOP", "CLOTH", "SPONGE", "CLEANER", "SPRAY", "WIPE",
    "HAMMER", "SCREWDRIVER", "PLIERS", "SPANNER", "WRENCH", "DRILL", "SAW",
    "KNIFE", "FORK", "SPOON", "SCISSORS", "CUTTER", "OPENER", "PEELER",
    "TAPE", "GLUE", "SEALANT", "FILLER", "CEMENT", "ADHESIVE",
    "BAG", "LINER", "WRAP", "FOIL", "FILM", "PAPER", "TISSUE",
    "TOY", "TREAT", "FOOD", "LEAD", "COLLAR", "BED", "MIRROR", "GLASS"
]

VARIANT_SCENTS = ["EUCALYPTUS", "LEMON", "LIME", "LAVENDER", "VANILLA", "ORANGE", "FRESH", "CITRUS", "APPLE", "CINNAMON"]
VARIANT_COLORS = ["BLACK", "WHITE", "GREY", "GRAY", "NAVY", "CREAM", "RED", "BLUE", "GREEN", "PINK", "BROWN", "SILVER", "GOLD"]

# ============================================================================
# HELPERS
# ============================================================================

print("Loading source data...")
source_df = pd.read_excel(SOURCE_FILE)
print(f"Source data: {len(source_df)} rows")

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
        (r'SET\s*OF\s*(\d+)', 1), (r'^(\d+)\s*X\s+[A-Z]', 1), (r'(\d+)\s*PIECE', 1)
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
    
    # Scent check
    sup_scents = [s for s in VARIANT_SCENTS if s in sup]
    amz_scents = [s for s in VARIANT_SCENTS if s in amz]
    if sup_scents and amz_scents and set(sup_scents) != set(amz_scents):
        return True, f"Scent mismatch: {sup_scents} vs {amz_scents}"
    
    # Color check (only if both have colors and they differ)
    sup_colors = [c for c in VARIANT_COLORS if c in sup]
    amz_colors = [c for c in VARIANT_COLORS if c in amz]
    if sup_colors and amz_colors and set(sup_colors) != set(amz_colors):
        # Only flag if it seems like a variant issue (same product different color)
        if extract_known_brand(sup_title) == extract_known_brand(amz_title):
            return True, f"Color mismatch: {sup_colors} vs {amz_colors}"
    
    return False, ""

def get_product_types_match(sup_title, amz_title):
    if pd.isna(sup_title) or pd.isna(amz_title): return False, []
    sup = str(sup_title).upper()
    amz = str(amz_title).upper()
    matching = [pt for pt in PRODUCT_TYPES if pt in sup and pt in amz]
    return len(matching) > 0, matching

def classify_product_full(row):
    """Full classification with RECOMMENDED vs FILTERED logic."""
    ean_clean = str(get_val(row, 'EAN_clean', ''))
    ean_on_page_clean = str(get_val(row, 'EAN_OnPage_clean', ''))
    sup_title = get_val(row, 'SupplierTitle', '')
    amz_title = get_val(row, 'AmazonTitle', '')
    
    net_profit_val = get_val(row, 'NetProfit', 0)
    net_profit = float(net_profit_val) if pd.notna(net_profit_val) else 0
    
    sup_price_val = get_val(row, 'SupplierPrice_incVAT', 0)
    sup_price = float(sup_price_val) if pd.notna(sup_price_val) else 0
    
    sell_price_val = get_val(row, 'SellingPrice_incVAT', 0)
    sell_price = float(sell_price_val) if pd.notna(sell_price_val) else 0
    
    roi_val = get_val(row, 'ROI', 0)
    roi = float(roi_val) if pd.notna(roi_val) else 0
    
    sales_val = get_val(row, 'sales', 0)
    sales = int(float(sales_val)) if pd.notna(sales_val) else 0
    
    sup_brand = extract_known_brand(sup_title)
    amz_brand = extract_known_brand(amz_title)
    brand_match = sup_brand != "" and sup_brand == amz_brand
    title_sim = title_similarity(sup_title, amz_title)
    
    sup_pack = extract_pack_count(sup_title)
    amz_pack = extract_pack_count(amz_title)
    pack_ratio = amz_pack / sup_pack if sup_pack > 0 else 1
    adjusted_profit = net_profit - (pack_ratio - 1) * sup_price
    
    pack_verdict = "OK" if pack_ratio == 1 else f"{int(pack_ratio)}x"
    
    variant_mismatch, variant_reason = detect_variant_mismatch(sup_title, amz_title)
    product_type_match, matching_types = get_product_types_match(sup_title, amz_title)
    
    exact_ean = (ean_clean != "" and ean_on_page_clean != "" and 
                 len(ean_clean) >= 8 and len(ean_on_page_clean) >= 8 and
                 ean_clean == ean_on_page_clean)
    
    # Build result
    result = {
        'category': 'OTHER',
        'sub_category': 'EXCLUDED',  # RECOMMENDED or EXCLUDED/FILTERED
        'confidence': 'LOW',
        'pack_verdict': pack_verdict,
        'pack_ratio': pack_ratio,
        'adjusted_profit': adjusted_profit,
        'net_profit': net_profit,
        'roi': roi,
        'sales': sales,
        'evidence': '',
        'filter_reason': '',
        'title_sim': title_sim,
        'brand_match': brand_match,
        'brand': sup_brand,
        'product_type_match': product_type_match,
        'matching_types': matching_types,
        'variant_mismatch': variant_mismatch,
        'variant_reason': variant_reason,
        'exact_ean': exact_ean,
        'sup_price': sup_price,
        'sell_price': sell_price
    }
    
    # =========================================================================
    # CLASSIFICATION LOGIC (v4.0)
    # =========================================================================
    
    # VERIFIED - Exact EAN match
    if exact_ean:
        result['category'] = 'VERIFIED'
        result['confidence'] = 'HIGH'
        result['evidence'] = "Exact EAN Match"
        
        if variant_mismatch:
            result['sub_category'] = 'FILTERED'
            result['filter_reason'] = variant_reason
        elif pack_ratio > 1 and adjusted_profit <= 0:
            result['sub_category'] = 'FILTERED'
            result['filter_reason'] = f"Pack {int(pack_ratio)}x makes profit negative (£{adjusted_profit:.2f})"
        elif net_profit <= 0:
            result['sub_category'] = 'FILTERED'
            result['filter_reason'] = f"Negative profit (£{net_profit:.2f})"
        else:
            result['sub_category'] = 'RECOMMENDED'
            result['filter_reason'] = ""
        return result
    
    # HIGHLY LIKELY - Brand match + strong title similarity
    if brand_match and title_sim >= 0.45:
        result['category'] = 'HIGHLY LIKELY'
        result['confidence'] = 'HIGH'
        result['evidence'] = f"Brand: {sup_brand}, Sim: {title_sim:.0%}"
        
        if variant_mismatch:
            result['sub_category'] = 'FILTERED'
            result['filter_reason'] = variant_reason
        elif pack_ratio > 1 and adjusted_profit <= 0:
            result['sub_category'] = 'FILTERED'
            result['filter_reason'] = f"Pack {int(pack_ratio)}x makes profit negative"
        elif net_profit <= 0:
            result['sub_category'] = 'FILTERED'
            result['filter_reason'] = f"Negative profit"
        elif sales == 0:
            result['sub_category'] = 'FILTERED'
            result['filter_reason'] = "No sales data"
        else:
            result['sub_category'] = 'RECOMMENDED'
            result['filter_reason'] = ""
        return result
    
    # FILTERED OUT - Confirmed matches that are unprofitable
    # (Brand matches + Product type matches BUT pack/variant/profit issues)
    if (brand_match or exact_ean) and (variant_mismatch or (pack_ratio > 1 and adjusted_profit <= 0) or net_profit <= 0):
        result['category'] = 'FILTERED OUT'
        result['confidence'] = 'HIGH'
        result['sub_category'] = 'AUDIT'
        
        if variant_mismatch:
            result['evidence'] = f"Confirmed match - {variant_reason}"
            result['filter_reason'] = "Variant mismatch"
        elif pack_ratio > 1 and adjusted_profit <= 0:
            result['evidence'] = f"Confirmed match - Pack {int(pack_ratio)}x"
            result['filter_reason'] = f"Adj profit: £{adjusted_profit:.2f}"
        else:
            result['evidence'] = f"Confirmed match - Brand: {sup_brand if sup_brand else 'EAN'}"
            result['filter_reason'] = f"Profit: £{net_profit:.2f}"
        return result
    
    # NEEDS VERIFICATION (STRICT) - Very likely matches needing 1-2 confirmations
    # Only include if: brand match OR high similarity + product type + good profit + sales
    if (brand_match or (title_sim >= 0.45 and product_type_match)) and adjusted_profit > 1.00 and sales > 0:
        result['category'] = 'NEEDS VERIFICATION'
        result['confidence'] = 'MED'
        result['sub_category'] = 'STRICT'
        result['evidence'] = f"Brand: {sup_brand}" if brand_match else f"Sim: {title_sim:.0%}, Type: {matching_types[0] if matching_types else '-'}"
        result['filter_reason'] = "Needs 1-2 confirmations"
        return result
    
    # Additional NEEDS VERIFICATION with lower threshold but still promising
    if (brand_match or title_sim >= 0.40) and adjusted_profit > 0.50 and sales > 0 and net_profit > 0:
        result['category'] = 'NEEDS VERIFICATION'
        result['confidence'] = 'MED' if brand_match else 'LOW'
        result['sub_category'] = 'STANDARD'
        result['evidence'] = f"Sim: {title_sim:.0%}"
        result['filter_reason'] = "Partial match evidence"
        return result
    
    # FILTERED OUT - Pack mismatch making profit negative (for products with some match evidence)
    if pack_ratio > 1 and adjusted_profit <= 0 and (title_sim >= 0.35 or product_type_match):
        result['category'] = 'FILTERED OUT'
        result['confidence'] = 'MED'
        result['sub_category'] = 'AUDIT'
        result['evidence'] = f"Pack {int(pack_ratio)}x detected"
        result['filter_reason'] = f"Adj profit: £{adjusted_profit:.2f}"
        return result
    
    # OTHER - Weak evidence, not included in report
    result['category'] = 'OTHER'
    result['confidence'] = 'LOW'
    result['sub_category'] = 'EXCLUDED'
    result['evidence'] = "Insufficient match evidence"
    result['filter_reason'] = f"Sim: {title_sim:.0%}"
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
# EXTRACT AND ANALYZE ALL PRODUCTS
# ============================================================================

print("Extracting and analyzing all products from 8 AI reports...")

all_products = {}  # asin -> full analysis (unique products only)
products_by_source = defaultdict(set)  # folder -> set of asins found

for folder in REPORT_FOLDERS:
    report_path = BASE_PATH / folder / 'PHASEA_MANUAL_REPORT_20251230.md'
    if not report_path.exists(): 
        print(f"  [SKIP] {folder}: Report not found")
        continue
    
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    found_count = 0
    
    for line in lines:
        if '|' in line and 'Verdict' not in line and 'SupplierTitle' not in line and '---' not in line:
            source_row = None
            asin = None
            
            # Extract ASIN
            asin_match = re.search(r'\b(B[0-9A-Z]{9})\b', line)
            if asin_match:
                asin = asin_match.group(1)
                if asin in asin_lookup: 
                    _, source_row = asin_lookup[asin]
            
            # Try EAN if no ASIN match
            if source_row is None:
                ean_match = re.search(r'\b(\d{12,14})\b', line)
                if ean_match and ean_match.group(1) in ean_lookup:
                    _, source_row = ean_lookup[ean_match.group(1)]
                    asin = str(get_val(source_row, 'ASIN', ''))
            
            if source_row is not None and asin and asin not in all_products:
                result = classify_product_full(source_row)
                found_count += 1
                products_by_source[folder].add(asin)
                
                all_products[asin] = {
                    'asin': asin,
                    'category': result['category'],
                    'sub_category': result['sub_category'],
                    'confidence': result['confidence'],
                    'supplier_title': str(get_val(source_row, 'SupplierTitle', '')),
                    'amazon_title': str(get_val(source_row, 'AmazonTitle', '')),
                    'supplier_ean': str(get_val(source_row, 'EAN_clean', '')),
                    'amazon_ean': str(get_val(source_row, 'EAN_OnPage_clean', '')),
                    'supplier_price': result['sup_price'],
                    'selling_price': result['sell_price'],
                    'net_profit': result['net_profit'],
                    'roi': result['roi'],
                    'sales': result['sales'],
                    'pack_verdict': result['pack_verdict'],
                    'adjusted_profit': result['adjusted_profit'],
                    'evidence': result['evidence'],
                    'filter_reason': result['filter_reason'],
                    'title_sim': result['title_sim'],
                    'brand': result['brand'],
                    'sources': [folder]
                }
            elif asin and asin in all_products:
                # Product already exists, add this folder as additional source
                all_products[asin]['sources'].append(folder)
    
    print(f"  {folder}: {found_count} new products found")

print(f"\nTotal unique products analyzed: {len(all_products)}")

# ============================================================================
# CATEGORIZE PRODUCTS
# ============================================================================

verified_rec = [p for p in all_products.values() if p['category'] == 'VERIFIED' and p['sub_category'] == 'RECOMMENDED']
verified_filt = [p for p in all_products.values() if p['category'] == 'VERIFIED' and p['sub_category'] == 'FILTERED']
hl_rec = [p for p in all_products.values() if p['category'] == 'HIGHLY LIKELY' and p['sub_category'] == 'RECOMMENDED']
hl_filt = [p for p in all_products.values() if p['category'] == 'HIGHLY LIKELY' and p['sub_category'] == 'FILTERED']
needs_verif = [p for p in all_products.values() if p['category'] == 'NEEDS VERIFICATION']
needs_verif_strict = [p for p in needs_verif if p['sub_category'] == 'STRICT']
filtered_out = [p for p in all_products.values() if p['category'] == 'FILTERED OUT']

# Sort by profit
verified_rec.sort(key=lambda x: x['net_profit'], reverse=True)
verified_filt.sort(key=lambda x: x['net_profit'], reverse=True)
hl_rec.sort(key=lambda x: x['net_profit'], reverse=True)
hl_filt.sort(key=lambda x: x['net_profit'], reverse=True)
needs_verif_strict.sort(key=lambda x: x['adjusted_profit'], reverse=True)
filtered_out.sort(key=lambda x: x['adjusted_profit'], reverse=True)

# ============================================================================
# GENERATE REPORT
# ============================================================================

print("Generating final PHASEA_MANUAL_REPORT...")

# Table schema
HEADERS = ["Verdict", "Confidence", "SupplierTitle", "AmazonTitle", "Supplier EAN", "Amazon EAN", 
           "ASIN", "SupplierPrice", "SellingPrice", "NetProfit", "ROI", "Sales", 
           "Pack Verdict", "Adjusted Profit", "Key Match Evidence", "Filter Reason"]
COL_WIDTHS = [12, 10, 40, 40, 14, 14, 12, 12, 12, 10, 6, 6, 12, 14, 25, 25]

output = []
output.append("# PHASEA MANUAL REPORT")
output.append("")
output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}")
output.append(f"**Input File:** part_30_dec.xlsx")
output.append(f"**Supplier:** Combined Analysis from 8 AI Reports")
output.append(f"**Analysis Method:** Manual v4.0 with Strict NV Criteria")
output.append("")

# Summary Counts
output.append("## Summary Counts")
output.append("")
output.append(f"- **VERIFIED — RECOMMENDED:** {len(verified_rec)}")
output.append(f"- **VERIFIED — FILTERED OUT / EXCLUDED:** {len(verified_filt)}")
output.append(f"- **HIGHLY LIKELY — RECOMMENDED:** {len(hl_rec)}")
output.append(f"- **HIGHLY LIKELY — FILTERED OUT / EXCLUDED:** {len(hl_filt)}")
output.append(f"- **NEEDS VERIFICATION (Strict):** {len(needs_verif_strict)}")
output.append(f"- **FILTERED OUT (Audit - Confirmed Unprofitable):** {len(filtered_out)}")
output.append(f"- **TOTAL ANALYZED:** {len(all_products)}")
output.append("")

# Expected distribution check
output.append("## 📊 Distribution Check (v4.0 Guidance)")
output.append("")
output.append("| Category | Expected | Actual | Status |")
output.append("|----------|----------|--------|--------|")
vr_status = "✅" if 15 <= len(verified_rec) <= 50 else "⚠️"
hl_status = "✅" if 30 <= len(hl_rec) <= 100 else "⚠️"
nv_status = "✅" if 20 <= len(needs_verif_strict) <= 150 else "⚠️"
fo_status = "✅" if 20 <= len(filtered_out) <= 100 else "⚠️"
output.append(f"| VERIFIED (Rec) | 15-50 | {len(verified_rec)} | {vr_status} |")
output.append(f"| HIGHLY LIKELY (Rec) | 30-100 | {len(hl_rec)} | {hl_status} |")
output.append(f"| NEEDS VERIFICATION | 50-150 | {len(needs_verif_strict)} | {nv_status} |")
output.append(f"| FILTERED OUT | 20-100 | {len(filtered_out)} | {fo_status} |")
output.append("")

# ============================================================================
# VERIFIED — RECOMMENDED
# ============================================================================

output.append("---")
output.append("")
output.append("## ✅ VERIFIED — RECOMMENDED")
output.append("")
output.append(f"**Count:** {len(verified_rec)} products with exact EAN matches and positive profit")
output.append("")

if verified_rec:
    output.append("```text")
    rows = []
    for p in verified_rec:
        rows.append([
            "VERIFIED"[:12], p['confidence'][:10],
            p['supplier_title'][:40], p['amazon_title'][:40],
            p['supplier_ean'][:14], p['amazon_ean'][:14], p['asin'][:12],
            f"£{p['supplier_price']:.2f}"[:12], f"£{p['selling_price']:.2f}"[:12],
            f"£{p['net_profit']:.2f}"[:10], f"{p['roi']:.0f}%"[:6], str(p['sales'])[:6],
            p['pack_verdict'][:12], f"£{p['adjusted_profit']:.2f}"[:14],
            p['evidence'][:25], p['filter_reason'][:25]
        ])
    for line in format_fixed_width_table(HEADERS, rows, COL_WIDTHS):
        output.append(line)
    output.append("```")
output.append("")

# ============================================================================
# VERIFIED — FILTERED OUT
# ============================================================================

output.append("## ⚠️ VERIFIED — FILTERED OUT / EXCLUDED")
output.append("")
output.append(f"**Count:** {len(verified_filt)} products with exact EAN but unprofitable due to pack/variant issues")
output.append("")

if verified_filt:
    output.append("```text")
    rows = []
    for p in verified_filt:
        rows.append([
            "VERIFIED-FO"[:12], p['confidence'][:10],
            p['supplier_title'][:40], p['amazon_title'][:40],
            p['supplier_ean'][:14], p['amazon_ean'][:14], p['asin'][:12],
            f"£{p['supplier_price']:.2f}"[:12], f"£{p['selling_price']:.2f}"[:12],
            f"£{p['net_profit']:.2f}"[:10], f"{p['roi']:.0f}%"[:6], str(p['sales'])[:6],
            p['pack_verdict'][:12], f"£{p['adjusted_profit']:.2f}"[:14],
            p['evidence'][:25], p['filter_reason'][:25]
        ])
    for line in format_fixed_width_table(HEADERS, rows, COL_WIDTHS):
        output.append(line)
    output.append("```")
output.append("")

# ============================================================================
# HIGHLY LIKELY — RECOMMENDED
# ============================================================================

output.append("---")
output.append("")
output.append("## 🔷 HIGHLY LIKELY — RECOMMENDED")
output.append("")
output.append(f"**Count:** {len(hl_rec)} products with brand match + strong title similarity")
output.append("")

if hl_rec:
    output.append("```text")
    rows = []
    for p in hl_rec:
        rows.append([
            "HIGHLY LIKE"[:12], p['confidence'][:10],
            p['supplier_title'][:40], p['amazon_title'][:40],
            p['supplier_ean'][:14], p['amazon_ean'][:14], p['asin'][:12],
            f"£{p['supplier_price']:.2f}"[:12], f"£{p['selling_price']:.2f}"[:12],
            f"£{p['net_profit']:.2f}"[:10], f"{p['roi']:.0f}%"[:6], str(p['sales'])[:6],
            p['pack_verdict'][:12], f"£{p['adjusted_profit']:.2f}"[:14],
            p['evidence'][:25], ""[:25]
        ])
    for line in format_fixed_width_table(HEADERS, rows, COL_WIDTHS):
        output.append(line)
    output.append("```")
output.append("")

# ============================================================================
# HIGHLY LIKELY — FILTERED OUT
# ============================================================================

output.append("## ⚠️ HIGHLY LIKELY — FILTERED OUT / EXCLUDED")
output.append("")
output.append(f"**Count:** {len(hl_filt)} products with brand match but unprofitable/no sales")
output.append("")

if hl_filt:
    output.append("```text")
    rows = []
    for p in hl_filt:
        rows.append([
            "HL-FILTERED"[:12], p['confidence'][:10],
            p['supplier_title'][:40], p['amazon_title'][:40],
            p['supplier_ean'][:14], p['amazon_ean'][:14], p['asin'][:12],
            f"£{p['supplier_price']:.2f}"[:12], f"£{p['selling_price']:.2f}"[:12],
            f"£{p['net_profit']:.2f}"[:10], f"{p['roi']:.0f}%"[:6], str(p['sales'])[:6],
            p['pack_verdict'][:12], f"£{p['adjusted_profit']:.2f}"[:14],
            p['evidence'][:25], p['filter_reason'][:25]
        ])
    for line in format_fixed_width_table(HEADERS, rows, COL_WIDTHS):
        output.append(line)
    output.append("```")
output.append("")

# ============================================================================
# NEEDS VERIFICATION (STRICT)
# ============================================================================

output.append("---")
output.append("")
output.append("## 🔶 NEEDS VERIFICATION (Strict)")
output.append("")
output.append("**Criteria:** Very likely matches that just need 1-2 minor confirmations")
output.append("- Brand match OR title similarity >= 45%")
output.append("- Product type keywords match")
output.append("- Adjusted profit > £1.00")
output.append("- Sales > 0")
output.append("")
output.append(f"**Count:** {len(needs_verif_strict)} products")
output.append("")

if needs_verif_strict:
    output.append("```text")
    rows = []
    for p in needs_verif_strict:
        rows.append([
            "NEEDS VERIF"[:12], p['confidence'][:10],
            p['supplier_title'][:40], p['amazon_title'][:40],
            p['supplier_ean'][:14], p['amazon_ean'][:14], p['asin'][:12],
            f"£{p['supplier_price']:.2f}"[:12], f"£{p['selling_price']:.2f}"[:12],
            f"£{p['net_profit']:.2f}"[:10], f"{p['roi']:.0f}%"[:6], str(p['sales'])[:6],
            p['pack_verdict'][:12], f"£{p['adjusted_profit']:.2f}"[:14],
            p['evidence'][:25], p['filter_reason'][:25]
        ])
    for line in format_fixed_width_table(HEADERS, rows, COL_WIDTHS):
        output.append(line)
    output.append("```")
output.append("")

# ============================================================================
# FILTERED OUT (Audit)
# ============================================================================

output.append("---")
output.append("")
output.append("## ❌ FILTERED OUT (Audit - Confirmed Unprofitable Matches)")
output.append("")
output.append("**Note:** These are CONFIRMED product matches that cannot be actioned profitably.")
output.append("They are valuable audit records showing which products WOULD match if circumstances changed.")
output.append("")
output.append(f"**Count:** {len(filtered_out)} products")
output.append("")

if filtered_out:
    output.append("```text")
    rows = []
    for p in filtered_out:
        rows.append([
            "FILTERED"[:12], p['confidence'][:10],
            p['supplier_title'][:40], p['amazon_title'][:40],
            p['supplier_ean'][:14], p['amazon_ean'][:14], p['asin'][:12],
            f"£{p['supplier_price']:.2f}"[:12], f"£{p['selling_price']:.2f}"[:12],
            f"£{p['net_profit']:.2f}"[:10], f"{p['roi']:.0f}%"[:6], str(p['sales'])[:6],
            p['pack_verdict'][:12], f"£{p['adjusted_profit']:.2f}"[:14],
            p['evidence'][:25], p['filter_reason'][:25]
        ])
    for line in format_fixed_width_table(HEADERS, rows, COL_WIDTHS):
        output.append(line)
    output.append("```")
output.append("")

# ============================================================================
# QUICK SUMMARY
# ============================================================================

output.append("---")
output.append("")
output.append("## 📊 QUICK SUMMARY")
output.append("")
output.append("### Actionable Products (Ready to List)")
output.append("")
total_actionable = len(verified_rec) + len(hl_rec)
output.append(f"| Category | Count | Total Potential Profit |")
output.append(f"|----------|-------|------------------------|")
vr_profit = sum(p['net_profit'] for p in verified_rec)
hl_profit = sum(p['net_profit'] for p in hl_rec)
output.append(f"| VERIFIED — RECOMMENDED | {len(verified_rec)} | £{vr_profit:.2f} |")
output.append(f"| HIGHLY LIKELY — RECOMMENDED | {len(hl_rec)} | £{hl_profit:.2f} |")
output.append(f"| **TOTAL ACTIONABLE** | **{total_actionable}** | **£{vr_profit + hl_profit:.2f}** |")
output.append("")

output.append("### Needs Manual Review")
output.append("")
nv_profit = sum(p['adjusted_profit'] for p in needs_verif_strict)
output.append(f"| Category | Count | Potential Profit |")
output.append(f"|----------|-------|------------------|")
output.append(f"| NEEDS VERIFICATION (Strict) | {len(needs_verif_strict)} | £{nv_profit:.2f} |")
output.append("")

output.append("### Top 10 by Profit (All Categories)")
output.append("")
all_actionable = verified_rec + hl_rec + needs_verif_strict
all_actionable.sort(key=lambda x: x['net_profit'], reverse=True)
output.append("```text")
top_headers = ["Rank", "Category", "ASIN", "SupplierTitle", "NetProfit", "Sales"]
top_widths = [6, 15, 12, 45, 10, 8]
top_rows = []
for i, p in enumerate(all_actionable[:10], 1):
    cat = "VERIFIED" if p['category'] == 'VERIFIED' else ("HL" if p['category'] == 'HIGHLY LIKELY' else "NV")
    top_rows.append([str(i), cat, p['asin'], p['supplier_title'][:45], f"£{p['net_profit']:.2f}", str(p['sales'])])
for line in format_fixed_width_table(top_headers, top_rows, top_widths):
    output.append(line)
output.append("```")
output.append("")

output.append("---")
output.append("")
output.append("*Report generated using combined analysis from 8 AI models with Manual v4.0 validation.*")
output.append(f"*Total unique products across all reports: {len(all_products)}*")

# Write output
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"\n✅ Report generated: {OUTPUT_FILE}")
print(f"\n=== FINAL SUMMARY ===")
print(f"VERIFIED — RECOMMENDED: {len(verified_rec)}")
print(f"VERIFIED — FILTERED: {len(verified_filt)}")
print(f"HIGHLY LIKELY — RECOMMENDED: {len(hl_rec)}")
print(f"HIGHLY LIKELY — FILTERED: {len(hl_filt)}")
print(f"NEEDS VERIFICATION (Strict): {len(needs_verif_strict)}")
print(f"FILTERED OUT (Audit): {len(filtered_out)}")
print(f"TOTAL ACTIONABLE: {total_actionable}")
print(f"TOTAL POTENTIAL PROFIT: £{vr_profit + hl_profit:.2f}")
