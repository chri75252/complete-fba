import pandas as pd
import re
import numpy as np
from difflib import SequenceMatcher
import sys

# ==========================================
# CONFIG & INPUTS
# ==========================================
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx"
OUTPUT_CSV = "deep_analysis_20251225.csv"
OUTPUT_MD = "PHASEA_MANUAL_REPORT_20251225.md"

# ==========================================
# STAGE 1: Data Loading & Initial Cleaning
# ==========================================
print("Loading data...")
try:
    df = pd.read_excel(INPUT_PATH)
except Exception as e:
    print(f"Error reading Excel, trying csv: {e}")
    df = pd.read_csv(INPUT_PATH)

# Clean EAN columns
df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Handle sales column
if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
else:
    # Try to find a sales column
    cols = [c for c in df.columns if 'sales' in c.lower()]
    if cols:
        df['sales'] = pd.to_numeric(df[cols[0]], errors='coerce').fillna(0)
    else:
        df['sales'] = 0

# RowID
df['RowID'] = df.index + 1

# ==========================================
# STAGE 1B: EAN Normalization Safety Flags
# ==========================================
def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

# ==========================================
# STAGE 2: Title Similarity
# ==========================================
def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x.get('SupplierTitle', ''), x.get('AmazonTitle', '')), axis=1)

# ==========================================
# STAGE 3 & 3B: Strict EAN Matching
# ==========================================
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
    if re.search(r'0{6,}$', normalized):
        return False
    return gtin_checksum_ok(normalized)

df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)

df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)

df['is_exact_ean_strict'] = (
    df['EAN_strict_valid']
    & df['EAN_OnPage_strict_valid']
    & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
)

# ==========================================
# STAGE 4: Pack Size Extraction
# ==========================================
def extract_quantity(title):
    if pd.isna(title):
        return 1.0
    title = str(title).lower()
    patterns = [
        r'pack of (\d+)', r'set of (\d+)', r'\b(\d+)\s*pack\b', r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b', r'(\d+)\s*pieces?\b', r'(\d+)\s*pairs?\b', r'\bx\s*(\d+)\b',
        r'\((\d+)\s*pack\)', r'\(pack of (\d+)\)', r'\b(\d+)\s*rolls?\b', r'\b(\d+)\s*piece\b',
    ]
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:
                return qty
    return 1.0

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']

def recalculate_profit(row):
    try:
        original_profit = float(row.get('NetProfit', 0))
        supplier_cost = float(row.get('SupplierPrice_incVAT', 0))
        ratio = row['Qty_Ratio']
        # If ratio > 1 (e.g. need 6 packs for 1 Amz unit), cost increases
        # Cost adjustment: we pay for (ratio) units.
        # Adjusted Profit = SellingPrice - Fees - (SupplierCost * Ratio)
        # Assuming original NetProfit = SellingPrice - Fees - SupplierCost
        # So Adjusted = NetProfit - SupplierCost * (Ratio - 1)
        adjustment = supplier_cost * (ratio - 1)
        return original_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# ==========================================
# STAGE 5B: MLS Calculation (Heuristic)
# ==========================================
# Brands
LUXURY_BRANDS = ['Jo Malone', 'Chanel', 'Dior', 'Gucci', 'Louis Vuitton', 'Prada', 'Hermès', 'Apple', 'Samsung', 'Sony', 'Microsoft', 'Nike', 'Adidas']
GENERIC_BRANDS = ['TIDYZ', 'SOUDAL', 'AMTECH', 'ROLSON', 'DRAPER', 'FAIRY', 'DETTOL', 'MARIGOLD', 'DUNLOP', 'MASON CASH', 'PYREX', 'EVERBUILD', 'HARRIS', 'STATUS', 'EXTRASTAR', 'ROUNDUP', 'LITTLE TREES']

def extract_brand(title):
    if pd.isna(title): return ""
    # Very crude: first word usually, or first 2 if strict
    parts = str(title).split()
    if not parts: return ""
    return parts[0].lower()

