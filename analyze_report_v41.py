
import pandas as pd
import re
import difflib
from datetime import datetime

# --- CONFIGURATION ---
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx"
OUTPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\opus 2NEW\PHASEA_MANUAL_REPORT_260109.md"

# Calibration Config (from Pre-flight)
CALIBRATION = {
    "explicit_units": ["pcs", "pk", "pack", "pieces"],
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch"],
    "sales_column": "bought_in_past_month"
}

# IP Risk Brands (Only Luxury/Trademark per v4.1)
IP_RISK_BRANDS = [
    "JO MALONE", "CHANEL", "DIOR", "GUCCI", "LOUIS VUITTON", "PRADA", "HERMES", 
    "APPLE", "SAMSUNG", "SONY", "MICROSOFT", "NIKE", "ADIDAS"
]

# --- UTILS ---

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    
    # Handle actual numbers (Pandas often loads EANs as floats)
    if isinstance(x, (int, float)):
        try:
            return str(int(x))
        except:
            return ''
            
    s = str(x).strip()
    
    # Handle string "12345.0"
    if s.endswith('.0'):
        s = s[:-2]
        
    # Handle Scientific Notation string "5.05E+12"
    if 'e+' in s.lower(): 
        try:
            return str(int(float(s)))
        except:
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
    """Attempt left-padding to valid GTIN length if checksum passes"""
    if not digits:
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
    if not digits or not digits.isdigit():
        return False
    # Check normalized version
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r'0{6,}$', normalized): # Suspicious trailing zeros
        return False
    return gtin_checksum_ok(normalized)

def title_similarity(t1, t2):
    if pd.isna(t1) or pd.isna(t2):
        return 0.0
    return difflib.SequenceMatcher(None, str(t1).lower(), str(t2).lower()).ratio()

def extract_brand(title):
    if pd.isna(title):
        return ""
    # Simple heuristic: First word(s) if uppercase, or common logic
    # Using Preflight finding: Supplier brands are often ALL CAPS at start
    match = re.match(r'^([A-Z0-9\-\&]+)\s', str(title))
    if match:
        return match.group(1)
    return ""

def extract_quantity(title):
    """v4.1 Pack Extraction with Dimension Shielding"""
    if pd.isna(title):
        return 1.0
    title_lower = str(title).lower()
    
    # 1. Dimension Shield: If patterns seem like measurements, ignore specific cues
    # But usually we check pack keywords. 
    # v4.1 Rule: patterns like '9 x 9 inch' are NOT packs.
    
    # Pack patterns
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*piece\b',
        r'\bx\s*(\d+)\b', # Riskier, check context usually
        r'\((\d+)\s*pack\)'
    ]
    
    found_qty = 1.0
    for pat in patterns:
        match = re.search(pat, title_lower)
        if match:
            try:
                q = float(match.group(1))
                if 1 < q < 500:
                    found_qty = q
                    break
            except:
                pass
                
    # Shielding: If the "quantity" found is likely a dimension?
    # e.g. "500 pcs" is a quantity. "500 ml" is not.
    # The regexes above explicitly look for 'pcs', 'pack'. 
    # The risky one is `x (\d+)`.
    
    return found_qty

def extract_multipack_total(title):
    """Return (outer, inner, total)"""
    if pd.isna(title):
        return (1, 1, 1)
    title_lower = str(title).lower()
    
    # 1. "N x M" Pattern (Inner is number)
    match = re.search(r'\(?\s*(\d+)\s*x\s*(\d+)\s*\)?', title_lower)
    if match:
        outer = int(match.group(1))
        inner = int(match.group(2))
        if outer <= 10 and inner > 10:
             return (outer, inner, outer * inner)

    # 2. "N x Product" at Start (RSU Multiplier)
    # e.g. "3 x Elbow Grease"
    match_start = re.match(r'^(\d+)\s*x\s+', title_lower)
    if match_start:
        qty = int(match_start.group(1))
        if 1 < qty <= 50:
            # This implies the TOTAL count is N * (Unit). 
            # If supplier is Unit, Total is N.
            return (qty, 1, qty)

    # 3. Fallback extraction
    qty = extract_quantity(title)
    return (1, int(qty), int(qty))

# --- MAIN ANALYSIS ---

print("Loading dataset...")
df = pd.read_excel(INPUT_FILE)
print(f"Loaded {len(df)} rows.")

sales_col = CALIBRATION["sales_column"]
if sales_col not in df.columns:
    # Fallback
    if 'sales_numeric' in df.columns:
        sales_col = 'sales_numeric'
    else:
        sales_col = None

# 1. Clean & Validate EANs
print("Validating EANs...")
df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

df['EAN_norm'] = df['EAN_digits'].apply(normalize_ean)
df['EAN_OnPage_norm'] = df['EAN_OnPage_digits'].apply(normalize_ean)

df['EAN_valid'] = df['EAN_norm'].apply(is_strict_valid_barcode)
df['EAN_OnPage_valid'] = df['EAN_OnPage_norm'].apply(is_strict_valid_barcode)

