"""
EFG Housewares Product List Regeneration
========================================
Implements 3-bucket classification with rigorous match verification.
"""

import csv
import json
import os
import re
from datetime import datetime
from difflib import SequenceMatcher
from collections import defaultdict

# ====================
# CONFIG
# ====================
REPO_ROOT = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
REPORT_PATH = os.path.join(REPO_ROOT, r"OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk__sandbox__4e269fb4\fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_RECONCILED_20260410_001500.csv")
LINKING_MAP_PATH = os.path.join(REPO_ROOT, r"OUTPUTS\FBA_ANALYSIS\linking_maps\efghousewares.co.uk__sandbox__4e269fb4\linking_map.json")
OUTPUT_DIR = os.path.join(REPO_ROOT, r"OUTPUTS\PRODUCTS_LISTS")

BUCKET_C_MAX_LOSS = -2.00
BUCKET_C_MIN_SALES = 50
T2_SIM_THRESHOLD = 0.55
T3_SIM_THRESHOLD = 0.35

CATEGORY_KEYWORDS = {
    'cleaning': ['cleaner', 'cleaning', 'detergent', 'bleach', 'wipe', 'cloth', 'mop', 'brush', 'sponge', 'duster'],
    'kitchen': ['plate', 'bowl', 'cup', 'mug', 'fork', 'knife', 'spoon', 'pan', 'pot', 'cookware', 'bakeware', 'kitchen'],
    'bathroom': ['soap', 'shower', 'bath', 'toilet', 'toothbrush', 'toothpaste', 'shampoo', 'conditioner'],
    'diy': ['screw', 'nail', 'bolt', 'drill', 'saw', 'hammer', 'wrench', 'padlock', 'tape', 'cable tie', 'glue'],
    'stationery': ['pen', 'pencil', 'marker', 'notebook', 'paper', 'envelope', 'sticky', 'folder'],
    'candles': ['candle', 'tea light', 'tealight', 'incense', 'fragrance', 'air freshener', 'reed diffuser'],
    'storage': ['storage', 'box', 'container', 'bag', 'bin', 'basket', 'tub'],
    'personal_care': ['razor', 'cotton', 'emery', 'nail file', 'tweezers', 'hair', 'comb', 'mirror'],
    'garden': ['garden', 'plant', 'seed', 'pot', 'hose', 'trowel'],
    'electrical': ['battery', 'bulb', 'led', 'torch', 'plug', 'cable', 'extension'],
    'pet': ['pet', 'dog', 'cat', 'fish', 'bird'],
    'party': ['party', 'balloon', 'banner', 'decoration', 'gift', 'wrap', 'ribbon'],
    'food_wrap': ['foil', 'cling', 'parchment', 'greaseproof', 'bacofoil'],
}


# ====================
# HELPERS
# ====================

def safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val, default=0):
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    return ' '.join(text.split())


def get_similarity(a, b):
    a, b = normalize_text(a), normalize_text(b)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def extract_brand(title):
    if not title:
        return ""
    words = title.strip().split()
    if not words:
        return ""
    return words[0].upper()


def categorize_product(title):
    title_lower = normalize_text(title)
    matched_cats = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in title_lower:
                matched_cats.append(cat)
                break
    return matched_cats if matched_cats else ['uncategorized']


def categories_compatible(sup_cats, amz_cats):
    return bool(set(sup_cats) & set(amz_cats))


# ====================
# MATCH VERIFICATION
# ====================