def calculate_mls_row(row):
    st = str(row.get('SupplierTitle', '')).lower()
    at = str(row.get('AmazonTitle', '')).lower()
    
    # Base from title match
    base_score = row.get('title_match', 0) * 80 # Scaling 0.5 -> 40, 1.0 -> 80
    
    score = base_score
    
    # Brand Match logic
    # Try to find known brands or first word match
    s_brand = extract_brand(row.get('SupplierTitle', ''))
    a_brand = extract_brand(row.get('AmazonTitle', ''))
    
    if s_brand and a_brand and s_brand == a_brand:
        score += 15
    elif any(b.lower() in st and b.lower() in at for b in GENERIC_BRANDS):
        score += 15
    
    # Penalties
    if "assorted" in st or "assorted" in at:
        score -= 20
        
    return min(100, max(0, int(score)))

df['MLS'] = df.apply(calculate_mls_row, axis=1)

# ==========================================
# STAGE 6 & 6B: Advanced Pack & Logic Check
# ==========================================
# This function assigns the FINAL Verdict and filtering reason
def analyze_row_final(row):
    verdict = "OTHER"
    reason = ""
    confidence = row['MLS'] # Default
    final_profit = row['Adjusted_Profit']
    pack_verdict = f"1:1 Match" if row['Qty_Ratio'] == 1 else f"Mismatch {row['Qty_Ratio']:.1f}"
    
    st = str(row.get('SupplierTitle', '')).lower()
    at = str(row.get('AmazonTitle', '')).lower()
    
    # 1. Dimension Shield
    # Check for dimension patterns (9 x 9, 30cm, etc)
    # Regex for "number x number"
    dim_regex = r'\d+\s*[xX]\s*\d+'
    has_dim_st = re.search(dim_regex, st)
    has_dim_at = re.search(dim_regex, at)
    
    # Check for measurements
    meas_regex = r'\d+\s*(cm|mm|inch|in|ml|l|g|kg|oz)\b'
    has_meas_st = re.search(meas_regex, st)
    has_meas_at = re.search(meas_regex, at)
    
    # If dimensions detected and strictly exact EAN -> Override pack logic
    is_dim_trap = (has_dim_st or has_dim_at or has_meas_st or has_meas_at)
    
    if row['is_exact_ean_strict']:
        confidence = 95
        # 6B Logic
        if is_dim_trap:
            # Override pack
            pack_verdict = "1:1 Match (Dim Shield)"
            final_profit = row.get('NetProfit', 0) # Restore profit
            
        # Capacity Tolerance
        # Extract capacity (ml/L)
        cap_regex = r'(\d+)\s*(ml|l)\b'
        s_cap = re.search(cap_regex, st)
        a_cap = re.search(cap_regex, at)
        if s_cap and a_cap and s_cap.group(2) == a_cap.group(2):
            val_s = float(s_cap.group(1))
            val_a = float(a_cap.group(1))
            if val_s > 0:
                diff_pct = abs(val_s - val_a) / val_s
                if 0 < diff_pct < 0.3:
                    verdict = "NEEDS VERIFICATION"
                    reason = f"Capacity variance {diff_pct:.0%} - verify manually"
                    return verdict, reason, confidence, final_profit, pack_verdict
        
        # Final Exact EAN decision
        if final_profit > 0 and row['sales'] > 0:
             verdict = "VERIFIED (Exact EAN)"
        elif final_profit <= 0:
             verdict = "VERIFIED (Filtered Out)"
             reason = "Not Profitable"
        elif row['sales'] == 0:
             # Sales=0
             verdict = "VERIFIED (Filtered Out)" # Actually prompt says Sales=0 w confidence -> Needs Verif?
             # "Sales = 0 with high confidence -> Route to NEEDS VERIFICATION"
             verdict = "NEEDS VERIFICATION" 
             reason = "Exact EAN but Sales=0"
             
    else:
        # Non-EAN Logic
        # Confidence = MLS
        confidence = row['MLS']
        
        if confidence >= 75:
            base_verdict = "HIGH LIKELIHOOD"
        elif confidence >= 50:
            base_verdict = "NEEDS VERIFICATION"
        elif confidence >= 35:
            base_verdict = "POSSIBLE"
        else:
            base_verdict = "OTHER" # UNLIKELY
            
        # Pack check for high confident
        if base_verdict in ["HIGH LIKELIHOOD", "NEEDS VERIFICATION"]:
             # If strictly dimension trap, be lenient
             if is_dim_trap and row['Qty_Ratio'] != 1:
                 # Override
                 pack_verdict = "1:1 Match (Dim Shield)"
                 final_profit = row.get('NetProfit', 0)
        
        # Final Decision
        if base_verdict == "OTHER":
            verdict = "OTHER"
        else:
            if final_profit > 0 and row['sales'] > 0:
                verdict = base_verdict
            elif row['sales'] == 0 and confidence >= 75:
                 verdict = "NEEDS VERIFICATION"
                 reason = "Sales=0 but High Confidence"
            elif final_profit <= 0:
                 if base_verdict == "HIGH LIKELIHOOD":
                    verdict = "HIGH LIKELIHOOD (Filtered Out)"
                    reason = "Profit <= 0"
                 else:
                    verdict = "OTHER" # Drop from needs verification list if not profitable?
                    # Prompt says: "NO ROW MAY APPEAR IN RECOMMENDATION TABLES unless ... NetProfit>0"
                    # Only Audit sections show filtered.
                    # Needs Verification recommendation must be profitable.
                    pass 

    return verdict, reason, confidence, final_profit, pack_verdict

