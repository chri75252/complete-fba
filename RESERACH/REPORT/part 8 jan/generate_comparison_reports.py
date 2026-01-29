
import pandas as pd
import re
import os
from difflib import SequenceMatcher
from datetime import datetime

# Paths
BASE_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan"
COMP_DIR = os.path.join(BASE_DIR, "COMP")
OUTPUT_COMP_FILE = os.path.join(BASE_DIR, "COMPREHENSIVE_COMPARISON_ANALYSIS_20260108.md")
OUTPUT_FINAL_FILE = os.path.join(BASE_DIR, "FINAL_CONSOLIDATED_PHASEA_REPORT_20260108.md")

REPORT_FILES = {
    "GEM_1": os.path.join(COMP_DIR, "GEM_1_PHASEA_MANUAL_REPORT_20260108.md"),
    "AGENT": os.path.join(COMP_DIR, "AGENT_PHASEA_MANUAL_REPORT_20260108.md"),
    "WEB": os.path.join(COMP_DIR, "WEB_PHASEA_MANUAL_REPORT_2601080356.md"),
    "PHASE2": os.path.join(COMP_DIR, "PHASE2_PHASEA_MANUAL_REPORT_20260109.md"),
    "PHASE3": os.path.join(COMP_DIR, "PHASE3_PHASEA_MANUAL_REPORT_20260109.md"),
    "PHASE4": os.path.join(COMP_DIR, "PHASE4_PHASEA_MANUAL_REPORT_20260109.md"),
    "PHASE5": os.path.join(COMP_DIR, "PHASE5_PHASEA_MANUAL_REPORT_20260109.md")
}


KNOWN_BRANDS = [
    "AMTECH", "MASON CASH", "ROLSON", "KILNER", "DRAPER", "PYREX", "CHEF AID",
    "BLUE CANYON", "ELLIOTT", "FALCON", "BAKER & SALT", "SCHOTT ZWIESEL",
    "MARIGOLD", "FAIRY", "DETTOL", "EVERBUILD", "SOUDAL", "TIDYZ", "BACOFOIL",
    "HARRIS", "EXTRASTAR", "GIFTMAKER", "PRIMA", "APOLLO", "KILROCK", "PRODEC",
    "HOUSE MATE", "TALA", "LITTLE TREES", "ELBOW GREASE", "ULTRATAPE", "FIRE UP",
    "DOFF", "GEEPAS", "STATUS", "ROUNDUP", "SUPERIOR", "FIRST STEPS", "MINKY",
    "RUSSELL HOBBS", "QUEST", "YALE", "VINERS", "MASTERCLASS", "HEM", "AIRWICK",
    "AIR WICK", "SPONTEX", "PASABAHCE", "DENBY", "HEAT HOLDERS", "KENWOOD",
    "SWAN", "TOWER", "MORPHY RICHARDS", "TEFAL", "SABICHI", "DUNLOP", "JML",
    "BELDRAY", "PROGRESS", "SALTER", "PRESTIGE", "STELLAR", "JUDGE", "PAN AROMA",
    "151", "COMMAND", "GORILLA", "WD-40", "HG", "ASTONISH", "STARDROPS", "ZOFALORA"
]

INVALID_FIRST_WORDS = [
    "MONEY", "HAPPY", "SALT", "LED", "BBQ", "DOOR", "PET", "CAT", "DOG",
    "CANDLE", "MIRROR", "BOTTLE", "BASKET", "GLOVES", "WATCH", "LARGE",
    "SMALL", "WOODEN", "METAL", "PLASTIC", "CHRISTMAS", "BIRTHDAY", "GARDEN", "SET", "PACK"
]

def clean_ean(x):
    if pd.isna(x): return ""
    s = str(x).strip()
    s = re.sub(r'\.0$', '', s)
    s = re.sub(r'\D', '', s)
    return s

def checksum(digits):
    if not digits.isdigit() or len(digits) not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])
    body_rev = list(map(int, body[::-1]))
    total = sum(d * (3 if i % 2 == 1 else 1) for i, d in enumerate(body_rev, start=1))
    calc = (10 - (total % 10)) % 10
    return calc == check

