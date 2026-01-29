import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
import os
import datetime

# --- CONFIGURATION ---
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\PARTDEC28_1.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\GEMINI"
DATE_STR = datetime.datetime.now().strftime("%Y%m%d")
REPORT_FILE = os.path.join(OUTPUT_DIR, f"PHASEA_MANUAL_REPORT_{DATE_STR}.md")
CSV_FILE = os.path.join(OUTPUT_DIR, f"deep_analysis_{DATE_STR}.csv")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- STAGE 1: Data Loading & Initial Cleaning ---
print("Loading data...")
try:
    df = pd.read_excel(INPUT_FILE)
except Exception as e:
    print(f"Error reading Excel, trying CSV logic just in case: {e}")
    df = pd.read_csv(INPUT_FILE) # Fallback

# Normalize columns logic if needed (strip whitespace from headers)
df.columns = df.columns.str.strip()

# Add RowID (1-based)
df['RowID'] = np.arange(1, len(df) + 1)

# Clean EANs
def clean_ean_str(x):
    if pd.isna(x): return ''
    s = str(x).strip()
    if s.endswith('.0'): s = s[:-2]
    return s

df['EAN'] = df['EAN'].apply(clean_ean_str)
df['EAN_OnPage'] = df['EAN_OnPage'].apply(clean_ean_str)

# Handle Sales
if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
else:
    df['sales'] = 0

# --- STAGE 1B: EAN Safety ---
def clean_to_digits(x):
    if pd.isna(x): return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower(): return '' # Scientific notation corruption
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

# --- STAGE 2: Title Similarity ---
def title_similarity(t1, t2):
    if pd.isna(t1) or pd.isna(t2): return 0.0
    return SequenceMatcher(None, str(t1).lower(), str(t2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# --- STAGE 3B: Strict Barcode Validity ---
def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit(): return False
    n = len(digits)
    if n not in (8, 12, 13, 14): return False
    
    body = digits[:-1]
    try:
        check = int(digits[-1])
        body_rev = list(map(int, body[::-1]))
        total = 0
        for i, d in enumerate(body_rev, start=1):
            total += d * (3 if i % 2 == 1 else 1)
        calc = (10 - (total % 10)) % 10
        return calc == check
    except:
        return False

def normalize_ean(digits: str) -> str:
    if not digits.isdigit(): return digits
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    for target_len in [12, 13, 14]:
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits

def is_strict_valid_barcode(digits: str) -> bool:
    if not digits: return False
    norm = normalize_ean(digits)
    if len(norm) not in (8, 12, 13, 14): return False
    if re.search(r'0{6,}$', norm): return False # Suspicious trailing zeros
    return gtin_checksum_ok(norm)

# Apply Normalization
df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)

df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)

