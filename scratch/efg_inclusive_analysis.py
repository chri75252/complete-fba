"""
FBA Validation - Inclusive Pipeline
Considers all tiers (including T3 and high-confidence T4) for Bucket A if profit > 0 and sales > 0.
"""
import csv, re, os, json, datetime
from collections import Counter

BASE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
ANALYSIS = os.path.join(BASE, r"FINAL STALE\19-04\fba_analysis_2026-04-18.csv")
FINREPORT = os.path.join(BASE, r"OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_efghousewares-co-uk_20260413_003445.csv")
SUPPLIER = "efghousewares-co-uk"

def safe_float(v):
    if v is None or str(v).strip() in ('', 'nan', 'NaN', 'None', 'N/A'):
        return None
    s = str(v).strip().replace('\u00a3','').replace(',','')
    try:
        return float(s)
    except:
        return None

def safe_int(v):
    try: return int(v)
    except: return 0

STOP_WORDS = {'the','and','with','for','in','of','a','an','to','by','at','on','is','it','or','&','-',''}

def meaningful_words(title):
    if not title: return set()
    words = re.findall(r'[a-zA-Z0-9]+', title.lower())
    return {w for w in words if w not in STOP_WORDS and len(w) > 1}

QTY_PATTERNS = [
    (r'(\d+)\s*x\s+', 'NxProduct'),
    (r'\bx\s*(\d+)\b', 'xN'),
    (r'[Pp]ack\s*(?:of\s*)?(\d+)', 'PackOfN'),
    (r'(\d+)\s*[Pp]ack\b', 'NPack'),
    (r'(\d+)\s*[Pp][CcKk]\b', 'NPk'),
    (r'[Ss]et\s*(?:of\s*)?(\d+)', 'SetOfN'),
    (r'[Bb]ox\s*(?:of\s*)?(\d+)', 'BoxOfN'),
    (r'(\d+)\s*[Pp]ieces?', 'NPieces'),
    (r'(\d+)\s*[Cc]ount', 'NCount'),
    (r'[Mm]ultipack', 'Multipack'),
    (r'[Bb]undle\s*(?:of\s*)?(\d+)', 'BundleOfN'),
    (r'\((\d+)\)', 'ParenN'),
    (r'(\d+)\s*\u00d7', 'NMultSign'),
]

def parse_qty(title):
    if not title: return 1, None
    for pattern, label in QTY_PATTERNS:
        m = re.search(pattern, title, re.IGNORECASE)
        if m:
            groups = m.groups()
            if groups:
                try:
                    qty = int(groups[0])
                    if 2 <= qty <= 200:
                        return qty, label
                except: pass
            elif label == 'Multipack':
                return 0, 'Multipack_unknown'
    return 1, None

def normalize_title(t):
    if not t: return ''
    return re.sub(r'[^a-z0-9 ]', '', t.lower()).strip()

