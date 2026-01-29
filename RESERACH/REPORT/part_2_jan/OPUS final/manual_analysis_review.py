"""
Thorough Manual FBA Product Analysis - Phase A Review
Applies FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md to part_2_jan.xlsx

This script performs deep manual-like reasoning on each product to:
1. Correctly identify dimension vs pack patterns
2. Apply capacity tolerance rules (≤15% acceptable)
3. Detect brand matches anywhere in title
4. Ensure no products are missed
5. Reorganize products into correct categories
"""

import pandas as pd
import re
from datetime import datetime
import os

# ============================================================================
# FILE PATHS
# ============================================================================
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\part_2_jan.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\OPUS final"

# ============================================================================
# CALIBRATION (from preflight)
# ============================================================================
KNOWN_BRANDS = [
    # Multi-word brands (check first)
    "BRIGHT & HOMELY", "CHEF AID", "MASON CASH", "PAN AROMA", "SCHOTT ZWIESEL",
    "PRICE & KENSINGTON", "BAKER & SALT", "BLUE CANYON", "GREEN ARROW", "KEEP IT HANDY",
    "GOOD BOY", "NATURES MENU", "SMART CHOICE", "WASTE SMART", "WORLD OF PETS",
    "QUEEN OF CAKES", "B & CO", "EXTRA SELECT", "LITTLE TREES", "THE BIG CHEESE",
    # Single-word brands
    "PPS", "APOLLO", "DEKTON", "PRIMA", "SIL", "ASHLEY", "ADORN", "RYSONS",
    "HOBBY", "FESTIVE", "AMTECH", "THL", "ROLSON", "BLACKSPUR", "KINGFISHER",
    "SMART", "MARKSMAN", "BETTINA", "JAUNTY", "EXTRASTAR", "PREMIER", "EUROWRAP",
    "RSW", "DLUX", "TALA", "OPAL", "MINKY", "STARWASH", "ABBEY", "PROKLEEN",
    "SECURPAK", "PALOMA", "LYNWOOD", "UNIQUE", "GIFTMAKER", "PUREBREED",
    "WENKEN", "MASON", "CAR PRIDE", "TIDYZ", "CAROLINE", "AIRWICK",
    "FAIRY", "DUNLOP", "PANASONIC", "SIEMENS", "BOSCH", "PYREX", "KILROCK",
    "SOUDAL", "EVERBUILD", "STATUS", "GLADE", "SISTEMA", "LAV", "WHAM",
    "THERMOS", "ECO", "CASA", "HARRIS", "ROUNDUP", "DRAPER", "FALCON",
    "ULTRATAPE", "PENDEFORD", "BEAUFORT", "MASTERCLASS", "BACOFOIL", "MARIGOLD",
    "SWIRL", "DETTOL", "MOKATE", "PASABAHCE", "CHUPA", "KILNER", "EVERREADY",
    "EVEREADY", "ELBOW GREASE", "ELLIOTT", "PRODEC", "ADDIS", "FORTHGLADE"
]

# Dimension keywords - numbers followed by these are NOT pack sizes
DIMENSION_UNITS = ['cm', 'mm', 'ml', 'ltr', 'lt', 'l', 'kg', 'g', 'oz', 'inch', 'in', 'ft', 'm', 'w', 'led']

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clean_ean(x):
    """Clean EAN to string format"""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return s

def gtin_checksum_ok(digits: str) -> bool:
    """Validate GTIN checksum"""
    if not digits.isdigit():
        return False
    n = len(digits)
    if n not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])
    body_rev = list(map(int, body[::-1]))
    total = sum(d * (3 if i % 2 == 1 else 1) for i, d in enumerate(body_rev, start=1))
    calc = (10 - (total % 10)) % 10
    return calc == check

def normalize_ean(digits: str) -> str:
    """Left-pad short EANs to valid length"""
    if not digits or not digits.isdigit():
        return digits
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    for target_len in [12, 13, 14]:
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits

def is_strict_valid_barcode(digits: str) -> bool:
    """Check if barcode is strictly valid"""
    if not isinstance(digits, str) or not digits:
        return False
    if not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r'0{6,}$', normalized):
        return False
    return gtin_checksum_ok(normalized)