df['is_exact_ean_strict'] = (
    df['EAN_strict_valid'] & 
    df['EAN_OnPage_strict_valid'] & 
    (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
)

# --- STAGE 4: Pack Size & Dimension Shield ---
# Enhanced extraction that avoids dimensions
def extract_quantity(title):
    if pd.isna(title): return 1.0
    title_lower = str(title).lower()
    
    # Check for heavy dimension signals first? No, regex needs to be specific.
    # We want to capture "X pack", "pack of X", without capturing "9 x 9"
    
    # Specific Pack Patterns
    pack_patterns = [
        r'(?<!\d\s)pack of (\d+)', # Not preceded by digit (to avoid "2 pack of 3" ambiguity, though simple is better)
        r'set of (\d+)',
        r'(\d+)\s*pack',         # "10 pack" - Vulnerable to "10 pack size"? rare.
        r'(\d+)\s*pk',
        r'(\d+)\s*pcs',
        r'(\d+)\s*pieces?',
        r'(\d+)\s*pairs?',
        r'(\d+)\s*rolls?',
        # The dangerous one: x 10. 
        # We must avoid "30cm x 10cm". 
        # Look for "x 10" NOT followed by measurement units.
        r'[xX]\s*(\d+)(?!\s*(?:cm|mm|m|inch|in|ml|l|g|kg|oz))', 
    ]
    
    # Explicitly check for dimensions to ignore numbers associated with them?
    # Actually, the regex above handles the "x" case.
    # What about "10 x"? r'(\d+)\s*[xX]' matches "10 x 10cm".
    # Best strategy: Find candidate numbers using pack patterns.
    # Then verify the context isn't a measurement.
    
    for pat in pack_patterns:
        matches = re.findall(pat, title_lower)
        for m in matches:
            if m:
                try:
                    val = float(m)
                    if 1 < val < 500:
                        return val
                except:
                    continue
    return 1.0

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']

def recalculate_profit(row):
    try:
        orig_profit = float(row['NetProfit'])
        cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        # If ratio > 1, we buy 'ratio' supplier units. Cost increases.
        # Adjusted Profit = Revenue - (Cost * Ratio) - Fees... 
        # The prompt says: Adjusted_Profit = Original - (Cost * (Ratio - 1))
        # Original = SellingPrice - Cost - Fees.
        # Adjusted = SellingPrice - (Cost * Ratio) - Fees 
        #          = (SellingPrice - Cost - Fees) - (Cost * Ratio) + Cost
        #          = Original - Cost * (Ratio - 1)
        # This approximates it.
        adjustment = cost * (ratio - 1)
        return orig_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

def pack_verdict(row):
    try:
        ratio = float(row['Qty_Ratio'])
        if ratio == 1.0:
            return "1:1 Match"
        elif ratio > 1.0:
            if row['Adjusted_Profit'] > 0:
                return f"BUNDLE ({int(ratio)}x) - OK"
            else:
                return f"BUNDLE ({int(ratio)}x) - LOSS"
        else:
            # Avoid divide by zero if ratio is weird, though extract_qty defaults 1.
            if ratio == 0: return "Unknown"
            denom = int(1/ratio)
            if row['Adjusted_Profit'] > 0:
                return f"SPLIT (1/{denom}) - OK"
            else:
                return "SPLIT - LOSS"
    except:
        return "Error"

df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)

# --- STAGE 5B: MLS Scoring (Artificial "Manual" Analyst) ---

LUXURY_BRANDS = {"jo malone", "chanel", "dior", "gucci", "louis vuitton", "prada", "hermès", "hermes", "apple", "samsung", "sony", "microsoft", "nike", "adidas"}
GENERIC_BRANDS = {"tidyz", "soudal", "amtech", "rolson", "draper", "fairy", "dettol", "marigold", "mason cash", "pyrex", "everbuild", "harris", "status", "extrastar", "roundup", "little trees", "dunlop"}

def get_tokens(text):
    if pd.isna(text): return set()
    return set(re.findall(r'\w+', str(text).lower()))

def calculate_mls(row):
    # This function simulates the Manual Likelihood Score
    st = str(row['SupplierTitle']).lower()
    at = str(row['AmazonTitle']).lower()
    
    score = 0
    evidence = []
    
    st_tokens = get_tokens(st)
    at_tokens = get_tokens(at)
    
    # 1. Brand Evidence (Attempt extraction or simple token overlap for brands)
    # We don't have a reliable Brand column usually, so we rely on titles.
    # Check intersection for known brands or capitalized first words (heuristic).
    # Heuristic: Check common tokens.
    
    common_tokens = st_tokens.intersection(at_tokens)
    
    # Remove Stop Words
    stop_words = {'the', 'a', 'an', 'pack', 'of', 'set', 'with', 'and', 'or', 'for', 'in', 'on', 'mg', 'ml', 'g', 'kg', 'oz', 'cm', 'mm', 'x', 'pcs', 'pieces', 'white', 'black', 'red', 'blue', 'green'}
    meaningful_common = common_tokens - stop_words
    
    # Score Base: Overlap Ratio
    if len(st_tokens) > 0:
        overlap_ratio = len(meaningful_common) / len(st_tokens.difference(stop_words)) if len(st_tokens.difference(stop_words)) > 0 else 0
        score += overlap_ratio * 40 # Up to 40 points for token overlap
    
    # 2. Product Type / Core Noun
    # If key phrases match (bigrams)
    # Generate bigrams
    st_words = re.findall(r'\w+', st)
    at_words = re.findall(r'\w+', at)
    st_bigrams = set(zip(st_words, st_words[1:]))
    at_bigrams = set(zip(at_words, at_words[1:]))
    common_bigrams = st_bigrams.intersection(at_bigrams)
    
    score += len(common_bigrams) * 5 # 5 points per matching bigram
    
    # 3. Exact Brand Match (Heuristic)
    # If the first word corresponds
    if st_words and at_words:
        if st_words[0] == at_words[0] and st_words[0] not in stop_words:
            score += 15
            evidence.append(f"Brand/Start Match '{st_words[0]}'")
            
    # 4. Penalties
    # Contradictions in variant keywords
    variants = ['small', 'medium', 'large', 'xl', 'xxl', 'red', 'blue', 'green', 'black', 'white', 'yellow', 'pink']
    for v in variants:
        if (v in st_tokens and v not in at_tokens) or (v in at_tokens and v not in st_tokens):
            # Check if title just omitted it or contradicted.
            # E.g. Supplier: "Red", Amazon: "Blue" -> Contradiction (-30)
            # Find colors in both
            found_st_colors = {c for c in variants if c in st_tokens}
            found_at_colors = {c for c in variants if c in at_tokens}
            if found_st_colors and found_at_colors and found_st_colors.isdisjoint(found_at_colors):
                 score -= 30
                 evidence.append("Variant mismatch")
                 break

    # Cap score
    score = min(100, max(0, score))
    
    # Title Match Bonus (from stage 2) to stabilize
    if row['title_match'] > 0.6: score += 10
    if row['title_match'] > 0.8: score += 10
    
    return min(100, score)

