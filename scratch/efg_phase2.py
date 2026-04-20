"""
FBA Validation Phase 2: Data Cleansing for efghousewares-co-uk
"""
import csv, re, os, json
from collections import Counter

BASE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
ANALYSIS = os.path.join(BASE, r"FINAL STALE\19-04\fba_analysis_2026-04-18.csv")

STOP_WORDS = {'the','and','with','for','in','of','a','an','to','by','at','on','is','it','or','&','-',''}

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

def safe_float(v):
    if v is None or str(v).strip() in ('', 'nan', 'NaN', 'None', 'N/A'):
        return None
    s = str(v).strip().replace('\u00a3','').replace(',','')
    try:
        return float(s)
    except:
        return None

def meaningful_words(title):
    if not title:
        return set()
    words = re.findall(r'[a-zA-Z0-9]+', title.lower())
    return {w for w in words if w not in STOP_WORDS and len(w) > 1}

def parse_qty(title):
    if not title:
        return 1, None
    for pattern, label in QTY_PATTERNS:
        m = re.search(pattern, title, re.IGNORECASE)
        if m:
            groups = m.groups()
            if groups:
                try:
                    qty = int(groups[0])
                    if 2 <= qty <= 200:
                        return qty, f"{label}={qty}"
                except:
                    pass
            elif label == 'Multipack':
                return 0, 'Multipack_unknown'
    return 1, None