def verify_t2_t3_match(supplier_title, amazon_title, similarity, is_ean_match):
    """
    Rigorous verification of T2/T3 matches.
    Returns (is_valid, tier, reason, confidence, validation_required)
    """
    if is_ean_match:
        # Even EAN matches need a sanity check - sometimes the EAN barcode resolves
        # to a completely unrelated product on Amazon (database errors, barcode reuse)
        if similarity < 0.20:
            # Titles are completely different - likely false EAN match
            return False, 'REJECTED', 'EAN match but titles completely unrelated (sim={:.2f}) - likely false EAN'.format(similarity), 'none', False
        return True, 'T1', 'Exact EAN match (title sim={:.2f})'.format(similarity), 'high', False

    sup_norm = normalize_text(supplier_title)
    amz_norm = normalize_text(amazon_title)
    sup_brand = extract_brand(supplier_title)
    amz_brand = extract_brand(amazon_title)
    sup_cats = categorize_product(supplier_title)
    amz_cats = categorize_product(amazon_title)

    # === REJECTION CRITERIA ===

    if similarity < 0.20:
        return False, 'REJECTED', 'Similarity too low ({:.2f})'.format(similarity), 'none', False

    if similarity < 0.45 and not categories_compatible(sup_cats, amz_cats):
        contamination_keywords = ['rc car', 'brushless', 'lego', 'building set', 'building block',
                                  'ferris wheel', 'chess', 'drone', 'robot',
                                  'toner', 'cartridge', 'laptop', 'phone case', 'headphone',
                                  'worcester', 'boiler', 'car part', 'engine', 'motor',
                                  'shed', 'furniture', 'desk', 'chair',
                                  'san pellegrino', 'sparkling', 'mineral water',
                                  'hp ', 'samsung', 'apple', 'xbox', 'playstation',
                                  'harry potter', 'retro futuristic', 'interstellar',
                                  'waterfall cabin', 'ninjago', 'hogwarts',
                                  'star wars', 'marvel', 'pokemon', 'disney',
                                  'compatible for', 'replacement for',
                                  'laptop battery', 'printer', 'vacuum cleaner',
                                  'washing machine', 'dishwasher',
                                  'dog food', 'cat food', 'harringtons',
                                  'v8 engine model', 'model kit',
                                  'shower door seal', 'olevs', 'watch',
                                  'honeywell', 'thermostat', 'valve compatible',
                                  'steam wallpaper', 'wagner']
        for ckw in contamination_keywords:
            if ckw in amz_norm:
                return False, 'REJECTED', 'Category mismatch: "{}" in Amazon title (sim={:.2f})'.format(
                    ckw, similarity), 'none', False

    # Also reject if similarity < 0.30 and categories don't match at all
    if similarity < 0.30 and not categories_compatible(sup_cats, amz_cats):
        return False, 'REJECTED', 'Low similarity ({:.2f}) with no category overlap'.format(similarity), 'none', False

    if similarity < 0.40 and sup_brand and amz_brand and sup_brand != amz_brand:
        if not categories_compatible(sup_cats, amz_cats):
            return False, 'REJECTED', 'Brand mismatch ({} vs {}) + category mismatch (sim={:.2f})'.format(
                sup_brand, amz_brand, similarity), 'none', False

    # === ACCEPTANCE CRITERIA ===

    if similarity >= T2_SIM_THRESHOLD:
        if categories_compatible(sup_cats, amz_cats):
            return True, 'T2', 'High title similarity ({:.2f}) with category match'.format(similarity), 'medium-high', True
        else:
            return True, 'T2', 'High title similarity ({:.2f}) - category uncertain'.format(similarity), 'medium', True

    if similarity >= T3_SIM_THRESHOLD:
        brand_match = sup_brand and amz_brand and sup_brand == amz_brand
        cat_match = categories_compatible(sup_cats, amz_cats)

        if brand_match and cat_match:
            return True, 'T3', 'Moderate similarity ({:.2f}) + brand match ({}) + category match'.format(
                similarity, sup_brand), 'medium', True
        elif brand_match:
            return True, 'T3', 'Moderate similarity ({:.2f}) + brand match ({})'.format(
                similarity, sup_brand), 'medium-low', True
        elif cat_match:
            return True, 'T3', 'Moderate similarity ({:.2f}) + category match'.format(similarity), 'medium-low', True
        else:
            return True, 'T3', 'Moderate similarity ({:.2f}) only - needs manual verification'.format(similarity), 'low', True

    # Between 0.25 and T3 threshold: only accept with category match
    if similarity >= 0.25:
        cat_match = categories_compatible(sup_cats, amz_cats)
        brand_match = sup_brand and amz_brand and sup_brand == amz_brand
        if cat_match and brand_match:
            return True, 'T3', 'Low similarity ({:.2f}) but brand+category match - re-check candidate'.format(similarity), 'low', True
        elif cat_match:
            return True, 'T3', 'Low similarity ({:.2f}) but category match - re-check candidate'.format(similarity), 'low', True
        else:
            return False, 'REJECTED', 'Below T3 threshold ({:.2f}) with no supporting evidence'.format(similarity), 'none', False

    return False, 'REJECTED', 'Below all thresholds ({:.2f})'.format(similarity), 'none', False