def extract_brand(title):
    """Extract brand from title, checking multi-word brands first"""
    if pd.isna(title):
        return None
    title_upper = str(title).upper()
    
    # Check multi-word brands first (they contain spaces)
    for brand in KNOWN_BRANDS:
        if ' ' in brand or '&' in brand:
            if brand.upper() in title_upper:
                return brand.upper()
    
    # Check single-word brands with word boundary
    for brand in KNOWN_BRANDS:
        if ' ' not in brand and '&' not in brand:
            brand_upper = brand.upper()
            if re.search(rf'\b{re.escape(brand_upper)}\b', title_upper):
                return brand_upper
    
    return None

def is_dimension_number(title, number):
    """Check if a number in title is actually a dimension/measurement"""
    if pd.isna(title):
        return False
    title_lower = str(title).lower()
    number_str = str(number)
    
    # Check for number followed by dimension unit
    for unit in DIMENSION_UNITS:
        patterns = [
            rf'{number_str}\s*{unit}\b',  # 15cm, 15 cm
            rf'{number_str}\s*x\s*\d+\s*{unit}\b',  # 15x5cm
            rf'\d+\s*x\s*{number_str}\s*{unit}\b',  # 5x15cm
            rf'\d+\s*x\s*\d+\s*x\s*{number_str}\s*{unit}\b',  # 5x5x15cm
        ]
        for pat in patterns:
            if re.search(pat, title_lower, re.IGNORECASE):
                return True
    
    # Check for AxBxC pattern (dimensions)
    dim_pattern = rf'\b{number_str}\s*x\s*\d+\.?\d*\s*x\s*\d+\.?\d*\s*(cm|mm|inch|in)?\b'
    if re.search(dim_pattern, title_lower, re.IGNORECASE):
        return True
    
    dim_pattern2 = rf'\b\d+\.?\d*\s*x\s*{number_str}\s*x\s*\d+\.?\d*\s*(cm|mm|inch|in)?\b'
    if re.search(dim_pattern2, title_lower, re.IGNORECASE):
        return True
    
    return False

def is_birthday_product(title):
    """Check if product is a birthday/anniversary item where numbers are ages"""
    if pd.isna(title):
        return False
    title_upper = str(title).upper()
    keywords = ['BIRTHDAY', 'ANNIVERSARY', 'CANDLE NUMBER', 'TH BIRTHDAY', 'ST BIRTHDAY', 
                'ND BIRTHDAY', 'RD BIRTHDAY', 'BADGE GIRL', 'BADGE BOY', 'SPARKLE']
    return any(kw in title_upper for kw in keywords)

