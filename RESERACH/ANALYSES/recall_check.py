
import json

path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\audit_final.json"

with open(path, 'r') as f:
    data = json.load(f)

# 1. Get VALID Items from PART3 (Canonical List of Truth)
# We need to reconstruct which ASINs/EANs were VALID in the source PART3 analysis
# The JSON doesn't store the full list of valid ASINs directly, but it stored 'missing_top_10_from_part3' relative to a winner.
# Actually, I can't easily get the *full* list of valid PART3 items from the JSON alone if it wasn't fully dumped.
# I should re-run a quick check on PART3.xlsx to get the set of all VALID keys.

# However, the JSON *does* have 'valid_entries' count for each report.
# Let's see the keys found in each report and cross-reference.
# Ah, the JSON 'reports' dict likely doesn't have the full list of keys unless I modify the script.
# The previous script calculated stats but didn't dump all keys.

# Use pandas to get the Truth Set again quickly, then compare against reports.

import pandas as pd
import re
import difflib

PART3_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx"
MD_PATHS = {
    "REPORT_20251224.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_20251224.md",
    "REPORT_2512240724.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240724.md",
    "REPORT_2512240124.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240124.md",
    "REPORT_2512240128.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240128.md"
}

def clean_ean(val):
    if pd.isna(val): return None
    s = str(val).split('.')[0].strip()
    s = re.sub(r'[^0-9]', '', s)
    if not s: return None
    if len(s) == 12: s = '0' + s
    return s

def extract_pack_qty(title):
    if not isinstance(title, str): return 1
    title = str(title).lower()
    m = re.search(r'pack\s*(?:of)?\s*(\d+)', title)
    if m: return int(m.group(1))
    m = re.search(r'\bx\s*(\d+)\b', title)
    if m: return int(m.group(1))
    return 1

def compute_similarity(s1, s2):
    if not isinstance(s1, str): s1 = ""
    if not isinstance(s2, str): s2 = ""
    return difflib.SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

def get_valid_keys_truth():
    df = pd.read_excel(PART3_PATH)
    valid_keys = set()
    
    for idx, row in df.iterrows():
        s_ean = clean_ean(row.get('EAN') or row.get('Supplier EAN'))
        a_ean = clean_ean(row.get('EAN_OnPage') or row.get('Amazon EAN'))
        s_title = str(row.get('SupplierTitle', ''))
        a_title = str(row.get('AmazonTitle', ''))
        s_pack = extract_pack_qty(s_title)
        a_pack = extract_pack_qty(a_title)
        
        conflict = (s_pack != a_pack) and (s_pack > 1 or a_pack > 1)
        title_sim = compute_similarity(s_title, a_title)
        
        is_valid = False
        if s_ean and a_ean and s_ean == a_ean:
            if not conflict: is_valid = True
        elif title_sim > 0.8 and not conflict:
            is_valid = True
            
        if is_valid:
            k = str(row.get('ASIN', '')).strip()
            if not k or k.lower() == 'nan':
                k = s_ean
            if k: valid_keys.add(k)
            
    return valid_keys # All ASINs/EANs that are TRUE VALID in PART3

def get_report_keys(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except: return set()
    
    keys = set()
    lines = [l.strip() for l in content.split('\n') if l.strip().startswith('|')]
    for l in lines:
        parts = [p.strip() for p in l.split('|') if p]
        for p in parts:
            if p.startswith('B0') and len(p) == 10: # ASIN
                keys.add(p)
    return keys

truth_set = get_valid_keys_truth()
print(f"TRUTH VALID COUNT: {len(truth_set)}")

scores = []
for name, p in MD_PATHS.items():
    rep_keys = get_report_keys(p)
    # How many of the TRUTH set are in this report?
    found_valid = truth_set.intersection(rep_keys)
    # Correct Count
    count = len(found_valid)
    # Any valid items MISSED by this report?
    missed = truth_set - rep_keys
    
    scores.append({
        "name": name,
        "valid_items_found": count,
        "total_rows_in_report": len(rep_keys), # Using keys found as proxy for rows
        "missed_valid_items": list(missed)
    })

scores.sort(key=lambda x: x['valid_items_found'], reverse=True)

for s in scores:
    print(f"\nREPORT: {s['name']}")
    print(f"  Valid Items Found: {s['valid_items_found']} / {len(truth_set)}")
    print(f"  Total Items In Report: {s['total_rows_in_report']}")
    print(f"  Noise (Invalid Items): {s['total_rows_in_report'] - s['valid_items_found']}")
    if s['missed_valid_items']:
        print(f"  Missed Valid Keys: {s['missed_valid_items']}")
