
import json
import pandas as pd
import re
import difflib

# ... (Previous imports)

MD_PATHS = {
    "REPORT_20251224.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_20251224.md",
    "REPORT_2512240724.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240724.md",
    "REPORT_2512240124.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240124.md",
    "REPORT_2512240128.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240128.md"
}

PART3_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx"

# Re-define helpers to be self-contained
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
    try:
        df = pd.read_excel(PART3_PATH)
    except:
        return set()
        
    valid_keys = set()
    
    for idx, row in df.iterrows():
        s_ean = clean_ean(row.get('EAN') or row.get('Supplier EAN'))
        a_ean = clean_ean(row.get('EAN_OnPage') or row.get('Amazon EAN'))
        s_title = str(row.get('SupplierTitle', ''))
        a_title = str(row.get('AmazonTitle', ''))
        
        # Logic matches Step 104
        s_pack = extract_pack_qty(s_title)
        a_pack = extract_pack_qty(a_title)
        conflict = (s_pack != a_pack) and (s_pack > 1 or a_pack > 1)
        
        is_valid = False
        if s_ean and a_ean and s_ean == a_ean:
            if not conflict: is_valid = True
        elif compute_similarity(s_title, a_title) > 0.8 and not conflict:
            is_valid = True
            
        if is_valid:
            k = str(row.get('ASIN', '')).strip()
            if not k or k.lower() == 'nan': k = s_ean
            if k: valid_keys.add(k)
            
    return valid_keys

def get_report_keys(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except: return set()
    
    keys = set()
    # Simple parser for markdown tables
    lines = [l.strip() for l in content.split('\n') if l.strip().startswith('|')]
    for l in lines:
        parts = [p.strip() for p in l.split('|') if p]
        for p in parts:
            p = p.strip()
            if p.startswith('B0') and len(p) == 10: keys.add(p)
            # Also catch EANs if ASIN not present?
            # Start with ASINs as they are unique keys
    return keys

truth = get_valid_keys_truth()
scores = []

for name, path in MD_PATHS.items():
    rep_keys = get_report_keys(path)
    found = truth.intersection(rep_keys)
    scores.append({
        "name": name,
        "valid_found": len(found),
        "total_in_report": len(rep_keys),
        "missed": list(truth - rep_keys)
    })

scores.sort(key=lambda x: x['valid_found'], reverse=True)
print(json.dumps(scores, indent=2))
