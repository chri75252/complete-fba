
import pandas as pd
import re
import os
import sys
from difflib import SequenceMatcher

# Paths
BASE_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan"
SOURCE_FILE = os.path.join(BASE_DIR, "part 8 jan.xlsx")
COMP_DIR = os.path.join(BASE_DIR, "COMP")

REPORT_FILES = {
    "GEM_1": os.path.join(COMP_DIR, "GEM_1_PHASEA_MANUAL_REPORT_20260108.md"),
    "AGENT": os.path.join(COMP_DIR, "AGENT_PHASEA_MANUAL_REPORT_20260108.md"),
    "WEB": os.path.join(COMP_DIR, "WEB_PHASEA_MANUAL_REPORT_2601080356.md")
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

# --- Utils ---
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
        # Explicit patterns
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
        # check (4 x 50) patterns
        m = re.search(r'\(?(\d+)\s*x\s*(\d+)', t)
        if m:
            return int(m.group(1)) * int(m.group(2))
        return ext(t)

    s_q = ext(sup_title)
    a_q = ext_amz_multi(amz_title)
    
    # Simple logic: if Amazon quantity is multiple of supplier quantity
    if a_q > 1 and s_q == 1:
        return a_q
    if a_q > 1 and s_q > 1 and a_q > s_q:
        return a_q / s_q
    return 1.0

def has_variant_mismatch(sup_title, amz_title):
    s = str(sup_title).upper()
    a = str(amz_title).upper()
    
    # Simple keyword negation sets
    pairs = [
        ({"LEMON"}, {"ORANGE", "LIME", "LAVENDER"}),
        ({"WHITE"}, {"BLACK", "RED", "BLUE", "GREY"}),
        ({"LARGE"}, {"SMALL", "MINI"}),
        ({"MENS", "MEN'S"}, {"WOMENS", "WOMEN'S", "LADIES"}),
        ({"GLASS"}, {"PLASTIC"}) 
    ]
    
    for set_a, set_b in pairs:
        has_a_s = any(w in s for w in set_a)
        has_b_s = any(w in s for w in set_b)
        has_a_a = any(w in a for w in set_a)
        has_b_a = any(w in a for w in set_b)
        
        # If supplier has A but not B, and amazon has B... mismatch
        if (has_a_s and not has_b_s) and (has_b_a and not has_a_a):
            return True
        if (has_b_s and not has_a_s) and (has_a_a and not has_b_a):
            return True
            
    return False

def check_brand(sup_title, amz_title):
    s = str(sup_title).upper()
    a = str(amz_title).upper()
    
    found_brand = None
    for b in KNOWN_BRANDS:
        if b in s and b in a:
            found_brand = b
            return True, b
            
    # Heuristic: First word check
    s_tokens = s.split()
    if s_tokens:
        tok = s_tokens[0]
        if len(tok) > 2 and tok not in INVALID_FIRST_WORDS:
             # Check if this token appears in Amazon title (exact word match)
             if re.search(r'\b' + re.escape(tok) + r'\b', a):
                 return True, tok
                 
    return False, None

def analyze_row(row, source_map):
    # Retrieve Source Data if possible
    # We use SupplierTitle as key. 
    # NOTE: In reality, reports might truncate titles. 
    # For now, we analyze the *Report's* view of the data, as that is what we are validating.
    # However, for EAN verification, validation against source is better.
    
    # Step 3: Manual Analysis
    s_ean = clean_ean(row.get('Supplier EAN', ''))
    a_ean = clean_ean(row.get('Amazon EAN', ''))
    
    s_title = row.get('SupplierTitle', '')
    a_title = row.get('AmazonTitle', '')
    
    # Financials
    try:
        price = float(str(row.get('SupplierPrice', '0')).replace('£', '').replace(',', ''))
        profit = float(str(row.get('NetProfit', '0')).replace('£', '').replace(',', ''))
    except:
        price = 0.0
        profit = 0.0

    # 3.1 EAN
    ean_match = False
    if s_ean and a_ean and len(s_ean) >= 8 and len(a_ean) >= 8:
        if s_ean == a_ean:
            # Check valid
            if checksum(s_ean):
                ean_match = True
    
    # 3.2 Brand
    brand_match, brand_name = check_brand(s_title, a_title)
    
    # 3.3 Similarity
    sim = SequenceMatcher(None, str(s_title).lower(), str(a_title).lower()).ratio()
    
    # 3.4 Pack
    pack_ratio = get_pack_ratio(s_title, a_title)
    adj_profit = profit
    if pack_ratio > 1:
        # Profit = Sell - (Cost * Ratio) - Fees... 
        # Actually report usually has NetProfit calculated for 1 unit. 
        # If Bundle, Cost increases. 
        # Approx: AdjProfit = NetProfit - (Cost * (Ratio - 1))
        adj_profit = profit - (price * (pack_ratio - 1))
        
    # 3.5 Variant
    mismatch = has_variant_mismatch(s_title, a_title)
    
    # Independent Class
    my_verdict = "UNRELATED"
    
    if ean_match and not mismatch and adj_profit > 0:
        my_verdict = "VERIFIED"
    elif ean_match and not mismatch and adj_profit <= 0:
        my_verdict = "FILTERED OUT" # Verified but unprofitable
        
    elif not ean_match:
        if mismatch:
            my_verdict = "FILTERED OUT"
        elif brand_match:
            if pack_ratio > 1 and adj_profit <= 0:
                my_verdict = "FILTERED OUT"
            elif adj_profit > 0 and sim > 0.35: # Looser sim if brand match
                 my_verdict = "HIGHLY LIKELY"
            else: 
                 my_verdict = "NEEDS VERIFICATION"
        else:
            # No brand match
            if sim > 0.6 and adj_profit > 0:
                my_verdict = "NEEDS VERIFICATION"
            else:
                my_verdict = "UNRELATED"
                
    # Additional logic for User's special "Need Verification" requirement:
    # "Shortlist really very likely ... strict qualifications"
    # We will tag this separately in returns
    
    valid_opportunity = (my_verdict in ["VERIFIED", "HIGHLY LIKELY"])
    
    strict_nv = False
    if my_verdict == "NEEDS VERIFICATION":
        # Check strict criteria
        if sim > 0.5 or (brand_match and sim > 0.3):
            if adj_profit > 0.5:
                strict_nv = True
                
    return {
        "MyVerdict": my_verdict,
        "ValidOpp": valid_opportunity,
        "StrictNV": strict_nv,
        "AdjProfit": adj_profit,
        "IsEanMatch": ean_match,
        "BrandMatch": brand_match,
        "Sim": sim
    }

def parse_markdown_table(file_path):
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_section = "UNKNOWN"
    headers = []
    
    for line in lines:
        line = line.strip()
        if line.startswith("##"):
            current_section = line.strip("# ").strip()
            continue
            
        if line.startswith("|") and "SupplierTitle" in line:
            headers = [h.strip() for h in line.strip("|").split("|")]
            continue
            
        if line.startswith("|") and "---" in line:
            continue
            
        if line.startswith("|"):
            vals = [v.strip() for v in line.strip("|").split("|")]
            if len(vals) == len(headers):
                row = dict(zip(headers, vals))
                row['ReportSection'] = current_section
                
                # Normalize report verdict from section
                verdict = "UNKNOWN"
                if "VERIFIED" in current_section and "RECOMMENDED" in current_section: verdict = "VERIFIED"
                elif "VERIFIED" in current_section: verdict = "FILTERED OUT" 
                elif "HIGHLY LIKELY" in current_section and "RECOMMENDED" in current_section: verdict = "HIGHLY LIKELY"
                elif "HIGHLY LIKELY" in current_section: verdict = "FILTERED OUT"
                elif "NEEDS VERIFICATION" in current_section: verdict = "NEEDS VERIFICATION"
                elif "FILTERED" in current_section or "EXCLUDED" in current_section: verdict = "FILTERED OUT"
                
                row['ClaimedVerdict'] = verdict
                rows.append(row)
                
    return rows

# --- Main Execution ---

all_stats = []

for model_name, path in REPORT_FILES.items():
    if not os.path.exists(path):
        print(f"Skipping {model_name}, file not found.")
        continue
        
    print(f"Analyze {model_name}...")
    try:
        rows = parse_markdown_table(path)
    except Exception as e:
        print(f"Error parse {model_name}: {e}")
        continue
        
    products = []
    stats = {
        "Total": 0, "Correct": 0, "Acceptable": 0, "Incorrect": 0,
        "ValidOpp_Count": 0, "StrictNV_Count": 0,
        "Claimed_V": 0, "Claimed_HL": 0, "Claimed_NV": 0
    }
    
    # Valid rows breakdown list
    valid_breakdown = []
    
    for r in rows:
        an = analyze_row(r, None) 
        
        # Accuracy
        claimed = r['ClaimedVerdict']
        mine = an['MyVerdict']
        
        is_corr = (claimed == mine)
        is_acc = False
        if not is_corr:
            if claimed == "VERIFIED" and mine == "HIGHLY LIKELY": is_acc = True
            if claimed == "HIGHLY LIKELY" and mine == "VERIFIED": is_acc = True
            if claimed == "HIGHLY LIKELY" and mine == "NEEDS VERIFICATION": is_acc = True
            # if claimed == "FILTERED OUT" and mine == "VERIFIED": ... Not acceptable
            
        r.update(an)
        products.append(r)
        
        stats["Total"] += 1
        if is_corr: stats["Correct"] += 1
        elif is_acc: stats["Acceptable"] += 1
        else: stats["Incorrect"] += 1
        
        if an["ValidOpp"]: 
            stats["ValidOpp_Count"] += 1
            if claimed not in ["VERIFIED", "HIGHLY LIKELY"]:
                 valid_breakdown.append(r)
                 
        if an["StrictNV"]: stats["StrictNV_Count"] += 1
        
        if claimed == "VERIFIED": stats["Claimed_V"] += 1
        if claimed == "HIGHLY LIKELY": stats["Claimed_HL"] += 1
        if claimed == "NEEDS VERIFICATION": stats["Claimed_NV"] += 1

    all_stats.append({
        "Model": model_name,
        "Stats": stats,
        "Products": products,
        "ValidBreakdown": valid_breakdown
    })

# Print Results for Report Gen
print("--- RESULTS ---")
for s in all_stats:
    st = s['Stats']
    acc = (st['Correct'] / st['Total'] * 100) if st['Total'] else 0
    print(f"MODEL: {s['Model']}")
    print(f"  Total Rows: {st['Total']}")
    print(f"  Accuracy: {acc:.1f}%")
    print(f"  Valid Opps (My Calc): {st['ValidOpp_Count']}")
    print(f"  Strict NV (My Calc): {st['StrictNV_Count']}")
    print(f"  Breakdown of 'Valid' but missed (Claimed != V/HL): {len(s['ValidBreakdown'])}")
    print("-" * 20)