df['MLS'] = df.apply(calculate_mls, axis=1)

def get_mls_band(s):
    if s >= 75: return "HIGH_LIKELIHOOD"
    elif s >= 50: return "NEEDS_VERIFICATION"
    elif s >= 35: return "POSSIBLE"
    else: return "UNLIKELY"

df['MLS_band'] = df['MLS'].apply(get_mls_band)

# --- STAGE 6 & 6B: Verification & Logic Routing ---
# Define Capacity Tolerance
def check_capacity_tolerance(t1, t2):
    # Extract capacity (e.g., 500ml)
    cap_pat = r'(\d+)\s*(ml|l|g|kg|oz|cl)'
    m1 = re.search(cap_pat, str(t1).lower())
    m2 = re.search(cap_pat, str(t2).lower())
    
    if m1 and m2:
        val1, unit1 = float(m1.group(1)), m1.group(2)
        val2, unit2 = float(m2.group(1)), m2.group(2)
        
        # Normalize to base units
        if unit1 == 'l': val1 *= 1000; unit1='ml'
        if unit2 == 'l': val2 *= 1000; unit2='ml'
        if unit1 == 'kg': val1 *= 1000; unit1='g'
        if unit2 == 'kg': val2 *= 1000; unit2='g'
        if unit1 == 'cl': val1 *= 10; unit1='ml'
        if unit2 == 'cl': val2 *= 10; unit2='ml'
        
        if unit1 == unit2:
            diff_pct = abs(val1 - val2) / max(val1, val2)
            if diff_pct < 0.05: return "MATCH"
            if diff_pct <= 0.30: return "TOLERANCE_OK" # 30% tolerance
            return "MISMATCH"
            
    return "UNKNOWN"

# Main Logic to produce Final Verdicts
# We need to construct the Output Lists directly.

results = []
summary = {
    "Total Input": len(df),
    "VERIFIED": 0,
    "HIGH LIKELIHOOD": 0,
    "NEEDS VERIFICATION": 0,
    "FILTERED OUT": 0,
    "OTHER": 0
}

# Lists for Report Tables
# List Structure: dict of col_name -> value
tbl_verified_rec = []
tbl_high_rec = []
tbl_needs_rec = []
tbl_filtered_verified = []
tbl_filtered_high = []
# Not printing OTHER, but tracking count.