# ====================
# BUCKET ASSESSMENT
# ====================

def assess_bucket_b_inclusion(row, similarity, tier):
    profit = safe_float(row.get('NetProfit', '0'))
    roi = safe_float(row.get('ROI', '0'))
    selling_price = safe_float(row.get('SellingPrice_incVAT', '0'))
    supplier_price = safe_float(row.get('SupplierPrice_exVAT', '0'))
    fba_sellers = safe_int(row.get('fba_seller_count', '0'))
    fbm_sellers = safe_int(row.get('fbm_seller_count', '0'))

    sup_title = row.get('SupplierTitle', '')
    sup_cats = categorize_product(sup_title)

    reasons = []
    priority_score = 0

    if profit > 5.0:
        reasons.append("Strong profit margin (GBP{:.2f})".format(profit))
        priority_score += 3
    elif profit > 2.0:
        reasons.append("Decent profit margin (GBP{:.2f})".format(profit))
        priority_score += 2
    elif profit > 0.5:
        reasons.append("Marginal profit (GBP{:.2f})".format(profit))
        priority_score += 1

    if roi > 100:
        reasons.append("Very high ROI ({:.0f}%)".format(roi))
        priority_score += 2
    elif roi > 50:
        reasons.append("Good ROI ({:.0f}%)".format(roi))
        priority_score += 1

    if fba_sellers <= 1:
        reasons.append("Low FBA competition ({} sellers)".format(fba_sellers))
        priority_score += 2
    elif fba_sellers <= 3:
        reasons.append("Moderate FBA competition ({} sellers)".format(fba_sellers))
        priority_score += 1

    high_demand_cats = ['cleaning', 'kitchen', 'bathroom', 'personal_care', 'food_wrap', 'candles']
    if any(c in sup_cats for c in high_demand_cats):
        reasons.append("High-demand category ({})".format('/'.join(c for c in sup_cats if c in high_demand_cats)))
        priority_score += 1

    if supplier_price < 2.0 and selling_price > 5.0:
        reasons.append("Low source cost (GBP{:.2f}) vs Amazon price (GBP{:.2f})".format(supplier_price, selling_price))
        priority_score += 1

    if tier == 'T1':
        priority_score += 3
    elif tier == 'T2':
        priority_score += 1

    # Decision
    if tier == 'T1' and profit > 0.50:
        include = True
        rationale = "EAN-verified product with positive profit. Zero sales may reflect data timing, new listing, or seasonal dormancy."
    elif tier == 'T2' and profit > 1.0 and priority_score >= 3:
        include = True
        rationale = "Likely match with meaningful profit and supporting signals. Zero sales may reflect stale data or low visibility."
    elif tier == 'T2' and profit > 2.0:
        include = True
        rationale = "Likely match with strong profit buffer. Worth investigation despite zero recorded sales."
    elif tier == 'T3' and profit > 3.0 and priority_score >= 4:
        include = True
        rationale = "Possible match but profit is attractive enough to warrant validation. Re-check recommended."
    elif tier == 'T1' and profit > 0:
        include = True
        rationale = "EAN-verified with marginal profit. Low priority but confirmed match."
    else:
        include = False
        rationale = "Insufficient evidence to justify inclusion with zero sales."

    if priority_score >= 6:
        priority = 'HIGH'
    elif priority_score >= 4:
        priority = 'MEDIUM'
    elif priority_score >= 2:
        priority = 'LOW'
    else:
        priority = 'VERY LOW'

    return include, '; '.join(reasons) if reasons else 'No strong signals', rationale, priority


