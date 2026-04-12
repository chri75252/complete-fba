import csv
import math
import re
from difflib import SequenceMatcher
from pathlib import Path

def s_ratio(a, b):
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

def has_contamination(title):
    t = str(title).lower()
    bad = ['lego', 'star wars', 'harry potter', 'ninjago', 'hogwarts', 'marvel', 'pokemon', 'disney',
           'laptop', 'phone case', 'headphone', 'printer', 'samsung', 'rc car', 'brushless', 
           'v8 engine', 'car part', 'engine', 'motor', 'dog food', 'cat food']
    return any(b in t for b in bad)

def determine_tier_and_confidence(ean_match, s_title, a_title):
    sim = s_ratio(s_title, a_title)
    if ean_match:
        if sim < 0.15 and not any(w in str(a_title).lower() for w in str(s_title).lower().split() if len(w)>3):
            return "REJECT", "Mismatched / False EAN", sim
        return "T1", "HIGH", sim
    elif sim >= 0.55:
        return "T2", "MEDIUM", sim
    elif sim >= 0.35:
        if has_contamination(a_title) and not has_contamination(s_title):
            return "REJECT", "Contamination", sim
        return "T3", "LOW", sim
    else:
        return "REJECT", "Low similarity", sim

def category_score(title):
    t = str(title).lower()
    if any(k in t for k in ['clean', 'wipe', 'mop', 'sponge', 'bleach', 'detergent']): return 2
    if any(k in t for k in ['kitchen', 'plate', 'bowl', 'mug', 'pan', 'pot', 'foil']): return 1
    if any(k in t for k in ['bathroom', 'soap', 'toothbrush', 'shampoo', 'toilet']): return 1
    if any(k in t for k in ['storage', 'box', 'container', 'bin']): return 1
    if any(k in t for k in ['candle', 'freshener', 'fragrance']): return 1
    if any(k in t for k in ['garden', 'pet', 'diy', 'tool', 'nail', 'screw']): return 1
    return 0