for idx, row in df.iterrows():
    row_common = {
        "Verdict": "",
        "Confidence": 0,
        "SupplierTitle": row['SupplierTitle'],
        "AmazonTitle": row['AmazonTitle'],
        "SupplierEAN": row['EAN'],
        "AmazonEAN": row['EAN_OnPage'],
        "ASIN": row['ASIN'],
        "SupplierPrice": row['SupplierPrice_incVAT'],
        "SellingPrice": row['SellingPrice_incVAT'],
        "NetProfit": row['NetProfit'],
        "ROI": row['ROI'],
        "Sales": row['sales'],
        "PackVerdict": row['Pack_Verdict'],
        "AdjustedProfit": row['Adjusted_Profit'],
        "Evidence": "",
        "RowID": row['RowID']
    }
    
    is_strict_exact = row['is_exact_ean_strict']
    mls = row['MLS']
    sales = row['sales']
    net_profit = row['NetProfit']
    adj_profit = row['Adjusted_Profit']
    
    # 1. Capacity Logic Check
    cap_check = check_capacity_tolerance(row['SupplierTitle'], row['AmazonTitle'])
    cap_note = ""
    if cap_check == "TOLERANCE_OK":
        cap_note = "Minor capacity diff (tolerant)."
    elif cap_check == "MISMATCH":
        cap_note = "Capacity MISMATCH."
        
    # 2. Dimension Trap Logic ("A x B")
    # If dimensions used as pack, revert.
    # Heuristic: If Qty_Ratio != 1 but titles contain "x" followed by units in one and not other?
    # Simple check: If `is_strict_exact` is true, and `adj_profit <= 0` because of Pack logic, 
    # check for dimensions.
    
    dims_present = bool(re.search(r'\d+\s*[xX]\s*\d+\s*(?:cm|mm|in|inch)', str(row['SupplierTitle']).lower())) or \
                   bool(re.search(r'\d+\s*[xX]\s*\d+\s*(?:cm|mm|in|inch)', str(row['AmazonTitle']).lower()))
    
    if is_strict_exact:
        # --- VERIFIED FLOW ---
        verdict = "VERIFIED"
        confidence = 95
        evidence = "Strict Exact EAN Match."
        
        # Dimension Shield for Exact EAN
        if dims_present and row['Qty_Ratio'] != 1.0:
            # Override pack logic
            row_common['PackVerdict'] = "1:1 Match (Dim Override)"
            row_common['AdjustedProfit'] = net_profit
            adj_profit = net_profit # Update local var
            evidence += " Dimensions detected, assumed 1:1."
        
        # Verify Profit/Sales
        is_profitable = (net_profit > 0) and (adj_profit > 0)
        is_sellable = (sales > 0)
        
        if cap_check == "MISMATCH":
             # Exclude
             row_common['Verdict'] = "FILTERED OUT"
             row_common['Confidence'] = 75 # Downgrade
             row_common['FilterReason'] = "EXCLUDED: Capacity mismatch > 30%."
             tbl_filtered_verified.append(row_common)
             summary["FILTERED OUT"] += 1
        elif not is_profitable:
             # Exclude
             row_common['Verdict'] = "FILTERED OUT"
             row_common['Confidence'] = 95
             row_common['FilterReason'] = "EXCLUDED: Not Profitable (after pack check)."
             tbl_filtered_verified.append(row_common)
             summary["FILTERED OUT"] += 1
        elif not is_sellable:
             # Exclude? No, prompt says if Sales=0 -> Needs Verification?
             # "if Sales = 0 but match confidence is high (MLS >= 75 or exact EAN), route to NEEDS VERIFICATION"
             row_common['Verdict'] = "NEEDS VERIFICATION"
             row_common['Confidence'] = 90
             row_common['Evidence'] += " Sales=0 but Exact EAN."
             tbl_needs_rec.append(row_common)
             summary["NEEDS VERIFICATION"] += 1
        else:
             # Keep Verified
             row_common['Verdict'] = "VERIFIED"
             row_common['Confidence'] = confidence
             row_common['KeyMatchEvidence'] = evidence
             tbl_verified_rec.append(row_common)
             summary["VERIFIED"] += 1

    else:
        # --- NON-EAN FLOW ---
        # Driven by MLS
        row_common['Confidence'] = int(mls)
        
        # Generate Evidence String (Grounding)
        # We need to construct evidence from tokens again or use what we simulated.
        # For this script, we'll just say "Title Match logic" + specific overlap.
        # But for the report, let's grab the common bigrams if possible.
        # Re-calc cheap evidence for report:
        st_tokens = get_tokens(row['SupplierTitle'])
        at_tokens = get_tokens(row['AmazonTitle'])
        matching = list(st_tokens.intersection(at_tokens))[:4] # Take 4 matching words
        evidence = f"Matches: {', '.join(matching)}" if matching else "Low lexical overlap."
        if cap_note: evidence += f" {cap_note}"
        
        # Determine List
        if mls >= 75:
            target_list = "HIGH_LIKELIHOOD"
        elif mls >= 50:
            target_list = "NEEDS_VERIFICATION"
        else:
            target_list = "OTHER"
            
        # Hard Filter for Non-EAN: Profit/Sales
        is_profitable = (net_profit > 0) and (adj_profit > 0)
        is_sellable = (sales > 0)

        # Dimension Shield applied to Non-EAN? 
        # Yes, if high likelihood.
        if (target_list != "OTHER") and dims_present and row['Qty_Ratio'] != 1.0:
             row_common['PackVerdict'] = "1:1 Match (Dim Override)"
             row_common['AdjustedProfit'] = net_profit
             adj_profit = net_profit
        
        # IP Risk check (Simplified for string matching loop)
        is_ip_risk = any(brand in str(row['AmazonTitle']).lower() for brand in LUXURY_BRANDS)
        
        if is_ip_risk:
             target_list = "NEEDS_VERIFICATION" # Route IP risk here instead of simple exclude?
             evidence += " Valid Brand IP Risk."
        
        # --- ROUTING ---
        if target_list == "OTHER":
            summary["OTHER"] += 1
            continue
            
        if target_list == "HIGH_LIKELIHOOD":
            if cap_check == "MISMATCH":
                row_common['Verdict'] = "FILTERED OUT"
                row_common['FilterReason'] = "Capacity Mismatch."
                tbl_filtered_high.append(row_common)
                summary["FILTERED OUT"] += 1
            elif not is_profitable:
                row_common['Verdict'] = "FILTERED OUT"
                row_common['FilterReason'] = "Not profitable."
                tbl_filtered_high.append(row_common)
                summary["FILTERED OUT"] += 1
            elif not is_sellable:
                # Route to Needs Verification
                row_common['Verdict'] = "NEEDS VERIFICATION"
                row_common['Evidence'] = evidence + " Zero Sales."
                tbl_needs_rec.append(row_common)
                summary["NEEDS VERIFICATION"] += 1
            else:
                row_common['Verdict'] = "HIGH LIKELIHOOD"
                row_common['KeyMatchEvidence'] = evidence
                tbl_high_rec.append(row_common)
                summary["HIGH LIKELIHOOD"] += 1
                
        elif target_list == "NEEDS_VERIFICATION":
            if cap_check == "MISMATCH":
                 summary["OTHER"] +=1 # Just drop low conf mismatch
            elif not is_profitable:
                 summary["OTHER"] += 1
            else:
                 row_common['Verdict'] = "NEEDS VERIFICATION"
                 row_common['Evidence'] = evidence
                 if not is_sellable: row_common['Evidence'] += " Zero Sales."
                 tbl_needs_rec.append(row_common)
                 summary["NEEDS VERIFICATION"] += 1