def assess_bucket_c_inclusion(row, similarity, tier):
    profit = safe_float(row.get('NetProfit', '0'))
    sales = safe_float(row.get('bought_in_past_month', '0'))
    selling_price = safe_float(row.get('SellingPrice_incVAT', '0'))
    fba_sellers = safe_int(row.get('fba_seller_count', '0'))

    sup_title = row.get('SupplierTitle', '')
    reasons = []
    priority_score = 0

    if sales >= 5000:
        reasons.append("Very high sales volume ({:.0f}/month)".format(sales))
        priority_score += 3
    elif sales >= 1000:
        reasons.append("High sales volume ({:.0f}/month)".format(sales))
        priority_score += 2
    elif sales >= 100:
        reasons.append("Moderate sales volume ({:.0f}/month)".format(sales))
        priority_score += 1

    loss_amount = abs(profit)
    if loss_amount < 0.50:
        reasons.append("Very close to breakeven (loss only GBP{:.2f})".format(loss_amount))
        priority_score += 3
    elif loss_amount < 1.0:
        reasons.append("Near breakeven (loss GBP{:.2f})".format(loss_amount))
        priority_score += 2
    elif loss_amount < 2.0:
        reasons.append("Within GBP2 of breakeven (loss GBP{:.2f})".format(loss_amount))
        priority_score += 1

    if selling_price > 0:
        pct_increase = (loss_amount / selling_price) * 100
        if pct_increase < 5:
            reasons.append("Only {:.1f}% price increase needed".format(pct_increase))
            priority_score += 2
        elif pct_increase < 10:
            reasons.append("{:.1f}% price increase needed".format(pct_increase))
            priority_score += 1

    if fba_sellers <= 2:
        reasons.append("Low FBA competition ({} sellers) - price increase feasible".format(fba_sellers))
        priority_score += 2
    elif fba_sellers <= 5:
        reasons.append("Moderate competition ({} FBA sellers)".format(fba_sellers))
        priority_score += 1

    multipack_keywords = ['pack', 'pk', 'set', 'twin', 'triple', '3pc', '4pc', '5pc', '6pc', '12pc']
    if any(kw in normalize_text(sup_title) for kw in multipack_keywords):
        reasons.append("Pack/multipack product - bundle variation potential")
        priority_score += 1

    if tier == 'T1':
        priority_score += 2
    elif tier == 'T2':
        priority_score += 1

    # Decision
    if tier == 'T1' and loss_amount < 1.0 and sales >= 100:
        include = True
        rationale = "EAN-verified with high sales and near-breakeven. Small adjustment makes this profitable."
    elif tier == 'T1' and loss_amount < 0.50:
        include = True
        rationale = "EAN-verified and extremely close to breakeven."
    elif tier in ('T1', 'T2') and sales >= 1000 and loss_amount < 1.0:
        include = True
        rationale = "High volume product very close to profitability."
    elif sales >= 5000 and loss_amount < 2.0 and tier in ('T1', 'T2'):
        include = True
        rationale = "Very high volume with manageable loss. Volume justifies investigation."
    elif priority_score >= 5:
        include = True
        rationale = "Multiple positive signals suggest path to profitability."
    else:
        include = False
        rationale = "Insufficient evidence of path to profitability."

    if priority_score >= 6:
        priority = 'HIGH'
    elif priority_score >= 4:
        priority = 'MEDIUM'
    elif priority_score >= 2:
        priority = 'LOW'
    else:
        priority = 'VERY LOW'

    return include, '; '.join(reasons) if reasons else 'No strong signals', rationale, priority


# ====================
# OUTPUT BUILDER
# ====================

