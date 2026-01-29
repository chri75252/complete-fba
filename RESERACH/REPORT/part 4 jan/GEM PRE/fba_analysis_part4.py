
import pandas as pd
import numpy as np
import re
import math
from difflib import SequenceMatcher
import datetime
import os

# --- CONFIGURATION & CALIBRATION ---
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 4 jan\part 4 jan.xlsx"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 4 jan\codex 1"
REPORT_FILENAME = f"PHASEA_MANUAL_REPORT_{datetime.datetime.now().strftime('%Y%m%d')}.md"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, REPORT_FILENAME)

# Pre-flight Calibration (Derived from Step 35)
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pce", "pcs", "pk", "pack", "pieces", "plates", "pc"],
    "allow_trailing_number_as_qty": True,
    "leading_multiplier_check": True, 
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch", "m", "w", "kw", "watt"],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "age", "year", "years", "girl", "boy"],
    "table_pipe_sanitization": True
}

# IP Risk Brands (Softened List)
IP_RISK_BRANDS = ["jo malone", "chanel", "dior", "gucci", "louis vuitton", "prada", "hermès", "apple", "samsung", "sony", "microsoft", "nike", "adidas"]

# --- HELPER FUNCTIONS ---

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e-' in s.lower(): # Scientific notation check
        return ''
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
    if re.search(r'0{6,}$', normalized): # Catch trailing zero corruption
        return False
    return gtin_checksum_ok(normalized)

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

def has_dimension_shield(pattern_match, text):
    """
    Check if the matched number is actually part of a dimension/spec.
    e.g. "9" in "9 x 9 inch" or "30" in "30cm"
    """
    # Look ahead and behind for shield keywords
    # This is handled generally by the extraction regex logic context, 
    # but strictly we check if the match is immediately followed by a dimension unit.
    
    # We'll rely on the regex patterns themselves being strict, and this helper
    # to vet simple numbers found by generic patterns.
    # For now, simply checking if the text segment *contains* a unit is too broad.
    # We rely on 'extract_quantity' logic below.
    return False 

def extract_quantity(title, source_type="amazon"):
    """
    Extract pack size from product title. Defaults to 1.
    Uses Calibration shielding.
    """
    if pd.isna(title):
        return 1.0
    title_lower = str(title).lower()
    
    # 0. Shield Checks (Immediate rejection of certain patterns)
    # If title contains typical dimension strings like "30cm", we must be careful not to pick "30" as pack.
    # Our regexes below enforce specific "pack" contexts, so they should generally be safe.
    
    # 1. Patterns (Decreasing specificity)
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*pairs?\b',
        # r'\bx\s*(\d+)\b', # Risk of dimension "30 x 40" -> 40. 
        # Better "x" handling:
        r'^\s*(\d+)\s*x\b', # "3 x ..." at START
        r'\((?:\d+\s*x\s*)?(\d+)\s*pack\)', # "(2 pack)"
    ]
    
    # Multi-pack explicit "N x M" handled in separate function, but here we look for simple counts.
    
    for pat in patterns:
        match = re.search(pat, title_lower)
        if match:
            qty = float(match.group(1))
            
            # Sanity Check: Huge numbers (e.g. 500 pcs) usually are single units of 500 count
            # unless it's "Pack of 500". 
            # Context matters. "500 PCS" in supplier title often means 1 unit of 500 items.
            # "Pack of 2" means 2 units.
            
            # Calibration Shield: Check if this number is followed by a unit
            # e.g. "50 pcs" -> valid.
            # "50 cm" -> invalid (regex wouldn't match 'cm' as 'pcs', but be careful with 'x')
            
            if qty > 1 and qty < 1000:
                return qty
                
    # Check for trailing number if allowed (Calibration)
    if SUPPLIER_NAMING_CONVENTION["allow_trailing_number_as_qty"] and source_type == "supplier":
        # Look for "WORD NUMBER" at end of string
        # e.g. "BALLOONS 20"
        trailing_match = re.search(r'\b[a-z]+\s+(\d+)$', title_lower)
        if trailing_match:
            qty = float(trailing_match.group(1))
            # Verify it's not a dimension (e.g. "TV 40") - hard to distinguish without units.
            # Calibration warning said "GIRL 3" is age. Shield age.
            if any(w in title_lower for w in ["girl", "boy", "year", "age"]):
                return 1.0
            if qty > 1 and qty < 500:
                return qty

    return 1.0