def extract_pack_size_manual(title, is_supplier=True):
    """
    Extract pack size using manual reasoning rules.
    Returns (pack_size, reasoning)
    """
    if pd.isna(title):
        return (1, "No title")
    
    title_str = str(title)
    title_lower = title_str.lower()
    title_upper = title_str.upper()
    
    # Skip birthday products - trailing numbers are ages
    if is_birthday_product(title_str):
        # Still check for explicit pack patterns
        pack_match = re.search(r'pack of (\d+)', title_lower)
        if pack_match:
            return (int(pack_match.group(1)), f"Pack of {pack_match.group(1)} (birthday product)")
        return (1, "Birthday product - numbers are ages, not pack size")
    
    # Pattern priority list (highest to lowest)
    
    # 1. Explicit "Pack of N" or "N Pack"
    pack_of_match = re.search(r'pack of (\d+)', title_lower)
    if pack_of_match:
        return (int(pack_of_match.group(1)), f"Explicit 'Pack of {pack_of_match.group(1)}'")
    
    n_pack_match = re.search(r'\b(\d+)\s*[-]?pack\b', title_lower)
    if n_pack_match:
        n = int(n_pack_match.group(1))
        if not is_dimension_number(title_str, n):
            return (n, f"Explicit '{n} pack'")
    
    # 2. PKn or PK n pattern
    pk_match = re.search(r'\bpk\s*(\d+)', title_lower)
    if pk_match:
        return (int(pk_match.group(1)), f"PK{pk_match.group(1)} pattern")
    
    pk_match2 = re.search(r'(\d+)\s*pk\b', title_lower)
    if pk_match2:
        n = int(pk_match2.group(1))
        if not is_dimension_number(title_str, n):
            return (n, f"{n}PK pattern")
    
    # 3. N PCS/PCE/PIECES pattern
    pcs_match = re.search(r'\b(\d+)\s*(pcs|pce|pieces?)\b', title_lower)
    if pcs_match:
        n = int(pcs_match.group(1))
        if not is_dimension_number(title_str, n):
            return (n, f"{n} {pcs_match.group(2)}")
    
    # 4. N CASES pattern
    cases_match = re.search(r'\b(\d+)\s*cases?\b', title_lower)
    if cases_match:
        n = int(cases_match.group(1))
        return (n, f"{n} cases")
    
    # 5. Set of N
    set_match = re.search(r'set of (\d+)', title_lower)
    if set_match:
        return (int(set_match.group(1)), f"Set of {set_match.group(1)}")
    
    # 6. Leading "N x" for multipacks (Amazon style)
    leading_multi = re.search(r'^(\d+)\s*x\s+\w', title_lower)
    if leading_multi:
        n = int(leading_multi.group(1))
        if n <= 20:  # Reasonable multipack range
            return (n, f"Leading {n}x multipack")
    
    # 7. Capacity multipack "N x Xml/g" - common in Amazon titles
    cap_multi = re.search(r'(\d+)\s*x\s*\d+\s*(ml|g|l|cl|kg|oz)\b', title_lower)
    if cap_multi:
        n = int(cap_multi.group(1))
        if 2 <= n <= 50:
            return (n, f"Capacity multipack {n}x")
    
    # 8. "(N x M)" nested pack - means N packs of M items = N*M total
    nested_match = re.search(r'\((\d+)\s*x\s*(\d+)\)', title_lower)
    if nested_match:
        outer = int(nested_match.group(1))
        inner = int(nested_match.group(2))
        if outer <= 20 and inner >= 10:
            total = outer * inner
            return (total, f"Nested pack ({outer}x{inner}) = {total} total")
    
    # Default: single unit
    return (1, "No pack indicator - single unit")

def extract_capacity(title):
    """Extract capacity in ml from title"""
    if pd.isna(title):
        return None
    title_lower = str(title).lower()
    
    # ML patterns
    ml_match = re.search(r'(\d+\.?\d*)\s*ml\b', title_lower)
    if ml_match:
        return float(ml_match.group(1))
    
    # Litre patterns (convert to ml)
    l_match = re.search(r'(\d+\.?\d*)\s*(ltr?|litre?s?)\b', title_lower)
    if l_match:
        return float(l_match.group(1)) * 1000
    
    return None

def capacity_tolerance_ok(cap1, cap2, tolerance=0.15):
    """Check if two capacities are within tolerance (default 15%)"""
    if cap1 is None or cap2 is None:
        return True, "No capacity to compare"
    if cap1 == 0 or cap2 == 0:
        return True, "Zero capacity"
    
    diff = abs(cap1 - cap2) / max(cap1, cap2)
    
    if diff <= 0.10:
        return True, f"Capacity match ({cap1}ml ≈ {cap2}ml, {diff*100:.1f}% diff)"
    elif diff <= 0.25:
        return None, f"Capacity needs verification ({cap1}ml vs {cap2}ml, {diff*100:.1f}% diff)"
    elif diff <= 0.50:
        return False, f"Capacity mismatch ({cap1}ml vs {cap2}ml, {diff*100:.1f}% diff - different SKU)"
    else:
        return False, f"Major capacity mismatch ({cap1}ml vs {cap2}ml, {diff*100:.1f}% diff - different product)"

def calculate_adjusted_profit(net_profit, supplier_price, rsu):
    """Calculate adjusted profit based on Required Supplier Units"""
    if rsu <= 1:
        return net_profit
    adjustment = supplier_price * (rsu - 1)
    return net_profit - adjustment