# 1. LOAD DATA
with open(ANALYSIS, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

with open(FINREPORT, 'r', encoding='utf-8-sig') as f:
    fin_rows = list(csv.DictReader(f))

fin_by_ean = {str(fr.get('EAN','')).strip(): fr for fr in fin_rows if str(fr.get('EAN','')).strip() not in ('nan', '')}
fin_by_asin = {str(fr.get('ASIN','')).strip(): fr for fr in fin_rows if str(fr.get('ASIN','')).strip() not in ('nan', '')}
fin_by_title = {normalize_title(fr.get('SupplierTitle','')): fr for fr in fin_rows if normalize_title(fr.get('SupplierTitle',''))}

excluded = []
def exclude(r, step, reason):
    r['_exclusion_step'] = step
    r['_exclusion_reason'] = reason
    excluded.append(r)

# 2. CLEANSING
print("--- CLEANSING ---")
kept = []

# Price Plausibility & False Match & Tier Verification & Unit Qty
for r in rows:
    st = r.get('SupplierTitle','')
    at = r.get('AmazonTitle','')
    s_words = meaningful_words(st)
    a_words = meaningful_words(at)
    overlap = len(s_words & a_words)
    ean_exact = str(r.get('ean_exact_match','')).lower() == 'true'
    tier = r.get('tier','')
    conf = safe_int(r.get('confidence_score'))
    
    # Tier 4 check
    if tier == 'TIER_4_REJECTED':
        if conf < 50 and overlap < 2 and not ean_exact:
            exclude(r, '2.1', f'T4 rejected (conf={conf}, overlap={overlap})')
            continue

    # Tier 3 check
    if tier == 'TIER_3_NEEDS_REVIEW':
        if overlap < 2 and not ean_exact:
            exclude(r, '2.1', f'T3 low overlap ({overlap})')
            continue

    # Price Plausibility
    sp = safe_float(r.get('SellingPrice_incVAT'))
    cp = safe_float(r.get('SupplierPrice_incVAT'))
    if sp and cp and cp > 0 and (sp/cp) > 20 and overlap < 2:
        exclude(r, '2.2', f'Price ratio > 20x and overlap < 2')
        continue

    # False Match
    if overlap < 2 and not ean_exact:
        exclude(r, '2.3', f'Overlap < 2 words')
        continue

    # Unit Qty
    s_qty, _ = parse_qty(st)
    a_qty, _ = parse_qty(at)
    
    if s_qty == a_qty or (s_qty == 1 and a_qty == 1):
        r['Unit_Qty_Flag'] = 'MATCH'
    elif a_qty == 0:
        r['Unit_Qty_Flag'] = 'UNCLEAR'
    elif a_qty > s_qty:
        profit = safe_float(r.get('NetProfit')) or 0
        if cp and cp > 0 and s_qty > 0:
            adj_cost = cp * (a_qty / s_qty)
            extra_cost = adj_cost - cp
            adj_profit = profit - extra_cost
            if adj_profit <= 0:
                exclude(r, '2.4', f'Unit qty mismatch: adj_profit={adj_profit:.2f}')
                continue
            r['Unit_Qty_Flag'] = 'MISMATCH_ADJUST'
            r['NetProfit'] = f"{adj_profit:.2f}"
            if cp > 0: r['ROI'] = f"{(adj_profit/adj_cost)*100:.1f}"
        else:
            r['Unit_Qty_Flag'] = 'UNCLEAR'
    elif s_qty > a_qty:
        r['Unit_Qty_Flag'] = 'MATCH'
    else:
        r['Unit_Qty_Flag'] = 'UNCLEAR'
        
    kept.append(r)

print(f"Original: {len(rows)} | Surviving: {len(kept)} | Excluded: {len(excluded)}")

# 3. BUCKETING (Inclusive)
print("\n--- BUCKETING ---")
bucket_a = []
bucket_b = []
bucket_c = []
no_bucket = []

for r in kept:
    profit = safe_float(r.get('NetProfit'))
    sales = safe_float(r.get('sales_value'))
    
    if profit is not None and profit > 0 and sales is not None and sales > 0:
        r['Bucket'] = 'A'
        r['_sort_key'] = sales * profit
        bucket_a.append(r)
    elif profit is not None and profit > 0:
        r['Bucket'] = 'B'
        r['_sort_key'] = profit
        bucket_b.append(r)
    elif sales is not None and sales > 50 and profit is not None and -3.0 <= profit <= 0.5:
        r['Bucket'] = 'C'
        r['_sort_key'] = profit
        bucket_c.append(r)
    else:
        exclude(r, '3.0', 'No bucket criteria met')
        no_bucket.append(r)

bucket_a.sort(key=lambda x: x.get('_sort_key', 0), reverse=True)
bucket_b.sort(key=lambda x: x.get('_sort_key', 0), reverse=True)
bucket_c.sort(key=lambda x: x.get('_sort_key', 0), reverse=True)

print(f"Bucket A (Profit>0 AND Sales>0): {len(bucket_a)}")
print(f"Bucket B (Profit>0, Sales unknown): {len(bucket_b)}")
print(f"Bucket C (Near Profit, Sales>50): {len(bucket_c)}")

# Tier breakdown in Bucket A
print("\nBucket A Tier Breakdown:")
tiers_a = Counter(r.get('tier','') for r in bucket_a)
for t, c in sorted(tiers_a.items()):
    print(f"  {t}: {c}")

# 4. CROSS-REFERENCE
for r in (bucket_a + bucket_b + bucket_c):
    ean = str(r.get('EAN','')).strip()
    asin = str(r.get('ASIN','')).strip()
    stitle = normalize_title(r.get('SupplierTitle',''))
    
    fin = None
    mm = None
    if ean and ean in fin_by_ean: fin = fin_by_ean[ean]; mm = 'EAN'
    elif asin and asin in fin_by_asin: fin = fin_by_asin[asin]; mm = 'ASIN'
    elif stitle and stitle in fin_by_title: fin = fin_by_title[stitle]; mm = 'SupplierTitle'
    
    if fin:
        r['FinReport_Match_Method'] = mm
        fp = safe_float(fin.get('NetProfit'))
        r['FinReport_NetProfit'] = f'{fp:.2f}' if fp is not None else ''
        ap = safe_float(r.get('NetProfit'))
        if fp is not None and ap is not None:
            r['Profit_Discrepancy'] = 'YES' if abs(ap - fp) > 1.0 else 'NO'
        else:
            r['Profit_Discrepancy'] = 'N/A'
    else:
        r['FinReport_Match_Method'] = 'NONE'
        r['FinReport_NetProfit'] = ''
        r['Profit_Discrepancy'] = 'N/A'

# 5. OUTPUT
now = datetime.datetime.now()
ts = now.strftime('%Y%m%d_%H%M%S')
dt = now.strftime('%Y%m%d')

outdir = os.path.join(BASE, 'OUTPUTS', 'PRODUCTS_LISTS', f'{SUPPLIER}_validation_{ts}')
csvdir = os.path.join(outdir, 'csvs')
os.makedirs(csvdir, exist_ok=True)

INPUT_COLS = list(rows[0].keys())
ADDON_COLS = ['Bucket', 'Unit_Qty_Flag', 'FinReport_NetProfit', 'FinReport_Match_Method', 'Profit_Discrepancy']
ALL_COLS = INPUT_COLS + ADDON_COLS

verified_path = os.path.join(csvdir, f'verified_profitable_{SUPPLIER}_{dt}.csv')
with open(verified_path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=ALL_COLS, extrasaction='ignore')
    w.writeheader()
    for r in (bucket_a + bucket_b + bucket_c):
        for col in ADDON_COLS:
            if col not in r: r[col] = ''
        w.writerow(r)

print(f"\nSaved {len(bucket_a + bucket_b + bucket_c)} products to {verified_path}")

print("\n--- TOP 20 BUCKET A PRODUCTS ---")
print(f"{'Tier':<25} {'Profit':>8} {'Sales':>8} {'SupplierTitle':<50}")
for r in bucket_a[:20]:
    t = r.get('tier','')
    p = safe_float(r.get('NetProfit')) or 0
    s = safe_float(r.get('sales_value')) or 0
    st = r.get('SupplierTitle','')[:50]
    print(f"{t:<25} {p:>8.2f} {s:>8.0f} {st}")