def load_csv(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

rows = load_csv(ANALYSIS)
excluded = []  # (row, step, reason)
waterfall = []

def exclude(row, step, reason):
    row['_exclusion_step'] = step
    row['_exclusion_reason'] = reason
    excluded.append(row)

total_start = len(rows)

# Step 2.1: Remove T4
before = len(rows)
kept = [r for r in rows if r.get('tier') != 'TIER_4_REJECTED']
removed_t4 = [r for r in rows if r.get('tier') == 'TIER_4_REJECTED']
for r in removed_t4:
    exclude(r, '2.1', 'TIER_4_REJECTED')
rows = kept
waterfall.append(('2.1 T4 filter', before, before - len(rows), len(rows), 'Dashboard rejected'))

# Step 2.2: Price plausibility
before = len(rows)
kept = []
for r in rows:
    sp = safe_float(r.get('SellingPrice_incVAT'))
    cp = safe_float(r.get('SupplierPrice_incVAT'))
    if sp and cp and cp > 0:
        ratio = sp / cp
        stitle = meaningful_words(r.get('SupplierTitle',''))
        atitle = meaningful_words(r.get('AmazonTitle',''))
        overlap = len(stitle & atitle)
        if ratio > 20 and overlap < 2:
            exclude(r, '2.2', f'Price ratio {ratio:.1f}x with <2 word overlap')
            continue
    kept.append(r)
rows = kept
waterfall.append(('2.2 Price plausibility', before, before - len(rows), len(rows), '>20x ratio + low overlap'))

# Step 2.3: False match detection
before = len(rows)
kept = []
for r in rows:
    ean_exact = str(r.get('ean_exact_match','')).lower() == 'true'
    if ean_exact:
        kept.append(r)
        continue
    stitle = meaningful_words(r.get('SupplierTitle',''))
    atitle = meaningful_words(r.get('AmazonTitle',''))
    overlap = len(stitle & atitle)
    if overlap < 2:
        exclude(r, '2.3', f'Title overlap={overlap} words: S="{r.get("SupplierTitle","")[:60]}" A="{r.get("AmazonTitle","")[:60]}"')
        continue
    kept.append(r)
rows = kept
waterfall.append(('2.3 False match', before, before - len(rows), len(rows), '<2 meaningful word overlap'))

# Step 2.4: Unit quantity mismatch detection
before = len(rows)
kept = []
qty_match = 0
qty_mismatch_adj = 0
qty_mismatch_removed = 0
qty_unclear = 0
for r in rows:
    s_qty, s_note = parse_qty(r.get('SupplierTitle',''))
    a_qty, a_note = parse_qty(r.get('AmazonTitle',''))
    
    r['_sup_qty_parsed'] = s_qty
    r['_amz_qty_parsed'] = a_qty
    
    if s_qty == a_qty or (s_qty == 1 and a_qty == 1):
        r['Unit_Qty_Flag'] = 'MATCH'
        r['Unit_Qty_Note'] = ''
        qty_match += 1
        kept.append(r)
    elif a_qty == 0:  # Multipack unknown
        r['Unit_Qty_Flag'] = 'UNCLEAR'
        r['Unit_Qty_Note'] = f'Amazon says Multipack but qty unknown'
        qty_unclear += 1
        kept.append(r)
    elif a_qty > s_qty:
        # Recalculate profit
        cp = safe_float(r.get('SupplierPrice_incVAT')) or 0
        profit = safe_float(r.get('NetProfit')) or 0
        if cp > 0 and s_qty > 0:
            adjusted_cost = cp * (a_qty / s_qty)
            extra_cost = adjusted_cost - cp
            adjusted_profit = profit - extra_cost
            if adjusted_profit <= 0:
                r['Unit_Qty_Flag'] = 'MISMATCH_REMOVED'
                r['Unit_Qty_Note'] = f'Amz qty={a_qty} vs Sup qty={s_qty}. Adjusted profit=£{adjusted_profit:.2f}'
                qty_mismatch_removed += 1
                exclude(r, '2.4', f'Unit mismatch: Amz={a_qty} Sup={s_qty}, adj profit=£{adjusted_profit:.2f}')
                continue
            else:
                r['Unit_Qty_Flag'] = 'MISMATCH_ADJUST'
                r['Unit_Qty_Note'] = f'Amz qty={a_qty} vs Sup qty={s_qty}. Profit adjusted £{profit:.2f}->£{adjusted_profit:.2f}'
                r['NetProfit'] = f'{adjusted_profit:.2f}'
                if cp > 0:
                    r['ROI'] = f'{(adjusted_profit / adjusted_cost) * 100:.1f}'
                qty_mismatch_adj += 1
                kept.append(r)
        else:
            r['Unit_Qty_Flag'] = 'UNCLEAR'
            r['Unit_Qty_Note'] = f'Amz qty={a_qty} vs Sup qty={s_qty} but cost data missing'
            qty_unclear += 1
            kept.append(r)
    elif s_qty > a_qty:
        # Supplier is multipack, Amazon is single - potentially GOOD for seller
        r['Unit_Qty_Flag'] = 'MATCH'
        r['Unit_Qty_Note'] = f'Sup pack={s_qty}, Amz pack={a_qty} - supplier multipack sold as singles'
        qty_match += 1
        kept.append(r)
    else:
        r['Unit_Qty_Flag'] = 'UNCLEAR'
        r['Unit_Qty_Note'] = ''
        qty_unclear += 1
        kept.append(r)

rows = kept
waterfall.append(('2.4 Unit qty mismatch', before, before - len(rows), len(rows),
    f'MATCH={qty_match} ADJ={qty_mismatch_adj} REMOVED={qty_mismatch_removed} UNCLEAR={qty_unclear}'))

# Step 2.5: T3 title verification
before = len(rows)
t3_rows = [r for r in rows if r.get('tier') == 'TIER_3_NEEDS_REVIEW']
non_t3 = [r for r in rows if r.get('tier') != 'TIER_3_NEEDS_REVIEW']
t3_kept = []
t3_verdicts = []

for r in t3_rows:
    st = r.get('SupplierTitle', '')
    at = r.get('AmazonTitle', '')
    s_words = meaningful_words(st)
    a_words = meaningful_words(at)
    overlap = s_words & a_words
    overlap_count = len(overlap)
    s_total = len(s_words) if s_words else 1
    overlap_ratio = overlap_count / s_total

    # Check if core product type matches
    profit = safe_float(r.get('NetProfit')) or 0
    
    # Strong overlap = keep
    if overlap_count >= 3 and overlap_ratio >= 0.3:
        r['_t3_verdict'] = f'KEEP: {overlap_count} words overlap ({", ".join(list(overlap)[:5])})'
        t3_kept.append(r)
        t3_verdicts.append(('KEEP', st[:50], at[:50], overlap_count))
    elif overlap_count >= 2 and profit > 3:
        r['_t3_verdict'] = f'KEEP: {overlap_count} words + good profit £{profit:.2f}'
        t3_kept.append(r)
        t3_verdicts.append(('KEEP', st[:50], at[:50], overlap_count))
    else:
        r['_t3_verdict'] = f'DROP: only {overlap_count} words overlap'
        exclude(r, '2.5', f'T3 low overlap={overlap_count}: S="{st[:50]}" A="{at[:50]}"')
        t3_verdicts.append(('DROP', st[:50], at[:50], overlap_count))

rows = non_t3 + t3_kept
t3_kept_count = len(t3_kept)
t3_dropped_count = len(t3_rows) - t3_kept_count
waterfall.append(('2.5 T3 verification', before, t3_dropped_count, len(rows),
    f'Kept {t3_kept_count}, dropped {t3_dropped_count}'))

# Step 2.6: T2 title verification
before = len(rows)
t2_rows = [r for r in rows if r.get('tier') == 'TIER_2_LIKELY']
non_t2 = [r for r in rows if r.get('tier') != 'TIER_2_LIKELY']
t2_kept = []

for r in t2_rows:
    st = r.get('SupplierTitle', '')
    at = r.get('AmazonTitle', '')
    s_words = meaningful_words(st)
    a_words = meaningful_words(at)
    overlap = s_words & a_words
    overlap_count = len(overlap)
    
    # T2 has higher baseline trust - keep if 2+ word overlap
    if overlap_count >= 2:
        r['_t2_verdict'] = f'KEEP: {overlap_count} words overlap'
        t2_kept.append(r)
    else:
        # Check EAN
        ean_exact = str(r.get('ean_exact_match','')).lower() == 'true'
        if ean_exact:
            r['_t2_verdict'] = 'KEEP: EAN exact match'
            t2_kept.append(r)
        else:
            exclude(r, '2.6', f'T2 low overlap={overlap_count}: S="{st[:50]}" A="{at[:50]}"')

rows = non_t2 + t2_kept
t2_dropped = len(t2_rows) - len(t2_kept)
waterfall.append(('2.6 T2 verification', before, t2_dropped, len(rows),
    f'Kept {len(t2_kept)}, dropped {t2_dropped}'))

# Print waterfall
print("\n" + "="*60)
print("PHASE 2: DATA CLEANSING WATERFALL")
print("="*60)
print(f"{'Step':<25} {'In':>6} {'Removed':>8} {'Out':>6}  Notes")
print("-"*80)
for step, rin, rem, rout, note in waterfall:
    print(f"{step:<25} {rin:>6} {rem:>8} {rout:>6}  {note}")
print(f"\nTotal excluded: {len(excluded)}")
print(f"Total surviving: {len(rows)}")

# Save for next phases
with open(os.path.join(BASE, 'scratch', 'phase2_surviving.json'), 'w') as f:
    json.dump(rows, f)
with open(os.path.join(BASE, 'scratch', 'phase2_excluded.json'), 'w') as f:
    json.dump(excluded, f)

# Print some T3 verdict samples
print(f"\nT3 Verdicts sample (first 10 KEEP, first 10 DROP):")
keeps = [v for v in t3_verdicts if v[0]=='KEEP'][:10]
drops = [v for v in t3_verdicts if v[0]=='DROP'][:10]
for verdict, st, at, ov in keeps:
    print(f"  KEEP ({ov}w): '{st}' <-> '{at}'")
for verdict, st, at, ov in drops:
    print(f"  DROP ({ov}w): '{st}' <-> '{at}'")

print("\nPhase 2 complete.")
