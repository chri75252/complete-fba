"""
Phase 3: Apply all Phase 2 validation findings and save updated files.
Incorporates:
- Bucket A browser validation results
- Bucket B browser validation results  
- Bucket C price movement validation results
- Tavily market research signals
"""
import csv
import sys
import os
from datetime import datetime
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

INPUT_FILE = 'OUTPUTS/PRODUCTS_LISTS/efghousewares_VALIDATED_master_20260413_021542.csv'
OUTPUT_DIR = 'OUTPUTS/PRODUCTS_LISTS'

# ── Phase 2 Validation Findings ────────────────────────────────────────────

# Bucket A: Browser validation results
# Products 1-8 were checked; most are legitimate T1/T2 matches
BUCKET_A_REMOVALS = set()  # ASINs to remove
BUCKET_A_FLAGS = {
    # Elbow Grease: confirmed 3-pack mismatch. Supplier sells 1 for ~£1.60, Amazon sells 3-pack.
    'B0CCJS5GKB': 'MISMATCH_CONFIRMED',
    # Beaufort 600ML matched to 13L container — wrong product
    'B0046MHRMM': 'FALSE_MATCH',
}
# The Beaufort matches (two rows for 600ml and 1L both mapped to 13L) are false
BUCKET_A_REMOVALS.add('B0046MHRMM')

# Bucket B: Browser validation results
BUCKET_B_REMOVALS = {
    'B07SPY1BLS',  # Fire Basket — unavailable/dead listing
}
BUCKET_B_UPGRADES = set()  # products confirmed with sales badge
BUCKET_B_DOWNGRADES = {
    # Rysons products — all active but no sales badges, inflated prices, ghost listings
    'B0D6NCDCLW', 'B09X617B1M', 'B0CJM9F5GD', 'B09WJ9RYG9', 'B0CJ9PYZZ9',
}

# Bucket C: Price movement validation results
BUCKET_C_FLIPS = {
    # These products have seen price increases since January -> now profitable
    'B010LFSDL6': {'current_price': 6.69, 'delta': 1.28, 'verdict': 'FLIP_TO_PROFIT'},   # Status Luggage Scale
    'B07K544FNT': {'current_price': 4.99, 'delta': 0.69, 'verdict': 'FLIP_TO_PROFIT'},   # Amtech Stubby Screwdriver
    'B001KOTNM6': {'current_price': 7.78, 'delta': 1.23, 'verdict': 'FLIP_TO_PROFIT'},   # Rolson Pipe Cutter
    'B003XKMSAE': {'current_price': 6.99, 'delta': 0.70, 'verdict': 'FLIP_TO_PROFIT'},   # Amtech Hammer
    'B0FG32Q5GB': {'current_price': 14.29, 'delta': 8.00, 'verdict': 'FLIP_TO_PROFIT'},  # Lynx Gift Set
    'B003XKPUSQ': {'current_price': 5.70, 'delta': 0.91, 'verdict': 'FLIP_TO_PROFIT'},   # Amtech LED Torch
}
BUCKET_C_STILL_NEG = {
    'B001DYUQZG',  # Kilner jar — price crashed from £11.99 to £8.77
    'B00JPL97SQ',  # Sealapack bag clips — price dropped from £3.29 to £2.99
    'B09NDK68VX',  # Chef Aid Ladle — price flat at £3.99
    'B00EWKQTZ4',  # Chef Aid Oven Thermometer — price barely moved (£5.99 to £6.01, not enough)
}

# Tavily market signals
STRONG_CATEGORIES = [
    'Household Cleaning',  # Confirmed high and growing demand
    'Car Air Fresheners',  # Growing demand, Little Trees strong brand
    'DIY / Home Improvement',  # Spring 2026 market growing 4.3% annually
    'Kitchen Utensils',  # Chef Aid trending up per Tavily
]

WEAK_CATEGORIES = [
    'Kilner',  # Price crashed, not confirmed demand
]

# ── Process ────────────────────────────────────────────────────────────────

with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

stats = Counter()
stats['input'] = len(rows)

updated = []

for r in rows:
    asin = r.get('ASIN', '')
    bucket = r.get('Bucket', '')
    
    # ── Bucket A removals ──
    if bucket == 'A' and asin in BUCKET_A_REMOVALS:
        stats['a_removed'] += 1
        continue
    
    # ── Bucket A flags ──
    if bucket == 'A' and asin in BUCKET_A_FLAGS:
        flag = BUCKET_A_FLAGS[asin]
        if flag == 'FALSE_MATCH':
            stats['a_removed'] += 1
            continue
        elif flag == 'MISMATCH_CONFIRMED':
            r['Unit_Qty_Flag'] = 'MISMATCH_CONFIRMED'
            r['Confidence'] = 'LOW'
            r['Priority'] = 'LOW'
            r['Validation_Required'] = 'Yes'
    
    # ── Bucket B removals / downgrades ──
    if bucket == 'B':
        if asin in BUCKET_B_REMOVALS:
            stats['b_removed'] += 1
            continue
        if asin in BUCKET_B_DOWNGRADES:
            r['Confidence'] = 'LOW'
            r['Priority'] = 'LOW'
            r['Validation_Required'] = 'Yes'
            r['Dashboard_Flags'] = (r.get('Dashboard_Flags', '') + ' | Rysons ghost listing — no sales badge observed').strip(' |')
            stats['b_downgraded'] += 1
        if asin in BUCKET_B_UPGRADES:
            r['Confidence'] = 'HIGH'
            r['Priority'] = 'HIGH'
            r['Validation_Required'] = 'No'
            stats['b_upgraded'] += 1
    
    # ── Bucket C price movement ──
    if bucket == 'C':
        if asin in BUCKET_C_FLIPS:
            flip = BUCKET_C_FLIPS[asin]
            r['Confidence'] = 'HIGH'
            r['Priority'] = 'HIGH'
            r['Validation_Required'] = 'No'
            r['Dashboard_Flags'] = (r.get('Dashboard_Flags', '') + 
                ' | PRICE FLIPPED: Current ' + str(flip['current_price']) + 
                ', Delta +' + str(flip['delta'])).strip(' |')
            r['Inclusion_Reason'] = 'UPGRADED: Price increased since Jan 8, now profitable'
            # Update the bucket to A since it's now profitable
            r['Bucket'] = 'A'
            stats['c_flipped'] += 1
        elif asin in BUCKET_C_STILL_NEG:
            stats['c_removed'] += 1
            continue  # Remove — confirmed still negative
    
    # ── Category-level confidence boost (from Tavily) ──
    cat = r.get('Category', '').lower()
    for sc in STRONG_CATEGORIES:
        if sc.lower() in cat:
            if r['Priority'] == 'LOW':
                r['Priority'] = 'MEDIUM'
            break
    
    updated.append(r)