def get_pack_ratio(sup_title, amz_title):
    def ext(t):
        if pd.isna(t): return 1
        t = str(t).lower()
        m = re.search(r'pack of (\d+)', t)
        if m: return int(m.group(1))
        m = re.search(r'\b(\d+)\s*pk\b', t)
        if m: return int(m.group(1))
        m = re.search(r'\b(\d+)\s*pack\b', t)
        if m: return int(m.group(1))
        m = re.search(r'^(\d+)\s*x\b', t)
        if m: return int(m.group(1))
        return 1
    def ext_amz_multi(t):
        if pd.isna(t): return 1
        t = str(t).lower()
        m = re.search(r'\(?(\d+)\s*x\s*(\d+)', t)
        if m: return int(m.group(1)) * int(m.group(2))
        return ext(t)
    s_q = ext(sup_title)
    a_q = ext_amz_multi(amz_title)
    if a_q > 1 and s_q == 1: return a_q
    if a_q > 1 and s_q > 1 and a_q > s_q: return a_q / s_q
    return 1.0

def has_variant_mismatch(sup_title, amz_title):
    s = str(sup_title).upper()
    a = str(amz_title).upper()
    pairs = [({"LEMON"}, {"ORANGE", "LIME", "LAVENDER"}), ({"WHITE"}, {"BLACK", "RED", "BLUE", "GREY"}),
             ({"LARGE"}, {"SMALL", "MINI"}), ({"MENS", "MEN'S"}, {"WOMENS", "WOMEN'S"}), ({"GLASS"}, {"PLASTIC"})]
    for set_a, set_b in pairs:
        has_a_s, has_b_s = any(w in s for w in set_a), any(w in s for w in set_b)
        has_a_a, has_b_a = any(w in a for w in set_a), any(w in a for w in set_b)
        if (has_a_s and not has_b_s) and (has_b_a and not has_a_a): return True
        if (has_b_s and not has_a_s) and (has_a_a and not has_b_a): return True
    return False

def check_brand(sup_title, amz_title):
    s, a = str(sup_title).upper(), str(amz_title).upper()
    for b in KNOWN_BRANDS:
        if b in s and b in a: return True, b
    s_tokens = s.split()
    if s_tokens:
        tok = s_tokens[0]
        if len(tok) > 2 and tok not in INVALID_FIRST_WORDS:
             if re.search(r'\b' + re.escape(tok) + r'\b', a): return True, tok
    return False, None

def analyze_row(row):
    s_ean = clean_ean(row.get('Supplier EAN', ''))
    a_ean = clean_ean(row.get('Amazon EAN', ''))
    s_title = row.get('SupplierTitle', '')
    a_title = row.get('AmazonTitle', '')
    try:
        price = float(str(row.get('SupplierPrice', '0')).replace('£', '').replace(',', ''))
        profit = float(str(row.get('NetProfit', '0')).replace('£', '').replace(',', ''))
    except:
        price = 0.0
        profit = 0.0

    ean_match = False
    if s_ean and a_ean and len(s_ean) >= 8 and len(a_ean) >= 8 and s_ean == a_ean and checksum(s_ean):
        ean_match = True
    
    brand_match, _ = check_brand(s_title, a_title)
    sim = SequenceMatcher(None, str(s_title).lower(), str(a_title).lower()).ratio()
    pack_ratio = get_pack_ratio(s_title, a_title)
    adj_profit = profit - (price * (pack_ratio - 1)) if pack_ratio > 1 else profit
    mismatch = has_variant_mismatch(s_title, a_title)
    
    my_verdict = "UNRELATED"
    
    # Correct Match Definitions (Profitable or Not)
    if ean_match and not mismatch:
        if adj_profit > 0: my_verdict = "VERIFIED"
        else: my_verdict = "VERIFIED_UNPROFITABLE"
        
    elif not ean_match:
        if mismatch: 
            my_verdict = "MISMATCH"
        elif brand_match:
            if pack_ratio > 1 and adj_profit <= 0:
                 my_verdict = "HL_UNPROFITABLE"
            elif adj_profit > 0 and sim > 0.35: 
                 my_verdict = "HIGHLY LIKELY"
            else: 
                 my_verdict = "NEEDS VERIFICATION" # Weak match
        else:
            if sim > 0.6 and adj_profit > 0: 
                 my_verdict = "NEEDS VERIFICATION"
            else: 
                 my_verdict = "UNRELATED"
            
    strict_nv = False
    if my_verdict == "NEEDS VERIFICATION":
        if (sim > 0.5 or (brand_match and sim > 0.3)) and adj_profit > 0.5:
             strict_nv = True
             
    row['Measured_AdjProfit'] = adj_profit
    row['Measured_Verdict'] = my_verdict
    row['Measured_StrictNV'] = strict_nv
    row['Measured_Valid'] = (my_verdict in ["VERIFIED", "HIGHLY LIKELY", "VERIFIED_UNPROFITABLE", "HL_UNPROFITABLE"])
    return row

