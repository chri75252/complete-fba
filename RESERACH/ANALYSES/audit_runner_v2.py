
import pandas as pd
import re
import os
import difflib
import json
import numpy as np

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
    s = str(val).split('.')[0].strip()
    s = re.sub(r'[^0-9]', '', s)
    if not s: return None
    if len(s) == 12: s = '0' + s
    return s

def extract_sales(val):
    if pd.isna(val): return 0
    s = str(val).lower()
    # "100+ bought..."
    m = re.search(r'(\d+)', s)
    if m: return int(m.group(1))
    return 0

def extract_pack_qty(title):
    if not isinstance(title, str): return 1
    title = title.lower()
    m = re.search(r'pack\s*(?:of)?\s*(\d+)', title)
    if m: return int(m.group(1))
    m = re.search(r'\bx\s*(\d+)\b', title)
    if m: return int(m.group(1))
    return 1

def compute_similarity(s1, s2):
    if not isinstance(s1, str) or not isinstance(s2, str): return 0.0
    return difflib.SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

def validate_row(row):
    s_ean = clean_ean(row.get('EAN') or row.get('Supplier EAN'))
    a_ean = clean_ean(row.get('EAN_OnPage') or row.get('Amazon EAN'))
    
    s_title = str(row.get('SupplierTitle', ''))
    a_title = str(row.get('AmazonTitle', ''))
    
    s_pack = extract_pack_qty(s_title)
    a_pack = extract_pack_qty(a_title)
    
    # Conflict if pack sizes differ and imply > 1
    # Simple logic
    conflict = (s_pack != a_pack) and (s_pack > 1 or a_pack > 1)
    
    title_sim = compute_similarity(s_title, a_title)
    
    if s_ean and a_ean and s_ean == a_ean:
        if conflict: return "NEEDS_REVIEW"
        return "VALID"
    
    # Non-EAN
    if title_sim > 0.8 and not conflict: return "LIKELY_VALID"
    if title_sim > 0.6: return "POSSIBLE"
    
    return "INVALID"

# --- MAIN ---

def main():
    try:
        df = pd.read_excel(PART3_PATH)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return

    # Normalize Columns
    # Map 'bought_in_past_month' to 'Sales' if not exists
    if 'Sales' not in df.columns:
        sales_col = 'bought_in_past_month' if 'bought_in_past_month' in df.columns else None
    else:
        sales_col = 'Sales'
    
    profit_col = 'NetProfit' if 'NetProfit' in df.columns else 'Profit'

    # Logic: Status
    df['ValidationStatus'] = df.apply(validate_row, axis=1)
    
    # Logic: Sales
    if sales_col:
        df['Sales_Clean'] = df[sales_col].apply(extract_sales)
    else:
        df['Sales_Clean'] = 0

    # Baseline Stats
    baseline = {
        'total_rows': len(df),
        'sales_gt_0': int(len(df[df['Sales_Clean'] > 0])) if sales_col else -1,
        'profit_gt_0': int(len(df[df[profit_col] > 0])) if profit_col in df.columns else -1,
        'valid_count': int(len(df[df['ValidationStatus'] == 'VALID'])),
        'likely_count': int(len(df[df['ValidationStatus'] == 'LIKELY_VALID'])),
        'needs_review_count': int(len(df[df['ValidationStatus'] == 'NEEDS_REVIEW'])),
        'invalid_count': int(len(df[df['ValidationStatus'] == 'INVALID']))
    }

    # Canonical Map
    canonical_map = {}
    for idx, row in df.iterrows():
        k = str(row.get('ASIN', '')).strip() # Prefer ASIN
        if not k or k.lower() == 'nan':
            k = clean_ean(row.get('EAN'))
        if k:
            canonical_map[k] = row.to_dict()
            canonical_map[k]['_orig_idx'] = idx

    results = {"baseline": baseline, "reports": {}}

    for name, path in MD_PATHS.items():
        results["reports"][name] = process_md_report(name, path, canonical_map, df, profit_col)
    
    # Cross-Report Gap Analysis (Missing from Winner logic done in reporting phase)
    # Output the JSON
    
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer): return int(obj)
            if isinstance(obj, np.floating): return float(obj)
            if isinstance(obj, np.ndarray): return obj.tolist()
            return super(NpEncoder, self).default(obj)
            
    print("JSON_START")
    print(json.dumps(results, cls=NpEncoder, indent=2))
    print("JSON_END")

def process_md_report(name, path, canonical_map, full_df, profit_col):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e), "keys_found": []}

    # Extract table rows
    lines = [l.strip() for l in content.split('\n') if l.strip().startswith('|')]
    
    headers = []
    parsed_rows = []
    
    # Heuristic: 
    # 1. Look for typical headers
    # 2. Map row data
    
    for l in lines:
        parts = [p.strip() for p in l.split('|') if p] # Remove empty chunks from |...|...|
        if not parts: continue
        
        lower_parts = [p.lower() for p in parts]
        if 'asin' in lower_parts or 'ean' in lower_parts or 'suppliertitle' in lower_parts:
            headers = [p.lower() for p in parts]
            continue
            
        if '---' in l: continue
        
        if headers and len(parts) >= 1: # Could be loose match
            # Try to map
            row = {}
            for i, val in enumerate(parts):
                if i < len(headers):
                    row[headers[i]] = val
            parsed_rows.append(row)

    # Match to PART3
    matched_keys = []
    valid_count = 0
    invalid_count = 0
    
    for r in parsed_rows:
        key = None
        # Try ASIN first
        for k, v in r.items():
            if 'asin' in k and len(v) >= 10:
                key = v.strip()
                break
        if not key:
            for k, v in r.items():
                if 'ean' in k:
                    key = clean_ean(v)
                    break
        
        if key and key in canonical_map:
            matched_keys.append(key)
            st = canonical_map[key].get('ValidationStatus')
            if st in ['VALID', 'LIKELY_VALID']:
                valid_count += 1
            else:
                invalid_count += 1
        # Else: item in report but not in PART3 (possibly fabricated or from another source)
    
    matched_keys = list(set(matched_keys)) # Dedupe identifiers found in this report

    # Missing Analysis (Top 10 Missing Valid Items)
    # We find items in FULL_DF that are VALID and NOT in matched_keys
    # Sort by Profit
    
    missing_mask = ~full_df.index.isin([canonical_map[k]['_orig_idx'] for k in matched_keys if k in canonical_map])
    valid_mask = full_df['ValidationStatus'] == 'VALID'
    
    missing_df = full_df[missing_mask & valid_mask]
    
    if profit_col in full_df:
        top_missing = missing_df.sort_values(by=profit_col, ascending=False).head(10)
    else:
        top_missing = missing_df.head(10)
        
    missing_list = []
    for _, row in top_missing.iterrows():
        missing_list.append({
            'ASIN': row.get('ASIN'),
            'Title': row.get('SupplierTitle'),
            'Profit': row.get(profit_col, 0)
        })

    return {
        "parsed_row_count": len(parsed_rows),
        "matched_count": len(matched_keys),
        "valid_entries": valid_count,
        "invalid_entries": invalid_count,
        "validity_rate": (valid_count / len(matched_keys)) if matched_keys else 0,
        "keys_found": matched_keys, 
        "missing_top_10": missing_list
    }

if __name__ == "__main__":
    main()