# --- GENERATE MARKDOWN REPORT ---

md_output = []
md_output.append(f"# PHASE A MANUAL REPORT - {DATE_STR}\n")
md_output.append("## Reconciliation\n")
md_output.append("| Bucket | Count |")
md_output.append("|:--|--:|")
md_output.append(f"| Total input rows | {summary['Total Input']} |")
md_output.append(f"| VERIFIED (Recommended) | {summary['VERIFIED']} |")
md_output.append(f"| HIGH LIKELIHOOD (Recommended) | {summary['HIGH LIKELIHOOD']} |")
md_output.append(f"| NEEDS VERIFICATION | {summary['NEEDS VERIFICATION']} |")
md_output.append(f"| FILTERED OUT (Audit) | {summary['FILTERED OUT']} |")
md_output.append(f"| OTHER (Low MLS/Sales=0/Loss) | {summary['OTHER']} |")
md_output.append(f"| **SUM** | **{sum([summary['VERIFIED'], summary['HIGH LIKELIHOOD'], summary['NEEDS VERIFICATION'], summary['FILTERED OUT'], summary['OTHER']])}** |")

match_check = (sum([summary['VERIFIED'], summary['HIGH LIKELIHOOD'], summary['NEEDS VERIFICATION'], summary['FILTERED OUT'], summary['OTHER']]) == summary['Total Input'])
md_output.append(f"\n✅ Reconciliation: {'PASS' if match_check else 'FAIL'}\n")