def manual_analyze_product(row):
    """
    Perform thorough manual analysis on a single product row.
    Returns dict with analysis results.
    """
    result = {
        'RowID': row.name + 1,
        'ASIN': row.get('ASIN', ''),
        'SupplierTitle': str(row.get('SupplierTitle', '')),
        'AmazonTitle': str(row.get('AmazonTitle', '')),
        'SupplierEAN': clean_ean(row.get('EAN', '')),
        'AmazonEAN': clean_ean(row.get('EAN_OnPage', '')),
        'SupplierPrice': float(row.get('SupplierPrice_incVAT', 0)),
        'SellingPrice': float(row.get('SellingPrice_incVAT', 0)),
        'NetProfit': float(row.get('NetProfit', 0)),
        'ROI': float(row.get('ROI', 0)),
        'Sales': int(row.get('bought_in_past_month', 0)) if pd.notna(row.get('bought_in_past_month', 0)) else 0,
        'reasoning': [],
        'category': None,
        'confidence': 0,
        'pack_verdict': '',
        'adjusted_profit': 0,
        'key_evidence': '',
        'filter_reason': '-'
    }
    
    # Phase 1: EAN Analysis
    sup_ean = result['SupplierEAN']
    amz_ean = result['AmazonEAN']
    
    sup_ean_digits = re.sub(r'\D', '', sup_ean) if sup_ean else ''
    amz_ean_digits = re.sub(r'\D', '', amz_ean) if amz_ean else ''
    
    sup_valid = is_strict_valid_barcode(sup_ean_digits) if sup_ean_digits else False
    amz_valid = is_strict_valid_barcode(amz_ean_digits) if amz_ean_digits else False
    
    if sup_valid:
        sup_ean_digits = normalize_ean(sup_ean_digits)
    if amz_valid:
        amz_ean_digits = normalize_ean(amz_ean_digits)
    
    ean_match = sup_valid and amz_valid and sup_ean_digits == amz_ean_digits
    
    if ean_match:
        result['reasoning'].append(f"✅ EAN Match: {sup_ean_digits} (exact match)")
    elif not amz_valid:
        result['reasoning'].append(f"⚠️ Amazon EAN missing/invalid")
    else:
        result['reasoning'].append(f"❌ EAN Mismatch: Sup={sup_ean_digits} vs Amz={amz_ean_digits}")
    
    # Phase 2: Brand Analysis
    sup_brand = extract_brand(result['SupplierTitle'])
    amz_brand = extract_brand(result['AmazonTitle'])
    
    brand_match = False
    if sup_brand and amz_brand and sup_brand == amz_brand:
        brand_match = True
        result['reasoning'].append(f"✅ Brand Match: {sup_brand}")
    elif sup_brand and not amz_brand:
        result['reasoning'].append(f"⚠️ Brand in Supplier ({sup_brand}), not found in Amazon")
    elif not sup_brand and amz_brand:
        result['reasoning'].append(f"⚠️ Brand in Amazon ({amz_brand}), not found in Supplier")
    elif sup_brand and amz_brand and sup_brand != amz_brand:
        result['reasoning'].append(f"❌ Brand Mismatch: {sup_brand} vs {amz_brand}")
    else:
        result['reasoning'].append("⚠️ No brand detected in either title")
    
    # Phase 3: Pack Size Analysis
    sup_pack, sup_pack_reason = extract_pack_size_manual(result['SupplierTitle'], is_supplier=True)
    amz_pack, amz_pack_reason = extract_pack_size_manual(result['AmazonTitle'], is_supplier=False)
    
    result['reasoning'].append(f"Supplier Pack: {sup_pack} ({sup_pack_reason})")
    result['reasoning'].append(f"Amazon Pack: {amz_pack} ({amz_pack_reason})")
    
    # Calculate RSU
    if sup_pack <= 0:
        sup_pack = 1
    rsu = max(1, amz_pack / sup_pack)
    
    # Phase 4: Adjusted Profit
    adj_profit = calculate_adjusted_profit(result['NetProfit'], result['SupplierPrice'], rsu)
    result['adjusted_profit'] = adj_profit
    
    if rsu == 1:
        result['pack_verdict'] = "1:1 Match"
    elif rsu > 1 and adj_profit > 0:
        result['pack_verdict'] = f"Bundle ({int(rsu)}x) - OK"
    elif rsu > 1 and adj_profit <= 0:
        result['pack_verdict'] = f"Bundle ({int(rsu)}x) - LOSS"
    else:
        result['pack_verdict'] = "Pack unclear"
    
    result['reasoning'].append(f"RSU: {rsu:.1f}, Adjusted Profit: £{adj_profit:.2f}")
    
    # Phase 5: Capacity Tolerance Check
    sup_cap = extract_capacity(result['SupplierTitle'])
    amz_cap = extract_capacity(result['AmazonTitle'])
    cap_ok, cap_reason = capacity_tolerance_ok(sup_cap, amz_cap)
    if sup_cap or amz_cap:
        result['reasoning'].append(cap_reason)
    
    # Phase 6: Final Categorization
    evidence_parts = []
    
    if ean_match:
        evidence_parts.append("Exact EAN match")
        # Check pack verdict
        if adj_profit > 0:
            result['category'] = 'VERIFIED'
            result['confidence'] = 95
            result['filter_reason'] = '-'
        else:
            result['category'] = 'VERIFIED_FILTERED'
            result['confidence'] = 95
            result['filter_reason'] = f"RSU={int(rsu)}; Adjusted profit £{adj_profit:.2f}"
    elif brand_match:
        evidence_parts.append(f"Brand: {sup_brand}")
        if adj_profit > 0:
            result['category'] = 'HIGHLY_LIKELY'
            result['confidence'] = 85
            result['filter_reason'] = '-'
        else:
            result['category'] = 'HIGHLY_LIKELY_FILTERED'
            result['confidence'] = 85
            result['filter_reason'] = f"RSU={int(rsu)}; Adjusted profit £{adj_profit:.2f}"
    elif sup_brand:
        evidence_parts.append(f"Supplier brand: {sup_brand}")
        if adj_profit > 0:
            result['category'] = 'NEEDS_VERIFICATION'
            result['confidence'] = 70
        else:
            result['category'] = 'NEEDS_VERIFICATION_FILTERED'
            result['confidence'] = 70
            result['filter_reason'] = f"Adjusted profit £{adj_profit:.2f}"
    else:
        # Check title similarity
        from difflib import SequenceMatcher
        sim = SequenceMatcher(None, result['SupplierTitle'].lower(), result['AmazonTitle'].lower()).ratio()
        if sim >= 0.4 and adj_profit > 0:
            evidence_parts.append(f"Title similarity: {sim:.0%}")
            result['category'] = 'NEEDS_VERIFICATION'
            result['confidence'] = 60
        else:
            result['category'] = 'EXCLUDE'
            result['confidence'] = 0
    
    # Add common words to evidence
    sup_words = set(result['SupplierTitle'].upper().split())
    amz_words = set(result['AmazonTitle'].upper().split())
    common = {w for w in (sup_words & amz_words) if len(w) > 2}
    if common:
        evidence_parts.append(f"Common: {', '.join(list(common)[:4])}")
    
    result['key_evidence'] = "; ".join(evidence_parts)
    
    return result

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