def build_product_entry(row, bucket, tier, match_reason, confidence,
                        inclusion_reason, rationale, priority, validation_required, similarity):
    return {
        'supplier_product_title': row.get('SupplierTitle', ''),
        'amazon_target_title': row.get('AmazonTitle', ''),
        'match_type': 'EAN' if tier == 'T1' else 'Title',
        'tier': tier,
        'ean_status': 'Confirmed' if (row.get('EAN') and row.get('EAN_OnPage') and row.get('EAN') == row.get('EAN_OnPage')) else 'Not matched',
        'ean': row.get('EAN', ''),
        'ean_on_page': row.get('EAN_OnPage', ''),
        'asin': row.get('ASIN', ''),
        'sales_value': row.get('bought_in_past_month', '0'),
        'net_profit': row.get('NetProfit', '0'),
        'roi': row.get('ROI', '0'),
        'selling_price': row.get('SellingPrice_incVAT', '0'),
        'supplier_price_ex_vat': row.get('SupplierPrice_exVAT', '0'),
        'supplier_price_inc_vat': row.get('SupplierPrice_incVAT', '0'),
        'fba_fee': row.get('FBAFee', '0'),
        'referral_fee': row.get('ReferralFee', '0'),
        'fba_seller_count': row.get('fba_seller_count', '0'),
        'fbm_seller_count': row.get('fbm_seller_count', '0'),
        'total_offer_count': row.get('total_offer_count', '0'),
        'bucket': bucket,
        'inclusion_reason': inclusion_reason,
        'rationale': rationale,
        'confidence': confidence,
        'validation_required': 'Yes' if validation_required else 'No',
        'priority': priority,
        'match_similarity': '{:.2f}'.format(similarity),
        'match_verification_result': match_reason,
        'supplier_url': row.get('SupplierURL', ''),
        'amazon_url': row.get('AmazonURL', ''),
    }


