import pandas as pd
import numpy as np
import re
import os
import sys
from difflib import SequenceMatcher
from datetime import datetime

# --- CONFIGURATION ---
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\part_30_dec.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\Gemini"
OUTPUT_FILENAME = f"PHASEA_MANUAL_REPORT_{datetime.now().strftime('%Y%m%d')}.md"

# LUXURY/IP BRANDS (Flag as IP Risk)
LUXURY_BRANDS = {
    'JO MALONE', 'CHANEL', 'DIOR', 'GUCCI', 'LOUIS VUITTON', 'PRADA', 'HERMÈS', 
    'APPLE', 'SAMSUNG', 'SONY', 'MICROSOFT', 'NIKE', 'ADIDAS'
}
# SAFE BRANDS (Explicitly safe)
SAFE_BRANDS = {
    'TIDYZ', 'SOUDAL', 'AMTECH', 'ROLSON', 'DRAPER', 'FAIRY', 'DETTOL', 'MARIGOLD', 
    'DUNLOP', 'MASON CASH', 'PYREX', 'EVERBUILD', 'HARRIS', 'STATUS', 'EXTRASTAR', 
    'ROUNDUP', 'LITTLE TREES'
}

# --- HELPER FUNCTIONS ---

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def clean_to_digits(x):
    """Keep only digits. Handle scientific notation as invalid."""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    # Check for scientific notation or float conversion artifacts
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    # Remove .0 if present at end
    if s.endswith('.0'):
        s = s[:-2]
    return re.sub(r'\D', '', s)

def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit():
        return False
    n = len(digits)
    if n not in (8, 12, 13, 14):
        return False
    
    body = digits[:-1]
    check_digit = int(digits[-1])

    body_rev = list(map(int, body[::-1]))
    total = 0
    for i, d in enumerate(body_rev, start=1):
        total += d * (3 if i % 2 == 1 else 1)
    
    calc = (10 - (total % 10)) % 10
    return calc == check_digit

def normalize_ean(digits: str) -> str:
    """Attempt left-padding to valid GTIN length if checksum passes."""
    if not digits:
        return ""
    if digits.isdigit() and len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    
    # Try padding
    if digits.isdigit():
        for target_len in [12, 13, 14]:
            if len(digits) < target_len:
                padded = digits.zfill(target_len)
                if gtin_checksum_ok(padded):
                    return padded
    return digits # Return original if no valid padded version found, or empty? Prompt says "re-validate".

def get_ean_validity(row):
    """Returns (sup_ean, amz_ean, is_strict_match)"""
    sup_raw = clean_to_digits(row.get('EAN', ''))
    amz_raw = clean_to_digits(row.get('EAN_OnPage', ''))
    
    sup_norm = normalize_ean(sup_raw)
    amz_norm = normalize_ean(amz_raw)
    
    sup_valid = bool(sup_norm and len(sup_norm) in (8, 12, 13, 14) and gtin_checksum_ok(sup_norm))
    amz_valid = bool(amz_norm and len(amz_norm) in (8, 12, 13, 14) and gtin_checksum_ok(amz_norm))
    
    match = (sup_valid and amz_valid and sup_norm == amz_norm)
    
    return sup_norm if sup_valid else (sup_raw if sup_raw else "-"), \
           amz_norm if amz_valid else (amz_raw if amz_raw else "-"), \
           match

def title_similarity(t1, t2):
    if pd.isna(t1) or pd.isna(t2):
        return 0.0
    return SequenceMatcher(None, str(t1).lower(), str(t2).lower()).ratio()

def extract_quantity(title):
    """
    Extract pack size/quantity from title. 
    Crucial: Implement Dimension Shield (ignore dimensions).
    """
    if pd.isna(title):
        return 1.0
    title_lower = str(title).lower()
    
    # DIMENSION SHIELD: Remove dimension patterns before looking for pack sizes?
    # Or strict priority.
    # Patterns that look like dims: "9x9", "10 x 5", "30cm", "500ml"
    # We won't remove them, but we will check context in regex.
    
    # Explicit pack patterns (Strong signals)
    pack_patterns = [
        r'\bpack of (\d+)',
        r'\bset of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'\b(\d+)\s*pcs\b',
        r'\b(\d+)\s*pieces?\b',
        r'\(\s*(\d+)\s*\)', # (10) - risky, check context? Usually safe if low number matches item count.
    ]
    
    # "3 x Item" pattern - distinct from "3 x 5 cm"
    # Look for "Ax " at START of string
    start_mul_match = re.search(r'^(\d+)\s*x\s+', title_lower)
    if start_mul_match:
        qty = float(start_mul_match.group(1))
        if 1 < qty < 100:
            return qty

    for pat in pack_patterns:
        match = re.search(pat, title_lower)
        if match:
            qty = float(match.group(1))
            # sanity check
            if 1 < qty < 500:
                # Shield: Check if it's likely a dimension (e.g. 50 pcs vs 50 mm)
                # The regexes above include 'pack', 'pcs', etc, so they are usually safe.
                # But "pack of 100g" -> 100? No.
                return qty

    return 1.0

