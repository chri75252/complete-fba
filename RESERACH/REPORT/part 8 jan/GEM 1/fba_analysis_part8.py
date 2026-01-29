import pandas as pd
import re
import os
import sys
from difflib import SequenceMatcher
from datetime import datetime

# --- CONFIGURATION ---
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx"
OUTPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\PHASEA_MANUAL_REPORT_20260108.md"

# Derived from Preflight Calibration
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pce", "pcs", "pces", "pc", "pk", "pack", "pieces", "set"],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": True,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch", "in", "m", "ft"],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times"]
}

# IP Brands (Softened List)
IP_BRANDS = [
    "JO MALONE", "CHANEL", "DIOR", "GUCCI", "LOUIS VUITTON", "PRADA", "HERMES", 
    "APPLE", "SAMSUNG", "SONY", "MICROSOFT", "NIKE", "ADIDAS"
]

SAFE_BRANDS = [
    "TIDYZ", "SOUDAL", "AMTECH", "ROLSON", "DRAPER", "FAIRY", "DETTOL", "MARIGOLD", 
    "DUNLOP", "MASON CASH", "PYREX", "EVERBUILD", "HARRIS", "STATUS", "EXTRASTAR", 
    "ROUNDUP", "LITTLE TREES"
]

# --- UTILS ---

def clean_to_digits(x):
    """Remove non-digits. Return empty string if scientific notation or invalid."""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e-' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

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
    """Attempt left-padding to valid GTIN length if checksum passes."""
    if not digits.isdigit():
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
    if not isinstance(digits, str):
        return False
    if not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r'^0{5,}', normalized): 
        return False
    return gtin_checksum_ok(normalized)

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

def extract_quantity(title):
    """
    Extract pack size from title using strict hierarchy.
    Returns 1.0 if not found.
    """
    if pd.isna(title):
        return 1.0
    title_lower = str(title).lower()
    
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*piece\b', # greedy
        r'(\d+)\s*pairs?\b',
        r'(\d+)\s*rolls?\b',
        r'^(\d+)\s*x\b',
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)'
    ]
    
    for pat in patterns:
        match = re.search(pat, title_lower)
        if match:
            try:
                q = float(match.group(1))
                if q > 1 and q < 1000:
                    return q
            except:
                pass
                
    return 1.0

def extract_multipack_total(title):
    """
    Look for amazon patterns like "(4 x 50)" or "3 x 500ml".
    Returns (outer, inner, total).
    """
    if pd.isna(title):
        return (1, 1, 1)
    title_lower = str(title).lower()
    
    pat = r'\(?\s*(\d+)\s*x\s*(\d+)'
    matches = re.findall(pat, title_lower)
    
    for outer_str, inner_str in matches:
        try:
            outer = int(outer_str)
            inner = int(inner_str)
            if outer > 1:
                return (outer, inner, outer*inner)
        except:
            continue
            
    base_qty = extract_quantity(title_lower)
    return (1, int(base_qty), int(base_qty))

def has_brand_match(sup_title, amz_title):
    if pd.isna(sup_title) or pd.isna(amz_title):
        return False
    sup = str(sup_title).upper()
    amz = str(amz_title).upper()
    
    tokens = sup.split()
    if not tokens:
        return False
        
    candidate_brand = tokens[0]
    if len(candidate_brand) > 2 and candidate_brand in amz:
        return True
        
    for b in SAFE_BRANDS:
        if b in sup and b in amz:
            return True
    return False

def check_ip_risk(title):
    if pd.isna(title):
        return False
    t = str(title).upper()
    for ip in IP_BRANDS:
        if ip in t:
            return True
    return False

# --- MAIN ANALYSIS ---