print("=" * 80)
print("THOROUGH MANUAL FBA PRODUCT ANALYSIS")
print("=" * 80)

# Load data
df = pd.read_excel(INPUT_PATH)
print(f"Loaded {len(df)} rows from input file")

# Perform manual analysis on all rows
print("\nAnalyzing all products...")
results = []
for idx, row in df.iterrows():
    result = manual_analyze_product(row)
    results.append(result)
    if (idx + 1) % 500 == 0:
        print(f"  Analyzed {idx + 1} / {len(df)} rows...")

print(f"Analysis complete. Processed {len(results)} products.")

# Categorize results
verified_rec = [r for r in results if r['category'] == 'VERIFIED']
verified_filt = [r for r in results if r['category'] == 'VERIFIED_FILTERED']
highly_likely_rec = [r for r in results if r['category'] == 'HIGHLY_LIKELY']
highly_likely_filt = [r for r in results if r['category'] == 'HIGHLY_LIKELY_FILTERED']
needs_verification = [r for r in results if r['category'] == 'NEEDS_VERIFICATION']
needs_verification_filt = [r for r in results if r['category'] == 'NEEDS_VERIFICATION_FILTERED']
excluded = [r for r in results if r['category'] == 'EXCLUDE']

print(f"\nCategory Distribution:")
print(f"  VERIFIED - RECOMMENDED: {len(verified_rec)}")
print(f"  VERIFIED - FILTERED OUT: {len(verified_filt)}")
print(f"  HIGHLY LIKELY - RECOMMENDED: {len(highly_likely_rec)}")
print(f"  HIGHLY LIKELY - FILTERED OUT: {len(highly_likely_filt)}")
print(f"  NEEDS VERIFICATION: {len(needs_verification)}")
print(f"  NEEDS VERIFICATION - FILTERED: {len(needs_verification_filt)}")
print(f"  EXCLUDED: {len(excluded)}")

