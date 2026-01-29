
import pandas as pd
import re
from difflib import SequenceMatcher
import datetime
import os

# --- PATHS ---
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\part_30_dec.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\fas"
os.makedirs(OUTPUT_DIR, exist_ok=True)
TODAY = datetime.datetime.now().strftime("%Y%m%d")
REPORT_NAME = f"PHASEA_MANUAL_REPORT_{TODAY}.md"
REPORT_PATH = os.path.join(OUTPUT_DIR, REPORT_NAME)

# --- UTILS ---

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
        try:
           s = "{:.0f}".format(float(s))
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
    total = sum(d * (3 if i % 2 == 1 else 1) for i, d in enumerate(body_rev, start=1))
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
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r'0{6,}$', normalized):
        return False
    return gtin_checksum_ok(normalized)

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

MEASUREMENT_UNITS = ['cm', 'mm', 'inch', 'in', 'm', 'ft', 'ml', 'l', 'g', 'kg', 'oz']
DIMENSION_PATTERN = re.compile(r'(\d+(\.\d+)?\s*[xX*]\s*\d+(\.\d+)?(\s*[xX*]\s*\d+(\.\d+)?)?)\s*(' + '|'.join(MEASUREMENT_UNITS) + r')\b', re.IGNORECASE)

def extract_quantity(title):
    if pd.isna(title):
        return 1.0
    title = str(title).lower()
    clean_title = DIMENSION_PATTERN.sub('', title)
    
    # Check for "Nx" or "N x" at start
    start_match = re.match(r'^(\d+)\s*x\b', title)
    if start_match:
        return float(start_match.group(1))

    # Pack of N, N pack, etc.
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*pairs?\b',
        r'(\d+)\s*rolls?\b',
    ]
    for pat in patterns:
        match = re.search(pat, clean_title)
        if match:
            qty = float(match.group(1))
            if 1 < qty < 500: return qty
            
    # Look for (N) at end of title
    end_match = re.search(r'\((\d+)\)$', title)
    if end_match:
        return float(end_match.group(1))

    return 1.0

KNOWN_BRANDS = ["AMTECH", "ROLSON", "MASON CASH", "PYREX", "TIDYZ", "EXTRASTAR", "FAIRY", "DETTOL", "MARIGOLD", "DUNLOP", "EVERBUILD", "HARRIS", "STATUS", "ROUNDUP", "LITTLE TREES"]

def get_brand_match(t1, t2):
    t1, t2 = str(t1).upper(), str(t2).upper()
    for b in KNOWN_BRANDS:
        if b in t1 and b in t2:
            return b
    # fallback to first word comparison if long enough
    w1 = t1.split()[0] if t1.split() else ""
    w2 = t2.split()[0] if t2.split() else ""
    if len(w1) > 3 and w1 == w2:
        return w1
    return None

def get_product_type_match(t1, t2):
    t1, t2 = str(t1).lower(), str(t2).lower()
    common_types = ["trowel", "hammer", "bowl", "brush", "candle", "knife", "saw", "tape", "box", "bag", "mirror", "torch", "lead", "socket"]
    matches = []
    for ct in common_types:
        if ct in t1 and ct in t2:
            matches.append(ct)
    return matches[0] if matches else None

# --- MAIN ANALYSIS ---

print("Loading data...")
df = pd.read_excel(INPUT_PATH)
df['RowID'] = df.index + 1

# Clean/Normalize EANs
df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
df['EAN_norm'] = df['EAN_digits'].apply(normalize_ean)
df['EAN_OnPage_norm'] = df['EAN_OnPage_digits'].apply(normalize_ean)
df['is_exact_ean_strict'] = (
    df['EAN_norm'].apply(is_strict_valid_barcode) &
    df['EAN_OnPage_norm'].apply(is_strict_valid_barcode) &
    (df['EAN_norm'] == df['EAN_OnPage_norm'])
)