def parse_md_table(file_path):
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    current_sec = "UNKNOWN"
    headers = []
    for line in lines:
        line = line.strip()
        if line.startswith("##"): current_sec = line.strip("# ").strip(); continue
        if line.startswith("|") and "SupplierTitle" in line:
            headers = [h.strip() for h in line.strip("|").split("|")]
            continue
        if line.startswith("|") and "---" in line: continue
        if line.startswith("|"):
            vals = [v.strip() for v in line.strip("|").split("|")]
            if len(vals) == len(headers):
                row = dict(zip(headers, vals))
                row['SourceCategory'] = current_sec
                # More granular ClaimedVerdict to capture Audited Out distinct from generic Filtered Out
                if "VERIFIED" in current_sec and "RECOMMENDED" in current_sec:
                    cv = "VERIFIED"
                elif "VERIFIED" in current_sec and ("FILTERED" in current_sec or "AUDITED" in current_sec or "EXCLUDED" in current_sec):
                    cv = "VERIFIED (AUDITED OUT)"
                elif "HIGHLY LIKELY" in current_sec and "RECOMMENDED" in current_sec:
                    cv = "HIGHLY LIKELY"
                elif "HIGHLY LIKELY" in current_sec and ("FILTERED" in current_sec or "AUDITED" in current_sec or "EXCLUDED" in current_sec):
                    cv = "HIGHLY LIKELY (AUDITED OUT)"
                elif "NEEDS VERIFICATION" in current_sec:
                    cv = "NEEDS VERIFICATION"
                else:
                    cv = "FILTERED OUT"
                
                row['ClaimedVerdict'] = cv
                rows.append(row)
    return rows

# Collect Data
all_results = []
valid_tracker = {} # Key: SupplierTitle, Value: Row (Best)
strict_nv_tracker = {}

for model, path in REPORT_FILES.items():
    if not os.path.exists(path): continue
    rows = parse_md_table(path)
    
    stats = {"Total": 0, "Correct": 0, "ValidOpp": 0, "StrictNV": 0, "Claimed_V": 0, "Claimed_HL": 0, "Claimed_NV": 0}
    
    for r in rows:
        r = analyze_row(r)
        
        # Stats
        stats['Total'] += 1
        if r['ClaimedVerdict'] == r['Measured_Verdict']: stats['Correct'] += 1
        if r['Measured_Valid']: stats['ValidOpp'] += 1
        if r['Measured_StrictNV']: stats['StrictNV'] += 1
        if r['ClaimedVerdict'] == "VERIFIED": stats['Claimed_V'] += 1
        elif r['ClaimedVerdict'] == "HIGHLY LIKELY": stats['Claimed_HL'] += 1
        elif r['ClaimedVerdict'] == "NEEDS VERIFICATION": stats['Claimed_NV'] += 1
        
        # Consolidation Logic
        key = r.get('SupplierTitle', 'UNK')
        
        # Add to Valid List
        if r['Measured_Valid']:
            if key not in valid_tracker:
                valid_tracker[key] = r
            else:
                # Keep the one with better provenance or "VERIFIED" status
                curr = valid_tracker[key]
                if r['Measured_Verdict'] == "VERIFIED" and curr['Measured_Verdict'] != "VERIFIED":
                    valid_tracker[key] = r
        
        # Add to NV List
        if r['Measured_StrictNV']:
             if key not in strict_nv_tracker and key not in valid_tracker: # Don't add if already valid
                 strict_nv_tracker[key] = r
                 
    all_results.append({"Model": model, "Stats": stats, "Rows": rows})

