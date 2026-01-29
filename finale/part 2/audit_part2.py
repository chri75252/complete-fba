
import json
import pandas as pd
import re
import difflib
import os

# --- PATHS ---
BASE_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 2"
PART3_PATH = os.path.join(BASE_DIR, "PART3.xlsx")

MD_FILES = {
    "Report_2.4": "prompt 2.4 PHASEA_MANUAL_REPORT_20251224 (1).md",
    "Report_2.5": "prompt 2.5 PHASEA_MANUAL_REPORT_2512241822.md",
    "Report_2.7": "prompt 2.7 PHASEA_MANUAL_REPORT_2512241836.md",
    "Report_2.8": "prompt 2.8PHASEA_MANUAL_REPORT_20251224 (2).md"
}

MD_PATHS = {k: os.path.join(BASE_DIR, v) for k, v in MD_FILES.items()}

# --- LOGIC ---
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

def get_truth_set():
    print("Reading PART3...")
    try:
        df = pd.read_excel(PART3_PATH)
    except Exception as e:
        print(f"Error reading PART3: {e}")
        return set()

    valid_keys = set()
    total_valid = 0
    
    for idx, row in df.iterrows():
        s_ean = clean_ean(row.get('EAN') or row.get('Supplier EAN'))
        a_ean = clean_ean(row.get('EAN_OnPage') or row.get('Amazon EAN'))
        s_title = str(row.get('SupplierTitle', ''))
        a_title = str(row.get('AmazonTitle', ''))
        
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
            
    print(f"Total Rows in PART3: {len(df)}")
    print(f"TRUTH Valid Items: {len(valid_keys)}")
    return valid_keys

def parse_report(path):
    keys = set()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return keys

    lines = [l.strip() for l in content.split('\n') if l.strip().startswith('|')]
    for l in lines:
        parts = [p.strip() for p in l.split('|') if p]
        for p in parts:
            p = p.strip()
            if p.startswith('B0') and len(p) == 10: keys.add(p)
    return keys

def main():
    truth = get_truth_set()
    
    results = []
    
    for name, path in MD_PATHS.items():
        rep_keys = parse_report(path)
        
        found = truth.intersection(rep_keys)
        # missed = truth - rep_keys
        
        valid_count = len(found)
        total_in_rep = len(rep_keys)
        
        accuracy = (valid_count / total_in_rep) if total_in_rep > 0 else 0
        recall = (valid_count / len(truth)) if len(truth) > 0 else 0
        
        results.append({
            "name": name,
            "filename": MD_FILES[name],
            "valid_found": valid_count,
            "total_rows": total_in_rep,
            "accuracy": accuracy,
            "recall": recall
        })

    # Sort by Valid Found (Recall) descending, then Accuracy descending
    results.sort(key=lambda x: (x['valid_found'], x['accuracy']), reverse=True)
    
    print("\n" + "="*40)
    print("RESULTS SUMMARY")
    print("="*40)
    for r in results:
        print(f"REPORT: {r['name']}")
        print(f"  File: {r['filename']}")
        print(f"  Valid Entries Found: {r['valid_found']} / {len(truth)}")
        print(f"  Total Entries Listed: {r['total_rows']}")
        print(f"  Recall (Completeness): {r['recall']:.1%}")
        print(f"  Accuracy (Precision): {r['accuracy']:.1%}")
        print(f"  Noise (Invalid Rows): {r['total_rows'] - r['valid_found']}")
        print("-" * 20)
        
    print("\nWINNER (Most Valid Entries):", results[0]['name'])

if __name__ == "__main__":
    main()