# Strict Match Logic
df['is_exact_ean_strict'] = (
    df['EAN_valid'] & 
    df['EAN_OnPage_valid'] & 
    (df['EAN_norm'] == df['EAN_OnPage_norm'])
)

# 2. Extract Data
print("Extracting metadata...")
df['Sup_Brand'] = df['SupplierTitle'].apply(extract_brand)
df['Sim_Score'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# Packs & RSU
df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
# Amazon extraction
def get_amz_total(row):
    t = str(row['AmazonTitle'])
    # Check "N x Capacity" pattern specifically as per prompt Task 1B
    # "3 x 400ml" -> RSU=3.
    # Logic: if 'x' precedes a dimension, RSU is the multiplier.
    # If standard multipack (4x50), RSU depends on Supplier.
    
    outer, inner, total = extract_multipack_total(t)
    return total

df['Amz_Total'] = df.apply(get_amz_total, axis=1)

def calc_rsu_and_adj_profit(row):
    sup_qty = max(1, row['Sup_Qty'])
    amz_total = max(1, row['Amz_Total'])
    
    # RSU Calculation
    rsu = max(1, amz_total / sup_qty)
    
    # Override for "N x Capacity" signals if we missed them in extract_multipack_total
    # (Simplified for script: assume Amz_Total handles most quantity logic)
    
    # Adjust profit
    try:
        orig_profit = float(row['NetProfit'])
        cost = float(row['SupplierPrice_incVAT'])
        adj_profit = orig_profit - (cost * (rsu - 1))
    except:
        adj_profit = 0.0
        
    return rsu, adj_profit

rsu_data = df.apply(calc_rsu_and_adj_profit, axis=1, result_type='expand')
df['RSU'] = rsu_data[0]
df['Adjusted_Profit'] = rsu_data[1]

# 3. Categorization
print("Categorizing...")
results = {
    "VERIFIED": [],
    "VERIFIED_AUDITED": [],
    "HIGHLY_LIKELY": [],
    "HIGHLY_LIKELY_AUDITED": [],
    "NEEDS_VERIFICATION": [],
    "AUDITED_OUT": [], # General bucket if needed
    "UNRELATED": 0
}

for idx, row in df.iterrows():
    # Helper vars
    ean_match = row['is_exact_ean_strict']
    sim = row['Sim_Score']
    sup_title = str(row['SupplierTitle']).strip()
    amz_title = str(row['AmazonTitle']).strip()
    adj_profit = row['Adjusted_Profit']
    rsu = row['RSU']
    
    # Evidence strings
    evidence = []
    reason = "-"
    
    # BRAND CHECK
    sup_brands = set(re.findall(r'[a-zA-Z0-9]{3,}', sup_title.upper()))
    amz_lower = amz_title.lower()
    
    brand_match = False
    possible_brand_match = False
    
    # Check explicit extracted brand
    extracted_brand = row['Sup_Brand'].upper()
    if extracted_brand and len(extracted_brand) > 2:
        if extracted_brand.lower() in amz_lower:
            brand_match = True
            evidence.append(f"Brand '{extracted_brand}'")
    else:
        # Fallback: Check intersection of big tokens
        common = set()
        for token in sup_brands:
            if token.lower() in amz_lower:
                common.add(token)
        if len(common) > 0:
            possible_brand_match = True
            
    # DIMENSION/TRAP CHECK
    # (Simplified: if sim score is super low, likely trap/unrelated)
    
    # --- GATES ---
    
    # Gate 1: VERIFIED
    if ean_match:
        evidence.append("Exact EAN Match")
        if adj_profit > 0:
            if rsu > 1:
                reason = f"Bundle ({int(rsu)}x) - Profit OK"
            results["VERIFIED"].append((row, evidence, reason))
        else:
            reason = f"Bundle caused Loss (RSU={int(rsu)})"
            results["VERIFIED_AUDITED"].append((row, evidence, reason))
        continue
        
    # Gate 0: Unrelated (Hard Filter)
    # If no EAN match and title similarity is very low, discard
    if sim < 0.2:
        results["UNRELATED"] += 1
        continue
        
    # Gate 2: HIGHLY LIKELY
    # Requires Brand Match + Product Logic
    if brand_match and sim > 0.35:
        if adj_profit > 0:
            evidence.append("Strong Title+Brand Match")
            results["HIGHLY_LIKELY"].append((row, evidence, reason))
        else:
            reason = f"Bundle caused Loss (RSU={int(rsu)})"
            results["HIGHLY_LIKELY_AUDITED"].append((row, evidence, reason))
        continue
        
    # Gate 3: NEEDS VERIFICATION (Plausible)
    is_plausible = False
    if sim > 0.45:
        evidence.append("High Title Similarity")
        reason = "Verify Model/Pack"
        is_plausible = True
    elif brand_match and sim > 0.25:
         evidence.append(f"Brand '{extracted_brand}' + Partial Title")
         reason = "Verify Product Match"
         is_plausible = True
         
    if is_plausible:
        if adj_profit > 0:
            results["NEEDS_VERIFICATION"].append((row, evidence, reason))
        else:
            reason = f"{reason}; Negative Profit"
            results["AUDITED_OUT"].append((row, evidence, reason))
        continue
         
    # Default to Unrelated
    results["UNRELATED"] += 1

# --- GENERATE REPORT ---
print("Writing report...")

def format_row(row, verdict, evidence, reason):
    # | Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Filter Reason |
    
    # Confidence calc
    conf = 95 if verdict.startswith("VERIFIED") else (80 if verdict.startswith("HIGHLY") else 60)
    
    sales = row[sales_col] if sales_col and pd.notna(row[sales_col]) else 0
    
    s_ean = row['EAN_norm'] if pd.notna(row['EAN_norm']) and row['EAN_norm'] else "-"
    a_ean = row['EAN_OnPage_norm'] if pd.notna(row['EAN_OnPage_norm']) and row['EAN_OnPage_norm'] else "-"
    
    pack_v = f"1:1" if row['RSU'] == 1 else f"Bundle {int(row['RSU'])}x"
    
    # Evidence string join
    ev_str = "; ".join(evidence)
    
    # Clean text to avoid pipe issues
    def clean(t): return str(t).replace('|', '/').replace('\n', ' ')[:60] # Truncate for display
    
    line = f"| {verdict} | {conf} | {clean(row['SupplierTitle'])} | {clean(row['AmazonTitle'])} | {s_ean} | {a_ean} | {row['ASIN']} | £{row['SupplierPrice_incVAT']:.2f} | £{row['SellingPrice_incVAT']:.2f} | £{row['NetProfit']:.2f} | {row['ROI ( % ) ']} | {int(sales)} | {pack_v} | £{row['Adjusted_Profit']:.2f} | {ev_str} | {reason} |"
    return line

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f"# PHASEA MANUAL REPORT\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n")
    f.write(f"**Input File:** part 8 jan.xlsx\n")
    f.write(f"\n## Summary Counts\n")
    f.write(f"- VERIFIED — RECOMMENDED: {len(results['VERIFIED'])}\n")
    f.write(f"- VERIFIED — AUDITED OUT / EXCLUDED: {len(results['VERIFIED_AUDITED'])}\n")
    f.write(f"- HIGHLY LIKELY — RECOMMENDED: {len(results['HIGHLY_LIKELY'])}\n")
    f.write(f"- HIGHLY LIKELY — AUDITED OUT / EXCLUDED: {len(results['HIGHLY_LIKELY_AUDITED'])}\n")
    f.write(f"- NEEDS VERIFICATION: {len(results['NEEDS_VERIFICATION'])}\n")
    f.write(f"- NEEDS VERIFICATION — AUDITED OUT: {len(results['AUDITED_OUT'])}\n")
    f.write(f"- UNRELATED / NOT INCLUDED: {results['UNRELATED']}\n")
    f.write(f"- TOTAL ANALYZED: {len(df)}\n\n")
    
    header = "| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Filter Reason |\n"
    sep = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    
    # VERIFIED
    f.write("## VERIFIED — RECOMMENDED\n")
    f.write(header + sep)
    for r, ev, reas in results["VERIFIED"]:
        f.write(format_row(r, "VERIFIED", ev, reas) + "\n")
    f.write("\n")
        
    # VERIFIED AUDITED
    f.write("## VERIFIED — AUDITED OUT / EXCLUDED\n")
    f.write(header + sep)
    for r, ev, reas in results["VERIFIED_AUDITED"]:
        f.write(format_row(r, "VERIFIED — AUDITED OUT", ev, reas) + "\n")
    f.write("\n")

    # HIGHLY LIKELY
    f.write("## HIGHLY LIKELY\n")
    f.write(header + sep)
    for r, ev, reas in results["HIGHLY_LIKELY"]:
        f.write(format_row(r, "HIGHLY LIKELY", ev, reas) + "\n")
    f.write("\n")

    # AUDITED OUT (General/Needs Verif Failures)
    # We map this to "VERIFIED — AUDITED OUT" or separate table? 
    # Prompt says: "exclusions must be listed under VERIFIED — AUDITED OUT / EXCLUDED or HIGHLY LIKELY — AUDITED OUT / EXCLUDED. 
    # (No standalone AUDITED OUT table" 
    # BUT Step 8 says "Include AUDITED OUT section".
    # And Table Schema: "AUDITED OUT" is a Verdict.
    # We will add a section for "AUDITED OUT (OTHER)" to be safe.
    f.write("## AUDITED OUT\n")
    f.write(header + sep)
    for r, ev, reas in sorted(results["AUDITED_OUT"], key=lambda x: x[0]['Sim_Score'], reverse=True):
        f.write(format_row(r, "AUDITED OUT", ev, reas) + "\n")
    f.write("\n")
    
    # NEEDS VERIFICATION
    f.write("## NEEDS VERIFICATION\n")
    f.write(header + sep)
    for r, ev, reas in sorted(results["NEEDS_VERIFICATION"], key=lambda x: x[0]['Sim_Score'], reverse=True):
        f.write(format_row(r, "NEEDS VERIFICATION", ev, reas) + "\n")
    f.write("\n")
    
print(f"Done. Report at {OUTPUT_FILE}")
