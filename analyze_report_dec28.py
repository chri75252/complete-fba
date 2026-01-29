
import pandas as pd
import re
import os
from difflib import SequenceMatcher
from datetime import datetime

# --- CONFIG ---
INPUT_PATH = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\PARTDEC28_1.xlsx'
OUTPUT_DIR = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\FLASH'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- STAGE 1: Data Loading & Initial Cleaning ---
df = pd.read_excel(INPUT_PATH)

# Clean EAN columns
df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Handle sales column
if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    def clean_sales(val):
        if pd.isna(val): return 0
        s = str(val).lower().replace('+', '').replace('k', '000').strip()
        match = re.search(r'(\d+)', s)
        return int(match.group(1)) if match else 0
    df['sales'] = df['bought_in_past_month'].apply(clean_sales)
else:
    df['sales'] = 0

df['RowID'] = df.index + 1

# --- STAGE 1B: EAN Normalization Safety Flags ---
def clean_to_digits(x):
    if pd.isna(x): return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower(): return ''
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

# --- STAGE 2: Title Similarity Calculation ---
def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2): return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# --- STAGE 3: STRICT EAN Matching ---
def is_valid_ean(ean):
    if pd.isna(ean): return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-']

def is_exact_ean_match(row):
    ean_sup = str(row['EAN']).strip()
    ean_amz = str(row['EAN_OnPage']).strip()
    if not is_valid_ean(ean_sup) or not is_valid_ean(ean_amz): return False
    return ean_sup == ean_amz

df['is_exact_ean'] = df.apply(is_exact_ean_match, axis=1)

# --- STAGE 3B: STRICT BARCODE VALIDITY + CHECKSUM + LEFT-PADDING ---
def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit(): return False
    n = len(digits)
    if n not in (8, 12, 13, 14): return False
    body = digits[:-1]
    check = int(digits[-1])
    body_rev = list(map(int, body[::-1]))
    total = 0
    for i, d in enumerate(body_rev, start=1):
        total += d * (3 if i % 2 == 1 else 1)
    calc = (10 - (total % 10)) % 10
    return calc == check

def normalize_ean(digits: str) -> str:
    if not digits.isdigit(): return digits
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits): return digits
    for target_len in [12, 13, 14]:
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded): return padded
    return digits

def is_strict_valid_barcode(digits: str) -> bool:
    if not isinstance(digits, str): return False
    if not digits.isdigit(): return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14): return False
    if re.search(r'0{6,}$', normalized): return False
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

# --- STAGE 4: Pack Size Extraction ---
def extract_quantity(title):
    if pd.isna(title): return 1.0
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
            if qty > 1 and qty < 500: return qty
    return 1.0

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']

def recalculate_profit(row):
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        adjustment = supplier_cost * (ratio - 1)
        return original_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# --- STAGE 5: Product Categorization ---
def categorize_baseline(row):
    if row['is_exact_ean_strict']: return 'EXACT_EAN_MATCH'
    elif row['title_match'] >= 0.50: return 'HIGH_LIKELIHOOD'
    elif row['title_match'] >= 0.30: return 'MODERATE_CONFIDENCE'
    else: return 'UNCERTAIN'

df['category'] = df.apply(categorize_baseline, axis=1)

def pack_verdict_fn(row):
    if row['Qty_Ratio'] == 1.0: return "1:1 Match"
    elif row['Qty_Ratio'] > 1.0:
        return f"BUNDLE ({int(row['Qty_Ratio'])}x) - {'OK' if row['Adjusted_Profit'] > 0 else 'LOSS'}"
    else:
        try:
            val = int(1/(row['Qty_Ratio'] or 1))
            return f"SPLIT (1/{val}) - {'OK' if row['Adjusted_Profit'] > 0 else 'LOSS'}"
        except:
            return "SPLIT - ERROR"

df['Pack_Verdict'] = df.apply(pack_verdict_fn, axis=1)

# --- STAGE 6B: MANUAL VERIFICATION FOR EXACT-EAN MATCHES (Dimension Shield) ---
def apply_stage_6b(row):
    if not row['is_exact_ean_strict']:
        return row['Pack_Verdict'], row['Adjusted_Profit']
    
    s_title = str(row['SupplierTitle']).lower()
    a_title = str(row['AmazonTitle']).lower()
    
    # Dimension patterns
    dim_units = ['inch', 'in', 'cm', 'mm', 'ml', ' l', ' g ', 'kg', 'oz']
    has_dim = any(unit in s_title or unit in a_title for unit in dim_units)
    has_x = ' x ' in s_title or ' x ' in a_title
    
    # Explicit pack words
    pack_words = ['pack of', 'set of', 'pk', 'pcs', 'piece', 'pair', 'rolls']
    has_pack = any(pw in s_title or pw in a_title for pw in pack_words)
    
    if (has_dim or has_x) and not has_pack:
        # Override to 1:1 if it looks like dimensions only
        return "1:1 Match (Dimension Shield)", row['NetProfit']
    
    return row['Pack_Verdict'], row['Adjusted_Profit']

new_results = df.apply(apply_stage_6b, axis=1)
df['Pack_Verdict'] = [r[0] for r in new_results]
df['Adjusted_Profit'] = [r[1] for r in new_results]

# --- STAGE 5B: MLS Calculation (Automated baseline) ---
def compute_mls(row):
    if row['is_exact_ean_strict']: return 95
    score = row['title_match'] * 70
    s_title = str(row['SupplierTitle']).lower()
    a_title = str(row['AmazonTitle']).lower()
    s_words = s_title.split()
    if s_words and s_words[0] in a_title: score += 15
    nouns = ['pack', 'set', 'bundle', 'pcs', 'piece', 'pair', 'roll', 'bag', 'bottle', 'box']
    for n in nouns:
        if n in s_title and n in a_title: score += 5
    if ('pack' in s_title and 'pack' not in a_title) or ('pack' not in s_title and 'pack' in a_title):
        if row['Qty_Ratio'] == 1.0: score -= 10
    return min(100, max(0, score))

df['MLS'] = df.apply(compute_mls, axis=1)

def get_mls_band(mls):
    if mls >= 75: return 'HIGH LIKELIHOOD'
    elif mls >= 50: return 'NEEDS VERIFICATION'
    elif mls >= 35: return 'POSSIBLE'
    else: return 'UNLIKELY'

df['MLS_band'] = df['MLS'].apply(get_mls_band)

today = datetime.now().strftime('%Y%m%d')
df.to_csv(os.path.join(OUTPUT_DIR, f'deep_analysis_{today}.csv'), index=False)

verified_rec = df[(df['is_exact_ean_strict']) & (df['sales'] > 0) & (df['NetProfit'] > 0)]
high_likelihood_rec = df[(~df['is_exact_ean_strict']) & (df['MLS'] >= 75) & (df['sales'] > 0) & (df['Adjusted_Profit'] > 0)]
needs_verif = df[((df['MLS'] >= 50) & (df['MLS'] < 75)) | ((df['sales'] == 0) & (df['MLS'] >= 75))]

print(f"Total rows: {len(df)}")
print(f"Verified Recommended: {len(verified_rec)}")
print(f"High Likelihood Recommended: {len(high_likelihood_rec)}")
print(f"Needs Verification: {len(needs_verif)}")