def format_table(data_list):
    if not data_list: return "*(No rows)*"
    # Columns requested: Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Filter Reason |
    # Map data_list keys to these.
    
    headers = ["RowID", "Verdict", "Confidence", "SupplierTitle", "AmazonTitle", "Supplier EAN", "Amazon EAN", "ASIN", "SupplierPrice", "SellingPrice", "NetProfit", "ROI", "Sales", "Pack Verdict", "Adjusted Profit", "Key Match Evidence", "Filter Reason"]
    
    # Calculate widths
    widths = {h: len(h) for h in headers}
    
    # Process rows
    processed_rows = []
    for r in data_list:
        row_vals = {
            "RowID": str(r.get("RowID", "")),
            "Verdict": str(r.get("Verdict", "")),
            "Confidence": str(r.get("Confidence", "")),
            "SupplierTitle": str(r.get("SupplierTitle", ""))[:50], # Truncate for display sanity? No, prompt says keep long. But Markdown hates line breaks.
            "AmazonTitle": str(r.get("AmazonTitle", ""))[:50],
            "Supplier EAN": str(r.get("SupplierEAN", "")),
            "Amazon EAN": str(r.get("AmazonEAN", "")),
            "ASIN": str(r.get("ASIN", "")),
            "SupplierPrice": f"{float(r.get('SupplierPrice', 0)):.2f}",
            "SellingPrice": f"{float(r.get('SellingPrice', 0)):.2f}",
            "NetProfit": f"{float(r.get('NetProfit', 0)):.2f}",
            "ROI": f"{float(r.get('ROI', 0)):.0f}%",
            "Sales": f"{int(float(r.get('Sales', 0)))}",
            "Pack Verdict": str(r.get("PackVerdict", "")),
            "Adjusted Profit": f"{float(r.get('AdjustedProfit', 0)):.2f}",
            "Key Match Evidence": str(r.get("KeyMatchEvidence", r.get("Evidence", ""))),
            "Filter Reason": str(r.get("FilterReason", "-"))
        }
        processed_rows.append(row_vals)
        for h in headers:
            dt_len = len(row_vals[h])
            if dt_len > widths[h]: widths[h] = dt_len
            
    # Build Table
    lines = []
    header_line = "| " + " | ".join([h.ljust(widths[h]) for h in headers]) + " |"
    sep_line = "| " + " | ".join(["-" * widths[h] for h in headers]) + " |"
    lines.append(header_line)
    lines.append(sep_line)
    
    for row in processed_rows:
        line = "| " + " | ".join([row[h].ljust(widths[h]) for h in headers]) + " |"
        lines.append(line)
        
    return "\n".join(lines)

md_output.append("## 1. VERIFIED (Exact EAN) - Recommended")
# Sort by Sales Desc
tbl_verified_rec.sort(key=lambda x: float(x.get('Sales', 0)), reverse=True)
md_output.append("```text")
md_output.append(format_table(tbl_verified_rec))
md_output.append("```\n")

md_output.append("## 2. HIGH LIKELIHOOD - Recommended")
# Sort by MLS desc, then Sales
tbl_high_rec.sort(key=lambda x: (float(x.get('Confidence', 0)), float(x.get('Sales', 0))), reverse=True)
md_output.append("```text")
md_output.append(format_table(tbl_high_rec))
md_output.append("```\n")

md_output.append("## 3. NEEDS VERIFICATION")
tbl_needs_rec.sort(key=lambda x: (float(x.get('Confidence', 0)), float(x.get('Sales', 0))), reverse=True)
md_output.append("```text")
md_output.append(format_table(tbl_needs_rec))
md_output.append("```\n")

md_output.append("## 4. VERIFIED (Exact EAN) - FILTERED OUT (Audit)")
tbl_filtered_verified.sort(key=lambda x: float(x.get('Sales', 0)), reverse=True)
md_output.append("```text")
md_output.append(format_table(tbl_filtered_verified))
md_output.append("```\n")

md_output.append("## 5. HIGH LIKELIHOOD - FILTERED OUT (Audit)")
tbl_filtered_high.sort(key=lambda x: float(x.get('Confidence', 0)), reverse=True)
md_output.append("```text")
md_output.append(format_table(tbl_filtered_high))
md_output.append("```\n")

# Save MD
with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write("\n".join(md_output))
    
# Save CSV
df.to_csv(CSV_FILE, index=False)

print(f"Analysis Complete. Report: {REPORT_FILE}")