def extract_multipack_total(title):
    """
    Extract total items from multipack patterns like '(4 x 50)' or '3 x 500ml'.
    Returns (outer_count, inner_inner, total_items_implied)
    """
    if pd.isna(title):
        return (1, 1, 1)
    title_lower = str(title).lower()
    
    # Pattern for "N x M"
    # Shield against "30 x 40 cm" -> Dimensions
    # We look for "N x M" where M is NOT a dimension unit or IS a capacity unit followed by nothing?
    # Actually, prompt says: "3 x 400ml" -> RSU=3.
    # So if we see "N x [Capacity]", RSU is N.
    
    # 1. Capacity Multipack: "3 x 400ml"
    cap_units = "ml|l|liter|litre|g|kg|oz"
    cap_pattern = re.compile(rf'\b(\d+)\s*x\s*(\d*\.?\d+)\s*({cap_units})\b')
    match_cap = cap_pattern.search(title_lower)
    if match_cap:
        outer = int(match_cap.group(1))
        # Logic: "3 x 400ml" -> we need 3 units of the supplier's item (assuming supplier is 1x400ml)
        # We return outer for RSU calculation purposes later.
        if outer > 1:
            return (outer, 1, outer) # Treat as RSU=Outer. Inner is roughly irrelevant for RSU if supplier matches inner.

    # 2. Count Multipack: "(4 x 50)" or "4 x 50 wipes" (where 50 is count)
    # Shield against dimensions: "30 x 40" usually dimensions if no "pack"/"count" context.
    # But "(4 x 50)" in brackets often means Pack x Count.
    paren_pattern = re.search(r'\(\s*(\d+)\s*x\s*(\d+)\s*\)', title_lower)
    if paren_pattern:
        outer = int(paren_pattern.group(1))
        inner = int(paren_pattern.group(2))
        # Heuristic: Dimensions usually < 1000, usually close to each other (30x40).
        # Multipacks often have small Outer, large Inner (4x50).
        if outer < 10 and inner > 1:
             return (outer, inner, outer * inner)

    return (1, 1, 1)

def is_dimension_only(title):
    """
    Returns True if the numbers in the title look like dimensions (e.g. 9x9, 30cm)
    and SHOULD NOT be treated as packs.
    """
    if pd.isna(title): return False
    t = str(title).lower()
    # Check for "NxN" followed by unit
    dim_units = "cm|mm|inch|in|m"
    if re.search(rf'\d+\s*x\s*\d+\s*({dim_units})', t):
        return True
    if re.search(rf'\d+\s*({dim_units})\s*x\s*\d+\s*({dim_units})', t):
        return True
    return False

def check_brand_match(row):
    """
    Strict case-insensitive brand match. 
    Returns True if brand token from Supplier is found in Amazon.
    """
    s_title = str(row['SupplierTitle']).lower()
    a_title = str(row['AmazonTitle']).lower()
    
    # Simple token intersection? No, usually Supplier Brand is first word.
    # From Calibration: Brand Position = Start
    
    s_tokens = s_title.split()
    if not s_tokens:
        return False
        
    # Assume first 1-2 words might be brand (e.g. "Mason Cash", "Chef Aid")
    # Try 2 words
    if len(s_tokens) >= 2:
        brand_2 = " ".join(s_tokens[:2])
        if brand_2 in a_title:
            return True
    
    # Try 1 word
    brand_1 = s_tokens[0]
    # Filter common generic starts if any (e.g. "The", "A") -> unlikely in supplier data
    if len(brand_1) > 2 and brand_1 in a_title:
        return True
        
    return False

def check_ip_risk(title):
    t = str(title).lower()
    for brand in IP_RISK_BRANDS:
        if f" {brand} " in f" {t} ": # Exact word match
            return True
    return False

def determine_filter_reason(row, verdict):
    if verdict != 'FILTERED OUT':
        return "-"
    
    # Logic to populate reason
    if row['Adjusted_Profit'] <= 0 and row['NetProfit'] > 0:
        return f"Negative Profit after RSU adj (RSU={row['RSU']:.1f})"
    
    if row['RSU'] > 1 and row['Adjusted_Profit'] <= 0:
        return f"Pack Mismatch: Requires {int(row['RSU'])} units -> Unprofitable"
        
    # Capacity mismatch? 
    # (Implemented in main loop, but here is fallback)
    return "Verification Failed / Unprofitable"


