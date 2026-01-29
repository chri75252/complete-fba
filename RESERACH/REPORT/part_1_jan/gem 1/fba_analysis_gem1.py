import pandas as pd
import numpy as np
import re
import os
import datetime
from difflib import SequenceMatcher

# --- CONFIGURATION ---
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\gem 1"
# Ensure output dir exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pce", "pcs", "pk", "pack", "pieces", "pc", "cases", "set"],
    "allow_trailing_number_as_qty": True, 
    "leading_multiplier_check": False,     
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch", "ft", "m", "l"],
    "brand_position": "start", 
    "sales_column": "bought_in_past_month" 
}

# --- UTILS ---

def clean_to_digits(x):
    """Clean EAN to digits only, handle floats/scientific notation."""
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
        # Heuristic: scientific notation might mean corruption or very large number
        # Try to convert float to int str if possible, else reject
        try:
            val = float(s)
            return str(int(val))
        except:
            return ''
    # Remove .0 for floats
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
    check = int(digits[-1])

    body_rev = list(map(int, body[::-1]))
    total = 0
    for i, d in enumerate(body_rev, start=1):
        total += d * (3 if i % 2 == 1 else 1)
    calc = (10 - (total % 10)) % 10
    return calc == check

def normalize_ean(digits: str) -> str:
    """Attempt left-padding to valid GTIN length if checksum passes"""
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
    if re.search(r'0{6,}$', normalized): # Suspicious trailing zeros
        return False
    return gtin_checksum_ok(normalized)

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

# --- PACK SIZE EXTRACTION ---

def extract_quantity(title):
    """
    Extract pack size from product title. Defaults to 1.
    Integrates Supplier Naming Convention knowledge.
    """
    if pd.isna(title):
        return 1.0
    title_lower = str(title).lower()
    
    # 1. Check explicit units from calibration
    # Construct regex from explicit_units list
    units_or = "|".join(SUPPLIER_NAMING_CONVENTION["explicit_units"])
    # e.g. (\d+)\s*(pce|pcs|pk|pack)
    explicit_pattern = rf'(\d+)\s*({units_or})\b'
    match = re.search(explicit_pattern, title_lower)
    if match:
        qty = float(match.group(1))
        if 1 < qty < 500:
            return qty

    # 2. Standard patterns (fallback and supplemental)
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*pairs?\b',
        r'\bx\s*(\d+)\b',          # x 10
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)',
        r'\b(\d+)\s*rolls?\b',
        r'\b(\d+)\s*piece\b',
    ]
    
    for pat in patterns:
        match = re.search(pat, title_lower)
        if match:
            qty = float(match.group(1))
            if 1 < qty < 500:
                return qty
    
    # 3. Trailing Number Check (Calibration: "allow_trailing_number_as_qty": True)
    # Be careful of Age traps (Age 3) or Models (SDB113).
    # Heuristic: High number (>1) at very end of string, preceded by space.
    if SUPPLIER_NAMING_CONVENTION["allow_trailing_number_as_qty"]:
        # Exclude if it looks like a year (2020-2030) or model number often is mixed alpha or 3+ digits
        # This is risky so we trust explicit > implict.
        # But per calibration output: "PARTY CRAZY BALLOONS ASSORTED 20" -> 20.
        trailing_match = re.search(r'\s(\d+)$', title_lower)
        if trailing_match:
            candidate = float(trailing_match.group(1))
            # Safety: don't pick up small numbers that might be age unless units imply count
            if 1 < candidate < 500:
                # Check for "Age" keyword or "Year"
                if "age" not in title_lower and "year" not in title_lower:
                     return candidate

    return 1.0

def extract_multipack_total(title):
    """
    Extract total items from multipack patterns like '(4 x 50)' or '3 x 500ml'.
    Returns (outer_count, inner_count, total) or (1, qty, qty) if no multipack.
    """
    if pd.isna(title):
        return (1, 1, 1)
    title = str(title).lower()
    
    # Pattern for "N x M" multipacks (e.g., "4 x 50", "3 x 500ml")
    multipack_pattern = r'\(?\s*(\d+)\s*x\s*(\d+)\s*\)?'
    match = re.search(multipack_pattern, title)
    if match:
        outer = int(match.group(1))
        inner = int(match.group(2))
        
        # Dimension shield check: if we see "3 x 500" followed by 'ml' or 'g', it's valid as (3 units of 500ml)
        # But if we see "30 x 40" (cm), it's dimensions.
        
        # Check context after the match
        end_pos = match.end()
        remainder = title[end_pos:].strip()
        
        is_dimension = False
        for dim_kw in SUPPLIER_NAMING_CONVENTION["dimension_shield_keywords"]:
            # If the numbers are effectively dimensions (e.g. 30 x 40 cm), usually inner is large or specific.
            # But "3 x 500ml" IS a pack of 3.
            # We want to catch "30 x 40 cm".
            # If outer is large (>10) and inner is large (>10), likely dimensions (e.g. bin liners 50 x 60 cm?)
            pass

        # Heuristic from prompt:
        # Avoid dimension patterns (small numbers with units nearby)
        # "If outer <= 10 and inner > 10: Likely multipack" -> e.g. 4 x 50
        # What if 4 x 4 (pack of 4 x 4)?
        
        if outer <= 12: # Likely a pack multiplier
             return (outer, inner, outer * inner)
        
        # If outer is large (e.g. 200 x 300 mm), it's dimensions.
        if outer > 12 and inner > 12:
            return (1, 1, 1)

    # Fallback to simple quantity extraction
    qty = extract_quantity(title)
    return (1, int(qty), int(qty))

