
import pandas as pd
import re
import os
import difflib
from datetime import datetime

# --- CONFIG ---
PART3_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx"
MD_PATHS = {
    "REPORT_20251224.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_20251224.md",
    "REPORT_2512240724.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240724.md",
    "REPORT_2512240124.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240124.md",
    "REPORT_2512240128.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240128.md"
}

# --- HELPERS ---

def clean_ean(val):
    if pd.isna(val): return None
    s = str(val).split('.')[0].strip() # Handle 123.0
    s = re.sub(r'[^0-9]', '', s)
    if not s: return None
    if len(s) == 12: s = '0' + s
    return s

def extract_pack_qty(title):
    if not isinstance(title, str): return 1
    # Heuristics for pack size
    title = title.lower()
    
    # "pack of X", "pack X"
    m = re.search(r'pack\s*(?:of)?\s*(\d+)', title)
    if m: return int(m.group(1))
    
    # "x 2", "x2" at end or surrounded by spaces
    m = re.search(r'\bx\s*(\d+)\b', title)
    if m: return int(m.group(1))

    # "24 cans", "24 units" - simplistic
    return 1

def compute_similarity(s1, s2):
    if not isinstance(s1, str) or not isinstance(s2, str): return 0.0
    return difflib.SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

def validate_row(row):
    # Map columns flexibly
    s_ean = clean_ean(row.get('EAN') or row.get('Supplier EAN'))
    a_ean = clean_ean(row.get('EAN_OnPage') or row.get('Amazon EAN')) # Heuristic mapping
    
    s_title = str(row.get('SupplierTitle', ''))
    a_title = str(row.get('AmazonTitle', ''))
    
    s_pack = extract_pack_qty(s_title)
    a_pack = extract_pack_qty(a_title)
    
    pack_contradiction = (s_pack != a_pack) and (s_pack > 1 or a_pack > 1)
    
    title_sim = compute_similarity(s_title, a_title)
    
    # Logic
    if s_ean and a_ean and s_ean == a_ean:
        if pack_contradiction:
            return "NEEDS_REVIEW"
        return "VALID" # Exact Match
    
    # Non-EAN
    if title_sim > 0.8 and not pack_contradiction:
        return "LIKELY_VALID"
    if title_sim > 0.6:
        return "POSSIBLE"
    
    return "INVALID"

# --- MAIN ---

def main():
    print(">>> LOADING PART3...")
    try:
        df = pd.read_excel(PART3_PATH)
    except Exception as e:
        print(f"FATAL: Could not load PART3: {e}")
        return

    # Normalize stats cols
    # Find profit col
    profit_col = next((c for c in df.columns if 'Profit' in c and 'Margin' not in c), 'NetProfit')
    sales_col = next((c for c in df.columns if 'Sales' in c), 'Sales')
    
    print(f"Mapped Profit: {profit_col}, Sales: {sales_col}")
    
    df['ValidationStatus'] = df.apply(validate_row, axis=1)
    
    # Baselines
    baseline = {
        'total_rows': len(df),
        'sales_gt_0': len(df[df[sales_col] > 0]),
        'profit_gt_0': len(df[df[profit_col] > 0]),
        'valid_count': len(df[df['ValidationStatus'] == 'VALID']),
        'likely_count': len(df[df['ValidationStatus'] == 'LIKELY_VALID']),
        'invalid_count': len(df[df['ValidationStatus'] == 'INVALID'])
    }
    
    print("### BASELINE STATS ###")
    print(baseline)
    
    # Save canonical map for lookup
    # Key = ASIN (preferred) or EAN
    canonical_map = {}
    for idx, row in df.iterrows():
        k = str(row.get('ASIN', '')).strip()
        if not k or k == 'nan':
            k = clean_ean(row.get('EAN'))
        if k:
            canonical_map[k] = row.to_dict()
            canonical_map[k]['_orig_idx'] = idx

    # Compare Reports
    results = {}
    
    for name, path in MD_PATHS.items():
        print(f"\n>>> PROCESSING {name}...")
        results[name] = process_md_report(name, path, canonical_map, df, profit_col)

    # Score and Rank
    print("\n### RESULTS JSON ###")
    import json
    # Custom encoder for NaN
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, float) and (obj != obj): return None
            return super(NpEncoder, self).default(obj)
            
    print(json.dumps(results, cls=NpEncoder, indent=2))
    
def process_md_report(name, path, canonical_map, full_df, profit_col):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e)}

    # Parse tables
    # Find lines starting with |
    lines = [l.strip() for l in content.split('\n') if l.strip().startswith('|')]
    
    parsed_rows = []
    headers = []
    
    if len(lines) > 2:
        # crude parser
        # Detect header: usually the first one or after a blank
        # We'll just iterate all "|...|" lines and look for ASIN/EAN pattern
        
        for l in lines:
            parts = [p.strip() for p in l.split('|') if p]
            # Check if this is a header
            if 'ASIN' in parts or 'EAN' in parts or 'Title' in parts:
                headers = [h.lower() for h in parts]
                continue
            if '---' in l: continue
            
            # Data row
            if not headers: continue # Skip untill header found
            
            if len(parts) == len(headers):
                row_data = dict(zip(headers, parts))
                parsed_rows.append(row_data)

    # Analyze Parsed
    matched_count = 0
    valid_in_report = 0
    invalid_in_report = 0
    missing_high_value = []
    
    report_keys = set()
    
    for r in parsed_rows:
        # Try to find key
        key = None
        # Try ASIN
        for k, v in r.items():
            if 'asin' in k and len(v) == 10 and v.startswith('B'):
                key = v
                break
        
        # Try EAN
        if not key:
            for k, v in r.items():
                if 'ean' in k and v.isdigit():
                    key = clean_ean(v)
                    break
        
        if key and key in canonical_map:
            report_keys.add(key)
            matched_count += 1
            status = canonical_map[key]['ValidationStatus']
            if status in ['VALID', 'LIKELY_VALID']:
                valid_in_report += 1
            else:
                invalid_in_report += 1
        else:
            # Item in report but not in PART3 map?
            # Could remain unknown
            pass

    # Coverage
    coverage_pct = matched_count / len(canonical_map) if len(canonical_map) > 0 else 0
    
    # Find Missing High Value
    # Look at PART3 rows strictly VALID and PROFIT > 10 (arbitrary threshold for "High Value" or just >0)
    # Filter full_df for items NOT in report_keys
    
    missing_df = full_df[
        (~full_df['ASIN'].isin(report_keys)) & 
        (~full_df['EAN'].apply(lambda x: clean_ean(x) if clean_ean(x) in report_keys else 'NO_MATCH').isin(report_keys))
    ]
    
    # Sort by profit
    top_missing = missing_df[missing_df['ValidationStatus'] == 'VALID'].sort_values(by=profit_col, ascending=False).head(10)
    
    missing_items_list = []
    for _, row in top_missing.iterrows():
        missing_items_list.append({
            'ASIN': row.get('ASIN'),
            'Title': row.get('SupplierTitle'),
            'Profit': row.get(profit_col),
            'Reason': 'Standard Miss'
        })
        
    return {
        "parsed_row_count": len(parsed_rows),
        "matched_count": matched_count,
        "valid_entries": valid_in_report,
        "invalid_entries": invalid_in_report,
        "validity_rate": valid_in_report / matched_count if matched_count else 0,
        "coverage_pct": coverage_pct,
        "missing_top_10": missing_items_list
    }

if __name__ == "__main__":
    main()