# Apply Analysis
results = []
for idx, row in df.iterrows():
    v, r, conf, fp, pv = analyze_row_final(row)
    results.append({
        "Final_Verdict": v,
        "Risk_Reason": r,
        "Final_Confidence": conf,
        "Final_Adjusted_Profit": fp,
        "Final_Pack_Verdict": pv
    })

df_res = pd.DataFrame(results)
df = pd.concat([df, df_res], axis=1)

# ==========================================
# OUTPUT GENERATION
# ==========================================
# Sort: Non-EAN by MLS desc, Exact-EAN by Sales desc
# We will split dataframes
df_verified = df[df['Final_Verdict'] == "VERIFIED (Exact EAN)"].sort_values('sales', ascending=False)
df_high = df[df['Final_Verdict'] == "HIGH LIKELIHOOD"].sort_values(['MLS', 'sales'], ascending=[False, False])
df_needs = df[df['Final_Verdict'] == "NEEDS VERIFICATION"].sort_values(['MLS', 'sales'], ascending=[False, False])
df_ver_filtered = df[df['Final_Verdict'] == "VERIFIED (Filtered Out)"].sort_values('sales', ascending=False)
df_high_filtered = df[df['Final_Verdict'] == "HIGH LIKELIHOOD (Filtered Out)"].sort_values(['MLS', 'sales'], ascending=[False, False])

# CSV
df.to_csv(OUTPUT_CSV, index=False)
print(f"CSV saved to {OUTPUT_CSV}")

# Markdown Report
def format_row(row):
    return f"| {row['Final_Verdict']} | {row['Final_Confidence']} | {row['SupplierTitle'][:60]} | {row['AmazonTitle'][:60]} | {row['EAN']} | {row['EAN_OnPage']} | {row['ASIN']} | {row.get('SupplierPrice_incVAT',0)} | {row.get('SellingPrice_incVAT',0)} | {row.get('NetProfit',0)} | {row.get('ROI',0)} | {row['sales']} | {row['Final_Pack_Verdict']} | {row['Final_Adjusted_Profit']:.2f} | MLS={row['MLS']} | {row['Risk_Reason']} |"

with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write("# PHASEA MANUAL REPORT\n\n")
    
    # Reconciliation
    counts = df['Final_Verdict'].value_counts()
    f.write("## Reconciliation\n")
    f.write("| Bucket | Count |\n|---|---|\n")
    f.write(f"| Total Input | {len(df)} |\n")
    for k, v in counts.items():
        f.write(f"| {k} | {v} |\n")
    f.write(f"| Sum | {counts.sum()} |\n\n")
    
    # Tables
    sections = [
        ("VERIFIED (Recommended)", df_verified),
        ("HIGH LIKELIHOOD (Recommended)", df_high),
        ("NEEDS VERIFICATION", df_needs),
        ("VERIFIED (Filtered Out)", df_ver_filtered),
        ("HIGH LIKELIHOOD (Filtered Out)", df_high_filtered)
    ]
    
    header = "| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adj Profit | Evidence | Notes |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    
    for title, sub_df in sections:
        f.write(f"## {title}\n")
        f.write(header)
        for _, row in sub_df.head(100).iterrows(): # Cap top 100 for safety in MD
            f.write(format_row(row) + "\n")
        f.write("\n")

print(f"Markdown saved to {OUTPUT_MD}")
