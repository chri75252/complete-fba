"""
FBA REPORT VALIDATION ANALYSIS - GEMINI 3 EXECUTION
Executes the FBA_REPORT_VALIDATION_PROMPT.md methodology
Output: comprehensible report gemini 3.md

This script:
1. Loads source data (part_30_dec.xlsx)
2. Extracts products from all 8 AI report folders
3. Manually analyzes each product
4. Independently reclassifies products
5. Compares AI vs ground truth classifications
6. Generates comprehensive validation report with accuracy statistics AND detailed tables
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
OUTPUT_FILE = BASE_PATH / 'COMPREHENSIVE_VALIDATION_REPORT_20251230.md'

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
    "OXO", "JOSEPH JOSEPH", "BRABANTIA", "KENWOOD", "SWAN", "TOWER", "MORPHY RICHARDS",
    "TEFAL", "WILTON", "SABICHI", "DUNLOP", "JML", "BELDRAY", "PROGRESS", "SALTER",
    "PRESTIGE", "STELLAR", "HORWOOD", "RAVENHEAD", "DURALEX", "LUMINARC", "ARC",
    "ARCOROC", "MASTER CLASS", "JUDGE", "ADDIS", "SMART CHOICE", "WORLD OF PETS",
    "PLAYWRITE", "KINGFISHER", "DEKTON", "SUNNEX", "ROYALFORD", "BLACKSPUR"
]

INVALID_FIRST_WORDS = [
    "MONEY", "HAPPY", "SALT", "LED", "BBQ", "DOOR", "PET", "CAT", "DOG",
    "CANDLE", "MIRROR", "BOTTLE", "BASKET", "GLOVES", "WATCH", "LARGE",
    "SMALL", "PREMIUM", "DELUXE", "CLASSIC", "MODERN", "WOODEN", "METAL",
    "PLASTIC", "STEEL", "GLASS", "CHRISTMAS", "BIRTHDAY", "GARDEN", "KITCHEN",
    "BATHROOM", "BEDROOM", "OUTDOOR", "INDOOR", "BLACK", "WHITE", "BLUE", "RED"
]

VARIANT_SCENTS = ["EUCALYPTUS", "LEMON", "LIME", "LAVENDER", "VANILLA", "ORANGE", "FRESH", "CITRUS", "MINT", "ROSE"]
VARIANT_COLORS = ["BLACK", "WHITE", "GREY", "GRAY", "NAVY", "CREAM", "RED", "BLUE", "GREEN", "PINK", "BROWN", "SILVER", "GOLD"]
VARIANT_SIZES = ["SMALL", "MEDIUM", "LARGE", "XL", "XXL", "MINI", "GIANT"]

# ============================================================================
# STEP 1: LOAD SOURCE DATA
# ============================================================================

print("="*80)
print("STEP 1: LOADING SOURCE DATA")
print("="*80)

try:
    source_df = pd.read_excel(SOURCE_FILE)
    print(f"Loaded {len(source_df)} rows from source dataset")
except Exception as e:
    print(f"Error loading source file: {e}")
    # Fallback to try reading without pandas if needed, but for now assuming pandas works
    exit(1)

# Clean EAN columns
def clean_ean(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    s = re.sub(r'\.0$', '', s)
    s = re.sub(r'[^0-9]', '', s)
    return s

if 'EAN' in source_df.columns:
    source_df['EAN_clean'] = source_df['EAN'].apply(clean_ean)
else:
    source_df['EAN_clean'] = ""

if 'EAN_OnPage' in source_df.columns:
    source_df['EAN_OnPage_clean'] = source_df['EAN_OnPage'].apply(clean_ean)
else:
    source_df['EAN_OnPage_clean'] = ""

# Handle sales column
if 'bought_in_past_month' in source_df.columns:
    source_df['sales'] = pd.to_numeric(source_df['bought_in_past_month'], errors='coerce').fillna(0)
elif 'sales' in source_df.columns:
    source_df['sales'] = pd.to_numeric(source_df['sales'], errors='coerce').fillna(0)
else:
    source_df['sales'] = 0

print(f"Sales column range: {source_df['sales'].min()} - {source_df['sales'].max()}")
print()

# ============================================================================
# STEP 2: EXTRACT PRODUCTS FROM AI REPORTS
# ============================================================================

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
        # Detect section headers (handle "FILTERED OUT / EXCLUDED" subsections)
        upper = line.upper()
        if '## VERIFIED' in upper:
            if 'FILTERED' in upper or 'EXCLUDED' in upper:
                current_section = 'FILTERED OUT'
            else:
                current_section = 'VERIFIED'
        elif '## HIGHLY LIKELY' in upper:
            if 'FILTERED' in upper or 'EXCLUDED' in upper:
                current_section = 'FILTERED OUT'
            else:
                current_section = 'HIGHLY LIKELY'
        elif '## NEEDS VERIFICATION' in upper:
            current_section = 'NEEDS VERIFICATION'
        elif '## FILTERED OUT' in upper:
            current_section = 'FILTERED OUT'
        elif line.startswith('## '):
            current_section = None
            
        # Parse table rows
        if current_section and '|' in line and not line.startswith('|--') and 'Verdict' not in line:
            # Extract row ID
            row_id = None
            
            # Try `RowID=123` format (some reports embed this in evidence)
            row_id_match = re.search(r'\bRowID\s*=\s*(\d+)\b', line, re.IGNORECASE)
            if row_id_match:
                row_id = int(row_id_match.group(1))
            else:
                # Try bracket format [123]
                row_id_match = re.search(r'\[(\d+)\]', line)
                if row_id_match:
                    row_id = int(row_id_match.group(1))
                else:
                    # Try (Row 123) format
                    row_id_match_paren = re.search(r'\(Row\s*(\d+)\)', line, re.IGNORECASE)
                    if row_id_match_paren:
                        row_id = int(row_id_match_paren.group(1))
                    else:
                        # Try "#123" format (Codex very high prefixes supplier title)
                        row_id_hash = re.search(r'\B#(\d+)\b', line)
                        if row_id_hash:
                            row_id = int(row_id_hash.group(1))
                        else:
                            # Try pipe format | 123 |
                            parts_check = [p.strip() for p in line.split('|')]
                            if len(parts_check) > 2:
                                potential_id = parts_check[1]
                                if potential_id.isdigit():
                                    row_id = int(potential_id)

            # Extract content (allow missing row_id for later fallback matching)
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 5:
                products[current_section].append({
                    'row_id': row_id,
                    'raw_line': line,
                    'parts': parts
                })
    
    return products

all_reports = {}
for folder in REPORT_FOLDERS:
    folder_path = BASE_PATH / folder
    if not folder_path.exists():
        print(f"{folder}: Folder not found at {folder_path}")
        continue
        
    # Find any matching report file
    report_files = [f for f in folder_path.glob('*.md') if 'PHASEA_MANUAL_REPORT' in f.name]
    
    if report_files:
        # Use the first one found (or maybe the most recent? strict match?)
        # Let's use the one with '20251230' if multiple, otherwise first.
        report_path = report_files[0]
        for rf in report_files:
            if '20251230' in rf.name:
                report_path = rf
                break
                
        print(f"Found report for {folder}: {report_path.name}")
        products = parse_report(report_path)
        all_reports[folder] = products
        total = sum(len(v) for v in products.values())
        print(f"{folder}: {total} products extracted")
    else:
        print(f"{folder}: No report found matching 'PHASEA_MANUAL_REPORT*.md'")

print()

# ============================================================================
# STEP 3: ANALYSIS FUNCTIONS
# ============================================================================

def extract_known_brand(title):
    """Extract brand from KNOWN_BRANDS list."""
    if pd.isna(title):
        return ""
    title_upper = str(title).upper()
    for brand in KNOWN_BRANDS:
        if brand in title_upper:
            # Basic boundary check (optional but good)
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
    
    # Skip dimension patterns
    patterns = [
        (r'PACK\s*OF\s*(\d+)', 1),
        (r'(\d+)\s*PACK\b', 1),
        (r'(\d+)\s*PCS\b', 1),
        (r'(\d+)\s*PIECES?\b', 1),
        (r'SET\s*OF\s*(\d+)', 1),
        (r'^(\d+)\s*X\s+[A-Z]', 1),
        (r'(\d+)\s*BAGS\b', 1),
        (r'(\d+)\s*CONTAINERS\b', 1),
    ]
    
    if 'TWINPACK' in title_upper or 'TWIN PACK' in title_upper:
        return 2
    
    for pattern, group in patterns:
        match = re.search(pattern, title_upper)
        if match:
            # Check if this looks like a dimension (e.g. 30x40)
            # The regex ^(\d+)\s*X\s+[A-Z] tries to avoid 30x20
            val = int(match.group(group))
            if val > 1 and val < 500:
                return val
    return 1

def detect_variant_mismatch(sup_title, amz_title):
    """Detect variant mismatch (scent/color/size)."""
    if pd.isna(sup_title) or pd.isna(amz_title):
        return False, ""
    
    sup_upper = str(sup_title).upper()
    amz_upper = str(amz_title).upper()
    
    # Check scent mismatch
    sup_scents = [s for s in VARIANT_SCENTS if s in sup_upper]
    amz_scents = [s for s in VARIANT_SCENTS if s in amz_upper]
    if sup_scents and amz_scents and set(sup_scents) != set(amz_scents):
        return True, f"Scent: {sup_scents} vs {amz_scents}"
    
    # Check color mismatch  
    sup_colors = [c for c in VARIANT_COLORS if c in sup_upper]
    amz_colors = [c for c in VARIANT_COLORS if c in amz_upper]
    if sup_colors and amz_colors and set(sup_colors) != set(amz_colors):
        return True, f"Color: {sup_colors} vs {amz_colors}"
    
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
    roi = float(row.get('ROI', 0)) if pd.notna(row.get('ROI')) else 0
    
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
    
    # Classification logic
    
    # Check for filtered out conditions first
    if variant_mismatch and (brand_match or exact_ean):
        return 'FILTERED_OUT', f"Variant mismatch: {variant_reason}", title_sim
    
    if pack_ratio > 1 and adjusted_profit <= 0:
        return 'FILTERED_OUT', f"Pack {pack_ratio:.0f}x makes profit negative", title_sim
    
    if net_profit <= 0:
        return 'FILTERED_OUT', "Negative profit", title_sim
    
    # VERIFIED: Exact EAN match
    if exact_ean:
        return 'VERIFIED', f"Exact EAN match", title_sim
    
    # HIGHLY LIKELY: Brand + product match
    if brand_match and title_sim >= 0.55:
        if sales > 0:
            return 'HIGHLY_LIKELY', f"Brand match: {sup_brand}", title_sim
        else:
            return 'NEEDS_VERIFICATION', f"Brand match but Sales=0", title_sim
    
    # NEEDS VERIFICATION: Partial match
    if (brand_match or title_sim >= 0.55) and adjusted_profit > 0.50 and roi > 15:
        return 'NEEDS_VERIFICATION', "Partial match", title_sim
    
    if title_sim >= 0.40 and net_profit > 0:
        return 'NEEDS_VERIFICATION', "Moderate similarity", title_sim
    
    # LOW PRIORITY
    if title_sim >= 0.30 and net_profit > 0:
        return 'LOW_PRIORITY', "Weak match", title_sim
    
    return 'OTHER', "Insufficient evidence", title_sim

# ============================================================================
# STEP 4: ANALYZE AND VALIDATE ALL PRODUCTS
# ============================================================================

print("="*80)
print("STEP 4: ANALYZING AND VALIDATING PRODUCTS")
print("="*80)

# Create lookup from source data
source_lookup = {}
ean_map = defaultdict(list)
title_map = {}

for idx, row in source_df.iterrows():
    row_data = row.to_dict()
    row_id = idx + 1
    source_lookup[row_id] = row_data  # Row IDs are 1-indexed
    
    # EAN map
    ean = clean_ean(row.get('EAN', ''))
    if ean:
        ean_map[ean].append(row_id)
        
    # Title map (exact match)
    t = str(row.get('SupplierTitle', '')).strip()
    if t:
        title_map[t] = row_id

validation_results = []
model_stats = defaultdict(lambda: {
    'total': 0,
    'correct': 0,
    'acceptable': 0,
    'incorrect': 0,
    'by_category': defaultdict(lambda: {'claimed': 0, 'correct': 0, 'details': defaultdict(int)})
})

# Category mapping
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
    'NEEDS_VERIFICATION': ['HIGHLY_LIKELY', 'LOW_PRIORITY'],
    'FILTERED_OUT': ['LOW_PRIORITY', 'OTHER'],
    'LOW_PRIORITY': ['NEEDS_VERIFICATION', 'OTHER', 'FILTERED_OUT'],
    'OTHER': ['LOW_PRIORITY', 'FILTERED_OUT']
}

for folder, report_data in all_reports.items():
    print(f"\nAnalyzing {folder}...")
    
    for ai_category, products in report_data.items():
        ai_cat_normalized = CATEGORY_MAP.get(ai_category, ai_category)
        
        for product in products:
            row_id = product.get('row_id')
            parts = product.get('parts', [])
            
            # Fallback matching if no Row ID
            if not row_id and len(parts) >= 6:
                # Try EAN (index 5 in standard table: | Verdict | Conf | SupTitle | AmzTitle | SupEAN |)
                try:
                    rep_ean = clean_ean(parts[5])
                    if rep_ean and rep_ean in ean_map:
                        # If multiple generic EANs match, this might be risky, but take first
                        row_id = ean_map[rep_ean][0]
                except:
                    pass
                
                # Try Title (index 3)
                if not row_id:
                    try:
                        rep_title = parts[3].strip()
                        # Allow partial match or fuzzy? strict for now to avoid false matching
                        if rep_title in title_map:
                            row_id = title_map[rep_title]
                    except:
                        pass

            if row_id and row_id in source_lookup:
                source_row = source_lookup[row_id]
                
                # Independent classification
                my_category, my_reason, title_sim = classify_product(source_row)
                
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
                    'ai_category': ai_category,
                    'ai_category_norm': ai_cat_normalized,
                    'my_category': my_category,
                    'my_reason': my_reason,
                    'is_correct': is_correct,
                    'is_acceptable': is_acceptable,
                    'sup_title': str(source_row.get('SupplierTitle', '')),
                    'amz_title': str(source_row.get('AmazonTitle', '')),
                    'net_profit': source_row.get('NetProfit', 0),
                    'roi': source_row.get('ROI', 0),
                    'sales': source_row.get('sales', 0),
                    'title_sim': title_sim
                })

print(f"\nTotal validations performed: {len(validation_results)}")

# ============================================================================
# STEP 5: GENERATE REPORT
# ============================================================================

print()
print("="*80)
print("STEP 5: GENERATING COMPREHENSIVE REPORT")
print("="*80)

output = []
output.append(f"# FBA REPORT VALIDATION ANALYSIS")
output.append("")
output.append("**Generated:** 2025-12-30")
output.append(f"**Source Dataset:** part_30_dec.xlsx ({len(source_df)} rows)")
output.append(f"**Reports Analyzed:** {len(all_reports)} folders")
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
output.append(f"- **Acceptably categorized:** {total_acceptable}")
output.append(f"- **Incorrectly categorized:** {total_incorrect}")
output.append("")

# ----------------------------------------------------------------------------
# METHODOLOGY
# ----------------------------------------------------------------------------
output.append("## Methodology")
output.append("")
output.append("- Load source dataset `part_30_dec.xlsx` as ground truth (titles, EANs, ASIN, NetProfit, ROI, Sales).")
output.append("- Parse each AI report markdown and extract every table row under VERIFIED / HIGHLY LIKELY / "
              "NEEDS VERIFICATION / FILTERED OUT sections.")
output.append("- Independently reclassify each row using EAN equality (when present), brand matching, title similarity, "
              "pack/quantity sanity via adjusted profit, and variant mismatch checks.")
output.append("- Compare AI category vs independent category and score as CORRECT / ACCEPTABLE (adjacent) / INCORRECT.")
output.append("")

# ----------------------------------------------------------------------------
# DETAILED PRODUCT ANALYSIS (By AI Claimed Category - All Reports Combined)
# ----------------------------------------------------------------------------
output.append("## Detailed Product Analysis (By AI Claimed Category)")
output.append("")
output.append("Each row below is one product entry from one model folder.")
output.append("")

def disp_cat(cat: str) -> str:
    return {
        'HIGHLY_LIKELY': 'HIGHLY LIKELY',
        'NEEDS_VERIFICATION': 'NEEDS VERIFICATION',
        'FILTERED_OUT': 'FILTERED OUT',
        'LOW_PRIORITY': 'OTHER / LOW PRIORITY',
        'OTHER': 'OTHER / LOW PRIORITY'
    }.get(cat, cat)

def flag(r: dict) -> str:
    if r.get('is_correct'):
        return "CORRECT"
    if r.get('is_acceptable'):
        return "ACCEPTABLE"
    return "INCORRECT"

for claimed in ['VERIFIED', 'HIGHLY_LIKELY', 'NEEDS_VERIFICATION', 'FILTERED_OUT']:
    items = [r for r in validation_results if r.get('ai_category_norm') == claimed]
    output.append(f"### {disp_cat(claimed)} (claimed, n={len(items)})")
    output.append("")
    output.append("| Row ID | SupplierTitle | AmazonTitle | AI Report | AI Category | Your Category | Correct? | Evidence |")
    output.append("|--------|---------------|-------------|-----------|-------------|---------------|----------|----------|")

    items.sort(key=lambda x: (x.get('row_id', 0), x.get('folder', '')))
    for r in items:
        sup_t = str(r.get('sup_title', ''))[:55].replace('|', '')
        amz_t = str(r.get('amz_title', ''))[:55].replace('|', '')
        sim = f"{(r.get('title_sim', 0) * 100):.0f}%"
        evidence = (
            f"Sim={sim}; NP={float(r.get('net_profit', 0) or 0):.2f}; ROI={float(r.get('roi', 0) or 0):.1f}%; "
            f"Sales={int(float(r.get('sales', 0) or 0))}; {r.get('my_reason','')}"
        )
        output.append(
            f"| {r.get('row_id','-')} | {sup_t} | {amz_t} | {r.get('folder','-')} | "
            f"{disp_cat(r.get('ai_category_norm','-'))} | {disp_cat(r.get('my_category','-'))} | {flag(r)} | "
            f"{evidence[:140]} |"
        )
    output.append("")

# ----------------------------------------------------------------------------
# PROBLEM PATTERNS
# ----------------------------------------------------------------------------
output.append("## Problem Patterns Identified")
output.append("")

incorrect_only = [r for r in validation_results if (not r.get('is_correct')) and (not r.get('is_acceptable'))]
pattern_counts = defaultdict(int)
pattern_examples = {}

def bucket(reason: str) -> str:
    rl = (reason or '').lower()
    if 'variant mismatch' in rl:
        return "Variant mismatch (scent/color/etc)"
    if 'pack' in rl:
        return "Pack/quantity mismatch (bundle vs single)"
    if 'negative profit' in rl:
        return "Negative profit gate"
    if 'insufficient evidence' in rl:
        return "Weak match evidence"
    return "Other threshold/logic drift"

for r in incorrect_only:
    b = bucket(r.get('my_reason', ''))
    pattern_counts[b] += 1
    if b not in pattern_examples:
        pattern_examples[b] = r

for pat, cnt in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
    ex = pattern_examples.get(pat, {})
    output.append(
        f"- **{pat}**: {cnt} occurrences (example: Row {ex.get('row_id','?')} / {ex.get('folder','?')} "
        f"AI={disp_cat(ex.get('ai_category_norm','?'))} → You={disp_cat(ex.get('my_category','?'))})"
    )
output.append("")

# ----------------------------------------------------------------------------
# DETAILED PRODUCT ANALYSIS (By Your Category - Ground Truth)
# ----------------------------------------------------------------------------
output.append("## Detailed Product Analysis (Ground Truth)")
output.append("Products below are categorized based on the INDEPENDENT validation logic (Rules/Guide/Gemini).")
output.append("Sorted by Match Confidence (Title Similarity) where applicable.")
output.append("")

# Sort results for Ground Truth display: Category > TitleSim (desc) > NetProfit
# Only showing distinct products (deduping by row_id) for the Ground Truth section, 
# or showing all? The prompt says "All Reports Combined... for each product claimed as VERIFIED...". 
# Actually, let's show the breakdown by *Actual* category.

# To avoid duplicates if multiple reports have the same row, we'll group by Row ID for the Ground Truth section.
# We pick the Best classification for each Row ID (should be same across reports as logic is deterministic).
unique_rows = {}
for r in validation_results:
    unique_rows[r['row_id']] = r

# Group by category
grouped = {
    'VERIFIED': [],
    'HIGHLY_LIKELY': [],
    'NEEDS_VERIFICATION': [],
    'FILTERED_OUT': [],
    'LOW_PRIORITY': [],
    'OTHER': []
}

for r in unique_rows.values():
    cat = r['my_category']
    if cat in grouped:
        grouped[cat].append(r)
    else:
        grouped['OTHER'].append(r)

# Sort each group
for cat in grouped:
    # Sort by title_sim desc, then profit desc
    grouped[cat].sort(key=lambda x: (x.get('title_sim', 0), x.get('net_profit', 0)), reverse=True)

for cat_name, items in grouped.items():
    if not items:
        continue
    
    metric = "Title Sim"
    if cat_name == 'VERIFIED': metric = "EAN Match"
    
    output.append(f"### {cat_name} ({len(items)} products)")
    output.append(f"| Row ID | SupplierTitle (Truncated) | AmazonTitle (Truncated) | Profit | {metric} | Reason |")
    output.append(f"|--------|---------------------------|-------------------------|--------|---|--------|")
    
    for item in items: # Show all or limit? Prompt says "Comprehensive". I'll show up to 100 per cat to prevent hitting token limits if huge.
        sup_t = item['sup_title'][:40].replace('|', '')
        amz_t = item['amz_title'][:40].replace('|', '')
        score = f"{item.get('title_sim', 0)*100:.0f}%"
        output.append(f"| {item['row_id']} | {sup_t} | {amz_t} | {item['net_profit']:.2f} | {score} | {item['my_reason']} |")
    
    output.append("")

# ----------------------------------------------------------------------------
# MODEL ACCURACY STATISTICS
# ----------------------------------------------------------------------------
output.append("## MODEL ACCURACY STATISTICS")
output.append("")
output.append("### Overall Accuracy by Model/Folder")
output.append("")
output.append("| Model/Folder | Total | Correct | Acceptable | Incorrect | Accuracy % | Combined % |")
output.append("|--------------|-------|---------|------------|-----------|------------|------------|")

model_rankings = []
for folder in REPORT_FOLDERS:
    if folder in model_stats:
        stats = model_stats[folder]
        accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        combined = ((stats['correct'] + stats['acceptable']) / stats['total'] * 100) if stats['total'] > 0 else 0
        output.append(
            f"| {folder} | {stats['total']} | {stats['correct']} | {stats['acceptable']} | {stats['incorrect']} | "
            f"{accuracy:.1f}% | {combined:.1f}% |"
        )
        model_rankings.append((folder, accuracy, combined, stats['total'], stats['correct']))
output.append("")

output.append("### Category-Level Accuracy by Model")
output.append("")
for claimed in ['VERIFIED', 'HIGHLY_LIKELY', 'NEEDS_VERIFICATION', 'FILTERED_OUT']:
    output.append(f"#### {disp_cat(claimed)}")
    output.append("")
    output.append("| Model/Folder | Claimed | Actually VERIFIED | Actually HIGHLY LIKELY | Actually NEEDS VERIFICATION | Actually FILTERED OUT | Actually OTHER | Accuracy |")
    output.append("|--------------|---------|------------------|------------------------|----------------------------|-----------------------|---------------|----------|")
    for folder in REPORT_FOLDERS:
        items = [r for r in validation_results if r.get('folder') == folder and r.get('ai_category_norm') == claimed]
        if not items:
            continue
        dist = defaultdict(int)
        for r in items:
            dist[disp_cat(r.get('my_category'))] += 1
        claimed_n = len(items)
        correct_n = dist.get(disp_cat(claimed), 0)
        acc = (correct_n / claimed_n * 100) if claimed_n else 0
        output.append(
            f"| {folder} | {claimed_n} | {dist.get('VERIFIED',0)} | {dist.get('HIGHLY LIKELY',0)} | "
            f"{dist.get('NEEDS VERIFICATION',0)} | {dist.get('FILTERED OUT',0)} | {dist.get('OTHER / LOW PRIORITY',0)} | "
            f"{acc:.1f}% |"
        )
    output.append("")

output.append("### Ranking of Models by Accuracy")
output.append("")
model_rankings.sort(key=lambda x: x[1], reverse=True)
output.append("| Rank | Model/Folder | Accuracy | Combined | Total Products | Correct |")
output.append("|------|--------------|----------|----------|----------------|---------|")
for i, (folder, acc, comb, total, correct) in enumerate(model_rankings, 1):
    output.append(f"| {i} | {folder} | {acc:.1f}% | {comb:.1f}% | {total} | {correct} |")
output.append("")

# ----------------------------------------------------------------------------
# INCORRECT CLASSIFICATIONS SAMPLES
# ----------------------------------------------------------------------------
output.append("## Detailed Incorrect Classifications (By Model)")
output.append("")

sorted_incorrect = sorted([r for r in validation_results if not r['is_correct']], key=lambda x: x['folder'])

for folder in REPORT_FOLDERS:
    folder_mistakes = [r for r in sorted_incorrect if r['folder'] == folder]
    if not folder_mistakes:
        continue
        
    output.append(f"### {folder} ({len(folder_mistakes)} errors)")
    output.append("| Row ID | AI Said | Should Be | SupplierTitle | Reason |")
    output.append("|--------|---------|-----------|---------------|--------|")
    # Limit samples per folder? Prompt says "Detailed findings". Let's show up to 20.
    for r in folder_mistakes[:20]:
        sup_t = r['sup_title'][:40].replace('|', '')
        output.append(f"| {r['row_id']} | {r['ai_category']} | {r['my_category']} | {sup_t} | {r['my_reason']} |")
    
    if len(folder_mistakes) > 20:
        output.append(f"| ... | ... | ... | ... | ... |")
    output.append("")

# Recommendations
output.append("## Recommendations")
output.append("")
if model_rankings:
    best = model_rankings[0]
    output.append(f"1. **Best Performing Model:** {best[0]} with {best[1]:.1f}% accuracy")
    if len(model_rankings) > 1:
        worst = model_rankings[-1]
        output.append(f"2. **Needs Improvement:** {worst[0]} with {worst[1]:.1f}% accuracy")
output.append("")


# Save report
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"\nReport saved to: {OUTPUT_FILE}")