def process_data(input_file):
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
        
    master = []
    bucket_a = []
    bucket_bc = []
    
    for r in rows:
        st = r.get('SupplierTitle', '').strip()
        at = r.get('AmazonTitle', '').strip()
        
        # 1. Hard Exclusion
        if 'superior' in st.lower() or 'superior' in at.lower():
            continue
            
        ean_on = r.get('EAN_OnPage', '')
        ean_sup = r.get('EAN', '')
        ean_match = bool(ean_on and ean_sup and ean_on == ean_sup)
        
        # Parse financials
        def pf(k):
            try:
                v = float(r.get(k, ''))
                return v if not math.isnan(v) else None
            except:
                return None
                
        sales = pf('bought_in_past_month')
        profit = pf('NetProfit')
        roi = pf('ROI')
        sp_sup = pf('SupplierPrice_incVAT')
        sp_amz = pf('SellingPrice_incVAT')
        
        # Price-plausibility gate for EAN matches
        if ean_match and sp_sup and sp_amz and sp_amz > (sp_sup * 50):
            sim = s_ratio(st, at)
            if sim < 0.15:
                continue # Reject outright
                
        tier, conf, sim = determine_tier_and_confidence(ean_match, st, at)
        if tier == "REJECT":
            continue
            
        is_t1 = (tier == "T1")
        ean_status = "Confirmed" if is_t1 else "Not matched"
        val_req = "No" if is_t1 else "Yes"
        
        bucket = None
        reason = ""
        rationale = ""
        priority = "LOW"
        
        if profit is not None and profit > 0 and sales is not None and sales > 0:
            bucket = "A"
            reason = "Proven Demand"
            rationale = "Product has confirmed positive profit and active monthly sales."
            if sales >= 100 and profit >= 1.5: priority = "HIGH"
            elif sales >= 50 or profit >= 1.0: priority = "MEDIUM"
            
        elif profit is not None and profit > 0 and (sales is None or sales == 0):
            score = category_score(st)
            include = False
            
            if is_t1 and profit > 1.0:
                include, priority = True, "MEDIUM" if profit > 3 else "LOW"
                reason = "Confirmed Match Margin"
                rationale = "High margin EAN match; zero sales may be missing data or timing."
            elif is_t1 and score > 0:
                include, priority = True, "LOW"
                reason = "Evergreen Category"
                rationale = "EAN match in high baseline demand category."
            elif (tier in ["T2"]) and profit > 2.0 and score > 0:
                include, priority = True, "LOW"
                reason = "T2 High Margin Evergreen"
                rationale = "Likely match in stable category with enough margin buffer."
                
            if include:
                bucket = "B"
                
        elif sales is not None and sales >= 50 and profit is not None and profit <= 0 and profit > -3.0:
            include = False
            is_pack = any(w in at.lower() for w in ['pack', 'pk', 'set', 'twin', 'x', 'pairs'])
            
            if is_t1 and profit > -1.0:
                include, priority = True, "MEDIUM" if sales > 200 else "LOW"
                reason = "Near Breakeven T1"
                rationale = "Small price increase could flip to profit on confirmed item."
            elif is_t1 and is_pack:
                include, priority = True, "HIGH"
                reason = "Pack Variation T1"
                rationale = "Possible pack mismatch; high volume item."
            elif tier == "T2" and sales > 1000 and profit > -1.5:
                include, priority = True, "LOW"
                reason = "High Volume Margin Flip"
                rationale = "Massive volume; tiny fee adjustment makes it viable."
                
            if include:
                bucket = "C"
                
        if bucket:
            out_row = {
                'Supplier_Title': st,
                'Amazon_Title': at,
                'Match_Type': 'EAN' if is_t1 else 'Title',
                'Tier': tier,
                'EAN_Status': ean_status,
                'Sales': sales if sales is not None else 'Unknown',
                'Net_Profit': profit,
                'ROI': roi,
                'Bucket': bucket,
                'Inclusion_Reason': reason,
                'Rationale': rationale,
                'Confidence': conf,
                'Validation_Required': val_req,
                'Priority': priority,
                'Similarity': round(sim, 2)
            }
            master.append(out_row)
            if bucket == "A": bucket_a.append(out_row)
            else: bucket_bc.append(out_row)
            
    # Sort
    sort_key = lambda x: (
        0 if x['Bucket'] == 'A' else 1 if x['Bucket'] == 'B' else 2,
        0 if x['Priority'] == 'HIGH' else 1 if x['Priority'] == 'MEDIUM' else 2,
        -x['Net_Profit'] if x['Net_Profit'] is not None else 0
    )
    master.sort(key=sort_key)
    bucket_a.sort(key=sort_key)
    bucket_bc.sort(key=sort_key)
    
    return master, bucket_a, bucket_bc

if __name__ == '__main__':
    source = r'OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_ALL_linking_map_20260108_005639.csv'
    m, a, bc = process_data(source)
    
    print(f"Master: {len(m)}")
    print(f"Bucket A: {len(a)}")
    print(f"Bucket B: {len([x for x in m if x['Bucket'] == 'B'])}")
    print(f"Bucket C: {len([x for x in m if x['Bucket'] == 'C'])}")
    
    out_dir = Path("OUTPUTS/PRODUCTS_LISTS")
    out_dir.mkdir(exist_ok=True)
    
    fields = ['Supplier_Title', 'Amazon_Title', 'Match_Type', 'Tier', 'EAN_Status', 'Sales', 'Net_Profit', 'ROI', 'Bucket', 'Inclusion_Reason', 'Rationale', 'Confidence', 'Validation_Required', 'Priority', 'Similarity']
    
    for fn, data in [('efghousewares_jan8_master.csv', m), ('efghousewares_jan8_bucketA.csv', a), ('efghousewares_jan8_bucketBC.csv', bc)]:
        if not data: continue
        with open(out_dir / fn, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(data)
    print("Files saved successfully.")