# --- OUTPUT 1: COMPARISON REPORT ---
with open(OUTPUT_COMP_FILE, 'w', encoding='utf-8') as f:
    f.write("# FBA REPORT COMPREHENSIVE VALIDATION ANALYSIS\n\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n")
    f.write("**Reference:** Consistent Source Data vs Model Outputs\n\n")
    
    f.write("## 1. Valid Product Opportunities by Model (Global)\n")
    f.write("Total unique items identified as **Correct Matches**, summing Verified, Highly Likely, AND Valid Needs Verification items. Includes 'Audited Out' correct matches.\n\n")
    f.write("| Model | Total Rows in File | **GRAND TOTAL CORRECT** (Ver+HL+NV) | Strong Matches (Ver/HL) | Weak Matches (NV) |\n")
    f.write("|---|---|---|---|---|\n")
    best_valid = 0
    winner = ""
    for r in all_results:
        s = r['Stats']
        # Calculate Grand Total here
        grand_total = s['ValidOpp'] + s['StrictNV']
        
        if grand_total > best_valid:
             best_valid = grand_total
             winner = r['Model']
        f.write(f"| {r['Model']} | {s['Total']} | **{grand_total}** | {s['ValidOpp']} | {s['StrictNV']} |\n")
    f.write(f"\n**Winner for Coverage:** {winner} ({best_valid} correct matches found)\n\n")
    f.write("*Note: 'Total Rows in File' refers to the number of tabular rows actually present in the markdown file. This count includes Audited Out/Filtered Out rows if present in the file bodies.* \n\n")

    f.write("## 2. Categorization Accuracy\n")
    f.write("Percentage of rows where the model's verdict matched independent verification.\n\n")
    f.write("| Model | Accuracy % | Correct Rows | Total Rows in File |\n")
    f.write("|---|---|---|---|\n")
    for r in all_results:
        s = r['Stats']
        acc = (s['Correct']/s['Total']*100) if s['Total'] else 0
        f.write(f"| {r['Model']} | {acc:.1f}% | {s['Correct']} | {s['Total']} |\n")
    
    f.write("\n## 3. Claimed vs Validated Verdicts\n")
    f.write("Breakdown of what the report *claimed* vs what was validated.\n\n")
    f.write("| Model | Claimed VERIFIED | Claimed HL | Claimed NV | **Actual Valid NV Matches** (Strict) |\n")
    f.write("|---|---|---|---|---|\n")
    for r in all_results:
         s = r['Stats']
         f.write(f"| {r['Model']} | {s['Claimed_V']} | {s['Claimed_HL']} | {s['Claimed_NV']} | {s['StrictNV']} |\n")

    f.write("\n## 4. Strict 'Needs Verification' Analysis\n") 
    f.write(" Breakdown of items categorized as NV that are potentially upgradeable matches.\n")
    f.write(" (See Final Report for full list)\n\n")

    f.write("## 5. Section-Level Diagnosis (AGENT Report)\n")
    f.write("Accuracy breakdown by specific report section.\n\n")
    f.write("| Report Section | Total Rows | **Valid Opps** (True Positives) | **Invalid/Unrelated** (False Positives) | Accuracy % |\n")
    f.write("|---|---|---|---|---|\n")
    
    # Extract AGENT specific stats if available
    agent_res = next((r for r in all_results if r['Model'] == 'AGENT'), None)
    if agent_res:
        # We need to re-process to group by original section if we didn't store it perfectly
        # But 'valid_rows' has 'SourceCategory'. Let's see if we can reconstruct or if we need to parse again.
        # Actually, let's just use the 'Rows' list from the agent result
        
        # Group by Source Category (which serves as the "Section")
        from collections import defaultdict
        section_stats = defaultdict(lambda: {'total': 0, 'valid': 0, 'invalid': 0})
        
        for row in agent_res['Rows']:
            sec = row['SourceCategory'] # usage: VERIFIED, HIGHLY_LIKELY, etc.
            # We need to distinguish Recommended vs Audited Out if possible. 
            # The parser might have just stored 'VERIFIED' or 'HIGHLY_LIKELY'. 
            # Let's check if 'Verdict' in row maps better.
            
            # Using Verdict as proxy for section if SourceCategory is generic
            # Actually, standard parser usually grabs the header. Let's assume Verdict is the section or map to it.
            
            # Re-read how parser works: it assigns verdict based on table.
            # If the report separates them into "VERIFIED - RECOMMENDED" tables, the parser *might* explicitly capture that if configured, 
            # but usually it just grabs the row. 
            # HOWEVER, we can infer "Audited Out" if the row is in a table but has 'Audit' or 'Exclud' in the header/text before it?
            # Or simpler: Check 'NetProfit' or 'AdjustedProfit'. If <=0, it's likely Audited Out section.
            # Or check the parsing logic. 
            # For now, let's just group by the Verdict column content.
            
            # Group by our refined Claimed Verdict
            # Group by our refined Claimed Verdict
            verdict = row.get('ClaimedVerdict', 'UNKNOWN')
            
            # REFINED DEFINITION OF VALIDITY:
            # A row is a "Correct Entry" if the Ground Truth confirms it is a Match (Verified or HL),
            # even if it is Unprofitable (VERIFIED_UNPROFITABLE, HL_UNPROFITABLE).
            gt = row['Measured_Verdict']
            is_valid_match = gt in {'VERIFIED', 'HIGHLY LIKELY', 'VERIFIED_UNPROFITABLE', 'HL_UNPROFITABLE'}
            # Note: We do NOT count 'NEEDS VERIFICATION' as a "Valid Match" for this high-bar metric unless strictly validated?
            # User asked for "Correct Entries". NV is usually "Maybe".
            # Let's keep strict NV as valid too??
            # Actually, let's stick to Strong Matches for "Correct Entries".
            if gt == 'NEEDS VERIFICATION' and row['Measured_StrictNV']:
                is_valid_match = True
            
            section_stats[verdict]['total'] += 1
            if is_valid_match:
                section_stats[verdict]['valid'] += 1
            else:
                section_stats[verdict]['invalid'] += 1
                
        for sec, stats in sorted(section_stats.items()):
            acc = (stats['valid'] / stats['total'] * 100) if stats['total'] > 0 else 0
            f.write(f"| {sec} | {stats['total']} | {stats['valid']} | {stats['invalid']} | {acc:.1f}% |\n")