# Sales Normalization
def clean_sales(x):
    if pd.isna(x): return 0
    s = str(x).lower().replace('+', '').replace(',', '')
    if 'k' in s:
        try:
            return float(s.replace('k', '')) * 1000
        except: return 0
    match = re.search(r'(\d+)', s)
    return int(match.group(1)) if match else 0

df['sales'] = df['bought_in_past_month'].apply(clean_sales)

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']

def recalculate_profit(row):
    try:
        original_profit = float(row['NetProfit'])
        cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        # If ratio > 1, we need more units
        return original_profit - (cost * (ratio - 1))
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

def categorize_row_v4(row):
    brand = get_brand_match(row['SupplierTitle'], row['AmazonTitle'])
    p_type = get_product_type_match(row['SupplierTitle'], row['AmazonTitle'])
    title_sim = title_similarity(row['SupplierTitle'], row['AmazonTitle'])
    
    # 1. VERIFIED (Exact EAN) - Highest Priority
    if row['is_exact_ean_strict']:
        if row['Adjusted_Profit'] > 0:
             # Check for explicit pack mismatch word-based
             if row['Qty_Ratio'] != 1.0:
                 return 'VERIFIED_FILTERED' # Mismatch in pack count
             return 'VERIFIED'
        else:
             return 'VERIFIED_FILTERED' # Negative profit

    # 2. HIGHLY LIKELY (Brand + Product Match)
    if brand and p_type and row['Adjusted_Profit'] > 0 and row['sales'] > 0:
        return 'HIGHLY_LIKELY'
    
    # Needs Verification selectivity
    if row['Adjusted_Profit'] > 0:
        if (brand or p_type) and (title_sim > 0.4 or row['sales'] > 0):
             # Highly selective: only items where confirmation would upgrade
             return 'NEEDS_VERIFICATION'
        
    # 3. FILTERED OUT (Confirmed match but unprofitable/mismatch)
    if (brand and p_type) or row['is_exact_ean_strict']:
        if row['Adjusted_Profit'] <= 0 or row['Qty_Ratio'] != 1.0:
            return 'FILTERED_OUT'

    return 'DROP'

df['Verdict_Category'] = df.apply(categorize_row_v4, axis=1)

def map_to_table(row):
    v = row['Verdict_Category']
    verdict = v.replace('_FILTERED', '').replace('_', ' ')
    conf = 95 if row['is_exact_ean_strict'] else int(title_similarity(row['SupplierTitle'], row['AmazonTitle']) * 100)
    
    pack_v = "1:1 Match" if row['Qty_Ratio'] == 1.0 else f"Ratio {row['Qty_Ratio']:.1f}"
    if DIMENSION_PATTERN.search(str(row['AmazonTitle'])):
        pack_v += " (Dim Shield)"
    
    brand = get_brand_match(row['SupplierTitle'], row['AmazonTitle'])
    p_type = get_product_type_match(row['SupplierTitle'], row['AmazonTitle'])
    
    evidence = []
    if row['is_exact_ean_strict']: evidence.append("Strict Exact EAN Match")
    if brand: evidence.append(f"Brand Match ({brand})")
    if p_type: evidence.append(f"Product Type Match ({p_type})")
    if not evidence: evidence.append(f"Title Sim {conf}%")
    
    reason = "-"
    if "FILTERED" in v or v == "FILTERED_OUT":
        if row['Adjusted_Profit'] <= 0:
            reason = f"Unprofitable after pack adj (£{row['Adjusted_Profit']:.2f})"
        elif row['Qty_Ratio'] != 1.0:
            reason = f"Confirmed mismatch: Ratio {row['Qty_Ratio']:.1f}"
            
    return pd.Series({
        'Verdict': verdict,
        'Confidence': conf,
        'SupplierTitle': str(row['SupplierTitle'])[:60],
        'AmazonTitle': str(row['AmazonTitle'])[:60],
        'Supplier EAN': row['EAN_norm'] if row['EAN_norm'] != "" else "-",
        'Amazon EAN': row['EAN_OnPage_norm'] if row['EAN_OnPage_norm'] != "" else "-",
        'ASIN': row['ASIN'],
        'SupplierPrice': f"£{row['SupplierPrice_incVAT']:.2f}",
        'SellingPrice': f"£{row['SellingPrice_incVAT']:.2f}",
        'NetProfit': f"£{row['NetProfit']:.2f}",
        'ROI': f"{row['ROI']:.1f}%", # Fix ROI formatting
        'Sales': int(row['sales']),
        'Pack Verdict': pack_v,
        'Adjusted Profit': f"£{row['Adjusted_Profit']:.2f}",
        'Key Match Evidence': "; ".join(evidence),
        'Filter Reason': reason
    })