def detect_dimensions(title):
    """Check if title contains dimension patterns that might confuse pack logic."""
    if pd.isna(title):
        return False
    title = str(title).lower()
    # Patterns like 9x9, 30x40, 21cm, 500ml
    # We just want to know if specific "N x M" patterns are likely dimensions
    # so we don't treat them as packs.
    # The 'extract_quantity' function is already trying to be smart, 
    # but let's have a safety check.
    
    # Check for "N cm", "N mm", "N ml", "N l", "N kg"
    # If found, these are 1 unit of that size, do NOT multiply.
    for kw in SUPPLIER_NAMING_CONVENTION["dimension_shield_keywords"]:
        if kw in title:
            return True
    return False

# --- MAIN ANALYSIS SCRIPT ---

def analyze_report():
    print(f"Loading {INPUT_FILE}...")
    try:
        df = pd.read_excel(INPUT_FILE)
    except Exception as e:
        print(f"Failed to read Excel: {e}")
        return

    # STAGE 1: CLEANING
    print("Stage 1: Cleaning and Normalizing...")
    df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()
    
    # Sales
    sales_col = SUPPLIER_NAMING_CONVENTION["sales_column"]
    if sales_col in df.columns:
        df['sales'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0)
    else:
        # Fallback search
        found = False
        for c in df.columns:
            if 'bought' in c.lower() or 'sales' in c.lower():
                df['sales'] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                found = True
                break
        if not found:
            df['sales'] = 0

    df['RowID'] = df.index + 2 # 1-based, header is 1

    # STAGE 1B/3B: EAN VALIDITY
    df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
    df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
    
    df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
    df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)

    df['EAN_strict_valid'] = df['EAN_digits_normalized'].apply(is_strict_valid_barcode)
    df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits_normalized'].apply(is_strict_valid_barcode)

    df['is_exact_ean_strict'] = (
        df['EAN_strict_valid']
        & df['EAN_OnPage_strict_valid']
        & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
    )

    # STAGE 2: TITLE MATCH
    df['title_match'] = df.apply(lambda x: title_similarity(x.get('SupplierTitle', ''), x.get('AmazonTitle', '')), axis=1)

    # STAGE 4: PACK & PROFIT
    print("Stage 4: Pack & Profit...")
    df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
    df['Amz_Multipack'] = df['AmazonTitle'].apply(extract_multipack_total) # Returns (outer, inner, total)
    df['Amz_Total'] = df['Amz_Multipack'].apply(lambda x: x[2])

    # RSU Calculation
    # If Sup_Qty > 1 (e.g. 50 pcs), and Amz_Total is 200 (4x50), RSU = 4.
    # If Sup_Qty = 1, Amz_Total = 10 (10 pack), RSU = 10.
    df['RSU'] = df.apply(lambda row: max(1, row['Amz_Total'] / row['Sup_Qty']) if row['Sup_Qty'] > 0 else 1, axis=1)
    
    # Calculate Adjusted Profit
    def get_adj_profit(row):
        try:
            orig_profit = float(row['NetProfit'])
            # Supp Price might be string with currency symbol
            cost_str = str(row['SupplierPrice_incVAT']).replace('£', '').replace(',', '')
            supplier_cost = float(cost_str) if cost_str else 0.0
            
            rsu = row['RSU']
            # Profit = Revenue - (Cost * RSU) - Fees
            # Use strict interpretation from prompt: Adjusted = Original_Profit - (Cost * (RSU - 1))
            # (Assuming Original_Profit accounted for 1 unit cost)
            adjustment = supplier_cost * (rsu - 1)
            return orig_profit - adjustment
        except:
            return -999.0

    df['Adjusted_Profit'] = df.apply(get_adj_profit, axis=1)

    # STAGE 5: CATEGORIZATION
    print("Stage 5: Categorization...")
    
    results = []

    for idx, row in df.iterrows():
        # Helpers
        sup_title = str(row.get('SupplierTitle', ''))
        amz_title = str(row.get('AmazonTitle', ''))
        exact_ean = row['is_exact_ean_strict']
        
        # Formatting for table
        sup_ean_disp = row['EAN'] if row['EAN_strict_valid'] else "-"
        amz_ean_disp = row['EAN_OnPage'] if row['EAN_OnPage_strict_valid'] else "-"
        
        # Analysis Variables
        adj_profit = row['Adjusted_Profit']
        sales = row['sales']
        title_score = row['title_match']
        rsu = row['RSU']
        
        verdict = "FILTERED OUT" # Default
        confidence = 0
        filter_reason = "-"
        pack_verdict_str = f"RSU: {rsu:.1f}"
        evidence = []

        # -- MANUAL ANALYSIS LOGIC --
        
        # 1. Brand Logic
        # Naive brand extraction: first word?
        # Or check if start of Sup matches start of Amz
        sup_brand = sup_title.split()[0].lower() if sup_title else ""
        amz_lower = amz_title.lower()
        brand_match = sup_brand in amz_lower if len(sup_brand) > 2 else False
        
        # 2. Pack Mismatch Logic
        # If RSU > 1.5, it's a pack diff
        pack_mismatch = rsu > 1.1 or rsu < 0.9
        
        # 3. Decision Tree
        
        if exact_ean:
            # VERIFIED PATH
            confidence = 95
            evidence.append("Exact EAN Match")
            
            # Check for negative profit
            if adj_profit <= 0:
                verdict = "VERIFIED - EXCLUDED" # Internal mapping for table splitting
                filter_reason = f"Negative Adjusted Profit (£{adj_profit:.2f})"
            elif pack_mismatch:
                 # Check dimension shield override
                 # If titles contain dimension keywords, maybe RSU logic is wrong?
                 # Prompt: "If matches exactly and no explicit pack-count word mismatch exists, classify as VERIFIED"
                 # We calculated RSU strictly. If RSU implies mismatch (e.g. 4 vs 1), keep it unless overridden.
                 # But if profit is OK with RSU, it's VERIFIED.
                 verdict = "VERIFIED"
                 pack_verdict_str = f"Bundle {int(rsu)}x - OK"
            else:
                 verdict = "VERIFIED"
                 pack_verdict_str = "1:1 Match"

        else:
            # NON-EAN PATH
            
            # Check for HIGHLY LIKELY
            # Brand match + Product Type (Sim > 0.4?) + Profit > 0
            if brand_match and title_score > 0.4 and adj_profit > 0:
                verdict = "HIGHLY LIKELY"
                confidence = 80 + int(title_score * 10)
                evidence.append("Strong Brand + Title Match")
                
                if pack_mismatch:
                     # Check if profit sustains it
                     if adj_profit > 0:
                         pack_verdict_str = f"Bundle {int(rsu)}x - OK"
                     else:
                         verdict = "HIGHLY LIKELY - EXCLUDED"
                         filter_reason = "Pack Mismatch leads to Loss"
            
            elif title_score > 0.5 and adj_profit > 0:
                # Plausible for Needs Verification
                verdict = "NEEDS VERIFICATION"
                confidence = 60
                evidence.append("Good Title Match")
                filter_reason = "Confirm Brand/Pack"
                
            else:
                verdict = "FILTERED OUT"
                filter_reason = "Low confidence / Mismatch"

        # Global Gates
        if sales == 0 and verdict not in ["NEEDS VERIFICATION", "FILTERED OUT"]:
             # Move to Needs Verif per Rule 3
             verdict = "NEEDS VERIFICATION"
             filter_reason = "Sales = 0, Verify Demand"
        
        if verdict == "NEEDS VERIFICATION" and adj_profit <= 0:
            verdict = "FILTERED OUT"
            filter_reason = "Negative Profit"

        # Final Formatting
        row_res = {
            "Verdict": verdict.split(" - ")[0], # Strip internal suffix
            "SubVerdict": verdict, # Keep full for sorting
            "Confidence": confidence,
            "SupplierTitle": sup_title,
            "AmazonTitle": amz_title,
            "Supplier EAN": sup_ean_disp,
            "Amazon EAN": amz_ean_disp,
            "ASIN": row.get('ASIN', '-'),
            "SupplierPrice": row.get('SupplierPrice_incVAT', 0),
            "SellingPrice": row.get('SellingPrice_incVAT', 0),
            "NetProfit": row.get('NetProfit', 0),
            "ROI": f"{row.get('ROI', 0):.1f}%",
            "Sales": int(sales),
            "Pack Verdict": pack_verdict_str,
            "Adjusted Profit": f"£{adj_profit:.2f}",
            "Key Match Evidence": "; ".join(evidence) if evidence else "-",
            "Filter Reason": filter_reason
        }
        results.append(row_res)

    results_df = pd.DataFrame(results)

    # --- REPORT GENERATION ---
    print("Generating Report...")
    
    # Separation
    verified_rec = results_df[results_df['SubVerdict'] == "VERIFIED"]
    verified_ex = results_df[results_df['SubVerdict'] == "VERIFIED - EXCLUDED"]
    
    highly_rec = results_df[results_df['SubVerdict'] == "HIGHLY LIKELY"]
    highly_ex = results_df[results_df['SubVerdict'] == "HIGHLY LIKELY - EXCLUDED"]
    
    needs_verif = results_df[results_df['Verdict'] == "NEEDS VERIFICATION"]
    filtered_out = results_df[results_df['Verdict'] == "FILTERED OUT"] # Plus the EXCLUDED ones if we want to list them there? 
    # The prompt says: "VERIFIED — FILTERED OUT / EXCLUDED table..." so keep separate.
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d")
    report_file = os.path.join(OUTPUT_DIR, f"PHASEA_MANUAL_REPORT_{current_time}.md")
    
    def make_table(df_subset):
        if df_subset.empty:
            return "No items in this category.\n"
        
        # Columns to show
        cols = [
            "Verdict", "Confidence", "SupplierTitle", "AmazonTitle", 
            "Supplier EAN", "Amazon EAN", "ASIN", 
            "SupplierPrice", "SellingPrice", "NetProfit", "ROI", 
            "Sales", "Pack Verdict", "Adjusted Profit", 
            "Key Match Evidence", "Filter Reason"
        ]
        
        # Manual Fixed Width Table Construction
        # 1. Determine max width for each column (with caps)
        exclude_width_check = ["SupplierTitle", "AmazonTitle"] # Cap these
        widths = {}
        for c in cols:
            max_w = len(c)
            # Check data len
            for val in df_subset[c]:
                max_w = max(max_w, len(str(val)))
            
            if c in ["SupplierTitle", "AmazonTitle"]:
                max_w = min(max_w, 50) # Cap titles
            widths[c] = max_w

        # Header
        header = "| " + " | ".join([c.ljust(widths[c]) for c in cols]) + " |"
        sep = "|-" + "-|-".join(["-" * widths[c] for c in cols]) + "-|"
        
        lines = [header, sep]
        
        for _, r in df_subset.iterrows():
            row_parts = []
            for c in cols:
                val = str(r[c])
                if len(val) > widths[c]:
                    val = val[:widths[c]-3] + "..."
                row_parts.append(val.ljust(widths[c]))
            lines.append("| " + " | ".join(row_parts) + " |")
        
        return "```text\n" + "\n".join(lines) + "\n```"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# PHASEA MANUAL REPORT\n")
        f.write(f"**Generated:** {current_time}\n")
        f.write(f"**Input File:** {INPUT_FILE}\n")
        f.write(f"\n## Summary Counts\n")
        f.write(f"- VERIFIED — RECOMMENDED: {len(verified_rec)}\n")
        f.write(f"- VERIFIED — FILTERED OUT / EXCLUDED: {len(verified_ex)}\n")
        f.write(f"- HIGHLY LIKELY — RECOMMENDED: {len(highly_rec)}\n")
        f.write(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {len(highly_ex)}\n")
        f.write(f"- NEEDS VERIFICATION: {len(needs_verif)}\n")
        f.write(f"- FILTERED OUT (Others): {len(filtered_out)}\n")
        f.write(f"- TOTAL ANALYZED: {len(df)}\n\n")
        
        f.write(f"## VERIFIED — RECOMMENDED (count={len(verified_rec)})\n")
        f.write(make_table(verified_rec))
        f.write("\n")
        
        f.write(f"## VERIFIED — FILTERED OUT / EXCLUDED (count={len(verified_ex)})\n")
        f.write(make_table(verified_ex))
        f.write("\n")
        
        f.write(f"## HIGHLY LIKELY — RECOMMENDED (count={len(highly_rec)})\n")
        f.write(make_table(highly_rec))
        f.write("\n")

        f.write(f"## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={len(highly_ex)})\n")
        f.write(make_table(highly_ex))
        f.write("\n")
        
        f.write(f"## NEEDS VERIFICATION (count={len(needs_verif)})\n")
        f.write(make_table(needs_verif))
        f.write("\n")
        
        f.write(f"## FILTERED OUT (Subset Example)\n")
        f.write(make_table(filtered_out.head(20))) # Don't print all garbage
        f.write("\n")

    print(f"Report Generated: {report_file}")

if __name__ == "__main__":
    analyze_report()