# ── Sort ───────────────────────────────────────────────────────────────
def sort_key(x):
    bk = 0 if x['Bucket'] == 'A' else 1 if x['Bucket'] == 'B' else 2
    pr = 0 if x['Priority'] == 'HIGH' else 1 if x['Priority'] == 'MEDIUM' else 2
    try:
        pv = -float(x['Net_Profit'])
    except:
        pv = 0
    return (bk, pr, pv)

updated.sort(key=sort_key)

# ── Save ───────────────────────────────────────────────────────────────
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
fields = list(updated[0].keys()) if updated else []

master = updated
bucket_a = [r for r in updated if r['Bucket'] == 'A']
bucket_bc = [r for r in updated if r['Bucket'] in ('B', 'C')]

def save_csv(filename, data):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(data)
    return path

p1 = save_csv('efghousewares_VALIDATED_master_' + ts + '.csv', master)
p2 = save_csv('efghousewares_VALIDATED_bucketA_' + ts + '.csv', bucket_a)
p3 = save_csv('efghousewares_VALIDATED_bucketBC_' + ts + '.csv', bucket_bc)

# ── Reporting ──────────────────────────────────────────────────────────

print("=" * 60)
print("PHASE 3 RESULTS — FINAL VALIDATED LIST")
print("=" * 60)
print("Input rows (from Phase 1): " + str(stats['input']))
print("Bucket A removed (false match): " + str(stats['a_removed']))
print("Bucket B removed (dead listing): " + str(stats['b_removed']))
print("Bucket B downgraded (ghost/no sales): " + str(stats['b_downgraded']))
print("Bucket B upgraded (confirmed sales): " + str(stats['b_upgraded']))
print("Bucket C flipped to profit (price increased): " + str(stats['c_flipped']))
print("Bucket C removed (still negative): " + str(stats['c_removed']))
print("Final total: " + str(len(master)))
print()

tier_dist = Counter(r['Tier'] for r in master)
print("Tier distribution:")
for t in sorted(tier_dist): print("  " + t + ": " + str(tier_dist[t]))

bucket_dist = Counter(r['Bucket'] for r in master)
print("\nBucket distribution:")
for b in sorted(bucket_dist): print("  Bucket " + b + ": " + str(bucket_dist[b]))

priority_dist = Counter(r['Priority'] for r in master)
print("\nPriority distribution:")
for p in sorted(priority_dist): print("  " + p + ": " + str(priority_dist[p]))

conf_dist = Counter(r['Confidence'] for r in master)
print("\nConfidence distribution:")
for c in sorted(conf_dist): print("  " + c + ": " + str(conf_dist[c]))

uq_dist = Counter(r['Unit_Qty_Flag'] for r in master)
print("\nUnit Qty Flags:")
for u in sorted(uq_dist): print("  " + u + ": " + str(uq_dist[u]))

# Top 10 highest conviction opportunities
print("\n" + "=" * 60)
print("TOP 10 HIGHEST-CONVICTION OPPORTUNITIES")
print("=" * 60)
high_conviction = [r for r in master if r['Confidence'] == 'HIGH']
high_conviction.sort(key=lambda x: (-float(x['Net_Profit']) if x['Net_Profit'] else 0))
for i, r in enumerate(high_conviction[:10]):
    print(str(i+1) + ". [" + r['Tier'] + "/" + r['Bucket'] + "] " + r['Supplier_Title'][:50])
    print("   -> " + r['Amazon_Title'][:50])
    print("   Profit: " + str(r['Net_Profit']) + ", Sales: " + str(r['Sales']) + 
          ", UQ: " + r['Unit_Qty_Flag'] + ", ASIN: " + r['ASIN'])
    print()

# MISMATCH_CHECK items
mm = [r for r in master if r['Unit_Qty_Flag'] in ('MISMATCH_CHECK', 'MISMATCH_CONFIRMED')]
print("Unit qty mismatches requiring manual review: " + str(len(mm)))
for r in mm:
    print("  [" + r['Tier'] + "] " + r['Supplier_Title'][:40] + " -> " + r['Amazon_Title'][:40])
    print("    Profit: " + str(r['Net_Profit']) + ", Note: " + str(r.get('Unit_Qty_Note', ''))[:80])

print("\nFiles saved:")
print("  " + p1)
print("  " + p2)
print("  " + p3)
