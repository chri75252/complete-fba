"""
EFG Housewares — Phase 1: Clean Data Preparation
Uses the dashboard's tier/confidence classifications directly.
Implements unit quantity mismatch detection and price plausibility gates.
"""
import csv
import math
import re
import os
from datetime import datetime
from difflib import SequenceMatcher
from collections import Counter

INPUT_FILE = r'temp\fba_analysis_2026-04-12 (1).csv'
OUTPUT_DIR = r'OUTPUTS\PRODUCTS_LISTS'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Helpers ────────────────────────────────────────────────────────────────

def pf(val):
    """Parse float, return None on failure."""
    try:
        v = float(val)
        return v if not math.isnan(v) else None
    except (ValueError, TypeError):
        return None

def title_sim(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

def shared_words(a, b, min_len=3):
    wa = {w for w in str(a).lower().split() if len(w) >= min_len}
    wb = {w for w in str(b).lower().split() if len(w) >= min_len}
    return wa & wb

# ── Pack Detection ─────────────────────────────────────────────────────────

PACK_PATTERNS = [
    re.compile(r'\bpack\s*(?:of\s*)?(\d+)\b', re.I),
    re.compile(r'\((\d+)\s*pack\)', re.I),
    re.compile(r'\b(\d+)\s*-?\s*pack\b', re.I),
    re.compile(r'\bset\s*of\s*(\d+)\b', re.I),
    re.compile(r'\bbox\s*of\s*(\d+)\b', re.I),
    re.compile(r'\b(\d+)\s*(?:pc|pcs|pieces?|count|ct)\b', re.I),
    re.compile(r'\b(\d+)\s*x\s', re.I),
    re.compile(r'\bx\s*(\d+)\b', re.I),
    re.compile(r'\((\d+)\s*(?:pk|strips?|rolls?|bottles?|pairs?|units?)\)', re.I),
    re.compile(r'\b(\d+)\s*(?:pk|strips?|rolls?|bottles?|pairs?|units?)\b', re.I),
    re.compile(r'\bmultipack\b', re.I),
]

def extract_pack_qty(title):
    """Extract the pack quantity from a title. Returns None if no pack indicator found."""
    for pat in PACK_PATTERNS:
        m = pat.search(str(title))
        if m:
            try:
                qty = int(m.group(1)) if m.lastindex else None
                if qty and qty > 1:
                    return qty
            except (ValueError, IndexError):
                if 'multipack' in str(title).lower():
                    return 2  # flag as multi but unknown qty
    return None

def detect_unit_mismatch(supplier_title, amazon_title):
    """Detect unit quantity mismatches between supplier and Amazon."""
    amz_qty = extract_pack_qty(amazon_title)
    sup_qty = extract_pack_qty(supplier_title)
    
    if amz_qty is None:
        return "MATCH", None  # No pack indicator on Amazon side
    
    if sup_qty is not None and sup_qty == amz_qty:
        return "MATCH", amz_qty  # Both titles mention same qty
    
    if sup_qty is not None and sup_qty != amz_qty:
        return "MISMATCH_CHECK", amz_qty
    
    # Amazon has pack qty, supplier doesn't mention any → likely selling singles
    if amz_qty and amz_qty > 1:
        return "MISMATCH_CHECK", amz_qty
    
    return "UNCLEAR", amz_qty

# ── False Match Detection ──────────────────────────────────────────────────

LUXURY_BRANDS = [
    'jo malone', 'versace', 'armani', 'giorgio armani', 'gucci', 'chanel',
    'prada', 'dior', 'ysl', 'yves saint laurent', 'burberry', 'tom ford',
    'dolce', 'gabbana', 'hermes', 'lancome', 'estee lauder', 'clinique',
    'mac cosmetics', 'nars', 'bobbi brown', 'la mer', 'dyson', 'kenwood',
    'kitchenaid', 'smeg', 'le creuset', 'samsung', 'apple', 'sony',
    'bose', 'nintendo', 'playstation', 'xbox', 'lego'
]

CONTAMINATION_KEYWORDS = [
    'laptop', 'phone case', 'headphone', 'printer', 'rc car', 'brushless',
    'v8 engine', 'car part', 'drone', 'tablet', 'smartphone',
    'gaming', 'console', 'wireless earbuds', 'bluetooth speaker',
]

def is_false_match(supplier_title, amazon_title, tier, sim_score):
    """Detect obvious false matches that should be rejected."""
    st = str(supplier_title).lower()
    at = str(amazon_title).lower()
    
    # Luxury brand in Amazon title but not in supplier title
    for brand in LUXURY_BRANDS:
        if brand in at and brand not in st:
            return True, f"Luxury brand mismatch: {brand} in Amazon but not supplier"
    
    # Contamination keywords in Amazon but not supplier
    for kw in CONTAMINATION_KEYWORDS:
        if kw in at and kw not in st:
            return True, f"Category contamination: {kw}"
    
    # For T3: require at least 2 meaningful shared words
    if tier == 'TIER_3_NEEDS_REVIEW':
        sw = shared_words(st, at, min_len=4)
        if len(sw) < 2:
            return True, f"T3 with <2 shared words (shared: {sw})"
    
    # For T2: require at least 1 meaningful shared word and sim > 0.4
    if tier == 'TIER_2_LIKELY':
        sw = shared_words(st, at, min_len=4)
        if len(sw) < 1 and sim_score < 0.4:
            return True, f"T2 with no shared words and low similarity"
    
    return False, ""

# ── Main Processing ────────────────────────────────────────────────────────

def process():
    with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    
    stats = Counter()
    stats['total_input'] = len(rows)
    
    # Pre-filter: only work with T1, T2, T3 (T4 already rejected by dashboard)
    working = [r for r in rows if r['tier'] in ('TIER_1_VERIFIED', 'TIER_2_LIKELY', 'TIER_3_NEEDS_REVIEW')]
    stats['after_tier4_filter'] = len(working)
    
    cleaned = []
    removal_log = []
    
    for r in working:
        st = r.get('SupplierTitle', '').strip()
        at = r.get('AmazonTitle', '').strip()
        tier = r['tier']
        
        # ── Step 1.2: Hard exclusions ──────────────────────────────────
        
        # Superior brand
        if 'superior' in st.lower() or 'superior' in at.lower():
            stats['removed_superior'] += 1
            removal_log.append((st, 'Superior brand'))
            continue
        
        # Price plausibility
        sp = pf(r.get('SupplierPrice_incVAT'))
        ap = pf(r.get('SellingPrice_incVAT'))
        sim = title_sim(st, at)
        
        if sp and ap and sp > 0:
            ratio = ap / sp
            if ratio > 20 and sim < 0.35:
                stats['removed_price_ratio'] += 1
                removal_log.append((st, f'Price ratio {ratio:.1f}x with sim {sim:.2f}'))
                continue
            if ap > 0 and ap < (sp * 0.5):
                stats['removed_underpriced'] += 1
                removal_log.append((st, f'Amazon price ({ap}) < 50% supplier ({sp})'))
                continue
        
        # False match detection
        conf_score = pf(r.get('confidence_score')) or 0
        is_false, reason = is_false_match(st, at, tier, sim)
        if is_false:
            stats['removed_false_match'] += 1
            removal_log.append((st, reason))
            continue
        
        # ── Step 1.3: Unit quantity scan ───────────────────────────────
        
        uq_flag, amz_qty = detect_unit_mismatch(st, at)
        
        profit = pf(r.get('NetProfit'))
        recalc_profit = profit  # default
        recalc_note = ''
        
        if uq_flag == 'MISMATCH_CHECK' and amz_qty and sp and profit is not None:
            true_cost = sp * amz_qty
            # Rough recalc: original profit was (selling_price - sp - fees)
            # True profit ≈ selling_price - (sp * qty) - fees
            # fees ≈ selling_price - sp - profit (from original calc)
            if ap:
                original_fees = ap - sp - profit
                recalc_profit = ap - true_cost - original_fees
                recalc_note = f'Recalculated: {amz_qty}x supplier cost. Original: {profit:.2f}, True: {recalc_profit:.2f}'
                
                if recalc_profit < 0:
                    stats['removed_qty_mismatch'] += 1
                    removal_log.append((st, f'Unit qty mismatch ({amz_qty}x): true profit = {recalc_profit:.2f}'))
                    continue
                else:
                    # Update the profit to recalculated value
                    profit = recalc_profit
        
        # ── Step 1.4: Bucket Classification ────────────────────────────
        
        sales = pf(r.get('sales_value')) or pf(r.get('bought_in_past_month'))
        
        bucket = None
        reason_text = ''
        priority = 'LOW'
        
        # Bucket A: Proven Demand (profit > 0, sales > 0, T1 or T2 ONLY)
        if profit is not None and profit > 0 and sales is not None and sales > 0:
            if tier in ('TIER_1_VERIFIED', 'TIER_2_LIKELY'):
                bucket = 'A'
                reason_text = 'Proven Demand: positive profit + confirmed sales'
                if sales >= 100 and profit >= 3: priority = 'HIGH'
                elif sales >= 50 or profit >= 1.5: priority = 'MEDIUM'
        
        # Bucket B: Positive Profit, Zero/Unknown Sales
        if bucket is None and profit is not None and profit > 0 and (sales is None or sales == 0):
            if tier == 'TIER_1_VERIFIED' and profit > 1.0:
                bucket = 'B'
                reason_text = 'T1 EAN match with positive margin, unknown sales'
                priority = 'MEDIUM' if profit > 5 else 'LOW'
            elif tier == 'TIER_2_LIKELY' and profit > 3.0 and sim >= 0.5:
                bucket = 'B'
                reason_text = 'T2 likely match with good margin, unknown sales'
                priority = 'LOW'
            elif tier == 'TIER_3_NEEDS_REVIEW' and profit > 5.0 and sim >= 0.5:
                bucket = 'B'
                reason_text = 'T3 possible match with high margin, needs validation'
                priority = 'LOW'
        
        # Bucket C: Near-Profit, High Sales (T1 + T2 ONLY, NO T3)
        if bucket is None and sales is not None and sales >= 50:
            if profit is not None and profit <= 0 and profit > -3.0:
                if tier in ('TIER_1_VERIFIED', 'TIER_2_LIKELY'):
                    bucket = 'C'
                    reason_text = f'Near-breakeven ({profit:.2f}) with {int(sales)} monthly sales'
                    if sales >= 200 and profit > -1: priority = 'HIGH'
                    elif sales >= 100 or profit > -1.5: priority = 'MEDIUM'
        
        if bucket is None:
            continue
        
        # Build output row
        out = {
            'Supplier_Title': st,
            'Amazon_Title': at,
            'ASIN': r.get('ASIN', ''),
            'EAN': r.get('EAN', ''),
            'Match_Type': 'EAN' if tier == 'TIER_1_VERIFIED' else 'Title',
            'Tier': tier.replace('TIER_1_VERIFIED', 'T1').replace('TIER_2_LIKELY', 'T2').replace('TIER_3_NEEDS_REVIEW', 'T3'),
            'Confidence_Score': r.get('confidence_score', ''),
            'EAN_Exact_Match': r.get('ean_exact_match', ''),
            'Sales': sales if sales is not None else 'Unknown',
            'Net_Profit': round(profit, 2) if profit is not None else '',
            'ROI': r.get('ROI', ''),
            'Supplier_Price': r.get('SupplierPrice_incVAT', ''),
            'Amazon_Price': r.get('SellingPrice_incVAT', ''),
            'Bucket': bucket,
            'Inclusion_Reason': reason_text,
            'Confidence': 'HIGH' if tier == 'TIER_1_VERIFIED' else 'MEDIUM' if tier == 'TIER_2_LIKELY' else 'LOW',
            'Validation_Required': 'No' if tier == 'TIER_1_VERIFIED' else 'Yes',
            'Priority': priority,
            'Similarity': round(sim, 2),
            'Unit_Qty_Flag': uq_flag,
            'Unit_Qty_Note': recalc_note,
            'Category': r.get('Category', ''),
            'Supplier_URL': r.get('SupplierURL', ''),
            'Amazon_URL': r.get('AmazonURL', ''),
            'FBA_Sellers': r.get('fba_seller_count', ''),
            'Dashboard_Flags': r.get('flags', ''),
        }
        cleaned.append(out)
    
    # ── Sort ───────────────────────────────────────────────────────────
    
    def sort_key(x):
        bk = 0 if x['Bucket'] == 'A' else 1 if x['Bucket'] == 'B' else 2
        pr = 0 if x['Priority'] == 'HIGH' else 1 if x['Priority'] == 'MEDIUM' else 2
        pv = -x['Net_Profit'] if isinstance(x['Net_Profit'], (int, float)) else 0
        return (bk, pr, pv)
    
    cleaned.sort(key=sort_key)
    
    # ── Save ───────────────────────────────────────────────────────────
    
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    fields = list(cleaned[0].keys()) if cleaned else []
    
    bucket_a = [r for r in cleaned if r['Bucket'] == 'A']
    bucket_bc = [r for r in cleaned if r['Bucket'] in ('B', 'C')]
    
    def save_csv(filename, data):
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(data)
        return path
    
    p1 = save_csv(f'efghousewares_VALIDATED_master_{ts}.csv', cleaned)
    p2 = save_csv(f'efghousewares_VALIDATED_bucketA_{ts}.csv', bucket_a)
    p3 = save_csv(f'efghousewares_VALIDATED_bucketBC_{ts}.csv', bucket_bc)
    
    # ── Stats ──────────────────────────────────────────────────────────
    
    print("=" * 60)
    print("PHASE 1 RESULTS")
    print("=" * 60)
    print(f"Input rows: {stats['total_input']}")
    print(f"After T4 filter: {stats['after_tier4_filter']}")
    print(f"Removed - Superior brand: {stats['removed_superior']}")
    print(f"Removed - Price ratio gate: {stats['removed_price_ratio']}")
    print(f"Removed - Underpriced: {stats['removed_underpriced']}")
    print(f"Removed - False match: {stats['removed_false_match']}")
    print(f"Removed - Qty mismatch (negative profit): {stats['removed_qty_mismatch']}")
    print(f"Final cleaned rows: {len(cleaned)}")
    print()
    
    tier_dist = Counter(r['Tier'] for r in cleaned)
    print("Tier distribution:")
    for t, c in sorted(tier_dist.items()):
        print(f"  {t}: {c}")
    
    bucket_dist = Counter(r['Bucket'] for r in cleaned)
    print(f"\nBucket distribution:")
    for b, c in sorted(bucket_dist.items()):
        print(f"  Bucket {b}: {c}")
    
    uq_dist = Counter(r['Unit_Qty_Flag'] for r in cleaned)
    print(f"\nUnit qty flags:")
    for f_, c in sorted(uq_dist.items()):
        print(f"  {f_}: {c}")
    
    # Show MISMATCH_CHECK items that survived (positive recalculated profit)
    mismatches = [r for r in cleaned if r['Unit_Qty_Flag'] == 'MISMATCH_CHECK']
    if mismatches:
        print(f"\nMISMATCH_CHECK items still in list ({len(mismatches)}):")
        for r in mismatches[:10]:
            print(f"  [{r['Tier']}] {r['Supplier_Title'][:50]} -> {r['Amazon_Title'][:50]}")
            print(f"    Profit: {r['Net_Profit']}, Note: {r['Unit_Qty_Note']}")
    
    # Show top 5 removals by reason
    reason_dist = Counter(reason for _, reason in removal_log)
    print(f"\nTop removal reasons:")
    for reason, count in reason_dist.most_common(10):
        print(f"  {count}x: {reason[:80]}")
    
    # Bucket A T3 check (should be 0)
    a_t3 = sum(1 for r in bucket_a if r['Tier'] == 'T3')
    print(f"\nBucket A T3 count (should be 0): {a_t3}")
    c_t3 = sum(1 for r in cleaned if r['Bucket'] == 'C' and r['Tier'] == 'T3')
    print(f"Bucket C T3 count (should be 0): {c_t3}")
    
    print(f"\nFiles saved:")
    print(f"  Master: {p1}")
    print(f"  Bucket A: {p2}")
    print(f"  Bucket BC: {p3}")
    
    # Top 10 by profit*sales for Bucket A (for Phase 2 validation)
    print("\n" + "=" * 60)
    print("TOP 15 BUCKET A (for Phase 2 validation)")
    print("=" * 60)
    for r in bucket_a[:15]:
        s = r['Sales'] if r['Sales'] != 'Unknown' else 0
        score = float(r['Net_Profit']) * float(s) if isinstance(s, (int, float)) else 0
        print(f"[{r['Tier']}] P={r['Net_Profit']}, S={r['Sales']}, UQ={r['Unit_Qty_Flag']}")
        print(f"  S: {r['Supplier_Title'][:60]}")
        print(f"  A: {r['Amazon_Title'][:60]}")
        print(f"  ASIN: {r['ASIN']}, URL: {r['Amazon_URL']}")
        print()
    
    print("=" * 60)
    print("TOP 10 BUCKET B (for Phase 2 validation)")
    print("=" * 60)
    for r in bucket_bc[:10]:
        if r['Bucket'] != 'B': continue
        print(f"[{r['Tier']}] P={r['Net_Profit']}, S={r['Sales']}, UQ={r['Unit_Qty_Flag']}")
        print(f"  S: {r['Supplier_Title'][:60]}")
        print(f"  A: {r['Amazon_Title'][:60]}")
        print(f"  ASIN: {r['ASIN']}, URL: {r['Amazon_URL']}")
        print()
    
    bucket_c_items = [r for r in cleaned if r['Bucket'] == 'C']
    print("=" * 60)
    print("TOP 10 BUCKET C (for Phase 2 validation)")
    print("=" * 60)
    for r in bucket_c_items[:10]:
        print(f"[{r['Tier']}] P={r['Net_Profit']}, S={r['Sales']}, UQ={r['Unit_Qty_Flag']}")
        print(f"  S: {r['Supplier_Title'][:60]}")
        print(f"  A: {r['Amazon_Title'][:60]}")
        print(f"  ASIN: {r['ASIN']}, URL: {r['Amazon_URL']}")
        print()


if __name__ == '__main__':
    process()