# ====================
# MAIN
# ====================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading financial report...")
    with open(REPORT_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print("  Total rows: {}".format(len(rows)))

    print("Loading linking map...")
    with open(LINKING_MAP_PATH, 'r', encoding='utf-8') as f:
        linking_data = json.load(f)

    lm_by_url = {}
    for entry in linking_data:
        url = entry.get('supplier_url', '')
        if url:
            lm_by_url[url] = entry
    print("  Linking map entries: {} (indexed by URL: {})".format(len(linking_data), len(lm_by_url)))

    stats = {
        'total_rows': len(rows),
        'superior_excluded': 0,
        'csv_lm_contaminated': 0,
        'bucket_a': {'total': 0, 'ean': 0, 't2': 0, 't3': 0},
        'bucket_b': {'total': 0, 'ean': 0, 't2': 0, 't3': 0, 'excluded': 0},
        'bucket_c': {'total': 0, 'ean': 0, 't2': 0, 't3': 0, 'excluded': 0},
        't2_rejected': 0,
        't3_rejected': 0,
        'total_rejected_matches': 0,
    }

    bucket_a = []
    bucket_b = []
    bucket_c = []
    all_rejected = []

    print("\nProcessing rows...")
    for row in rows:
        sup_title = row.get('SupplierTitle', '')
        amz_title = row.get('AmazonTitle', '')

        # === HARD EXCLUSION: Superior brand ===
        if 'superior' in sup_title.lower() or 'superior' in amz_title.lower():
            stats['superior_excluded'] += 1
            continue

        sales = safe_float(row.get('bought_in_past_month', '0'))
        profit = safe_float(row.get('NetProfit', '0'))

        is_ean_match = bool(
            row.get('EAN') and row.get('EAN_OnPage') and
            row.get('EAN') == row.get('EAN_OnPage')
        )

        similarity = get_similarity(sup_title, amz_title)

        # === DECONTAMINATION: Cross-check CSV Amazon title vs Linking Map ===
        lm_entry = lm_by_url.get(row.get('SupplierURL', ''))
        lm_match_method = lm_entry.get('match_method', '') if lm_entry else ''
        lm_amazon_title = lm_entry.get('amazon_title', '') if lm_entry else ''

        if lm_entry and lm_amazon_title and amz_title:
            # Check if the CSV's Amazon product matches the linking map's Amazon product
            lm_vs_csv_sim = get_similarity(lm_amazon_title, amz_title)
            if lm_vs_csv_sim < 0.40:
                # CSV row is contaminated - Amazon product doesn't match linking map
                # The financial data in this row is UNRELIABLE (calculated against wrong Amazon listing)
                stats['csv_lm_contaminated'] += 1
                continue

        if lm_match_method == 'EAN':
            is_ean_match = True

        # === MATCH VERIFICATION ===
        is_valid, tier, match_reason, confidence, validation_required = verify_t2_t3_match(
            sup_title, amz_title, similarity, is_ean_match
        )

        if not is_valid:
            stats['total_rejected_matches'] += 1
            if similarity >= T2_SIM_THRESHOLD:
                stats['t2_rejected'] += 1
            elif similarity >= T3_SIM_THRESHOLD:
                stats['t3_rejected'] += 1
            all_rejected.append({
                'supplier_title': sup_title[:60],
                'amazon_title': amz_title[:60],
                'similarity': similarity,
                'reason': match_reason,
                'sales': sales,
                'profit': profit,
            })
            continue

        # === BUCKET CLASSIFICATION ===

        if sales > 0 and profit > 0:
            # BUCKET A
            entry = build_product_entry(
                row, 'A', tier, match_reason, confidence,
                'Proven demand: Sales > 0 and Profit > 0',
                'Product has demonstrated sales and positive profit margin.',
                'HIGH' if (sales >= 100 and profit >= 2) else 'MEDIUM' if (sales >= 50 or profit >= 1) else 'LOW',
                validation_required, similarity
            )
            bucket_a.append(entry)
            stats['bucket_a']['total'] += 1
            if tier == 'T1': stats['bucket_a']['ean'] += 1
            elif tier == 'T2': stats['bucket_a']['t2'] += 1
            elif tier == 'T3': stats['bucket_a']['t3'] += 1

        elif profit > 0 and sales == 0:
            # BUCKET B candidate
            include, reason, rationale, priority = assess_bucket_b_inclusion(row, similarity, tier)
            if include:
                entry = build_product_entry(
                    row, 'B', tier, match_reason, confidence,
                    reason, rationale, priority, validation_required, similarity
                )
                bucket_b.append(entry)
                stats['bucket_b']['total'] += 1
                if tier == 'T1': stats['bucket_b']['ean'] += 1
                elif tier == 'T2': stats['bucket_b']['t2'] += 1
                elif tier == 'T3': stats['bucket_b']['t3'] += 1
            else:
                stats['bucket_b']['excluded'] += 1

        elif sales > 0 and profit <= 0 and profit > BUCKET_C_MAX_LOSS:
            # BUCKET C candidate
            if sales >= BUCKET_C_MIN_SALES:
                include, reason, rationale, priority = assess_bucket_c_inclusion(row, similarity, tier)
                if include:
                    entry = build_product_entry(
                        row, 'C', tier, match_reason, confidence,
                        reason, rationale, priority, validation_required, similarity
                    )
                    bucket_c.append(entry)
                    stats['bucket_c']['total'] += 1
                    if tier == 'T1': stats['bucket_c']['ean'] += 1
                    elif tier == 'T2': stats['bucket_c']['t2'] += 1
                    elif tier == 'T3': stats['bucket_c']['t3'] += 1
                else:
                    stats['bucket_c']['excluded'] += 1

    # Sort buckets
    bucket_a.sort(key=lambda x: (-safe_float(x['sales_value']), -safe_float(x['net_profit'])))
    bucket_b.sort(key=lambda x: (-safe_float(x['net_profit']),))
    bucket_c.sort(key=lambda x: (-safe_float(x['sales_value']), safe_float(x['net_profit'])))

    # === WRITE OUTPUT FILES ===
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    all_products = bucket_a + bucket_b + bucket_c
    fieldnames = list(all_products[0].keys()) if all_products else []

    # 1. Master combined file
    master_path = os.path.join(OUTPUT_DIR, 'efghousewares_master_product_list_{}.csv'.format(timestamp))
    with open(master_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_products)
    print("\nMaster file: {} ({} products)".format(master_path, len(all_products)))

    # 2. Bucket A file
    bucket_a_path = os.path.join(OUTPUT_DIR, 'efghousewares_bucket_A_proven_demand_{}.csv'.format(timestamp))
    with open(bucket_a_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bucket_a)
    print("Bucket A: {} ({} products)".format(bucket_a_path, len(bucket_a)))

    # 3. Bucket B+C file
    bucket_bc_path = os.path.join(OUTPUT_DIR, 'efghousewares_bucket_BC_opportunities_{}.csv'.format(timestamp))
    with open(bucket_bc_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bucket_b + bucket_c)
    print("Bucket B+C: {} ({} products)".format(bucket_bc_path, len(bucket_b) + len(bucket_c)))

    # 4. JSON version
    master_json_path = os.path.join(OUTPUT_DIR, 'efghousewares_master_product_list_{}.json'.format(timestamp))
    with open(master_json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'supplier': 'efghousewares.co.uk',
                'sandbox_id': '4e269fb4',
                'source_report': os.path.basename(REPORT_PATH),
                'total_source_rows': len(rows),
                'stats': stats,
            },
            'bucket_a': bucket_a,
            'bucket_b': bucket_b,
            'bucket_c': bucket_c,
        }, f, indent=2)

    # 5. Summary file
    summary_path = os.path.join(OUTPUT_DIR, 'efghousewares_summary_{}.md'.format(timestamp))
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# EFG Housewares Product List Regeneration Summary\n\n")
        f.write("**Generated:** {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        f.write("**Supplier:** efghousewares.co.uk (sandbox 4e269fb4)\n")
        f.write("**Source report:** {}\n\n".format(os.path.basename(REPORT_PATH)))

        f.write("## Counts\n\n")
        f.write("| Metric | Count |\n")
        f.write("|--------|-------|\n")
        f.write("| Total source rows | {} |\n".format(stats['total_rows']))
        f.write("| Superior brand excluded | {} |\n".format(stats['superior_excluded']))
        f.write("| CSV/Linking Map contaminated (skipped) | {} |\n".format(stats['csv_lm_contaminated']))
        f.write("| Total matches rejected (T2/T3 verification) | {} |\n".format(stats['total_rejected_matches']))
        f.write("| **Bucket A (Proven Demand)** | **{}** |\n".format(stats['bucket_a']['total']))
        f.write("| **Bucket B (Profit/Zero-Sales)** | **{}** |\n".format(stats['bucket_b']['total']))
        f.write("| **Bucket C (Near-Profit/High-Sales)** | **{}** |\n".format(stats['bucket_c']['total']))
        f.write("| Bucket B excluded (insufficient evidence) | {} |\n".format(stats['bucket_b']['excluded']))
        f.write("| Bucket C excluded (insufficient evidence) | {} |\n".format(stats['bucket_c']['excluded']))
        total_final = stats['bucket_a']['total'] + stats['bucket_b']['total'] + stats['bucket_c']['total']
        f.write("| **TOTAL PRODUCTS IN FINAL LIST** | **{}** |\n\n".format(total_final))

        f.write("## Match Type Distribution\n\n")
        f.write("| Bucket | EAN (T1) | T2 (Likely) | T3 (Possible) | Total |\n")
        f.write("|--------|----------|-------------|---------------|-------|\n")
        for bname, bstats in [('A', stats['bucket_a']), ('B', stats['bucket_b']), ('C', stats['bucket_c'])]:
            f.write("| {} | {} | {} | {} | {} |\n".format(
                bname, bstats['ean'], bstats['t2'], bstats['t3'], bstats['total']))
        totals = {k: stats['bucket_a'][k] + stats['bucket_b'][k] + stats['bucket_c'][k] for k in ['ean', 't2', 't3', 'total']}
        f.write("| **Total** | **{}** | **{}** | **{}** | **{}** |\n\n".format(
            totals['ean'], totals['t2'], totals['t3'], totals['total']))

        f.write("## Top Priority Opportunities\n\n")

        f.write("### Bucket A - Top 15 by Profit\n\n")
        f.write("| # | Supplier Title | Amazon Title | Tier | Sales | Profit | ROI |\n")
        f.write("|---|---------------|--------------|------|-------|--------|-----|\n")
        for i, p in enumerate(sorted(bucket_a, key=lambda x: -safe_float(x['net_profit']))[:15], 1):
            f.write("| {} | {} | {} | {} | {} | {} | {}% |\n".format(
                i, p['supplier_product_title'][:40], p['amazon_target_title'][:40],
                p['tier'], p['sales_value'], p['net_profit'],
                '{:.0f}'.format(safe_float(p['roi']))))

        f.write("\n### Bucket B - Top 15 Opportunities\n\n")
        f.write("| # | Supplier Title | Amazon Title | Tier | Profit | Priority | Rationale |\n")
        f.write("|---|---------------|--------------|------|--------|----------|-----------|\n")
        for i, p in enumerate(bucket_b[:15], 1):
            f.write("| {} | {} | {} | {} | {} | {} | {} |\n".format(
                i, p['supplier_product_title'][:35], p['amazon_target_title'][:35],
                p['tier'], p['net_profit'], p['priority'], p['rationale'][:60]))

        f.write("\n### Bucket C - Top 15 Opportunities\n\n")
        f.write("| # | Supplier Title | Amazon Title | Tier | Sales | Loss | Priority | Rationale |\n")
        f.write("|---|---------------|--------------|------|-------|------|----------|-----------|\n")
        for i, p in enumerate(bucket_c[:15], 1):
            f.write("| {} | {} | {} | {} | {} | {} | {} | {} |\n".format(
                i, p['supplier_product_title'][:35], p['amazon_target_title'][:35],
                p['tier'], p['sales_value'], p['net_profit'], p['priority'], p['rationale'][:60]))

        f.write("\n## Rejected T2/T3 Matches (Sample)\n\n")
        f.write("Top 20 rejected matches by sales:\n\n")
        f.write("| Supplier Title | Amazon Title | Sim | Sales | Profit | Rejection Reason |\n")
        f.write("|---------------|--------------|-----|-------|--------|------------------|\n")
        rejected_sorted = sorted(all_rejected, key=lambda x: -x['sales'])
        for r in rejected_sorted[:20]:
            f.write("| {} | {} | {:.2f} | {:.0f} | {:.2f} | {} |\n".format(
                r['supplier_title'][:35], r['amazon_title'][:35],
                r['similarity'], r['sales'], r['profit'], r['reason'][:50]))

        f.write("\n## Assumptions and Risks\n\n")
        f.write("1. **Data staleness**: Financial data from sandbox run ~2026-04-10. Sales figures reflect Amazon's 'bought in past month' at scan time.\n")
        f.write("2. **T2/T3 matches**: All non-EAN matches are flagged with `validation_required=Yes`. These need manual or Keepa/SellerAmp verification.\n")
        f.write("3. **Zero-sales products**: Bucket B inclusions are based on profit margin, category demand signals, and competition analysis - not confirmed current sales.\n")
        f.write("4. **Near-breakeven products**: Bucket C products require price/cost optimization to become profitable.\n")
        f.write("5. **Seasonal effects**: Some products may have weak demand at analysis time but stronger demand at other times of year.\n")

    print("\nSummary file: {}".format(summary_path))

    # Console summary
    print("\n" + "=" * 80)
    print("REGENERATION COMPLETE")
    print("=" * 80)
    print("\n  Total source rows:              {}".format(stats['total_rows']))
    print("  Superior excluded:              {}".format(stats['superior_excluded']))
    print("  CSV/LM contaminated (skipped):  {}".format(stats['csv_lm_contaminated']))
    print("  Rejected matches (T2/T3 fail):  {}".format(stats['total_rejected_matches']))
    print("  ---")
    print("  BUCKET A (Proven Demand):       {}  (EAN={}, T2={}, T3={})".format(
        stats['bucket_a']['total'], stats['bucket_a']['ean'], stats['bucket_a']['t2'], stats['bucket_a']['t3']))
    print("  BUCKET B (Profit/No Sales):     {}  (EAN={}, T2={}, T3={})".format(
        stats['bucket_b']['total'], stats['bucket_b']['ean'], stats['bucket_b']['t2'], stats['bucket_b']['t3']))
    print("  BUCKET C (Near-Profit):         {}  (EAN={}, T2={}, T3={})".format(
        stats['bucket_c']['total'], stats['bucket_c']['ean'], stats['bucket_c']['t2'], stats['bucket_c']['t3']))
    print("  ---")
    total = stats['bucket_a']['total'] + stats['bucket_b']['total'] + stats['bucket_c']['total']
    print("  TOTAL IN FINAL LIST:            {}".format(total))
    print("  Bucket B excluded:              {}".format(stats['bucket_b']['excluded']))
    print("  Bucket C excluded:              {}".format(stats['bucket_c']['excluded']))
    print("  T2 rejected in verification:    {}".format(stats['t2_rejected']))
    print("  T3 rejected in verification:    {}".format(stats['t3_rejected']))


if __name__ == '__main__':
    main()
