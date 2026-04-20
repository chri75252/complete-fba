import json, os
import pandas as pd

base = r'OUTPUTS\FBA_ANALYSIS\linking_maps\efghousewares.co.uk'

# Load the target report's EANs
df = pd.read_csv(
    r'OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_ALL_linking_map_20260108_005639.csv',
    engine='python', on_bad_lines='skip', encoding_errors='replace',
    dtype={'EAN': str}
)
report_eans = set(df['EAN'].dropna().astype(str).values)
report_asins = set(df['ASIN'].dropna().astype(str).values)
print(f"Target report: {len(df)} rows, {len(report_eans)} unique EANs, {len(report_asins)} unique ASINs")
print()

# For each linking map, count how many of the report's EANs it contains
for f in sorted(os.listdir(base)):
    if not f.endswith('.json'):
        continue
    fpath = os.path.join(base, f)
    if os.path.getsize(fpath) < 10:
        continue
    try:
        with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
            content = fh.read()
        # Try to parse; if broken, skip
        try:
            data = json.loads(content)
        except:
            # Try to fix common issues
            content_fixed = content.rstrip().rstrip(',')
            if not content_fixed.endswith(']'):
                content_fixed += ']'
            try:
                data = json.loads(content_fixed)
            except:
                print(f"{f:<45} PARSE_ERROR - skipping")
                continue
        
        if not isinstance(data, list):
            print(f"{f:<45} NOT_A_LIST (type={type(data).__name__})")
            continue
            
        lm_eans = set()
        lm_asins = set()
        for entry in data:
            if isinstance(entry, dict):
                ean = entry.get('supplier_ean', '')
                asin = entry.get('amazon_asin', '')
                if ean:
                    lm_eans.add(str(ean))
                if asin:
                    lm_asins.add(str(asin))
        
        ean_overlap = len(report_eans & lm_eans)
        asin_overlap = len(report_asins & lm_asins)
        
        print(f"{f:<45} entries={len(data):>6}  EAN_overlap={ean_overlap:>6}/{len(report_eans)}  ASIN_overlap={asin_overlap:>6}/{len(report_asins)}  LM_EANs={len(lm_eans):>6}  LM_ASINs={len(lm_asins):>6}")
    except Exception as e:
        print(f"{f:<45} ERROR: {str(e)[:80]}")