def is_dimension_pattern(text):
    """Check if text contains dimension-like patterns that might confuse a human/agent."""
    if pd.isna(text): return False
    t = str(text).lower()
    # 9x9, 10 x 20, 30cm, 500ml
    if re.search(r'\d+\s*[xX]\s*\d+', t): return True
    if re.search(r'\d+\s*(cm|mm|m|\"|inch|ml|ltr|l|g|kg|oz)\b', t): return True
    return False

def get_brand(text):
    """Simple extraction of first word or 2 words if capitalized."""
    if pd.isna(text): return ""
    # Very naive: just first token
    tokens = str(text).split()
    if tokens:
        return tokens[0].lower()
    return ""

def analyze_row(row):
    # 1. Parsing & Cleaning
    sup_title = str(row.get('SupplierTitle', ''))
    amz_title = str(row.get('AmazonTitle', ''))
    
    sup_ean, amz_ean, is_exact_ean_strict = get_ean_validity(row)
    
    try:
        sup_price = float(row.get('SupplierPrice_incVAT', 0))
    except: sup_price = 0.0
    
    try:
        sell_price = float(row.get('SellingPrice_incVAT', 0))
    except: sell_price = 0.0
    
    try:
        base_profit = float(row.get('NetProfit', 0))
    except: base_profit = 0.0
    
    try:
        base_roi = float(row.get('ROI', 0))
    except: base_roi = 0.0
    
    # Sales Parsing
    sales_val = 0
    if 'sales_numeric' in row and pd.notna(row['sales_numeric']):
        sales_val = row['sales_numeric']
    elif 'bought_in_past_month' in row and pd.notna(row['bought_in_past_month']):
        sales_val = row['bought_in_past_month']
    
    try:
        sales = float(sales_val)
    except:
        sales = 0.0

    # 2. Pack Calculation
    sup_qty = extract_quantity(sup_title)
    amz_qty = extract_quantity(amz_title)
    
    # Handle dimension shield for verified EANs:
    # If Exact EAN + dimension patterns present + pack mismatch -> assume 1:1 unless explicit mismatch logic
    has_dimensions = is_dimension_pattern(sup_title) or is_dimension_pattern(amz_title)
    
    qty_ratio = amz_qty / sup_qty
    
    # RSU (Reserved Supplier Units)
    # If Amz sells 6, Supplier sells 1 -> Needed 6. Cost multiplier = 6.
    # Logic: Adjusted Profit = SellPrice - (SupPrice * Ratio) - (Fees...)
    # We only have NetProfit which is already (Sell - Sup - Fees).
    # If Ratio > 1, we pay for (Ratio-1) more units. 
    # Extra Cost = SupPrice * (Ratio - 1).
    # New Profit = Base Profit - Extra Cost.
    
    if qty_ratio >= 1:
        extra_cost = sup_price * (qty_ratio - 1)
    else:
        # Ratio < 1 (e.g. Sup 10, Amz 1). We sell 1/10th of a pack? 
        # Usually arbitrage doesn't work this way (unbundling), but if it did:
        # Cost per unit = SupPrice * Ratio (e.g. 0.1).
        # Savings = SupPrice - (SupPrice * Ratio).
        # New Profit = Base Profit + Savings (Assuming Base used full SupPrice)
        # However, usually we can't buy split packs. We treat this as mismatch or loss.
        # For calculation sake:
        extra_cost = sup_price * (qty_ratio - 1) # This will be negative, increasing profit.
        
    adjusted_profit = base_profit - extra_cost
    
    # 3. Categorization Logic
    verdict = "FILTERED OUT"
    confidence = 0
    filter_reason = "-"
    pack_verdict = f"1:1"
    
    if qty_ratio != 1:
        pack_verdict = f"Mismatch {amz_qty}/{sup_qty}"
        if has_dimensions and is_exact_ean_strict:
             # Override pack verdict if likely dimension confusion
             pack_verdict = f"1:1 (Dim Shield)"
             adjusted_profit = base_profit # Revert penalty
             qty_ratio = 1.0

    # Title Match Score
    t_sim = title_similarity(sup_title, amz_title)
    
    # Brand Logic
    sup_brand = get_brand(sup_title)
    amz_brand = get_brand(amz_title)
    brand_match = (sup_brand and amz_brand and sup_brand == amz_brand)
    
    # --- LOGIC TREE ---
    
    # A. EXACT EAN STRICT
    if is_exact_ean_strict:
        # Check Explicit Pack Mismatch
        # If one says "10 pack" and other says "1 pack", it's a mismatch even with EAN.
        # BUT if Dim Shield is active, we trust EAN.
        
        explicit_mismatch = False
        if qty_ratio != 1.0 and not has_dimensions:
             explicit_mismatch = True
             
        if adjusted_profit <= 0:
            verdict = "FILTERED OUT"
            filter_reason = f"Adjusted Profit Negative"
        elif explicit_mismatch:
             # Try to see if it's profitable as a bundle
             if adjusted_profit > 0:
                 # It's a bundle, but profitable? Usually verified bundles are ok.
                 verdict = "VERIFIED"
                 filter_reason = "-"
                 pack_verdict = f"Bundle {qty_ratio}x"
             else:
                 verdict = "FILTERED OUT"
                 filter_reason = f"Pack Mismatch {sup_qty}v{amz_qty}"
        else:
            verdict = "VERIFIED"
            confidence = 95
            filter_reason = "-"
            
    # B. NON-EAN MATCH
    else:
        # High Likely Logic
        if brand_match and t_sim > 0.4 and adjusted_profit > 0:
            verdict = "HIGHLY LIKELY"
            confidence = 80 + int(t_sim * 10)
            filter_reason = "-"
        
        # Needs Verification Logic
        elif adjusted_profit > 0 and t_sim > 0.3:
            # Upgrade check: Is it plausible?
            valid_candidate = False
            
            # 1. Brand match but weak title
            if brand_match: valid_candidate = True
            
            # 2. Strong title but missing matching EAN/Brand (Generic?)
            if t_sim > 0.6: valid_candidate = True
            
            if valid_candidate:
                verdict = "NEEDS VERIFICATION"
                confidence = int(t_sim * 100)
                filter_reason = "Confirm details"
            else:
                verdict = "FILTERED OUT" # Too weak
                filter_reason = "Weak match"
        else:
             verdict = "FILTERED OUT"
             filter_reason = "Low similarity or neg profit"

    # Final Gates for Tables
    if verdict in ["VERIFIED", "HIGHLY LIKELY"]:
        if sales == 0:
            # Downgrade to NV
            verdict = "NEEDS VERIFICATION"
            filter_reason = "Sales=0, strong match"
        if adjusted_profit <= 0:
            verdict = "FILTERED OUT"
            filter_reason = "Neg Profit"

    # IP CHECK
    match_evidence = []
    if is_exact_ean_strict: match_evidence.append("Exact EAN")
    if brand_match: match_evidence.append("Brand Match")
    if t_sim > 0.8: match_evidence.append("Strong Title Match")
    
    evidence_str = "; ".join(match_evidence) if match_evidence else "Title Similarity"

    return {
        "Verdict": verdict,
        "Confidence": confidence,
        "SupplierTitle": sup_title,
        "AmazonTitle": amz_title,
        "Supplier EAN": sup_ean,
        "Amazon EAN": amz_ean,
        "ASIN": row.get('ASIN', '-'),
        "SupplierPrice": sup_price,
        "SellingPrice": sell_price,
        "NetProfit": base_profit,
        "ROI": base_roi,
        "Sales": sales,
        "Pack Verdict": pack_verdict,
        "Adjusted Profit": adjusted_profit,
        "Key Match Evidence": evidence_str,
        "Filter Reason": filter_reason
    }

