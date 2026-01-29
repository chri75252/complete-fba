"""
FBA Product Analysis - Stage 5B-6B: Thorough Manual Analysis & Report Generation
v4.0 Protocol Implementation
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
from pathlib import Path

# Paths
INPUT_PATH = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\Opus\intermediate_analysis.csv")
OUTPUT_DIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\Opus")

# Load preprocessed data
df = pd.read_csv(INPUT_PATH)
print(f"Loaded {len(df)} rows for thorough analysis")

# ===== KNOWN BRANDS LIST =====
KNOWN_BRANDS = [
    'AMTECH', 'ROLSON', 'DRAPER', 'STANLEY', 'FAITHFULL', 'SILVERLINE',
    'EVERBUILD', 'SOUDAL', 'UNIBOND', 'GORILLA', 'LOCTITE', 'BOSTIK',
    'KILROCK', 'DETTOL', 'FAIRY', 'FLASH', 'FINISH', 'VANISH', 'CILLIT',
    'MARIGOLD', 'VILEDA', 'SPONTEX', 'ADDIS', 'WHATMORE', 'WHAM',
    'PYREX', 'MASON CASH', 'KITCHENCRAFT', 'CHEF AID', 'JUDGE', 'PRESTIGE',
    'HARRIS', 'HAMILTON', 'PRODEC', 'RONSEAL', 'CUPRINOL', 'DULUX',
    'STATUS', 'ENERGIZER', 'DURACELL', 'PANASONIC', 'EVEREADY',
    'DUNLOP', 'SLAZENGER', 'DONNAY', 'PUMA', 'LONSDALE',
    'LITTLE TREES', 'CALIFORNIA SCENTS', 'AIRWICK', 'GLADE', 'FEBREZE',
    'TIDYZ', 'EASY BAG', 'REFUSE', 'DUZZIT', 'JEYES',
    'ROUNDUP', 'WEEDOL', 'MIRACLE GRO', 'LEVINGTON', 'WESTLAND',
    'EXTRA', 'EXTRASTAR', 'PIFCO', 'TOWER', 'BREVILLE',
    'BLUE CANYON', 'CROYDEX', 'SHOWERDRAPE', 'AQUALUX',
    'SABICHI', 'PREMIER', 'APOLLO', 'HOME COLLECTION',
    'KLEENEZE', 'JML', 'OXO', 'JOSEPH JOSEPH',
    # More brands from the data
    'KINGFISHER', 'WILKO', 'B&Q', 'HOMEBASE', 'SCREWFIX',
    'LEIFHEIT', 'BRABANTIA', 'CURVER', 'RUBBERMAID',
    'ZIPLOC', 'GLAD', 'HEFTY', 'BACOFOIL',
    '151', '151 PRODUCTS', 'ONTEX', 'ID EXPERT',
    'TENA', 'ATTENDS', 'ALWAYS', 'BODYFORM',
]

# IP RISK BRANDS (luxury/trademark - only flag these)
IP_RISK_BRANDS = [
    'JO MALONE', 'CHANEL', 'DIOR', 'GUCCI', 'LOUIS VUITTON', 'PRADA', 
    'HERMES', 'APPLE', 'SAMSUNG', 'SONY', 'MICROSOFT', 'NIKE', 'ADIDAS',
    'DYSON', 'BOSE', 'BEATS', 'ROLEX', 'OMEGA', 'CARTIER',
]

def extract_brand(title):
    """Extract brand from title"""
    if pd.isna(title):
        return None
    title_upper = str(title).upper()
    for brand in KNOWN_BRANDS:
        if brand.upper() in title_upper:
            return brand
    return None

def titles_share_brand(sup_title, amz_title):
    """Check if both titles share the same brand"""
    sup_brand = extract_brand(sup_title)
    amz_brand = extract_brand(amz_title)
    if sup_brand and amz_brand:
        return sup_brand.upper() == amz_brand.upper()
    return False

def is_ip_risk(title):
    """Check if title contains IP risk brand"""
    if pd.isna(title):
        return False
    title_upper = str(title).upper()
    for brand in IP_RISK_BRANDS:
        if brand in title_upper:
            return True
    return False

def extract_product_type(title):
    """Extract product type keywords from title"""
    if pd.isna(title):
        return []
    title_lower = str(title).lower()
    
    product_keywords = [
        'hammer', 'screwdriver', 'pliers', 'wrench', 'spanner', 'saw',
        'drill', 'chisel', 'trowel', 'brush', 'roller', 'tape',
        'glue', 'adhesive', 'sealant', 'filler', 'putty',
        'bowl', 'plate', 'cup', 'mug', 'dish', 'pan', 'pot', 'casserole',
        'bin', 'bucket', 'basket', 'box', 'container', 'bag', 'bags',
        'torch', 'light', 'lamp', 'bulb', 'battery', 'plug', 'socket',
        'mirror', 'hook', 'hanger', 'rail', 'shelf', 'bracket',
        'gloves', 'mask', 'goggles', 'pad', 'pads', 'liner', 'liners',
        'spray', 'cleaner', 'polish', 'wax', 'oil', 'grease',
        'candle', 'candles', 'scent', 'freshener', 'diffuser',
        'towel', 'cloth', 'wipe', 'wipes', 'sponge', 'mop',
        'string', 'rope', 'wire', 'cable', 'chain', 'strap',
        'stone', 'sharpener', 'file', 'sandpaper', 'abrasive',
        'tray', 'mat', 'cover', 'sheet', 'film', 'foil',
        'lock', 'key', 'padlock', 'bolt', 'screw', 'nail', 'pin',
    ]
    
    found = []
    for kw in product_keywords:
        if kw in title_lower:
            found.append(kw)
    return found

def titles_share_product_type(sup_title, amz_title):
    """Check if both titles share product type keywords"""
    sup_types = set(extract_product_type(sup_title))
    amz_types = set(extract_product_type(amz_title))
    return len(sup_types & amz_types) > 0

def has_explicit_pack_mismatch(sup_title, amz_title):
    """Check for explicit pack count word mismatch"""
    if pd.isna(sup_title) or pd.isna(amz_title):
        return False, None
    
    sup_lower = str(sup_title).lower()
    amz_lower = str(amz_title).lower()
    
    # Extract explicit pack counts
    pack_pattern = r'(?:pack\s*of\s*|set\s*of\s*|\b)(\d+)\s*(?:pack|pk|pcs|pieces?|bags?|rolls?|containers?|x\b)'
    
    sup_packs = re.findall(pack_pattern, sup_lower)
    amz_packs = re.findall(pack_pattern, amz_lower)
    
    if sup_packs and amz_packs:
        sup_max = max(int(p) for p in sup_packs)
        amz_max = max(int(p) for p in amz_packs)
        if sup_max != amz_max:
            return True, f"Supplier {sup_max}pcs vs Amazon {amz_max}pcs"
    
    # Check for single vs multipack keywords
    single_words = ['single', 'each', 'sold individually', '1 x', 'x 1']
    multi_words = ['pack of', 'set of', 'multipack', 'multi-pack', 'bundle']
    
    sup_is_single = any(w in sup_lower for w in single_words)
    amz_is_multi = any(w in amz_lower for w in multi_words)
    
    if sup_is_single and amz_is_multi:
        return True, "Supplier single vs Amazon multipack"
    
    return False, None

def is_dimension_pattern(title):
    """Check if title contains dimension patterns (not pack counts)"""
    if pd.isna(title):
        return False
    title_lower = str(title).lower()
    
    dim_patterns = [
        r'\d+\s*x\s*\d+\s*(x\s*\d+\s*)?(cm|mm|inch|in|m|ft|"|\')',
        r'\d+x\d+mm',
        r'\d+x\d+cm',
        r'\d+\s*cm\s*x\s*\d+',
        r'\d+\s*mm\s*x\s*\d+',
    ]
    
    for pat in dim_patterns:
        if re.search(pat, title_lower):
            return True
    return False

def get_key_evidence(row):
    """Generate key match evidence for a row"""
    evidence = []
    
    if row['is_exact_ean_strict']:
        evidence.append("Exact EAN match")
    
    sup_title = str(row['SupplierTitle']).upper() if not pd.isna(row['SupplierTitle']) else ''
    amz_title = str(row['AmazonTitle']).upper() if not pd.isna(row['AmazonTitle']) else ''
    
    # Find shared brand
    for brand in KNOWN_BRANDS:
        if brand.upper() in sup_title and brand.upper() in amz_title:
            evidence.append(f"Brand: {brand}")
            break
    
    # Find shared product type
    sup_types = set(extract_product_type(row['SupplierTitle']))
    amz_types = set(extract_product_type(row['AmazonTitle']))
    shared_types = sup_types & amz_types
    if shared_types:
        evidence.append(f"Product: {list(shared_types)[0]}")
    
    # Title similarity
    if row['title_match'] >= 0.7:
        evidence.append(f"Title match: {row['title_match']:.0%}")
    
    if not evidence:
        evidence.append("Weak evidence")
    
    return "; ".join(evidence)

def categorize_row(row):
    """
    Apply v4.0 categorization logic:
    1. Exact EAN → VERIFIED (unless explicit pack mismatch or negative profit)
    2. Brand + Product match with positive profit → HIGHLY LIKELY
    3. Plausible match needing 1-2 confirmations → NEEDS VERIFICATION
    4. Confirmed match but unprofitable → FILTERED OUT
    """
    
    # Check for exact EAN match
    if row['is_exact_ean_strict']:
        # Check for explicit pack mismatch
        has_mismatch, mismatch_reason = has_explicit_pack_mismatch(
            row['SupplierTitle'], row['AmazonTitle']
        )
        
        if row['Adjusted_Profit'] <= 0:
            return 'VERIFIED_FILTERED', f"Negative adjusted profit: £{row['Adjusted_Profit']:.2f}"
        elif has_mismatch and row['Adjusted_Profit'] <= 0:
            return 'VERIFIED_FILTERED', f"{mismatch_reason}; negative profit"
        else:
            # VERIFIED - even with dimension patterns, EAN is definitive
            return 'VERIFIED', '-'
    
    # Non-EAN matches: Check for HIGHLY LIKELY criteria
    brand_match = titles_share_brand(row['SupplierTitle'], row['AmazonTitle'])
    product_match = titles_share_product_type(row['SupplierTitle'], row['AmazonTitle'])
    profit_positive = row['Adjusted_Profit'] > 0
    
    if brand_match and product_match and profit_positive:
        return 'HIGHLY_LIKELY', '-'
    
    # Check for HIGHLY_LIKELY filtered (brand+product but unprofitable)
    if brand_match and product_match and not profit_positive:
        return 'HIGHLY_LIKELY_FILTERED', f"Negative adjusted profit: £{row['Adjusted_Profit']:.2f}"
    
    # Check for NEEDS VERIFICATION criteria
    # - Plausible match but missing 1-2 confirmable details
    # - Must have positive profit
    if profit_positive:
        # Strong title match but no brand confirmation
        if row['title_match'] >= 0.5 and not brand_match:
            return 'NEEDS_VERIFICATION', 'Confirm brand on packaging'
        
        # Brand in one title, product type matches
        sup_brand = extract_brand(row['SupplierTitle'])
        amz_brand = extract_brand(row['AmazonTitle'])
        if (sup_brand or amz_brand) and product_match:
            if sup_brand and not amz_brand:
                return 'NEEDS_VERIFICATION', f"Brand '{sup_brand}' not in Amazon title - verify"
            elif amz_brand and not sup_brand:
                return 'NEEDS_VERIFICATION', f"Brand '{amz_brand}' not in Supplier title - verify"
        
        # Moderate title match
        if row['title_match'] >= 0.4:
            return 'NEEDS_VERIFICATION', 'Moderate title match - verify product details'
    
    # Everything else is filtered out or not included
    if not profit_positive:
        return 'FILTERED_OUT', f"Negative adjusted profit: £{row['Adjusted_Profit']:.2f}"
    
    return 'NOT_INCLUDED', 'Weak evidence'

# ===== Apply categorization =====
print("Applying v4.0 categorization...")
df['category'], df['filter_reason'] = zip(*df.apply(categorize_row, axis=1))
df['key_evidence'] = df.apply(get_key_evidence, axis=1)

# ===== Generate category counts =====
cat_counts = df['category'].value_counts()
print("\n===== CATEGORY COUNTS =====")
for cat, count in cat_counts.items():
    print(f"  {cat}: {count}")

# ===== Prepare output dataframes =====
# VERIFIED - RECOMMENDED
verified_rec = df[df['category'] == 'VERIFIED'].copy()
verified_rec = verified_rec.sort_values('sales', ascending=False)
print(f"\nVERIFIED RECOMMENDED: {len(verified_rec)}")

# VERIFIED - FILTERED OUT
verified_filt = df[df['category'] == 'VERIFIED_FILTERED'].copy()
print(f"VERIFIED FILTERED OUT: {len(verified_filt)}")

# HIGHLY LIKELY - RECOMMENDED
highly_likely_rec = df[df['category'] == 'HIGHLY_LIKELY'].copy()
highly_likely_rec = highly_likely_rec.sort_values(['title_match', 'sales'], ascending=[False, False])
print(f"HIGHLY LIKELY RECOMMENDED: {len(highly_likely_rec)}")

# HIGHLY LIKELY - FILTERED OUT
highly_likely_filt = df[df['category'] == 'HIGHLY_LIKELY_FILTERED'].copy()
print(f"HIGHLY LIKELY FILTERED OUT: {len(highly_likely_filt)}")

# NEEDS VERIFICATION
needs_verification = df[df['category'] == 'NEEDS_VERIFICATION'].copy()
needs_verification = needs_verification.sort_values(['title_match', 'sales'], ascending=[False, False])
print(f"NEEDS VERIFICATION: {len(needs_verification)}")

# FILTERED OUT (other)
filtered_out = df[df['category'] == 'FILTERED_OUT'].copy()
print(f"FILTERED OUT (other): {len(filtered_out)}")

# ===== Helper function for table formatting =====
def format_table_row(row, verdict):
    """Format a row for markdown table"""
    # Handle EAN display
    sup_ean = row['EAN_digits_normalized'] if row['EAN_strict_valid'] else '-'
    amz_ean = row['EAN_OnPage_digits_normalized'] if row['EAN_OnPage_strict_valid'] else '-'
    
    # Truncate titles for display
    sup_title = str(row['SupplierTitle'])[:50] + '...' if len(str(row['SupplierTitle'])) > 50 else str(row['SupplierTitle'])
    amz_title = str(row['AmazonTitle'])[:60] + '...' if len(str(row['AmazonTitle'])) > 60 else str(row['AmazonTitle'])
    
    # Get confidence
    if verdict == 'VERIFIED':
        confidence = 95
    elif verdict == 'HIGHLY LIKELY':
        confidence = 85
    else:
        confidence = int(row['title_match'] * 100) if row['title_match'] > 0 else 50
    
    return {
        'RowID': int(row['RowID']),
        'Verdict': verdict,
        'Confidence': confidence,
        'SupplierTitle': sup_title,
        'AmazonTitle': amz_title,
        'Supplier EAN': sup_ean,
        'Amazon EAN': amz_ean,
        'ASIN': row['ASIN'],
        'SupplierPrice': f"£{float(row['SupplierPrice_incVAT']):.2f}" if not pd.isna(row['SupplierPrice_incVAT']) else '-',
        'SellingPrice': f"£{float(row['SellingPrice_incVAT']):.2f}" if not pd.isna(row['SellingPrice_incVAT']) else '-',
        'NetProfit': f"£{float(row['NetProfit']):.2f}" if not pd.isna(row['NetProfit']) else '-',
        'ROI': f"{float(row['ROI']):.1f}%" if not pd.isna(row['ROI']) else '-',
        'Sales': int(row['sales']),
        'Pack Verdict': row['Pack_Verdict'],
        'Adjusted Profit': f"£{float(row['Adjusted_Profit']):.2f}",
        'Key Match Evidence': row['key_evidence'],
        'Filter Reason': row['filter_reason'],
    }

# ===== Generate Markdown Report =====
report_date = datetime.now().strftime('%Y%m%d')
report_path = OUTPUT_DIR / f'PHASEA_MANUAL_REPORT_{report_date}.md'

print(f"\nGenerating report: {report_path}")

# Collect all data for the report
verified_rec_rows = [format_table_row(row, 'VERIFIED') for _, row in verified_rec.iterrows()]
verified_filt_rows = [format_table_row(row, 'VERIFIED') for _, row in verified_filt.iterrows()]
highly_likely_rec_rows = [format_table_row(row, 'HIGHLY LIKELY') for _, row in highly_likely_rec.iterrows()]
highly_likely_filt_rows = [format_table_row(row, 'HIGHLY LIKELY') for _, row in highly_likely_filt.iterrows()]
needs_ver_rows = [format_table_row(row, 'NEEDS VERIFICATION') for _, row in needs_verification.iterrows()]

# Save row data as JSON for report generation
import json
report_data = {
    'date': report_date,
    'input_file': str(INPUT_PATH.parent.parent / 'part_30_dec.xlsx'),
    'total_rows': len(df),
    'verified_recommended': verified_rec_rows,
    'verified_filtered': verified_filt_rows,
    'highly_likely_recommended': highly_likely_rec_rows,
    'highly_likely_filtered': highly_likely_filt_rows,
    'needs_verification': needs_ver_rows,
    'counts': {
        'verified_rec': len(verified_rec_rows),
        'verified_filt': len(verified_filt_rows),
        'highly_likely_rec': len(highly_likely_rec_rows),
        'highly_likely_filt': len(highly_likely_filt_rows),
        'needs_verification': len(needs_ver_rows),
    }
}

with open(OUTPUT_DIR / 'report_data.json', 'w', encoding='utf-8') as f:
    json.dump(report_data, f, indent=2, ensure_ascii=False)

print(f"Report data saved to: {OUTPUT_DIR / 'report_data.json'}")
print("\n===== FINAL COUNTS =====")
print(f"VERIFIED — RECOMMENDED: {report_data['counts']['verified_rec']}")
print(f"VERIFIED — FILTERED OUT: {report_data['counts']['verified_filt']}")
print(f"HIGHLY LIKELY — RECOMMENDED: {report_data['counts']['highly_likely_rec']}")
print(f"HIGHLY LIKELY — FILTERED OUT: {report_data['counts']['highly_likely_filt']}")
print(f"NEEDS VERIFICATION: {report_data['counts']['needs_verification']}")