# --- OUTPUT 2: FINAL CONSOLIDATED REPORT ---
# Filter and Sort
final_valid = sorted(valid_tracker.values(), key=lambda x: x.get('Measured_AdjProfit', 0), reverse=True)
final_nv = sorted(strict_nv_tracker.values(), key=lambda x: x.get('Measured_AdjProfit', 0), reverse=True)

verified_list = [x for x in final_valid if x['Measured_Verdict'] == "VERIFIED"]
hl_list = [x for x in final_valid if x['Measured_Verdict'] == "HIGHLY LIKELY"]

with open(OUTPUT_FINAL_FILE, 'w', encoding='utf-8') as f:
    f.write("# PHASEA MANUAL REPORT\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n")
    f.write("**Input File:** part 8 jan.xlsx (Consolidated)\n")
    f.write("**Supplier:** (Unknown)\n\n")
    
    f.write("## Summary Counts\n")
    f.write(f"- VERIFIED — RECOMMENDED: {len(verified_list)}\n")
    f.write(f"- VERIFIED — AUDITED OUT / EXCLUDED: 0 (Filtered out in consolidation)\n")
    f.write(f"- HIGHLY LIKELY — RECOMMENDED: {len(hl_list)}\n")
    f.write(f"- HIGHLY LIKELY — AUDITED OUT / EXCLUDED: 0\n")
    f.write(f"- NEEDS VERIFICATION: {len(final_nv)}\n")
    f.write(f"- TOTAL VALID OPPORTUNITIES: {len(final_valid)}\n\n")
    
    def write_table(title, data):
        f.write(f"## {title} (count={len(data)})\n")
        f.write("```text\n")
        cols = ['Measured_Verdict', 'SupplierTitle', 'AmazonTitle', 'Supplier EAN', 'Amazon EAN', 'ASIN', 'SupplierPrice', 'SellingPrice', 'Measured_AdjProfit']
        headers = ['Verdict', 'SupplierTitle', 'AmazonTitle', 'Supplier EAN', 'Amazon EAN', 'ASIN', 'Sup Price', 'Sell Price', 'Adj Profit']
        
        # Calculate Widths
        widths = {h: len(h) for h in headers}
        rows_fmt = []
        for d in data:
            r = []
            for i, c in enumerate(cols):
                val = str(d.get(c, '-'))
                if c == 'Measured_AdjProfit': val = f"£{float(val):.2f}"
                r.append(val)
                widths[headers[i]] = max(widths[headers[i]], len(val))
            rows_fmt.append(r)
            
        # Header
        f.write("| " + " | ".join([h.ljust(widths[h]) for h in headers]) + " |\n")
        f.write("| " + " | ".join(['-'*widths[h] for h in headers]) + " |\n")
        
        # Rows
        for r in rows_fmt:
            f.write("| " + " | ".join([val.ljust(widths[headers[i]]) for i, val in enumerate(r)]) + " |\n")
        f.write("```\n\n")
        
    write_table("VERIFIED — RECOMMENDED", verified_list)
    write_table("HIGHLY LIKELY — RECOMMENDED", hl_list)
    write_table("NEEDS VERIFICATION (Strict Checklist Applied)", final_nv)

print("Generated Comparison Reports Successfully.")