def run_analysis():
    print(f"Loading data from: {INPUT_FILE}")
    try:
        df = pd.read_excel(INPUT_FILE)
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    # Basic Cleaning
    df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()
    
    # Handle Sales
    sales_col = SUPPLIER_NAMING_CONVENTION['sales_column']
    if sales_col not in df.columns:
        if 'sales_numeric' in df.columns: sales_col = 'sales_numeric'
        elif 'bought_in_past_month' in df.columns: sales_col = 'bought_in_past_month'
        else: sales_col = None
    
    if sales_col:
        df['Sales'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0).astype(int)
    else:
        df['Sales'] = 0

    # Clean Digits
    df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
    df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
    
    # Title Similarity
    df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

    # Strict EAN
    df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
    df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)

    df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
    df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)

    df['is_exact_ean_strict'] = (
        df['EAN_strict_valid'] & 
        df['EAN_OnPage_strict_valid'] & 
        (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
    )

    # Pack Analysis
    def calculate_pack_logic(row):
        sup_t = str(row['SupplierTitle'])
        amz_t = str(row['AmazonTitle'])
        
        sup_qty = extract_quantity(sup_t)
        outer, inner, total = extract_multipack_total(amz_t)
        
        if outer > 1:
            pass
        else:
            amz_qty = extract_quantity(amz_t)
            outer = amz_qty
            
        rsu = max(1, outer / sup_qty)
        return rsu

    df['RSU'] = df.apply(calculate_pack_logic, axis=1)
    
    # Profit Recalc
    def get_adj_profit(row):
        try:
            orig = float(row['NetProfit'])
            cost = float(row['SupplierPrice_incVAT'])
            rsu = row['RSU']
            if rsu > 1:
                return orig - (cost * (rsu - 1))
            return orig
        except:
            return 0.0
            
    df['Adjusted_Profit'] = df.apply(get_adj_profit, axis=1)

    # --- CATEGORIZATION ENGINE ---
    
    records = []
    
    for idx, row in df.iterrows():
        # Defaults
        base_verdict = "UNRELATED" 
        confidence = 0
        filter_reason = "-"
        pack_verdict_str = f"1:1" if row['RSU'] == 1 else f"Bundle {row['RSU']}x"
        
        is_exact = row['is_exact_ean_strict']
        match_score = row['title_match']
        sup_t = str(row['SupplierTitle']) 
        amz_t = str(row['AmazonTitle'])
        brand_match = has_brand_match(sup_t, amz_t)
        adj_profit = row['Adjusted_Profit']
        
        if check_ip_risk(amz_t):
            base_verdict = "NEEDS VERIFICATION"
            filter_reason = "IP Brand Risk"
            confidence = 50

        # Exact EAN Logic
        if is_exact:
            base_verdict = "VERIFIED"
            confidence = 95
            filter_reason = "-"
            
        else:
            # Non-EAN Logic
            if brand_match:
                if match_score > 0.4:
                     base_verdict = "HIGHLY LIKELY"
                     confidence = 85
                elif match_score > 0.25:
                     base_verdict = "NEEDS VERIFICATION"
                     confidence = 60
                     filter_reason = "Brand match ok, titles diverge"
            
            elif match_score > 0.5:
                 base_verdict = "NEEDS VERIFICATION"
                 confidence = 50
                 filter_reason = "Strong Title Match, Brand uncertain"
                 
            if base_verdict == "UNRELATED" and match_score > 0.6:
                 base_verdict = "NEEDS VERIFICATION" 
                 filter_reason = "High text similarity"

        # Categorize into Sub-sections
        final_section = "UNRELATED"
        
        if base_verdict == "VERIFIED":
            if adj_profit > 0:
                final_section = "VERIFIED — RECOMMENDED"
            else:
                final_section = "VERIFIED — AUDITED OUT / EXCLUDED"
                if filter_reason == "-": filter_reason = "Unprofitable after pack calc"
                
        elif base_verdict == "HIGHLY LIKELY":
            if adj_profit > 0:
                final_section = "HIGHLY LIKELY — RECOMMENDED"
            else:
                final_section = "HIGHLY LIKELY — AUDITED OUT / EXCLUDED"
                if filter_reason == "-": filter_reason = "Unprofitable"

        elif base_verdict == "NEEDS VERIFICATION":
            if adj_profit > 0:
                final_section = "NEEDS VERIFICATION"
            else:
                final_section = "UNRELATED" # Map unprofitable needs-verify to unrelated

        records.append({
            "Verdict": final_section,
            "BaseVerdict": base_verdict,
            "Confidence": confidence,
            "Filter Reason": filter_reason,
            "Pack Verdict": pack_verdict_str,
            "Adjusted_Profit": adj_profit
        })
        
    v_df = pd.DataFrame(records)
    final_df = pd.concat([df.reset_index(drop=True), v_df.drop(columns=['Adjusted_Profit'])], axis=1) 
    
    # --- REPORT GENERATION ---
    
    report_df = final_df[final_df['Verdict'] != "UNRELATED"].copy()
    
    def clean_cell(x):
        return str(x).replace('|', '/').replace('\n', ' ').strip()
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# PHASEA MANUAL REPORT\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Input File:** {os.path.basename(INPUT_FILE)}\n")
        f.write(f"**Supplier:** (Unknown)\n")
        
        # Calculate Counts
        counts = report_df['Verdict'].value_counts()
        ver_rec = counts.get("VERIFIED — RECOMMENDED", 0)
        ver_ex = counts.get("VERIFIED — AUDITED OUT / EXCLUDED", 0)
        hl_rec = counts.get("HIGHLY LIKELY — RECOMMENDED", 0)
        hl_ex = counts.get("HIGHLY LIKELY — AUDITED OUT / EXCLUDED", 0)
        nv_count = counts.get("NEEDS VERIFICATION", 0)
        total_rows = len(df)
        unrelated = total_rows - (ver_rec + ver_ex + hl_rec + hl_ex + nv_count)
        
        f.write("## Summary Counts\n")
        f.write(f"- VERIFIED — RECOMMENDED: {ver_rec}\n")
        f.write(f"- VERIFIED — AUDITED OUT / EXCLUDED: {ver_ex}\n")
        f.write(f"- HIGHLY LIKELY — RECOMMENDED: {hl_rec}\n")
        f.write(f"- HIGHLY LIKELY — AUDITED OUT / EXCLUDED: {hl_ex}\n")
        f.write(f"- NEEDS VERIFICATION: {nv_count}\n")
        f.write(f"- UNRELATED / NOT INCLUDED: {unrelated}\n")
        f.write(f"- TOTAL ANALYZED: {total_rows}\n")
        f.write("This report applies v4.0 Thorough Manual Analysis:\n")
        f.write("- HIGHLY LIKELY requires Brand + Product type match with positive profit.\n")
        f.write("- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade.\n")
        f.write("- AUDITED OUT contains CONFIRMED matches that are unprofitable (for audit).\n\n")
        
        sections = [
            "VERIFIED — RECOMMENDED",
            "VERIFIED — AUDITED OUT / EXCLUDED",
            "HIGHLY LIKELY — RECOMMENDED",
            "HIGHLY LIKELY — AUDITED OUT / EXCLUDED",
            "NEEDS VERIFICATION"
        ]
        
        cols = [
            'BaseVerdict', 'Confidence', 'SupplierTitle', 'AmazonTitle', 
            'EAN', 'EAN_OnPage', 'ASIN', 
            'SupplierPrice_incVAT', 'SellingPrice_incVAT', 'NetProfit', 'ROI', 'Sales',
            'Pack Verdict', 'Adjusted_Profit', 'Filter Reason'
        ]
        
        col_map = {
            'BaseVerdict': 'Verdict',
            'SupplierPrice_incVAT': 'SupplierPrice',
            'SellingPrice_incVAT': 'SellingPrice',
            'EAN': 'Supplier EAN',
            'EAN_OnPage': 'Amazon EAN',
            'Adjusted_Profit': 'Adjusted Profit'
        }
        
        for section in sections:
            count_in_sec = counts.get(section, 0)
            f.write(f"## {section} (count={count_in_sec})\n")
            
            subset = report_df[report_df['Verdict'] == section]
            if subset.empty:
                f.write("\n")
                continue
            
            table_rows = []
            for _, row in subset.iterrows():
                r_dict = {}
                for c in cols:
                    val = row.get(c, '-')
                    if isinstance(val, (float, int)): 
                         if c in ['SupplierPrice_incVAT', 'SellingPrice_incVAT', 'NetProfit', 'Adjusted_Profit']:
                             val = f"£{float(val):.2f}"
                         elif c == 'ROI':
                             val = f"{float(val):.1f}%"
                    header = col_map.get(c, c)
                    r_dict[header] = clean_cell(val)
                r_dict['Key Match Evidence'] = "-"
                table_rows.append(r_dict)
                
            if not table_rows:
                continue

            headers = list(table_rows[0].keys())
            widths = {h: len(h) for h in headers}
            for r in table_rows:
                for h in headers:
                    widths[h] = max(widths[h], len(r[h]))
            
            header_line = "| " + " | ".join([h.ljust(widths[h]) for h in headers]) + " |"
            sep_line = "| " + " | ".join(['-' * widths[h] for h in headers]) + " |"
            
            f.write("```text\n")
            f.write(header_line + "\n")
            f.write(sep_line + "\n")
            for r in table_rows:
                line = "| " + " | ".join([r[h].ljust(widths[h]) for h in headers]) + " |"
                f.write(line + "\n")
            f.write("```\n\n")
            
    print(f"Report Generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_analysis()