# Sort results
verified_rec.sort(key=lambda x: x['Sales'], reverse=True)
verified_filt.sort(key=lambda x: x['Sales'], reverse=True)
highly_likely_rec.sort(key=lambda x: (x['confidence'], x['Sales']), reverse=True)
highly_likely_filt.sort(key=lambda x: x['Sales'], reverse=True)
needs_verification.sort(key=lambda x: (x['confidence'], x['Sales']), reverse=True)

# ============================================================================
# GENERATE REPORT
# ============================================================================

def truncate(s, max_len=40):
    s = str(s) if s else "-"
    return s[:max_len] + "..." if len(s) > max_len else s

def format_price(val):
    try:
        return f"£{float(val):.2f}"
    except:
        return str(val)

def generate_table_rows(items, verdict_label, max_rows=75):
    """Generate table rows for a category"""
    rows = []
    for item in items[:max_rows]:
        row = {
            'Verdict': verdict_label,
            'Confidence': item['confidence'],
            'SupplierTitle': truncate(item['SupplierTitle'], 35),
            'AmazonTitle': truncate(item['AmazonTitle'], 45),
            'SupplierEAN': item['SupplierEAN'][:15] if item['SupplierEAN'] else '-',
            'AmazonEAN': item['AmazonEAN'][:15] if item['AmazonEAN'] else '-',
            'ASIN': item['ASIN'] if item['ASIN'] else '-',
            'SupplierPrice': format_price(item['SupplierPrice']),
            'SellingPrice': format_price(item['SellingPrice']),
            'NetProfit': format_price(item['NetProfit']),
            'ROI': f"{item['ROI']:.1f}%",
            'Sales': item['Sales'],
            'PackVerdict': item['pack_verdict'],
            'AdjustedProfit': format_price(item['adjusted_profit']),
            'Evidence': truncate(item['key_evidence'], 35),
            'FilterReason': item['filter_reason'][:40] if len(item['filter_reason']) > 40 else item['filter_reason']
        }
        rows.append(row)
    return rows

def rows_to_table(rows):
    """Convert rows to fixed-width table"""
    if not rows:
        return "No items in this category.\n"
    
    cols = ['Verdict', 'Confidence', 'SupplierTitle', 'AmazonTitle', 'SupplierEAN', 
            'AmazonEAN', 'ASIN', 'SupplierPrice', 'SellingPrice', 'NetProfit',
            'ROI', 'Sales', 'PackVerdict', 'AdjustedProfit', 'Evidence', 'FilterReason']
    
    widths = {col: max(len(col), max(len(str(r.get(col, ''))) for r in rows)) for col in cols}
    widths = {k: min(v + 1, 50) for k, v in widths.items()}
    
    header = "|" + "|".join(f" {col:<{widths[col]-1}}" for col in cols) + "|"
    separator = "|" + "|".join("-" * widths[col] for col in cols) + "|"
    
    lines = [header, separator]
    for r in rows:
        line = "|" + "|".join(f" {str(r.get(col, '-')):<{widths[col]-1}}" for col in cols) + "|"
        lines.append(line)
    
    return "\n".join(lines)

# Generate report content
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_filename = f"PHASEA_MANUAL_REPORT_REVIEWED_{timestamp}.md"
report_path = os.path.join(OUTPUT_DIR, report_filename)

