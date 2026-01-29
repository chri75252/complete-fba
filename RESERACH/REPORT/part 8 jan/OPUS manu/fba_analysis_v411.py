"""
FBA Product Analysis Script v4.1.1 AG1
Implements the full analysis pipeline with:
- Strict EAN validation with checksum + left-padding
- Title similarity analysis
- Pack size extraction with dimension shielding
- Thorough manual categorization
"""

import pandas as pd
import re
from difflib import SequenceMatcher
from datetime import datetime

# ============== CALIBRATION CONFIG (from preflight) ==============
CALIBRATION = {
    "explicit_units": ['PIECES', 'PK', 'PCS', 'PC', 'PACK'],
    "allow_trailing_number_as_qty": False,  # Trailing numbers are often variant codes
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch", "m"],
    "brand_position": "start",
    "brand_in_supplier_usually_present": True,
    "brand_in_amazon_usually_present": False,
    "brand_sparse_supplier_mode": True,
    "strong_similarity_threshold": 0.20,
    "strong_shared_tokens_threshold": 2,
    "very_strong_similarity_threshold": 0.30,
    "very_strong_shared_tokens_threshold": 3,
    "gate_mode": "C_brand_sparse",
    "sales_column": "bought_in_past_month",
    "high_mismatch_rate": True,
    "mismatch_percentage": 78.0,
    "require_strict_ean_validation": True,
}

# Known brands list
KNOWN_BRANDS = [
    'MINKY', 'CHEF AID', 'TALA', 'PANASONIC', 'DUNLOP', 'AIRWICK', 'TONKITA', 
    'PROKLEEN', 'DEKTON', 'GRAFIX', 'EUROWRAP', 'STATUS', 'TOM SMITH', 'LYNWOOD',
    'PRIMA', 'SECURPAK', 'STARWASH', 'DLUX', 'RSW', 'AMTECH', 'ROLSON', 'DRAPER',
    'FAIRY', 'DETTOL', 'MARIGOLD', 'MASON CASH', 'PYREX', 'EVERBUILD', 'HARRIS',
    'EXTRASTAR', 'ROUNDUP', 'LITTLE TREES', 'TIDYZ', 'SOUDAL', 'KILROCK', 'CHEF',
    'WORLD OF PETS', 'PARTY CRAZY', 'UNIQUE', 'BRIGHT & HOMELY', 'TONTIKA',
    'SNOW WHITE', 'ADORN', 'FESTIVE MAGIC', 'EASY STORAGE', 'SPARKLE', 'PAPER',
    'POP', 'REVITALISE', 'RED CROWN', 'VERSACE', 'PETSAFE', 'LEGO', 'NESPRESSO'
]

# IP Risk brands (TRUE luxury/trademark)
IP_RISK_BRANDS = [
    'JO MALONE', 'CHANEL', 'DIOR', 'GUCCI', 'LOUIS VUITTON', 'PRADA', 'HERMES',
    'APPLE', 'SAMSUNG', 'SONY', 'MICROSOFT', 'NIKE', 'ADIDAS', 'VERSACE', 'NESPRESSO'
]

# ============== STAGE 1: Data Loading ==============
print("=" * 60)
print("FBA ANALYSIS v4.1.1 AG1 - THOROUGH MANUAL ANALYSIS")
print("=" * 60)

INPUT_PATH = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx'

df = pd.read_excel(INPUT_PATH)
print(f"\nLoaded {len(df)} rows from input file")
print(f"Columns: {df.columns.tolist()}")

# Add RowID for traceability
df['RowID'] = df.index + 1

# ============== STAGE 1B: EAN Normalization ==============
def clean_to_digits(x):
    """Normalize EANs safely"""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    
    # Reject scientific notation
    if re.search(r'[eE][+-]?\d+', s):
        return ''
    
    # Remove Excel float artifact
    if re.fullmatch(r'\d+\.(0+)', s):
        s = s.split('.', 1)[0]
    
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits) if 'EAN_OnPage' in df.columns else ''