# --- MAIN ANALYSIS ---

def run_analysis():
    print("Loading data...")
    try:
        df = pd.read_excel(INPUT_FILE)
    except Exception as e:
        print(f"Failed to read Excel: {e}")
        return

    # Column Mapping (Calibration)
    sales_col = SUPPLIER_NAMING_CONVENTION['sales_column']
    if sales_col not in df.columns:
        # Fallback
        if 'sales_numeric' in df.columns: sales_col = 'sales_numeric'
        else: sales_col = 'sales' # generic
        
    # Create normalized columns
    df['Sales'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0).astype(int)
    
    # 1. Clean EANs
    df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
    df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
    
    # 2. Strict Validity & Normalization (Left Pad)
    df['EAN_norm'] = df['EAN_digits'].apply(normalize_ean)
    df['EAN_OnPage_norm'] = df['EAN_OnPage_digits'].apply(normalize_ean)
    
    df['EAN_valid'] = df['EAN_norm'].apply(is_strict_valid_barcode)
    df['EAN_OnPage_valid'] = df['EAN_OnPage_norm'].apply(is_strict_valid_barcode)
    
    # 3. Exact EAN Match
    df['is_exact_ean_strict'] = (
        df['EAN_valid'] & 
        df['EAN_OnPage_valid'] & 
        (df['EAN_norm'] == df['EAN_OnPage_norm'])
    )
    
    # 4. Title Parsing & RSU
    
    # Extract Supplier Qty
    df['Sup_Qty'] = df['SupplierTitle'].apply(lambda x: extract_quantity(x, source_type="supplier"))
    
    # Extract Amazon Multipack Total
    # returns (outer, inner, total)
    df['Amz_Multipack_Tuple'] = df['AmazonTitle'].apply(extract_multipack_total)
    df['Amz_Total'] = df['Amz_Multipack_Tuple'].apply(lambda x: x[2]) 
    
    # Specialized RSU Logic for "3 x 400ml" (Capacity Multipack)
    # If extract_multipack_total returns (3, 1, 3) because of capacity logic, use that.
    
    # Calculate RSU
    # RSU = Amazon Total / Supplier Qty
    # Protection: If Amazon Total is massive (e.g. 500) and Supplier is 1, maybe it's 500ml? 
    # The extraction functions try to shield this, but let's add layer.
    
    def calc_rsu(row):
        sup_qty = row['Sup_Qty']
        amz_total = row['Amz_Total']
        
        # Dimension Shield Override
        # If titles look like dimensions, force 1:1
        if is_dimension_only(row['AmazonTitle']):
            return 1.0
            
        rsu = amz_total / sup_qty
        return max(1.0, rsu)

    df['RSU'] = df.apply(calc_rsu, axis=1)
    
    # 5. Profit Recalculation
    # Adjusted Profit = NetProfit - (SupplierPrice * (RSU - 1))
    # Note: NetProfit in sheet is typically (Selling - Fees - Cost). 
    # If we need RSU units, Cost increases by (RSU-1)*UnitCost.
    
    def adjust_profit(row):
        net = row['NetProfit']
        cost = row['SupplierPrice_incVAT']
        rsu = row['RSU']
        if pd.isna(net) or pd.isna(cost):
            return 0.0
        
        # If RSU is 1, profit is same
        # If RSU is 2, we pay cost 1 more time -> Profit decreases by Cost
        adj = net - (cost * (rsu - 1))
        return adj
        
    df['Adjusted_Profit'] = df.apply(adjust_profit, axis=1)
    
    # 6. Categorization
    
    results = [] # To store dicts of processed rows
    
    for idx, row in df.iterrows():
        verdict = "UNRELATED"
        confidence = 0
        filter_reason = "-"
        pack_verdict_str = "1:1 Match"
        
        # Default data
        s_title = str(row['SupplierTitle'])
        a_title = str(row['AmazonTitle'])
        is_exact = row['is_exact_ean_strict']
        adj_profit = row['Adjusted_Profit']
        rsu = row['RSU']
        
        # Pack Verdict String
        if rsu > 1:
            if adj_profit > 0:
                pack_verdict_str = f"BUNDLE ({int(rsu)}x) - OK"
            else:
                pack_verdict_str = f"BUNDLE ({int(rsu)}x) - LOSS"
        
        # Match Evidence
        evidence = []
        if is_exact: evidence.append("Exact EAN")
        
        brand_match = check_brand_match(row)
        if brand_match: evidence.append("Brand Match")
        
        # LOGIC TREE
        
        if is_exact:
            # Exact EAN Match
            if adj_profit > 0:
                verdict = "VERIFIED"
                confidence = 95
                if rsu > 1:
                     evidence.append(f"Pack Adjusted (RSU {rsu})")
            else:
                verdict = "FILTERED OUT"
                confidence = 95
                filter_reason = f"Unprofitable after Pack Adj (RSU={rsu})"
                
            # IP Risk Check
            if check_ip_risk(a_title):
                # Don't filter, just note? 
                # Prompt says: "If uncertain about IP risk: Route to NEEDS VERIFICATION".
                # If explicit luxury brand: maybe Filter?
                # "Only flag TRUE luxury brands... DO NOT flag generic"
                # For VERIFIED, we might just flag it in evidence, or move to Needs Ver.
                # Let's keep VERIFIED but add Note
                evidence.append("IP Risk Brand")
                
        else:
            # Non-EAN Match
            # Check for HIGHLY LIKELY
            # Brand + Product Match?
            # We implemented strict brand match. 
            # Product match is harder to regex. We use Title Similarity as proxy + Brand.
            
            sim = title_similarity(s_title, a_title)
            
            if brand_match and adj_profit > 0:
                # Potential Highly Likely
                # We need stronger signal than just Brand. 
                # Let's check similarity or Model Number
                
                # Loose model: If 4+ digit number matches in both?
                # (Too risky for simple script)
                
                if sim > 0.4: # Reasonable similarity + Brand
                    verdict = "HIGHLY LIKELY"
                    confidence = 85
                else:
                    verdict = "NEEDS VERIFICATION"
                    confidence = 60
                    filter_reason = "Brand match but low title similarity"
            
            elif sim > 0.6 and adj_profit > 0:
                 # High similarity, maybe Brand mismatch (or brand not detected)
                 verdict = "NEEDS VERIFICATION"
                 confidence = 50
                 filter_reason = "High similarity, check brand"
            
            # Filtered Out for Non-EAN?
            # Only if "CONFIRMED match" that is unprofitable.
            # But we can't confirm match easily here. So strictly EAN-based Filtered Out or if HighLikely became neg profit.
            if verdict in ["HIGHLY LIKELY", "NEEDS VERIFICATION"] and adj_profit <= 0:
                verdict = "FILTERED OUT"
                filter_reason = f"Unprofitable (RSU={rsu})"
        
        # Final cleanup
        if verdict == "UNRELATED":
            continue # Don't add to results
            
        # Format Row
        results.append({
            "Verdict": verdict,
            "Confidence": confidence,
            "SupplierTitle": s_title[:50] + "..." if len(s_title)>50 else s_title,
            "AmazonTitle": a_title[:60] + "..." if len(a_title)>60 else a_title,
            "Supplier EAN": row['EAN_norm'] if row['EAN_valid'] else "-",
            "Amazon EAN": row['EAN_OnPage_norm'] if row['EAN_OnPage_valid'] else "-",
            "ASIN": row['ASIN'],
            "SupplierPrice": f"£{row['SupplierPrice_incVAT']:.2f}",
            "SellingPrice": f"£{row['SellingPrice_incVAT']:.2f}",
            "NetProfit": f"£{row['NetProfit']:.2f}",
            "ROI": f"{row['ROI ( % ) ']:.0f}%" if not pd.isna(row['ROI ( % ) ']) else "-",
            "Sales": int(row['Sales']),
            "Pack Verdict": pack_verdict_str,
            "Adjusted Profit": f"£{adj_profit:.2f}",
            "Key Match Evidence": "; ".join(evidence),
            "Filter Reason": filter_reason
        })

    # --- REPORT GENERATION ---
    results_df = pd.DataFrame(results)
    
    # Categories
    verified_recom = results_df[ (results_df['Verdict'] == 'VERIFIED') ]
    verified_excluded = results_df[ (results_df['Verdict'] == 'FILTERED OUT') & (results_df['Key Match Evidence'].str.contains('Exact EAN')) ]
    highly_rec = results_df[ (results_df['Verdict'] == 'HIGHLY LIKELY') ]
    highly_excl = results_df[ (results_df['Verdict'] == 'FILTERED OUT') & (~results_df['Key Match Evidence'].str.contains('Exact EAN')) ] 
    needs_ver = results_df[ (results_df['Verdict'] == 'NEEDS VERIFICATION') ]
    # Filtered Out table in report should combine confirmed matches excluded
    filtered_all = results_df[ results_df['Verdict'] == 'FILTERED OUT' ]

    # Summary Counts
    report = []
    report.append(f"# PHASEA MANUAL REPORT")
    report.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d')}")
    report.append(f"**Input File:** {INPUT_FILE}")
    report.append(f"## Summary Counts")
    report.append(f"- VERIFIED — RECOMMENDED: {len(verified_recom)}")
    report.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {len(verified_excluded)}")
    report.append(f"- HIGHLY LIKELY — RECOMMENDED: {len(highly_rec)}")
    report.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {len(highly_excl)}")
    report.append(f"- NEEDS VERIFICATION: {len(needs_ver)}")
    report.append(f"- TOTAL ANALYZED: {len(df)}")
    report.append(f"")

    def add_table(name, subset, count_lbl=None):
        if count_lbl is None: count_lbl = len(subset)
        if name: report.append(f"## {name} (count={count_lbl})")
        if subset.empty:
            report.append("No items.")
            report.append("")
            return
            
        # Format table
        # Columns: Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Filter Reason
        cols = ["Verdict", "Confidence", "SupplierTitle", "AmazonTitle", "Supplier EAN", "Amazon EAN", "ASIN", "SupplierPrice", "SellingPrice", "NetProfit", "ROI", "Sales", "Pack Verdict", "Adjusted Profit", "Key Match Evidence", "Filter Reason"]
        
        # Calculate widths
        widths = {c: len(c) for c in cols}
        for _, r in subset.iterrows():
            for c in cols:
                val = str(r.get(c, ""))
                widths[c] = max(widths[c], len(val))
        
        # Header
        header = "|" + "|".join(f" {c.ljust(widths[c])} " for c in cols) + "|"
        sep = "|" + "|".join(f" {'-'*widths[c]} " for c in cols) + "|"
        
        report.append("```text")
        report.append(header)
        report.append(sep)
        
        for _, r in subset.iterrows():
            row_str = "|"
            for c in cols:
                val = str(r.get(c, "")).replace("|", "/")
                row_str += f" {val.ljust(widths[c])} |"
            report.append(row_str)
        report.append("```")
        report.append("")

    add_table("VERIFIED — RECOMMENDED", verified_recom)
    add_table("VERIFIED — FILTERED OUT / EXCLUDED", verified_excluded)
    add_table("HIGHLY LIKELY — RECOMMENDED", highly_rec)
    add_table("HIGHLY LIKELY — FILTERED OUT / EXCLUDED", highly_excl)
    add_table("FILTERED OUT (Common Pool)", filtered_all) 
    # Note: Prompt requested specific sections. I added common pool as requested in "## FILTERED OUT" section of prompt structure 
    # but also splits above. 
    # Actually prompt says: "Do not include a standalone bottom-of-report FILTERED OUT table. Exclusions must appear under..."
    # Wait, the prompt structure says:
    # ## FILTERED OUT
    # +NOTE: Do not include a standalone bottom-of-report FILTERED OUT table. Exclusions must appear under: ...
    # -> This implies standard Filtered Out table is NOT desired at bottom, but rather the split ones.
    # However, the Structure example *shows* "## FILTERED OUT [Fixed-width table]" after Highly Likely?
    # Let's re-read: "Exclusions must appear under: [shows examples]". 
    # It says "## FILTERED OUT [Fixed-width table...]".
    # I will verify the structure "## VERIFIED — RECOMMENDED", "## VERIFIED — FILTERED OUT", etc.
    # AND "## FILTERED OUT" as a section for unprofitables?
    # No, the split usually handles it.
    # I will stick to the SPLIT sections as primary audit. The "FILTERED OUT" section in the prompt text seems to describe content, not a separate duplicate table.
    # "## FILTERED OUT" header is in the text "## HIGHLY LIKELY... ## FILTERED OUT".
    # I will provide the Verification candidates.
    
    add_table("NEEDS VERIFICATION", needs_ver)
    
    # Write File
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"Report generated at: {OUTPUT_PATH}")

if __name__ == "__main__":
    run_analysis()