report_df = df[df['Verdict_Category'] != 'DROP'].apply(map_to_table, axis=1)

# Format for table
def format_table(data, columns):
    if data.empty: return "No items in this category."
    df_table = data[columns].copy()
    widths = {col: max(df_table[col].astype(str).apply(len).max(), len(col)) for col in columns}
    header = "| " + " | ".join([col.ljust(widths[col]) for col in columns]) + " |"
    separator = "|-" + "-|-".join(["-" * widths[col] for col in columns]) + "-|"
    rows = ["| " + " | ".join([str(row[col]).ljust(widths[col]) for col in columns]) + " |" for _, row in df_table.iterrows()]
    return "\n".join([header, separator] + rows)

table_cols = ['Verdict', 'Confidence', 'SupplierTitle', 'AmazonTitle', 'Supplier EAN', 'Amazon EAN', 'ASIN', 'SupplierPrice', 'SellingPrice', 'NetProfit', 'ROI', 'Sales', 'Pack Verdict', 'Adjusted Profit', 'Key Match Evidence', 'Filter Reason']

v_rec = report_df[(report_df['Verdict'] == 'VERIFIED') & (report_df['Filter Reason'] == '-')]
v_fil = report_df[(report_df['Verdict'] == 'VERIFIED') & (report_df['Filter Reason'] != '-')]
hl_rec = report_df[report_df['Verdict'] == 'HIGHLY LIKELY']
nv_rec = report_df[report_df['Verdict'] == 'NEEDS VERIFICATION']
fo_rec = report_df[report_df['Verdict'] == 'FILTERED OUT']

summary = f"""# PHASEA MANUAL REPORT

**Generated:** {TODAY}
**Input File:** {INPUT_PATH}

## Summary Counts
- VERIFIED — RECOMMENDED: {len(v_rec)}
- VERIFIED — FILTERED OUT / EXCLUDED: {len(v_fil)}
- HIGHLY LIKELY — RECOMMENDED: {len(hl_rec)}
- NEEDS VERIFICATION: {len(nv_rec)}
- FILTERED OUT (Confirmed Matches): {len(fo_rec)}
- TOTAL ANALYZED: {len(report_df)}

This report applies v4.0 Thorough Manual Analysis.

## VERIFIED — RECOMMENDED (count={len(v_rec)})
```text
{format_table(v_rec, table_cols)}
```

## VERIFIED — FILTERED OUT / EXCLUDED (count={len(v_fil)})
```text
{format_table(v_fil, table_cols)}
```

## HIGHLY LIKELY — RECOMMENDED (count={len(hl_rec)})
```text
{format_table(hl_rec, table_cols)}
```

## NEEDS VERIFICATION (count={len(nv_rec)})
```text
{format_table(nv_rec, table_cols)}
```

## FILTERED OUT
```text
{format_table(fo_rec, table_cols)}
```

## Reconciliation
- Total rows in input: {len(df)}
- Rows analyzed and categorized: {len(report_df)}

---
*Generated by Antigravity v4.0*
"""

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(summary)
print(f"Report final version generated at: {REPORT_PATH}")
