import csv, re

BASE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
ANALYSIS = BASE + r"\FINAL STALE\19-04\fba_analysis_2026-04-18.csv"

def safe_float(v):
    if v is None or str(v).strip() in ('', 'nan', 'NaN', 'None', 'N/A'):
        return None
    s = str(v).strip().replace('\u00a3','').replace(',','')
    try:
        return float(s)
    except:
        return None

with open(ANALYSIS, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

# Raw count: profit > 0 AND sales > 0, ALL tiers, no cleansing
profitable_with_sales = [r for r in rows
    if (safe_float(r.get('NetProfit')) or 0) > 0
    and (safe_float(r.get('sales_value')) or 0) > 0
]

print(f"RAW: profit>0 AND sales>0 (ALL tiers, no cleansing): {len(profitable_with_sales)}")

# Break down by tier
from collections import Counter
tier_dist = Counter(r.get('tier','') for r in profitable_with_sales)
for t, c in sorted(tier_dist.items()):
    print(f"  {t}: {c}")

# Now show what was removed by each cleansing step for this subset
STOP_WORDS = {'the','and','with','for','in','of','a','an','to','by','at','on','is','it','or','&','-',''}
def meaningful_words(title):
    if not title:
        return set()
    words = re.findall(r'[a-zA-Z0-9]+', title.lower())
    return {w for w in words if w not in STOP_WORDS and len(w) > 1}

# Step 1: Remove T4
after_t4 = [r for r in profitable_with_sales if r.get('tier') != 'TIER_4_REJECTED']
print(f"\nAfter T4 removal: {len(after_t4)}")

# Step 2: Price plausibility
after_pp = []
for r in after_t4:
    sp = safe_float(r.get('SellingPrice_incVAT'))
    cp = safe_float(r.get('SupplierPrice_incVAT'))
    if sp and cp and cp > 0 and sp/cp > 20:
        overlap = len(meaningful_words(r.get('SupplierTitle','')) & meaningful_words(r.get('AmazonTitle','')))
        if overlap < 2:
            continue
    after_pp.append(r)
print(f"After price plausibility: {len(after_pp)}")

# Step 3: False match (non-EAN rows only)
after_fm = []
for r in after_pp:
    ean_exact = str(r.get('ean_exact_match','')).lower() == 'true'
    if ean_exact:
        after_fm.append(r)
        continue
    overlap = len(meaningful_words(r.get('SupplierTitle','')) & meaningful_words(r.get('AmazonTitle','')))
    if overlap >= 2:
        after_fm.append(r)
print(f"After false match: {len(after_fm)}")

# Step 4: Unit quantity
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

after_uq = []
uq_removed = []
for r in after_fm:
    s_qty, _ = parse_qty(r.get('SupplierTitle',''))
    a_qty, _ = parse_qty(r.get('AmazonTitle',''))
    if a_qty > s_qty and a_qty > 1:
        cp = safe_float(r.get('SupplierPrice_incVAT')) or 0
        profit = safe_float(r.get('NetProfit')) or 0
        if cp > 0:
            adj_profit = profit - (cp * (a_qty / s_qty) - cp)
            if adj_profit <= 0:
                uq_removed.append(r)
                continue
    after_uq.append(r)
print(f"After unit qty: {len(after_uq)} (removed {len(uq_removed)})")

# Now show tier breakdown of survivors
tier_dist2 = Counter(r.get('tier','') for r in after_uq)
print(f"\nSurvivors by tier:")
for t, c in sorted(tier_dist2.items()):
    print(f"  {t}: {c}")

# Show all survivors
print(f"\nAll {len(after_uq)} products with profit>0, sales>0 after cleansing:")
print(f"{'Tier':<25} {'Profit':>8} {'Sales':>8} {'Title':<50}")
print("-"*100)
for r in sorted(after_uq, key=lambda x: -(safe_float(x.get('sales_value')) or 0) * (safe_float(x.get('NetProfit')) or 0)):
    t = r.get('tier','')
    p = safe_float(r.get('NetProfit')) or 0
    s = safe_float(r.get('sales_value')) or 0
    st = r.get('SupplierTitle','')[:50]
    at = r.get('AmazonTitle','')[:30]
    print(f"{t:<25} {p:>8.2f} {s:>8.0f}  {st} | {at}")