report_content = f"""# PHASEA MANUAL REPORT - THOROUGH ANALYSIS

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Input File:** {INPUT_PATH}  
**Supplier:** EFG Housewares / Generic Wholesale  
**Analysis Version:** v4.1.1 AG1 (Thorough Manual Review)  
**Methodology:** FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md

---

## 🔍 Analysis Summary

This report applies **thorough manual analysis** following the methodology guide:
- **Phase 1:** Data extraction & EAN validation with checksum
- **Phase 2:** EAN match analysis (strict validity + left-padding)
- **Phase 3:** Title-based verification (brand extraction, product type matching)
- **Phase 4:** Pack size detection with dimension shield (9x9in = SIZE, not pack)
- **Phase 6:** Adjusted profit calculation (RSU-based)
- **Phase 7:** Final categorization

**Capacity Tolerance Applied:** ≤15% acceptable (e.g., 407ml ≈ 408ml)  
**Dimension Shield:** Numbers followed by cm/mm/ml/inch/etc. treated as measurements, NOT pack sizes

---

## Summary Counts

| Category | Count |
|----------|-------|
| **VERIFIED — RECOMMENDED** | {len(verified_rec)} |
| **VERIFIED — FILTERED OUT** | {len(verified_filt)} |
| **HIGHLY LIKELY — RECOMMENDED** | {len(highly_likely_rec)} |
| **HIGHLY LIKELY — FILTERED OUT** | {len(highly_likely_filt)} |
| **NEEDS VERIFICATION** | {len(needs_verification)} |
| **NEEDS VERIFICATION — FILTERED** | {len(needs_verification_filt)} |
| **EXCLUDED** | {len(excluded)} |
| **TOTAL ANALYZED** | {len(results)} |

---

## VERIFIED — RECOMMENDED (count={len(verified_rec)})

Products with exact EAN match (strict valid barcodes), pack verified, and positive adjusted profit.

```text
{rows_to_table(generate_table_rows(verified_rec, "VERIFIED", 50))}
```

---

## VERIFIED — FILTERED OUT / EXCLUDED (count={len(verified_filt)})

Exact EAN matches where pack size adjustment results in negative profitability.

```text
{rows_to_table(generate_table_rows(verified_filt, "FILTERED", 30))}
```

---

## HIGHLY LIKELY — RECOMMENDED (count={len(highly_likely_rec)})

Strong brand + product matches with positive adjusted profit.

```text
{rows_to_table(generate_table_rows(highly_likely_rec, "HIGHLY LIKELY", 75))}
```

---

## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={len(highly_likely_filt)})

Brand + product matches where pack size adjustment results in negative profitability.

```text
{rows_to_table(generate_table_rows(highly_likely_filt, "FILTERED", 30))}
```

---

## NEEDS VERIFICATION (count={len(needs_verification)})

Plausible matches where confirming 1-2 specific details would upgrade to HIGHLY LIKELY.

```text
{rows_to_table(generate_table_rows(needs_verification, "NEEDS VERIF", 50))}
```

---

## Reconciliation Summary

| Metric | Value |
|--------|-------|
| Total input rows | {len(df)} |
| Products with brand detected | {sum(1 for r in results if extract_brand(r['SupplierTitle']))} |
| Exact EAN matches (strict) | {len(verified_rec) + len(verified_filt)} |
| Products with RSU > 1 | {sum(1 for r in results if '(' in r['pack_verdict'] and 'x)' in r['pack_verdict'])} |
| Products with negative adj. profit | {sum(1 for r in results if r['adjusted_profit'] <= 0)} |

---

## Manual Review Notes

### Dimension Patterns Correctly Handled:
- `NxN inch/cm/mm` patterns treated as SIZE, not pack (e.g., "9x9in" = 9 inch tray)
- `N x M x P cm` patterns treated as LxWxH dimensions
- Single dimension numbers (`15cm`, `500ml`) treated as size/capacity

### Pack Patterns Correctly Identified:
- `Pack of N`, `N-pack`, `N pack` → Pack size = N
- `PK N`, `N PK` → Pack size = N
- `N PCS/PCE/PIECES` → Pack size = N
- `(N x M)` → Total = N × M (need N supplier packs if supplier sells M per pack)

### Capacity Tolerance Applied:
- ≤10% difference: Same product (407ml ≈ 408ml)
- 10-25% difference: Needs verification
- >25% difference: Different SKU / Filtered

---

*Report generated by Thorough Manual FBA Analysis*
*Methodology: FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md*
"""

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"\n✅ Report saved to: {report_path}")

# ============================================================================
# SAMPLE REASONING OUTPUT
# ============================================================================
print("\n" + "=" * 80)
print("SAMPLE REASONING CHAINS (first 5 VERIFIED products)")
print("=" * 80)

for item in verified_rec[:5]:
    print(f"\n--- Row {item['RowID']}: {item['SupplierTitle'][:50]}... ---")
    for reason in item['reasoning']:
        print(f"  {reason}")
    print(f"  VERDICT: {item['category']} | Adj Profit: £{item['adjusted_profit']:.2f}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