# ============== STAGE 2: Title Similarity ==============
def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

def shared_tokens(title1, title2):
    """Count significant shared tokens between titles"""
    if pd.isna(title1) or pd.isna(title2):
        return 0
    words1 = set(re.findall(r'[A-Za-z]{4,}', str(title1).upper()))
    words2 = set(re.findall(r'[A-Za-z]{4,}', str(title2).upper()))
    return len(words1.intersection(words2))

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)
df['shared_tokens'] = df.apply(lambda x: shared_tokens(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# ============== STAGE 3: Strict EAN Validation ==============
def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit():
        return False
    n = len(digits)
    if n not in (8, 12, 13, 14):
        return False
    
    body = digits[:-1]
    check = int(digits[-1])
    
    body_rev = list(map(int, body[::-1]))
    total = 0
    for i, d in enumerate(body_rev, start=1):
        total += d * (3 if i % 2 == 1 else 1)
    calc = (10 - (total % 10)) % 10
    return calc == check

def normalize_ean(digits: str) -> str:
    """Attempt left-padding to valid GTIN length if checksum passes"""
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

df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean) if 'EAN_OnPage' in df.columns else ''

df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode) if 'EAN_OnPage' in df.columns else False

# Strict exact EAN match
df['is_exact_ean_strict'] = (
    df['EAN_strict_valid'] &
    df['EAN_OnPage_strict_valid'] &
    (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
)

print(f"\nStrict EAN valid (Supplier): {df['EAN_strict_valid'].sum()}/{len(df)}")
print(f"Strict EAN valid (Amazon): {df['EAN_OnPage_strict_valid'].sum()}/{len(df)}")
print(f"Strict Exact EAN matches: {df['is_exact_ean_strict'].sum()}/{len(df)}")

# ============== STAGE 4: Pack Size Extraction ==============
def is_dimension_pattern(text, number_str):
    """Check if a number is part of a dimension pattern"""
    if pd.isna(text):
        return False
    text = str(text).upper()
    
    # Patterns that indicate dimensions, not pack sizes
    dimension_patterns = [
        rf'{number_str}\s*(CM|MM|INCH|IN|M|")\b',  # 40CM, 10MM, 7 INCH
        rf'{number_str}\s*[xX×]\s*\d+\s*(CM|MM|INCH|IN|M|")',  # 9x9 inch, 30x20cm
        rf'\d+\s*[xX×]\s*{number_str}\s*(CM|MM|INCH|IN|M|")',  # 30x20cm
        rf'{number_str}\s*(ML|LTR|L|G|KG|OZ)\b',  # 500ML, 1.6L, 100G
    ]
    
    for pattern in dimension_patterns:
        if re.search(pattern, text):
            return True
    return False

def extract_pack_size(title):
    """Extract pack size with dimension shielding"""
    if pd.isna(title):
        return 1
    
    title_str = str(title).upper()
    
    # Explicit pack patterns (highest priority)
    pack_patterns = [
        (r'PACK\s*OF\s*(\d+)', 1),
        (r'SET\s*OF\s*(\d+)', 1),
        (r'\b(\d+)\s*PACK\b', 1),
        (r'\b(\d+)\s*PK\b', 1),
        (r'(\d+)\s*PCS\b', 1),
        (r'(\d+)\s*PCE\b', 1),
        (r'(\d+)\s*PIECES?\b', 1),
        (r'\((\d+)\s*PACK\)', 1),
        (r'\(PACK\s*OF\s*(\d+)\)', 1),
    ]
    
    for pattern, group in pack_patterns:
        match = re.search(pattern, title_str)
        if match:
            qty = int(match.group(group))
            if 1 < qty < 500:
                # Check it's not a dimension
                if not is_dimension_pattern(title_str, str(qty)):
                    return qty
    
    return 1

def extract_multipack_total(title):
    """Extract total from multipack patterns like '(4 x 50)'"""
    if pd.isna(title):
        return (1, 1, 1)
    
    title_str = str(title).upper()
    
    # Pattern: N x M (e.g., "4 x 50", "3 x 500ml")
    multipack_match = re.search(r'\(?\s*(\d+)\s*[xX×]\s*(\d+)\s*(ML|G|L|KG|OZ|PCS|PCE|PIECES?)?\s*\)?', title_str)
    if multipack_match:
        outer = int(multipack_match.group(1))
        inner = int(multipack_match.group(2))
        unit = multipack_match.group(3) if multipack_match.group(3) else ''
        
        # Check if this is dimensions (small numbers with dimension units nearby)
        full_match = multipack_match.group(0)
        if re.search(r'(CM|MM|INCH|IN|")\s*$', full_match) or re.search(rf'{outer}\s*[xX×]\s*{inner}\s*(CM|MM|INCH|IN)', title_str):
            return (1, 1, 1)  # Dimensions, not pack
        
        # Check if it's capacity multipack (e.g., 3 x 400ml means 3 units)
        if unit in ['ML', 'G', 'L', 'KG', 'OZ']:
            return (outer, 1, outer)  # RSU = outer (the first number)
        
        # Otherwise it's a true multipack (4 x 50 = 200 total)
        if outer <= 20 and inner > 1:
            return (outer, inner, outer * inner)
    
    # Fallback to simple pack extraction
    pack = extract_pack_size(title_str)
    return (1, pack, pack)

df['Sup_Pack'] = df['SupplierTitle'].apply(extract_pack_size)
df['Amz_Multipack'] = df['AmazonTitle'].apply(extract_multipack_total)
df['Amz_Total'] = df['Amz_Multipack'].apply(lambda x: x[2])

# Calculate RSU (Required Supplier Units)
def calculate_rsu(row):
    sup_qty = row['Sup_Pack'] if row['Sup_Pack'] > 0 else 1
    amz_total = row['Amz_Total'] if row['Amz_Total'] > 0 else 1
    return max(1, amz_total / sup_qty)

df['RSU'] = df.apply(calculate_rsu, axis=1)

# Adjusted Profit
def recalculate_profit(row):
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT']) if 'SupplierPrice_incVAT' in row else float(row.get('SupplierPrice_exVAT', 0))
        rsu = row['RSU']
        adjustment = supplier_cost * (rsu - 1)
        return round(original_profit - adjustment, 2)
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# Pack Verdict
def get_pack_verdict(row):
    rsu = row['RSU']
    if rsu == 1.0:
        return "1:1 Match"
    elif rsu > 1.0:
        if row['Adjusted_Profit'] > 0:
            return f"BUNDLE ({int(rsu)}x) - OK"
        else:
            return f"BUNDLE ({int(rsu)}x) - LOSS"
    else:
        return "1:1 Match"

df['Pack_Verdict'] = df.apply(get_pack_verdict, axis=1)

# ============== STAGE 5: Brand Detection ==============
def extract_brand(title):
    """Extract brand from title"""
    if pd.isna(title):
        return None
    title_upper = str(title).upper()
    
    for brand in KNOWN_BRANDS:
        if brand in title_upper:
            return brand
    return None

def check_ip_risk(title):
    """Check if product has IP risk"""
    if pd.isna(title):
        return False
    title_upper = str(title).upper()
    
    for brand in IP_RISK_BRANDS:
        if brand in title_upper:
            return True
    return False

df['Supplier_Brand'] = df['SupplierTitle'].apply(extract_brand)
df['Amazon_Brand'] = df['AmazonTitle'].apply(extract_brand)
df['IP_Risk'] = df['AmazonTitle'].apply(check_ip_risk)

# ============== STAGE 5B: Categorization ==============
def categorize_product(row):
    """
    Apply Master Decision Tree for categorization
    Returns: (category, confidence, evidence, filter_reason)
    """
    sup_title = str(row['SupplierTitle']).upper() if pd.notna(row['SupplierTitle']) else ""
    amz_title = str(row['AmazonTitle']).upper() if pd.notna(row['AmazonTitle']) else ""
    
    is_exact_ean = row['is_exact_ean_strict']
    title_sim = row['title_match']
    shared_tok = row['shared_tokens']
    adj_profit = row['Adjusted_Profit']
    rsu = row['RSU']
    sup_brand = row['Supplier_Brand']
    amz_brand = row['Amazon_Brand']
    ip_risk = row['IP_Risk']
    
    evidence = []
    filter_reason = "-"
    
    # ----- DECISION TREE -----
    
    # 1. STRICT EXACT EAN MATCH
    if is_exact_ean:
        evidence.append("Exact EAN match (checksum valid)")
        
        # Check for pack contradiction
        if rsu > 1 and adj_profit <= 0:
            return ("VERIFIED — AUDITED OUT", 95, "; ".join(evidence), f"RSU={int(rsu)}; Adjusted Profit £{adj_profit:.2f}")
        
        # Check IP Risk
        if ip_risk:
            return ("VERIFIED — AUDITED OUT", 95, "; ".join(evidence), f"IP Risk: Luxury/trademark brand detected")
        
        # Valid VERIFIED
        if adj_profit > 0:
            if rsu > 1:
                evidence.append(f"RSU={int(rsu)} but profit remains positive")
            return ("VERIFIED", 95, "; ".join(evidence), "-")
        else:
            return ("VERIFIED — AUDITED OUT", 95, "; ".join(evidence), f"Negative adjusted profit: £{adj_profit:.2f}")
    
    # 2. Check for brand conflict (both explicit + different)
    if sup_brand and amz_brand and sup_brand != amz_brand:
        return ("UNRELATED", 0, f"Brand conflict: {sup_brand} vs {amz_brand}", "Different brands")
    
    # 3. Check title similarity and shared tokens
    if shared_tok == 0:
        # No shared tokens - likely mismatch (per calibration: 78% mismatch rate)
        return ("UNRELATED", 0, "No shared significant tokens", "Title mismatch - no overlap")
    
    # 4. BRAND MATCH + anchors
    brand_match = (sup_brand and sup_brand == amz_brand)
    
    if brand_match:
        evidence.append(f"Brand match: {sup_brand}")
        
        # Check profit
        if adj_profit <= 0:
            return ("AUDITED OUT", 80, "; ".join(evidence), f"Negative adjusted profit: £{adj_profit:.2f}")
        
        # Check IP Risk
        if ip_risk:
            return ("NEEDS VERIFICATION", 70, "; ".join(evidence) + "; IP Risk flagged", "Check IP/trademark status")
        
        # Strong match with brand
        if shared_tok >= 3:
            evidence.append(f"Strong anchor match ({shared_tok} shared tokens)")
            return ("HIGHLY LIKELY", 85, "; ".join(evidence), "-")
        elif shared_tok >= 2:
            evidence.append(f"Moderate anchor match ({shared_tok} shared tokens)")
            return ("HIGHLY LIKELY", 75, "; ".join(evidence), "-")
        else:
            evidence.append(f"Weak anchors ({shared_tok} shared tokens)")
            return ("NEEDS VERIFICATION", 60, "; ".join(evidence), "Verify product type match")
    
    # 5. One brand present (not both)
    if sup_brand or amz_brand:
        detected_brand = sup_brand or amz_brand
        evidence.append(f"Brand in {'supplier' if sup_brand else 'Amazon'}: {detected_brand}")
        
        if adj_profit <= 0:
            return ("AUDITED OUT", 60, "; ".join(evidence), f"Negative adjusted profit: £{adj_profit:.2f}")
        
        if shared_tok >= 3:
            evidence.append(f"Strong product anchors ({shared_tok} shared tokens)")
            return ("NEEDS VERIFICATION", 65, "; ".join(evidence), "Verify brand on packaging")
        elif shared_tok >= 2:
            evidence.append(f"Moderate product anchors ({shared_tok} shared tokens)")
            return ("NEEDS VERIFICATION", 55, "; ".join(evidence), "Verify brand and product match")
        else:
            return ("UNRELATED", 0, "Weak anchors, brand mismatch risk", "Insufficient evidence")
    
    # 6. No brand detected - rely on title similarity
    if title_sim >= 0.4 and shared_tok >= 3:
        evidence.append(f"Title similarity: {title_sim:.0%}; {shared_tok} shared tokens")
        if adj_profit > 0:
            return ("NEEDS VERIFICATION", 50, "; ".join(evidence), "Verify brand/product without explicit brand")
        else:
            return ("AUDITED OUT", 50, "; ".join(evidence), f"Negative adjusted profit: £{adj_profit:.2f}")
    
    # 7. Default: UNRELATED
    return ("UNRELATED", 0, f"Low match indicators (sim:{title_sim:.0%}, tokens:{shared_tok})", "Insufficient evidence")

# Apply categorization
results = df.apply(categorize_product, axis=1)
df['Category'] = results.apply(lambda x: x[0])
df['Confidence'] = results.apply(lambda x: x[1])
df['Evidence'] = results.apply(lambda x: x[2])
df['Filter_Reason'] = results.apply(lambda x: x[3])

# ============== SUMMARY ==============
print("\n" + "=" * 60)
print("CATEGORIZATION SUMMARY")
print("=" * 60)

categories = df['Category'].value_counts()
for cat, count in categories.items():
    print(f"  {cat}: {count}")

# ============== GENERATE REPORT ==============
timestamp = datetime.now().strftime("%y%m%d%H%M")
output_path = rf'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\OPUS manu\PHASEA_MANUAL_REPORT_{timestamp}.md'

# Prepare data for each category
verified_rec = df[df['Category'] == 'VERIFIED'].sort_values('Adjusted_Profit', ascending=False)
verified_out = df[df['Category'] == 'VERIFIED — AUDITED OUT'].sort_values('Adjusted_Profit', ascending=False)
highly_likely = df[df['Category'] == 'HIGHLY LIKELY'].sort_values(['Confidence', 'Adjusted_Profit'], ascending=[False, False])
needs_verif = df[df['Category'] == 'NEEDS VERIFICATION'].sort_values(['Confidence', 'Adjusted_Profit'], ascending=[False, False])
audited_out = df[df['Category'] == 'AUDITED OUT'].sort_values('Adjusted_Profit', ascending=False)
unrelated = df[df['Category'] == 'UNRELATED']

def sanitize_cell(text, max_len=50):
    """Sanitize cell content for markdown tables"""
    if pd.isna(text):
        return "-"
    s = str(text)
    s = s.replace('|', '/').replace('\n', ' ').replace('\r', '')
    if len(s) > max_len:
        s = s[:max_len-3] + "..."
    return s

def format_price(val):
    """Format price values"""
    try:
        return f"£{float(val):.2f}"
    except:
        return "-"

def format_pct(val):
    """Format percentage values"""
    try:
        return f"{float(val):.1f}%"
    except:
        return "-"

def generate_table(df_subset, category_name):
    """Generate a markdown table for a category"""
    if len(df_subset) == 0:
        return f"\n*No items in this category*\n"
    
    lines = []
    lines.append("```text")
    
    # Header
    header = "| Verdict | Conf | SupplierTitle | AmazonTitle | Sup EAN | Amz EAN | ASIN | SupPrice | SellPrice | NetProfit | ROI | Sales | Pack Verdict | Adj Profit | Evidence | Filter Reason |"
    sep = "|---------|------|---------------|-------------|---------|---------|------|----------|-----------|-----------|-----|-------|--------------|------------|----------|---------------|"
    lines.append(header)
    lines.append(sep)
    
    for _, row in df_subset.iterrows():
        verdict = category_name if 'AUDITED' not in category_name else row['Category'].replace('VERIFIED — ', '')
        conf = int(row['Confidence'])
        sup_title = sanitize_cell(row['SupplierTitle'], 35)
        amz_title = sanitize_cell(row['AmazonTitle'], 40)
        sup_ean = row['EAN_digits_normalized'] if row['EAN_strict_valid'] else "-"
        amz_ean = row['EAN_OnPage_digits_normalized'] if row['EAN_OnPage_strict_valid'] else "-"
        asin = str(row['ASIN']) if pd.notna(row['ASIN']) else "-"
        sup_price = format_price(row.get('SupplierPrice_incVAT', row.get('SupplierPrice_exVAT', 0)))
        sell_price = format_price(row.get('SellingPrice_incVAT', 0))
        net_profit = format_price(row['NetProfit'])
        roi = format_pct(row.get('ROI ( % )', row.get('ROI', 0)))
        sales = int(row.get('bought_in_past_month', row.get('sales_numeric', 0)))
        pack_verdict = sanitize_cell(row['Pack_Verdict'], 20)
        adj_profit = format_price(row['Adjusted_Profit'])
        evidence = sanitize_cell(row['Evidence'], 40)
        filter_reason = sanitize_cell(row['Filter_Reason'], 30)
        
        line = f"| {verdict} | {conf} | {sup_title} | {amz_title} | {sup_ean} | {amz_ean} | {asin} | {sup_price} | {sell_price} | {net_profit} | {roi} | {sales} | {pack_verdict} | {adj_profit} | {evidence} | {filter_reason} |"
        lines.append(line)
    
    lines.append("```")
    return "\n".join(lines)

# Build report
report = []
report.append("# PHASEA MANUAL REPORT")
report.append(f"**Generated:** 2026-01-10")
report.append(f"**Input File:** part 8 jan.xlsx")
report.append(f"**Supplier:** UK Wholesale Supplier")
report.append(f"**Analysis Version:** v4.1.1 AG1 (Antigravity Enhanced)")
report.append("")
report.append("---")
report.append("")
report.append("## ⚠️ CRITICAL DATA QUALITY NOTE")
report.append("")
report.append("**Preflight Calibration Finding:** 78% of rows (39/50 sample) have NO word overlap between SupplierTitle and AmazonTitle.")
report.append("This indicates severe EAN-to-ASIN mapping issues. EAN validation is the ONLY reliable link between supplier and Amazon data.")
report.append("Title-based matching has been applied with strict thresholds due to this data quality issue.")
report.append("")
report.append("---")
report.append("")
report.append("## Summary Counts")
report.append("")
report.append(f"- **VERIFIED — RECOMMENDED:** {len(verified_rec)}")
report.append(f"- **VERIFIED — AUDITED OUT / EXCLUDED:** {len(verified_out)}")
report.append(f"- **HIGHLY LIKELY — RECOMMENDED:** {len(highly_likely)}")
report.append(f"- **NEEDS VERIFICATION:** {len(needs_verif)}")
report.append(f"- **AUDITED OUT (Non-EAN):** {len(audited_out)}")
report.append(f"- **UNRELATED / NOT INCLUDED:** {len(unrelated)}")
report.append(f"- **TOTAL ANALYZED:** {len(df)}")
report.append("")
report.append("---")
report.append("")

# VERIFIED — RECOMMENDED
report.append(f"## VERIFIED — RECOMMENDED (count={len(verified_rec)})")
report.append("")
if len(verified_rec) > 0:
    report.append("*Exact EAN matches with positive adjusted profit*")
    report.append("")
    report.append(generate_table(verified_rec, "VERIFIED"))
else:
    report.append("*No items in this category. This is expected if no strict exact EAN matches were found in the data.*")
report.append("")
report.append("---")
report.append("")

# VERIFIED — AUDITED OUT
report.append(f"## VERIFIED — AUDITED OUT / EXCLUDED (count={len(verified_out)})")
report.append("")
if len(verified_out) > 0:
    report.append("*Exact EAN matches confirmed but excluded due to pack/variant/profit/IP gates*")
    report.append("")
    report.append(generate_table(verified_out, "AUDITED OUT"))
else:
    report.append("*No items in this category.*")
report.append("")
report.append("---")
report.append("")

# HIGHLY LIKELY — RECOMMENDED
report.append(f"## HIGHLY LIKELY — RECOMMENDED (count={len(highly_likely)})")
report.append("")
if len(highly_likely) > 0:
    report.append("*Strong brand + product matches with positive adjusted profit*")
    report.append("")
    report.append(generate_table(highly_likely, "HIGHLY LIKELY"))
else:
    report.append("*No items in this category. Due to high mismatch rate (78%), few products met HIGHLY LIKELY criteria.*")
report.append("")
report.append("---")
report.append("")

# NEEDS VERIFICATION
report.append(f"## NEEDS VERIFICATION (count={len(needs_verif)})")
report.append("")
if len(needs_verif) > 0:
    report.append("*Plausible matches requiring 1-2 confirmable details to upgrade*")
    report.append("")
    report.append(generate_table(needs_verif, "NEEDS VERIF"))
else:
    report.append("*No items in this category.*")
report.append("")
report.append("---")
report.append("")

# AUDITED OUT (Non-EAN)
report.append(f"## AUDITED OUT (count={len(audited_out)})")
report.append("")
if len(audited_out) > 0:
    report.append("*Confirmed matches excluded due to pack/variant/profit gates (non-EAN based)*")
    report.append("")
    report.append(generate_table(audited_out, "AUDITED OUT"))
else:
    report.append("*No items in this category.*")
report.append("")
report.append("---")
report.append("")

# Reconciliation
report.append("## Reconciliation Summary")
report.append("")
report.append("| Category | Count | % of Total |")
report.append("|----------|-------|------------|")
report.append(f"| VERIFIED — RECOMMENDED | {len(verified_rec)} | {100*len(verified_rec)/len(df):.1f}% |")
report.append(f"| VERIFIED — AUDITED OUT | {len(verified_out)} | {100*len(verified_out)/len(df):.1f}% |")
report.append(f"| HIGHLY LIKELY — RECOMMENDED | {len(highly_likely)} | {100*len(highly_likely)/len(df):.1f}% |")
report.append(f"| NEEDS VERIFICATION | {len(needs_verif)} | {100*len(needs_verif)/len(df):.1f}% |")
report.append(f"| AUDITED OUT (Non-EAN) | {len(audited_out)} | {100*len(audited_out)/len(df):.1f}% |")
report.append(f"| UNRELATED / NOT INCLUDED | {len(unrelated)} | {100*len(unrelated)/len(df):.1f}% |")
report.append(f"| **TOTAL** | **{len(df)}** | **100%** |")
report.append("")
report.append("---")
report.append("")
report.append("## Calibration Config Applied")
report.append("")
report.append("```python")
for k, v in CALIBRATION.items():
    report.append(f'"{k}": {repr(v)},')
report.append("```")
report.append("")
report.append("---")
report.append("")
report.append("*Report generated by FBA Analysis v4.1.1 AG1*")

# Write report
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"\n✅ Report saved to: {output_path}")

# Also save detailed CSV for further analysis
csv_output = output_path.replace('.md', '_detailed.csv')
df.to_csv(csv_output, index=False)
print(f"✅ Detailed CSV saved to: {csv_output}")