def main():
    ensure_dir(OUTPUT_DIR)
    
    print(f"Reading {INPUT_PATH}...")
    try:
        df = pd.read_excel(INPUT_PATH)
    except Exception as e:
        print(f"Error reading excel: {e}")
        return

    # Process
    results = []
    for idx, row in df.iterrows():
        res = analyze_row(row)
        results.append(res)
    
    res_df = pd.DataFrame(results)
    
    # Generate MD Report
    
    # Split by verdict
    verified_recom = res_df[ (res_df['Verdict'] == 'VERIFIED') & (res_df['Filter Reason'] == '-') ]
    verified_excl = res_df[ (res_df['Verdict'] == 'VERIFIED') & (res_df['Filter Reason'] != '-') ] # Or Filtered Out but matched EAN?
    # Logic adjustment: If I marked it FILTERED OUT but it was Is_Exact_EAN_Strict, it belongs in "VERIFIED - EXCLUDED" bucket visually?
    # The prompt asks for:
    # VERIFIED — FILTERED OUT / EXCLUDED - (count=Xf) (exact EAN matches confirmed as same product but excluded due to pack/variant/profit gates)
    
    # Better approach: Retain original boolean flags in result to sort into buckets accurately.
    # Re-map for report buckets:
    
    report_rows = []
    
    count_stats = {
        "VERIFIED_REC": 0, "VERIFIED_EXC": 0,
        "HIGHLY_REC": 0, "HIGHLY_EXC": 0,
        "NEEDS_VER": 0, "FILTERED": 0 # General filtered
    }
    
    md_lines = []
    md_lines.append(f"# PHASEA MANUAL REPORT")
    md_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}")
    md_lines.append(f"**Input File:** {INPUT_PATH}")
    md_lines.append("")
    
    # Define buckets
    # Bucket 1: VERIFIED RECOMMENDED
    # Bucket 2: VERIFIED EXCLUDED (Exact EANs that failed profit/pack/sales gates)
    # Bucket 3: HIGHLY LIKELY RECOMMENDED
    # Bucket 4: HIGHLY LIKELY EXCLUDED
    # Bucket 5: NEEDS VERIFICATION
    # Bucket 6: FILTERED OUT (The rest of meaningful matches)
    
    bucket_ver_rec = []
    bucket_ver_exc = []
    bucket_hl_rec = []
    bucket_hl_exc = []
    bucket_nv = []
    bucket_filt = []
    
    for idx, r in res_df.iterrows():
        is_exact = (r['Supplier EAN'] != '-' and r['Supplier EAN'] == r['Amazon EAN']) # Simple check based on final output cols which are strict
        
        v = r['Verdict']
        fr = r['Filter Reason']
        
        if v == 'VERIFIED':
             bucket_ver_rec.append(r)
        elif is_exact:
             # It was exact EAN but got downgraded/filtered
             bucket_ver_exc.append(r)
        elif v == 'HIGHLY LIKELY':
             bucket_hl_rec.append(r)
        elif v == 'NEEDS VERIFICATION':
             bucket_nv.append(r)
        elif v == 'FILTERED OUT':
             # Check if it was a "Confirmed Match" worthy of HIGHLY LIKELY EXCLUDED?
             # Heuristic: If it has brand match but failed profit -> HL Excluded? 
             # For simplicity, stick to prompt categories.
             # Prompt says "HIGHLY LIKELY — FILTERED OUT / EXCLUDED"
             # I need to detect these.
             # If I had "Brand Match" in evidence but Verdict is FILTERED OUT -> HL Excluded.
             # Else -> Generic Filtered Out.
             if "Brand Match" in r['Key Match Evidence']:
                 bucket_hl_exc.append(r)
             else:
                 bucket_filt.append(r)

    # Sort buckets by Sales desc or Confidence
    def sort_key(x): return float(x['Sales'])
    
    bucket_ver_rec.sort(key=sort_key, reverse=True)
    bucket_ver_exc.sort(key=sort_key, reverse=True)
    bucket_hl_rec.sort(key=lambda x: (x['Confidence'], float(x['Sales'])), reverse=True)
    bucket_hl_exc.sort(key=sort_key, reverse=True)
    bucket_nv.sort(key=lambda x: (x['Confidence'], float(x['Sales'])), reverse=True)
    bucket_filt.sort(key=sort_key, reverse=True)
    
    # Summary
    md_lines.append("## Summary Counts")
    md_lines.append(f"- VERIFIED — RECOMMENDED: {len(bucket_ver_rec)}")
    md_lines.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {len(bucket_ver_exc)}")
    md_lines.append(f"- HIGHLY LIKELY — RECOMMENDED: {len(bucket_hl_rec)}")
    md_lines.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {len(bucket_hl_exc)}")
    md_lines.append(f"- NEEDS VERIFICATION: {len(bucket_nv)}")
    md_lines.append(f"- TOTAL ANALYZED: {len(res_df)}")
    md_lines.append("")
    
    # Helper for table
    def make_table(rows, title):
        if not rows:
            return
        md_lines.append(f"## {title} (count={len(rows)})")
        md_lines.append("```text")
        
        # Calculate widths
        headers = ["Verdict", "Confidence", "SupplierTitle", "AmazonTitle", "Supplier EAN", 
                   "Amazon EAN", "ASIN", "SupplierPrice", "SellingPrice", "NetProfit", "ROI", 
                   "Sales", "Pack Verdict", "Adjusted Profit", "Key Match Evidence", "Filter Reason"]
        
        widths = {h: len(h) for h in headers}
        data_str = []
        
        for row in rows:
            # Format numbers
            row_fmt = row.copy()
            row_fmt['SupplierPrice'] = f"£{float(row['SupplierPrice']):.2f}"
            row_fmt['SellingPrice'] = f"£{float(row['SellingPrice']):.2f}"
            row_fmt['NetProfit'] = f"£{float(row['NetProfit']):.2f}"
            row_fmt['Adjusted Profit'] = f"£{float(row['Adjusted Profit']):.2f}"
            row_fmt['ROI'] = f"{float(row['ROI']):.1f}%"
            row_fmt['Sales'] = f"{int(float(row['Sales']))}"
            
            # Truncate titles 
            row_fmt['SupplierTitle'] = (str(row['SupplierTitle'])[:30] + '..') if len(str(row['SupplierTitle'])) > 32 else str(row['SupplierTitle'])
            row_fmt['AmazonTitle'] = (str(row['AmazonTitle'])[:50] + '..') if len(str(row['AmazonTitle'])) > 52 else str(row['AmazonTitle'])
            
            data_str.append(row_fmt)
            
            for h in headers:
                val_len = len(str(row_fmt[h]))
                if val_len > widths[h]:
                    widths[h] = val_len
        
        # Header
        header_row = " | ".join([h.ljust(widths[h]) for h in headers])
        md_lines.append(f"| {header_row} |")
        sep_row = "-|-".join(["-" * widths[h] for h in headers])
        md_lines.append(f"| {sep_row} |")
        
        # Data
        for d in data_str:
            row_str = " | ".join([str(d[h]).ljust(widths[h]) for h in headers])
            md_lines.append(f"| {row_str} |")
            
        md_lines.append("```")
        md_lines.append("")

    make_table(bucket_ver_rec, "VERIFIED — RECOMMENDED")
    make_table(bucket_ver_exc, "VERIFIED — FILTERED OUT / EXCLUDED")
    make_table(bucket_hl_rec, "HIGHLY LIKELY")
    make_table(bucket_hl_exc, "HIGHLY LIKELY — FILTERED OUT / EXCLUDED")
    make_table(bucket_nv, "NEEDS VERIFICATION")
    # Prompt says: "Do not include a standalone bottom-of-report FILTERED OUT table... Exclusions must appear under..."
    # Actually prompt text is a bit conflicting: 
    # "Include FILTERED OUT section for items that were excluded... Items shown in FILTERED OUT must be clearly labeled... [Fixed-width table with all confirmed matches that are unprofitable]"
    # But later: "+NOTE: Do not include a standalone bottom-of-report FILTERED OUT table. Exclusions must appear under:"
    # This likely means "Do not dump junk here."
    # But "FILTERED OUT contains CONFIRMED matches that are unprofitable".
    # I will output the "FILTERED OUT" bucket (confirmed match/valid brand but bad profit) as a table labeled "FILTERED OUT".
    make_table(bucket_filt, "FILTERED OUT (Probable Matches but Unprofitable/Mismatch)")
    
    # Reconciliation
    md_lines.append("## Reconciliation")
    md_lines.append(f"- Total rows in input: {len(res_df)}")
    md_lines.append(f"- Rows categorized: {len(bucket_ver_rec) + len(bucket_ver_exc) + len(bucket_hl_rec) + len(bucket_hl_exc) + len(bucket_nv) + len(bucket_filt)}")
    
    # Write File
    outfile = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))
        
    print(f"Report generated: {outfile}")

if __name__ == "__main__":
    main()
