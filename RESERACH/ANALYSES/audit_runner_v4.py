
import pandas as pd
import re
import os
import difflib
import json
import numpy as np

PART3_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx"
MD_PATHS = {
    "REPORT_20251224.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_20251224.md",
    "REPORT_2512240724.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240724.md",
    "REPORT_2512240124.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240124.md",
    "REPORT_2512240128.md": r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240128.md"
}
OUTPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\audit_final.json"

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
    m = re.search(r'(\d+)', s)
    if m: return int(m.group(1))
    return 0

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

def validate_row(row):
    s_ean = clean_ean(row.get('EAN') or row.get('Supplier EAN'))
    a_ean = clean_ean(row.get('EAN_OnPage') or row.get('Amazon EAN'))
    s_title = str(row.get('SupplierTitle', ''))
    a_title = str(row.get('AmazonTitle', ''))
    s_pack = extract_pack_qty(s_title)
    a_pack = extract_pack_qty(a_title)
    conflict = (s_pack != a_pack) and (s_pack > 1 or a_pack > 1)
    title_sim = compute_similarity(s_title, a_title)
    
    if s_ean and a_ean and s_ean == a_ean:
        if conflict: return "NEEDS_REVIEW"
        return "VALID"
    if title_sim > 0.8 and not conflict: return "LIKELY_VALID"
    if title_sim > 0.6: return "POSSIBLE"
    return "INVALID"

def main():
    try:
        df = pd.read_excel(PART3_PATH)
    except Exception as e:
        with open(OUTPUT_FILE, 'w') as f:
            json.dump({"error": str(e)}, f)
        return

    profit_col = 'NetProfit' if 'NetProfit' in df.columns else 'Profit'
    
    if 'bought_in_past_month' in df.columns:
        df['Sales_Clean'] = df['bought_in_past_month'].apply(extract_sales)
        sales_col_status = "Used bought_in_past_month"
    else:
        df['Sales_Clean'] = 0
        sales_col_status = "Missing"

    df['ValidationStatus'] = df.apply(validate_row, axis=1)

    baseline = {
        'total_rows': len(df),
        'sales_gt_0': int(len(df[df['Sales_Clean'] > 0])),
        'profit_gt_0': int(len(df[df[profit_col] > 0])) if profit_col in df.columns else 0,
        'valid_count': int(len(df[df['ValidationStatus'] == 'VALID'])),
        'likely_count': int(len(df[df['ValidationStatus'] == 'LIKELY_VALID'])),
        'invalid_count': int(len(df[df['ValidationStatus'] == 'INVALID']))
    }
    
    canonical_map = {}
    for idx, row in df.iterrows():
        k = str(row.get('ASIN', '')).strip()
        if not k or k.lower() == 'nan':
            k = clean_ean(row.get('EAN'))
        if k:
            canonical_map[k] = row.to_dict()
            canonical_map[k]['_orig_idx'] = idx

    results = {"baseline": baseline, "reports": {}}
    report_keys = {}

    for name, path in MD_PATHS.items():
        res, keys = process_md_report(name, path, canonical_map, df, profit_col)
        results["reports"][name] = res
        report_keys[name] = set(keys)

    best_score = -1
    best_report = None
    
    for name, data in results["reports"].items():
        score = (data['validity_rate'] * 0.7) + (data['coverage_pct'] * 0.3)
        data['calculated_score'] = score
        if score > best_score:
            best_score = score
            best_report = name
            
    results['winner'] = best_report
    results['gaps'] = {}
    
    if best_report:
        winner_keys = report_keys[best_report]
        for other, keys in report_keys.items():
            if other == best_report: continue
            
            diff = keys - winner_keys
            diff_items = []
            for k in diff:
                if k in canonical_map:
                    row = canonical_map[k]
                    diff_items.append({
                        'ASIN': k,
                        'Title': row.get('SupplierTitle', 'Unknown'),
                        'Profit': row.get(profit_col, 0),
                        'Status': row.get('ValidationStatus')
                    })
            diff_items.sort(key=lambda x: x['Profit'] if x['Profit'] else 0, reverse=True)
            results['gaps'][f"In_{other}_MissingFrom_{best_report}"] = diff_items[:10]

    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer): return int(obj)
            if isinstance(obj, np.floating): return float(obj)
            if isinstance(obj, np.ndarray): return obj.tolist()
            if isinstance(obj, set): return list(obj)
            return super(NpEncoder, self).default(obj)

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, cls=NpEncoder, indent=2)

def process_md_report(name, path, canonical_map, full_df, profit_col):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return {"error": "File not found"}, []

    lines = [l.strip() for l in content.split('\n') if l.strip().startswith('|')]
    headers = []
    parsed_rows = []
    
    for l in lines:
        parts = [p.strip() for p in l.split('|') if p]
        if not parts: continue
        low_parts = [p.lower() for p in parts]
        if 'asin' in low_parts or 'ean' in low_parts:
            headers = low_parts
            continue
        if '---' in l: continue
        if headers and len(parts) >= 1:
            row = {}
            for i, val in enumerate(parts):
                if i < len(headers):
                    row[headers[i]] = val
            parsed_rows.append(row)

    matched_keys = []
    valid_count = 0
    invalid_count = 0
    
    for r in parsed_rows:
        key = None
        for k, v in r.items():
            if 'asin' in k and len(v) >= 10:
                key = v.strip(); break
        if not key:
            for k, v in r.items():
                if 'ean' in k:
                    key = clean_ean(v); break
        
        if key and key in canonical_map:
            matched_keys.append(key)
            if canonical_map[key]['ValidationStatus'] in ['VALID', 'LIKELY_VALID']:
                valid_count += 1
            else:
                invalid_count += 1
    
    matched_keys_set = set(matched_keys)
    
    missing_mask = ~full_df.index.isin([canonical_map[k]['_orig_idx'] for k in matched_keys_set if k in canonical_map])
    valid_mask = full_df['ValidationStatus'] == 'VALID'
    missing_df = full_df[missing_mask & valid_mask]
    
    if profit_col in full_df:
        top_missing = missing_df.sort_values(by=profit_col, ascending=False).head(10)
    else:
        top_missing = missing_df.head(10)

    miss_list = []
    for _, row in top_missing.iterrows():
        miss_list.append({
            'ASIN': row.get('ASIN'),
            'Title': row.get('SupplierTitle'),
            'Profit': row.get(profit_col, 0)
        })

    stats = {
        "parsed_row_count": len(parsed_rows),
        "matched_count": len(matched_keys_set),
        "valid_entries": valid_count,
        "invalid_entries": invalid_count,
        "validity_rate": (valid_count / len(matched_keys)) if matched_keys else 0,
        "coverage_pct": len(matched_keys_set) / len(canonical_map) if len(canonical_map) else 0,
        "missing_top_10_from_part3": miss_list
    }
    return stats, list(matched_keys_set)

if __name__ == "__main__":
    main()
